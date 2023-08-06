"""
The Command module includes the Command class, useful for creating chat commands.

New commands can be made by simply subclassing the Command class, and then modifying the run() method. After correct modification, the command need only be registered in the postLoad method of the Mod class.
"""

from api.packets import SendCommandPacket

import util

class Command:
    """
    The generic class for creating chat commands. Commands should be subclassed from this class, and then registered to an appropriate command string with the GameRegistry.
    """
    def __init__(self, game):
        #: A stored instance of the Game object
        self.game = game

    def run(self, username, *args):
        """
        Run the logic associated with this command.

        The side (Client or Server) which this method is being run at can be found with self.game.args.getRuntimeType()

        :raises NotImplementedError: If the method has not been overridden in a subclass.
        """
        raise NotImplementedError('[ERROR] A command has not been told to do anything')

class FailedCommand(Command):
    """
    A subclassed command for the default behaviour upon use of an incorrect command.
    """
    def run(self, username, *args):
        """
        Inform the player of the invalid command through a global message.
        """
        # Send a failure message back to the client
        self.game.packetPipeline.sendToPlayer(SendCommandPacket('/message global ' + args[0] + ' is not a valid command.'), username)
        return

class MessageCommand(Command):
    """
    A subclassed command for the default handling of chat messages.
    """
    def run(self, username, *args):
        """
        Redirect or relay the chat message to the appropriate clients if applicable.
        """
        # Redirect the message if on the server
        if self.game.args.getRuntimeType() == util.SERVER:
            pp = self.game.packetPipeline
            # Send messages back to one or more clients based on the message mode
            mode = args[0]
            args = [args[0], '<{}>'.format(username)] + list(args[1:])
            if mode == 'global':
                pp.sendToAll(SendCommandPacket('/message ' + ' '.join(args)))
            elif mode == 'local':
                pp.sendToNearby(SendCommandPacket('/message ' + ' '.join(args)), username)
            else:
                # Send /message <username> message here to the user
                # Send /message <user> message here to username
                pp.sendToPlayer(SendCommandPacket('/message ' + ' '.join(args)), username)
                pp.sendToPlayer(SendCommandPacket('/message {} {}'.format(username, ' '.join(args[1:]))), args[0])
