"""
The Network module has classes for handling connections and packet communication between clients and the server.

Classes in this module should not need to be extended or subclassed, but can be if desired. These classes are designed to handle a vast range of possible scenarios and use cases.
"""

# Import the game's modules
import util
from api.packets import *

# Import the Python standard libraries
import socket
import math
import re
import time
import io
from threading import Thread
from multiprocessing import Process

class PacketHandler:
    """
    The class for processing Connections and transmitting and receiving packets. This class should handle all packets registered without modification.
    """
    def __init__(self, game, side, port=util.DEFAULT_PORT):
        #: The Game object instance.
        self.game = game
        #: The side of the connection which this PacketHandler is running on (SERVER or CLIENT).
        self.side = side
        #: Integer value of the port which this PacketHandler listens and talks over.
        self.port = port

        #: Dictionary of the Connection objects handled by this PacketHandler.
        self.connections = {}
        #: A list of registered packets that are safe to be executed and/or sent.
        self.safePackets = [
                            WorldUpdatePacket, LoginPacket,
                            DisconnectPacket, SyncPlayerPacket,
                            ResetPlayerPacket, InvalidLoginPacket,
                            SetupClientPacket, SendCommandPacket,
                            MountPacket, AttackPacket
                           ]

        #: The main Python socket used for communication in this PacketHandler.
        self.socket = socket.socket()

        # Bind the socket if the PacketHandler is server-side
        if side == util.SERVER:
            try:
                self.socket.bind(('0.0.0.0', self.port))
            except OSError:
                print('[ERROR] Previous server instance still clearing data. Please wait about 30 seconds')
                game.quit()
            connPoll = Thread(target=self.pollForConnections)
            connPoll.daemon = True
            connPoll.start()

    def connectToServer(self, address):
        """
        Connect the PacketHandler (Client-side) to a server bound at ``address``.

        :returns: Error message string or None.
        """
        self.socket = socket.socket()

        try:
            self.socket.connect((address, self.port))

        except socket.gaierror:
            return 'Invalid Hostname or IP Address'

        except ConnectionRefusedError:
            return 'Connection Refused By Server'

        except OSError:
            pass

        self.connections[max(self.connections, default=0) + 1] = Connection(self.socket, address)
        # Fork a connection handling thread
        t = Thread(target=self.handleConn, args=(max(self.connections, default=0),))
        t.daemon = True
        t.start()

        # Send a login packet
        self.sendToServer(LoginPacket(self.game.player))

    def pollForConnections(self):
        """
        Initiate server-side polling for clients' connection requests. Only polls for a number of connections equal to maxplayers value in config file.
        """
        self.socket.listen(util.MAX_PLAYERS)
        while True:
            conn, addr = self.socket.accept()
            self.connections[max(self.connections, default=0) + 1] = Connection(conn, addr)

            # Fork a connection handling thread
            t = Thread(target=self.handleConn, args=(max(self.connections, default=0),))
            t.daemon = True
            t.start()

    def getPacket(self, conn):
        """
        Get the bytes of a data packet from the socket in ``conn``.

        :returns: Bytestring of packet header, data and trailer.
        :raises ConnectionResetError: If null byte received during data reception.
        """
        # Initialise a buffer for bytes
        byteBuf = b'\x01'
        # Clear any rubbish bytes that fill up the connection
        currentByte = conn.recv(1)
        # Wait for Start-Of-Transmission byte
        while currentByte != b'\x01':
            if currentByte == b'':
                raise ConnectionResetError
            currentByte = conn.recv(1)

        # Start fetching the useful info
        # Get the packet type and part sections
        byteBuf += conn.recv(34)

        # Get the packet length section
        length = conn.recv(2)
        byteBuf += length
        length = int.from_bytes(length, 'big')

        # Get the packet data section
        buf = b''
        while len(buf) < length:
            buf += conn.recv(length - len(buf))

        byteBuf += buf

        # Get the checksum and End-Of-Transmission byte
        byteBuf += conn.recv(4)

        # If the packet is not the correct length, something strange has happened
        if len(byteBuf) != 41 + length:
            print(byteBuf)
            print(length)
            raise ConnectionResetError

        return byteBuf

    def parsePacket(self, data):
        """
        Parse the ``data`` bytestring and return the collected data as a dictionary.

        :returns: Dictionary with packet type, data length, part id and raw data of ``data``.
        :raises Exception: If the packet has been corrupted during transmission.
        """
        # Remove the control bytes
        data = data[1:-1]
        dataDictionary = {}

        try:
            # Pull the values from the byte string
            dataDictionary['type'] = data[:32].decode().strip()
            data = data[32:]
            dataDictionary['part'] = str(data[0]) + '/' + str(data[1])
            data = data[2:]
            dataDictionary['length'] = int.from_bytes(data[:2], 'big')
            data = data[2:]
            dataDictionary['data'] = data[:dataDictionary['length']]
            checksum = data[-3:]

        except IndexError:
            return {}

        # Compare the checksum
        toCompare = util.calcChecksum(dataDictionary['data'])
        if toCompare != checksum:
            raise Exception('Packet corrupted')

        return dataDictionary

    def handleConn(self, connIndex):
        """
        Handle received packets for connection object corresponding to ``connIndex``.
        """
        conn = self.connections[connIndex].connObj
        while True:
            # Receive the packet data
            try:
                data = self.getPacket(conn)

            except ConnectionResetError as e:
                print('ConnectionResetError')
                # Properly disconnect if the connection is reset from the other side
                if self.side == util.CLIENT:
                    self.game.fireEvent('onDisconnect', 'Server Connection Reset')

                else:
                    try:
                        self.game.fireEvent('onDisconnect', self.connections[connIndex].username)
                    except KeyError:
                        # Another thread has already disconnected this one
                        return

                return

            except UnicodeDecodeError:
                pass

            # Parse the byte data of the packet
            try:
                dataDictionary = self.parsePacket(data)

            except Exception as e:
                print(e)
                continue

            # print('Received packet:', dataDictionary['type'])

            # Handle the packet asynchronously
            t = Thread(target=self.handlePacket, args=(dataDictionary, connIndex))
            t.daemon = True
            t.start()

    def handlePacket(self, dataDictionary, connIndex):
        """
        Handle a received packet from the connection at ``connIndex``, containing the data in ``dataDictionary``.
        """
        # Loop through the registered packets and handle the received data accordingly
        for packet in self.safePackets:
            if packet.__name__ == dataDictionary['type']:
                try:
                    # Fetch the current buffer for this packet type
                    try:
                        # This just quits quietly, it doesn't actually help. The socket seems to close for no apparent reason.
                        # TODO
                        parts = self.connections[connIndex].multipartBuffer.get(dataDictionary['type'], [])
                    except KeyError:
                        return

                    packetNum, size = [int(a) for a in dataDictionary['part'].split('/')]

                    # If it's the first part, initialise the parts buffer for this packet type
                    if parts == []:
                        parts = ['' for a in range(size)]

                    # Fill in the part in the buffer
                    try:
                        parts[packetNum - 1] = dataDictionary['data']
                    except IndexError:
                        print(packetNum,'/',size)

                    # Update the connection object's buffer
                    self.connections[connIndex].multipartBuffer[dataDictionary['type']] = parts

                    # Check if the buffer is filled (all parts of the packet have been received)
                    bufferData = list(parts)
                    if all(bufferData):
                        # Replace the data with the bufferData if required
                        if bufferData:
                            dataDictionary['data'] = b''.join(bufferData)

                            # Clear the packet buffer
                            del self.connections[connIndex].multipartBuffer[dataDictionary['type']]

                        # Initialise the packet, and handle it accordingly
                        try:
                            p = packet()
                            p.fromBytes(dataDictionary['data'])

                            # Pass the connection list in if a login packet
                            if packet.__name__ in ['LoginPacket', 'SetupConnPacket']:
                                response = p.onReceive(self.connections[connIndex], self.side, self.game, self.connections)
                            else:
                                response = p.onReceive(self.connections[connIndex], self.side, self.game)

                        except Exception as e:
                            print('Packet unable to be handled correctly.')
                            print('Error is:', e)
                            return

                        self.game.fireEvent('onPacketReceived', p)

                        # Send packet(s) in response to the received packet
                        if response:
                            # Send any required response and reset the receive size
                            if isinstance(response, list):
                                for res in response:
                                    self.connections[connIndex].sendPacket(res)
                            else:
                                self.connections[connIndex].sendPacket(response)
                    break
                except KeyError as e:
                    print(dataDictionary)
                    return

    def closeConnection(self, username=''):
        """
        Close the connection connected to user, ``username``, on server-side or all connections on client-side.
        """
        if self.side == util.SERVER and username:
            # Loop the connections and find a connection matching the username
            for conn in self.connections:
                if self.connections[conn].username == username:
                    # Close the socket object and delete the connection object from memory
                    try:
                        self.connections[conn].connObj.shutdown(socket.SHUT_RDWR)

                    except OSError:
                        self.connections[conn].connObj.close()

                    try:
                        del self.connections[conn]
                    except KeyError:
                        pass
                    return

        elif self.side != util.SERVER:
            keys = list(self.connections.keys())
            for conn in keys:
                # Close the socket object and delete the connection object from memory
                try:
                    try:
                        self.connections[conn].connObj.shutdown(socket.SHUT_RDWR)

                    except OSError:
                        self.connections[conn].connObj.close()

                    del self.connections[conn]
                except KeyError:
                    continue

    def registerPacket(self, packetClass):
        """
        Register ``packetClass`` for use in the PacketHandler.
        """
        self.safePackets.append(packetClass)

    def isPacketSafe(self, packet):
        """
        Return if ``packet`` has been registered in the PacketHandler.
        """
        return any([isinstance(packet, a) for a in self.safePackets])

    def checkClientPacket(self, packet):
        """
        Check if ``packet`` is valid to be sent to the client.

        :returns: 'error' if invalid, None if valid.
        """
        if not self.isPacketSafe(packet):
            # Reject the packet
            print('[ERROR] Packet was not sent to clients because it was not registered.')
            print(packet)
            return 'error'

        if self.side == util.CLIENT:
            print('[WARNING] Cannot send a packet to clients from a client runtime!')
            return 'error'

    def checkServerPacket(self, packet):
        """
        Check if ``packet`` is valid to be sent to the server.

        :returns: 'error' if invalid, None if valid.
        """
        if not self.isPacketSafe(packet):
            # Reject the packet
            print('[ERROR] Packet was not sent to server because it was not registered.')
            print(packet)
            return 'error'

        if self.side == util.SERVER:
            print('[WARNING] Cannot send a packet to server from a server runtime!')
            return 'error'

    def sendToAll(self, packet):
        """
        Send ``packet`` object on all Connections.
        """
        if self.checkClientPacket(packet):
            return

        # Loop and send the packet to each connection
        try:
            for conn in self.connections.values():
                self.sendToPlayer(packet, conn.username)

        except RuntimeError:
            # Bail out if a client disappears during the transfer
            return

    def sendToNearby(self, packet, username, radius=16):
        """
        Send ``packet`` to all players within a distance of `radius`` of player, ``username``.
        """
        if self.checkClientPacket(packet):
            return

        player = self.game.getPlayer(username)
        pos = player.pos
        dim = player.dimension

        # Loop all players and find the distance to the given player
        for p in self.game.getWorld(dim).getPlayersNear(pos, radius):
            self.sendToPlayer(packet, p.name)

    def sendToPlayer(self, packet, username):
        """
        Send ``packet`` to a client connected on ``username``.
        """
        if self.checkClientPacket(packet):
            return

        for conn in self.connections.values():
            if conn.username == username:
                conn.sendPacket(packet)
                return

    def sendToServer(self, packet):
        """
        Send ``packet`` to the connected server.
        """
        if self.checkServerPacket(packet):
            return

        try:
            self.connections[1].sendPacket(packet)
        except KeyError:
            print(packet)
            return

class GamePacketHandler(PacketHandler):
    """
    A subclass of the PacketHandler class representing the default PacketHandler in the Game instance.
    """
    def __init__(self, game, side):
        super().__init__(game, side, util.DEFAULT_PORT)

class Connection:
    """
    The class for holding data associated with a connection between a client and server engine instance.
    """
    def __init__(self, conn, addr):
        #: The username of the player on the other end of this connection.
        self.username = ''
        #: The Python socket object for this connection.
        self.connObj = conn
        #: The remote IP address of the device on the other end of this connection.
        self.address = addr

        #: A buffer for temporarily holding data for parts of a fragmented packet.
        self.multipartBuffer = {}

    def __repr__(self):
        return 'Connection(username={}, connObj={})'.format(self.username, self.connObj.fileno())

    def sendPacket(self, packet):
        """
        Send ``packet`` over this connection's socket.
        """
        # print('Sending packet: '+packet.__class__.__name__)

        # Initialise a new buffer, and write the packet byte data to it
        buf2 = io.BytesIO()
        packet.toBytes(buf2)
        packetString = buf2.getvalue()

        # Split the packet if required
        dataSize = len(packetString)
        dataList = [packetString[a:a+950] for a in range(0, dataSize, 950)]

        if dataList == []:
            dataList.append(b'')

        for p, part in enumerate(dataList):
            # Format the partitioning information correctly
            partDetail = (p + 1).to_bytes(1, 'big') + len(dataList).to_bytes(1, 'big')

            # Prepare the packet buffer
            buf = io.BytesIO()

            # Write Start-Of-Transmission, Packet type, then part info
            packetType = packet.__class__.__name__

            # Check for packet name overflow
            if len(packetType) > 32:
                raise Exception('[ERROR] Packet name longer than 32 characters')

            # Pad the packet name
            packetType = ' ' * (32 - len(packetType)) + packetType

            # Write the header of the packet
            buf.write(b'\x01' + packetType.encode() + partDetail)

            # Write the length
            buf.write(len(part).to_bytes(2, 'big'))

            # Write the actual data
            buf.write(part)

            # Calc then write the checksum
            buf.write(util.calcChecksum(part) + b'\x17')

            # Run error checks here to stop the server from crashing
            try:
                # Sanitise and send the two packets one after the other
                self.connObj.send(buf.getvalue())

            except Exception as e:
                if isinstance(e, ConnectionResetError):
                    # The client might still be connected
                    print('[ERROR] The Packet Failed To Send For Some Reason.')

                elif isinstance(e, BrokenPipeError):
                    # The client is completely disconnected
                    print('[WARNING] The Client Has Disconnected Badly. Clearing Connection...')
                    # Disconnect the client
                    self.connObj.close()
                    del self
                    return

                else:
                    if str(e) == "[Errno 9] Bad file descriptor":
                        print('Bad File descriptor')
                        return

                    print('[ERROR] An Error Occurred! ' + str(e))
