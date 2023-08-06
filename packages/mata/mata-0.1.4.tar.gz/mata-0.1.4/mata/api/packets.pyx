"""
The Packet module contains a framework for defining raw binary packets for client to server communication.

The Packet class is the base class, with each other class performing a single low level operation common to most games created in the engine.
"""

from api.entity import Player
from api.vehicle import Vehicle
from api.dimension import WorldMP
from api.biome import TileMap
from api.item import Item

import util

from datetime import datetime
import random
import time
import math

class Packet:
    """
    The main parent class for defining a data packet in the M.A.T.A engine. Packets must be registered with the appropriate PacketHandler instances before they can be used.
    """
    def toBytes(self, buf):
        """
        Convert the packet's data to a bytestring and write it to ``buf``.

        At least one byte must be written to ``buf`` or the packet will not be sent.

        :raises NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError('toBytes method is empty in a packet class!')

    def fromBytes(self, data):
        """
        Read the bytestring, ``data``, and convert it to a the packet's data.

        :raises NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError('fromBytes method is empty in a packet class!')

    def onReceive(self, connection, side, game):
        """
        Run any required logic upon receiving the packet, using the packet's data.

        :raises NotImplementedError: If not overridden in a subclass.
        :returns: Packet object or list of Packet objects to be sent back to the sender of this Packet as a response.
        """
        raise NotImplementedError('onReceive method is empty in a packet class!')

class LoginPacket(Packet):
    """
    A Packet for confirming a new connection from a client to server and defining a new user for the connection.
    """
    def __init__(self, player=None):
        #: The player object defined on the client to be logged in on the server
        self.player = player

    def toBytes(self, buf):
        buf.write(self.player.toBytes())

    def fromBytes(self, data):
        self.player = Player.fromBytes(data)

    def onReceive(self, connection, side, game, connections):
        """
        Verify that the player can login, and log them in if possible.

        :returns: InvalidLoginPacket() upon login failure or SetupClientPacket and ResetPlayerPacket upon success.
        """
        # Stop one player from being controlled by two computers simultaneously
        for conn in connections:
            if connections[conn].username == self.player.name:
                print('existing connection found')
                return InvalidLoginPacket()

        if self.player.name in ['local', 'global']:
            return InvalidLoginPacket()

        connection.username = self.player.name

        # Add the player
        self.player = game.getWorld(0).addPlayer(game, self.player)

        # Fire a login event
        game.fireEvent('onPlayerLogin', self.player)

        # Sync the player back to the Client
        return [
                SetupClientPacket(game.getDimension(0).getBiomeSize(), game.modLoader.gameRegistry.seed),
                ResetPlayerPacket(self.player)
               ]

class SetupClientPacket(Packet):
    """
    A Packet for setting up the main dimension values on the client from the server.
    """
    def __init__(self, biomeSize=0, seed=0):
        #: The generation seed (as an integer) for the main dimension.
        self.seed = seed
        #: The biomeSize field for the main dimension.
        self.size = biomeSize

    def toBytes(self, buf):
        buf.write(self.size.to_bytes(1, 'big'))
        buf.write(str(round(self.seed, 5)).encode())

    def fromBytes(self, data):
        self.size = data[0]
        self.seed = float(data[1:].decode())

    def onReceive(self, connection, side, game):
        """
        Set the seed and biomeSize for the main dimension on the client.
        """
        # Set the seed and biomesize
        game.modLoader.gameRegistry.seed = self.seed
        game.getDimension(0).biomeSize = self.size
        # Fire the login event
        game.fireEvent('onPlayerLogin', game.player)

class ResetPlayerPacket(Packet):
    """
    A Packet for resetting player attributes on the client.
    """
    def __init__(self, player='', pos=True, hp=True, dimension=True, exp=True, bits=0):
        #: The player object being synchronised to the client.
        self.player = player

        # If the bits arguments has been set, use that as the bits
        if bits:
            #: A collection of bits (stored as an integer) used to determine what values are replaced on the client.
            #:
            #: The 8 bit corresponds to the exp attribute.
            #: The 4 bit corresponds to the dimension attribute.
            #: The 2 bit corresponds to the health attribute.
            #: The 1 bit corresponds to the pos attribute.
            self.bits = bits
            return

        # Otherwise, create the bits value from the boolean parameters.
        pos, hp, dimension, exp = int(pos), int(hp) * 2, int(dimension) * 4, int(exp) * 8
        self.bits = pos | hp | dimension | exp

    def toBytes(self, buf):
        buf.write(self.bits.to_bytes(1, 'big') + self.player.toBytes())

    def fromBytes(self, data):
        self.bits = data[0]
        playerData = data[1:]
        self.player = Player.fromBytes(playerData)

    def onReceive(self, connection, side, game):
        """
        Sync the player attributes based on the bits value.
        """
        # Sync the player object on the client
        if self.bits & 1:
            game.player.pos = self.player.pos
        if self.bits & 2:
            game.player.health = self.player.health
        if self.bits & 4:
            game.player.dimension = self.player.dimension
        if self.bits & 8:
            game.player.exp = self.player.exp

class SyncPlayerPacket(Packet):
    """
    A Packet for requesting the client player status to be synchronised to the server.
    """
    def __init__(self, player=''):
        #: The player object being synchronised to the server.
        self.player = player

    def toBytes(self, buf):
        buf.write(self.player.toBytes())

    def fromBytes(self, data):
        self.player = Player.fromBytes(data)

    def onReceive(self, connection, side, game):
        """
        Check the validity of the changes to the client player and synchronise them.
        """
        # Update their status on the server if everything is ok
        # Reset them if it's not
        if connection.username and self.player.name != connection.username:
            # This is someone trying to mess with another player, do nothing
            return

        playerList = game.getWorld(self.player.dimension)
        serverPlayer = game.getPlayer(self.player.name)
        if serverPlayer is None:
            return

        # Get the deltaTime, and deltaTicks since last synchronisation
        if isinstance(serverPlayer.synced, datetime):
            deltaTime = (datetime.now() - serverPlayer.synced).total_seconds()
        else:
            deltaTime = 4

        # Write the new sync time (in case we need to reset)
        serverPlayer.synced = datetime.now()

        # Check if the player's motion is not greater than a certain threshold
        threshold = serverPlayer.getSpeed(game) * (deltaTime + 0.1) + 0.0005 # <- Add this tiny extra bit to account for float imprecision
        if max([abs(self.player.pos[a] - serverPlayer.pos[a]) for a in (0, 1)]) > threshold:
            return ResetPlayerPacket(serverPlayer)

        # Sync the player object on the server
        serverPlayer.setPos(self.player.pos)
        serverPlayer.dimension = self.player.dimension

class MountPacket(Packet):
    """
    A Packet to synchronise a player mounting a vehicle to the server.
    """
    def __init__(self, vehicle=None, player=None):
        if isinstance(vehicle, Vehicle):
            vehicle = vehicle.uuid
        if isinstance(player, Player):
            player = player.name

        #: The vehicle being mounted.
        self.entity = str(vehicle)
        #: The player object corresponding to the player mounting the entity.
        self.player = str(player)

    def toBytes(self, buf):
        buf.write(self.entity.encode() + b'|')
        buf.write(self.player.encode())

    def fromBytes(self, data):
        self.entity, self.player = data.decode().split('|')

    def onReceive(self, connection, side, game):
        """
        Verify the action, and modify the mountings accordingly.
        """
        # Set up the entity and player values
        if self.entity != 'None':
            self.entity = game.getVehicle(int(self.entity))
        else:
            self.entity = None

        self.player = game.getPlayer(self.player)

        # Adjust on the client
        if side != util.SERVER:
            # Accept the changes without question
            game.player.ridingEntity = self.entity
            if self.entity is not None:
                success = self.entity.mountRider(game.player, game)
                game.fireEvent('onPlayerMount', self.player, self.entity, success, 'mount')
            else:
                success = self.entity.unmountRider(game.player)
                game.fireEvent('onPlayerMount', self.player, self.entity, success, 'dismount')

        # Adjust on the server
        elif side == util.SERVER and self.player:
            # Attempt to connect a player to a vehicle
            if self.entity is not None:
                # Calculate the distance between the player and vehicle
                pos = [(self.entity.pos[a] - self.player.pos[a])**2 for a in [0, 1]]
                dist = sum(pos)**.5
                # Check for equal dimension and distance
                if self.entity.dimension == self.player.dimension and dist < 8:
                    print('Mounting player {} to vehicle {}'.format(self.player.name, self.entity.uuid))
                    # If all prerequisites are met, connect the player to the vehicle
                    success = self.entity.mountRider(self.player, game)
                    game.fireEvent('onPlayerMount', self.player, self.entity, success, 'mount')
                else:
                    return MountPacket()

            elif self.player.ridingEntity:
                print('dismounting player from entity')
                # Dismount the entity/player
                success = game.getVehicle(self.player.ridingEntity).unmountRider(self.player)
                game.fireEvent('onPlayerMount', self.player, self.entity, success, 'dismount')

class WorldUpdatePacket(Packet):
    """
    A Packet to update the world on the client with the changes from the server.
    """
    def __init__(self, world=None, player=None):
        #: The world object to get update data about.
        self.world = world
        #: The player to send the update data to.
        self.player = player

    def toBytes(self, buf):
        buf.write(self.world.getUpdateData(self.player))

    def fromBytes(self, data):
        self.world = data

    def onReceive(self, connection, side, game):
        """
        Process the binary update data in the client-side world.
        """
        # Update the world on the Client side
        if game.world:
            game.world.handleUpdate(self.world, game)

class SendCommandPacket(Packet):
    """
    A Packet for transmitting a chat command between a client and server.
    """
    def __init__(self, text=''):
        #: The chat command's text value
        self.text = text

    def toBytes(self, buf):
        buf.write(self.text.encode())

    def fromBytes(self, data):
        self.text = data.decode()

    def onReceive(self, connection, side, game):
        """
        Adjust the command if required, then fire the command in the Game instance.
        """
        if self.text[0] != '/':
            self.text = '/message global ' + self.text
        game.fireCommand(self.text, connection.username)

class AttackPacket(Packet):
    """
    A Packet to perform an attack calculation on the server and adjust entity and player attributes accordingly.
    """
    def __init__(self, player=None, weapon=None):
        if isinstance(player, str):
            #: The player performing the attack.
            self.player = player
        elif player != None:
            self.player = player.name
        else:
            self.player = None

        #: The weapon being used to perform the attack.
        self.weapon = weapon

    def toBytes(self, buf):
        length = len(self.player).to_bytes(1, 'big')
        buf.write(length + self.player.encode())
        buf.write(self.weapon.toBytes())

    def fromBytes(self, data):
        length = data[0]
        self.player = data[1:length + 1].decode()
        self.weapon = data[length + 1:]

    def onReceive(self, connection, side, game):
        """
        Check for weapon and perform attack calculations.
        """
        # Decode the player and weapon data
        self.player = game.getPlayer(self.player)
        gameRegistry = game.modLoader.gameRegistry
        self.weapon = Item.fromBytes(gameRegistry.items.values(), gameRegistry.resources, self.weapon)

        # If the weapon isn't in their (correct) server-side inventory, just stop processing
        # if not self.player.inventory.checkWeapon(self.weapon):
        #     return

        # Calculate the direction the player is facing
        theta = util.calcDirection(self.player.pos, self.player.lastPos)

        # Find the entities within the weapon's range
        entitiesInRange = game.getWorld(self.player.dimension).getEntitiesNear(self.player.pos, self.weapon.range)
        players = game.getWorld(self.player.dimension).getPlayersNear(self.player.pos, self.weapon.range)
        players = [a for a in players if a.name != self.player.name]
        entitiesInRange += players

        # Then only keep those within the weapon's attack arc
        entitiesInArc = []
        for e in entitiesInRange:
            eTheta = util.calcDirection(e.pos, self.player.pos)
            if abs(theta - eTheta) >= self.weapon.spread:
                continue

            # Store entity, and knockback falloff
            falloff = (1 - (abs(theta - eTheta)/self.weapon.spread)**2)**(1/7)

            # Calculate and apply the knockback
            knockback = random.randint(self.weapon.knockback//2, self.weapon.knockback) * falloff
            deltaX = knockback * math.sin(eTheta * math.pi)
            deltaY = knockback * math.cos(eTheta * math.pi)

            pos = [e.pos[0] + deltaX, e.pos[1] + deltaY]
            e.setPos(pos)
            entitiesInArc.append(e)

        # Calculate and set the tickDamage value
        self.weapon.calcDamage(game, self.player.name, entitiesInArc)

class InvalidLoginPacket(Packet):
    """
    A Packet to inform a client of a failed attempt to login to a server.
    """
    def toBytes(self, buf):
        # Write a rubbish byte to ensure the packet sends correctly
        buf.write(b'a')

    def fromBytes(self, data):
        pass

    def onReceive(self, connection, side, game):
        pass

class DisconnectPacket(Packet):
    """
    A Packet to send a disconnection signal to a client or to the server.
    """
    def __init__(self, message='null'):
        #: A message to be sent with the disconnection signal.
        self.message = message

    def toBytes(self, buf):
        buf.write(self.message.encode())

    def fromBytes(self, data):
        self.message = data.decode()
        if self.message == 'null':
            self.message = ''

    def onReceive(self, connection, side, game):
        """
        Fire an onDisconnect event to handle disconnection.
        """
        if side == util.SERVER:
            game.fireEvent('onDisconnect', connection.username)
        else:
            game.fireEvent('onDisconnect', self.message)
