"""
game.py
A module containing the main game object/class
"""

# Import the standard libraries
import time
import multiprocessing
import socket
import sys
import os

if 'SERVER' not in sys.argv:
    import pygame
    pygame.init()
    from api.gui.gui import GUIState

# Import the game's modules
import util
import mod
from api.entity import Player
from api import network
from api.packets import *

class Game:
    """
    A class to hold all of the elements of the game together
    """
    def __init__(self, argHandler):
        # Initialise the child process value
        self.child = None
        #Initilise the port handling variable
        self.lastUsedPort = util.DEFAULT_PORT

        # Load mods and process cmd args
        self.modLoader = mod.ModLoader(self)
        self.processCmdArgs(argHandler)
        self.args = argHandler

        # Initialise the GUI variables
        self.currentGUIState = None
        self.prevGUIState = None

        # Set up the window, and the window icon
        if self.args.getRuntimeType() != util.SERVER:
            pygame.display.set_mode(util.SCREEN_SIZE, util.DISPLAY_FLAGS)
            pygame.display.set_icon(pygame.image.load('icon.png').convert_alpha())

        # Load all of the registered mods
        self.modLoader.loadRegisteredMods()

        # Create a default packetPipeline for the game instance
        self.packetPipeline = network.GamePacketHandler(self, self.args.getRuntimeType())

        if self.args.getRuntimeType() != util.SERVER:
            # Set the world and player up
            self.world = self.getWorld(0)
            self.dimensionId = 0
            self.player = Player()

            # Store a blank texture resource
            surf = pygame.Surface((40, 40)).convert_alpha()
            surf.fill(pygame.Color(255, 255, 255, 0))
            self.modLoader.gameRegistry.resources['tile_null_obj'] = surf

    def quit(self):
        """
        Safely disconnect all players, unload the mods and quit the game
        """
        # Terminate the child server process if running a combined game
        if self.child:
            # Ask the process to die nicely...
            self.child.terminate()
            if self.child.is_alive():
                # o_o
                # -_-
                # Drastic times call for drastic measures...
                if sys.platform == 'linux':
                    os.system('kill -KILL {}'.format(self.child.pid))
        if self.args.getRuntimeType() != util.SERVER:
            pygame.quit()
        sys.exit()

    def run(self):
        """
        Run the game after initialising all of the mods
        """
        self.fireEvent('onGameLaunch')
        self.tick = 0
        self.deltaTime = 0
        # Run at 30 ticks per second
        while True:
            self.tick += 1
            # Get the start time of the tick
            startTickTime = time.time()

            # Tick the world object
            for d in self.modLoader.gameRegistry.dimensions.keys():
                world = self.getWorld(d)
                if world and self.args.getRuntimeType() == util.SERVER:
                    # If there are players in the world, update the world every tick
                    if world.players:
                        world.tickUpdate(self)
                    elif (self.tick + d)%(5 * util.FPS) == True:
                        # Fuzzy/slow logic if there are no players inside
                        world.tickUpdate(self)

            # Trigger all of the onTick events
            self.fireEvent('onTick', self.deltaTime, self.tick)

            # If running a client side game then do some extra things
            if self.args.getRuntimeType() != util.SERVER:
                # Check for dimension change
                if self.dimensionId != self.player.dimension:
                    self.fireEvent('onDimensionChange', self.player, self.player.dimension, dimensionId)
                    self.dimensionId = self.player.dimension
                    self.world = self.getWorld(self.player.dimension)

                # Get the mouse position
                pos = pygame.mouse.get_pos()

                # Draw the client game
                self.drawClientGame(pos)

                # Get the current gui object
                currentGui = self.getGui()

                # Handle the pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()

                    elif currentGui:
                        if event.type == pygame.VIDEORESIZE:
                            oldSurface = pygame.display.get_surface().copy()
                            width = min(max(400, event.w), 65535)
                            height = min(max(300, event.h), 49151)
                            pygame.display.set_mode((width, height), util.DISPLAY_FLAGS)
                            pygame.display.get_surface().blit(oldSurface, [0, 0])
                            pygame.display.flip()
                            # Fire an onResize call to rescale the gui
                            self.currentGUIState.onResize(pygame.display.get_surface())

                        elif event.type == pygame.KEYDOWN:
                            # Handle a keypress on the gui
                            if currentGui[1].currentTextBox is not None:
                                currentGui[1].textboxes[currentGui[1].currentTextBox].doKeyPress(event)
                            currentGui[1].doKeyPress(event)
                            # If the keypress is not applicable to the gui, revert to the overlays
                            for i, overlay in enumerate(self.getOverlays()):
                                self.getOverlays()[i][1].doKeyPress(event)

                            # Finally, trigger any registered event functions
                            self.fireEvent('onKeyPress', event)

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            pressed = pygame.mouse.get_pressed()
                            # Handle a mouse click on buttons
                            if self.getGUIState() and pressed[0]:
                                for button in self.getGUIState().getButtons():
                                    if button.isHovered(pos) and button.enabled:
                                        button.onClick(self)

                            # Then, handle a mouse click on a text box
                            if currentGui and pressed[0]:
                                currentGui[1].currentTextBox = None
                                for t, textbox in enumerate(currentGui[1].textboxes):
                                    if textbox.isHovered(pos):
                                        currentGui[1].currentTextBox = t

                            # Finally, trigger any registered event functions
                            self.fireEvent('onMouseClick', pos, pressed, event)

            # Get the time that the tick took to run
            self.deltaTime = time.time() - startTickTime
            # Sleep if running faster than preset tps/fps
            if self.deltaTime < 1/util.FPS:
                time.sleep((1/util.FPS) - self.deltaTime)
                self.deltaTime = 1/util.FPS

    def drawClientGame(self, pos):
        """
        Draw the game to the pygame display
        """
        pygame.display.get_surface().fill((255, 255, 255))

        # Draw the GUIState to screen
        if self.currentGUIState:
            self.currentGUIState.draw(pos)

        # Draw the graphics to the screen
        pygame.display.flip()

    def getModInstance(self, modName):
        """
        Return an instance of a mod with the given name
        """
        return self.modLoader.mods.get(modName)

    def fireEvent(self, eventType, *args):
        """
        Fire an event on the event bus
        """
        if eventType == 'onAttack':
            funcs = self.modLoader.gameRegistry.EVENT_BUS.get(eventType, [])
            if not len(args):
                print('[ERROR] onAttack event requires at least one argument, the base damage.')
                return
            baseDamage = args[0]
            for func in funcs:
                baseDamage = func(self, *args)
            return baseDamage

        for func in self.modLoader.gameRegistry.EVENT_BUS.get(eventType, []):
            try:
                func(self, *args)
            except Exception as e:
                print('[WARNING] Event hook, {}, threw an error, {}:{}'.format(func.__name__, e.__class__.__name__, e))

    def fireCommand(self, text, username):
        """
        Fire a command on either side
        """
        # split the command and arguments
        command, *args = text.split()
        # Fetch the command class
        commandClass = self.modLoader.gameRegistry.commands.get(command)
        if commandClass is None:
            commandClass = self.modLoader.gameRegistry.commands.get('/failedCommand')
            args = [command]
        # Instantiate the command
        self.fireEvent('onCommand', commandClass, username, args)
        commandClass = commandClass(self)
        commandClass.run(username, *args)

    def getGui(self):
        """
        Return the currently open gui
        """
        if self.currentGUIState:
            return self.currentGUIState.gui
        return None

    def getOverlays(self):
        """
        Return a list of the currently open overlays
        """
        if self.currentGUIState:
            return self.currentGUIState.overlays
        return []

    def getGUIState(self):
        """
        Return the current GUIState of the game
        """
        return self.currentGUIState

    def loadGUIState(self, guiState):
        """
        Load a given GUIState into the game
        """
        self.prevGUIState = self.currentGUIState
        self.currentGUIState = guiState

    def openGui(self, guiID, *args):
        """
        Open the GUI with the given id for this client
        """
        if self.currentGUIState:
            self.prevGUIState = self.currentGUIState

        newGUIState = GUIState(self)
        self.currentGUIState = newGUIState
        self.currentGUIState.openGui(guiID, *args)

    def openOverlay(self, guiID, *args):
        if self.currentGUIState:
            self.currentGUIState.openOverlay(guiID, *args)

    def restoreGui(self):
        """
        Restore the previous GUI state for the client
        """
        if self.prevGUIState:
            self.currentGUIState = self.prevGUIState

        self.prevGUIState = None

    def closeGui(self):
        """
        Close the currently open gui
        """
        self.prevGUIState = self.currentGUIState
        self.currentGUIState = None

    def getDimension(self, dimensionId):
        """
        Get the DimensionHandler for the given dimension id
        """
        return self.modLoader.gameRegistry.dimensions.get(dimensionId)

    def getWorld(self, dimensionId):
        """
        Get the world object corresponding to the given dimension id
        """
        dimension = self.getDimension(dimensionId)
        if dimension:
            return dimension.getWorldObj()
        return None

    def getEntity(self, uuid):
        """
        Get an entity object by its uuid
        """
        # Loop each dimension
        for dimensionId in self.modLoader.gameRegistry.dimensions:
            world = self.getWorld(dimensionId)
            # Loop the entities in the dimension
            for entity in world.entities:
                # Check if its the correct one, and if so, return it
                if entity.uuid == uuid:
                    return entity
        return None

    def getVehicle(self, uuid):
        """
        Get a vehicle object by its uuid
        """
        # Loop each dimension
        for dimensionId in self.modLoader.gameRegistry.dimensions:
            world = self.getWorld(dimensionId)
            # Loop the vehicles in the dimension
            for entity in world.vehicles:
                # Check if its the correct one, and if so, return it
                if entity.uuid == uuid:
                    return entity
        return None

    def getPlayer(self, username):
        """
        Get a given player in the world player list
        """
        # If a player object is accidentally passed in, run comparison with the username
        if isinstance(username, Player):
            username = username.name

        # Check the main player if running on the client
        if self.args.getRuntimeType() != util.SERVER:
            if self.player.name == username:
                return self.player

        # Iterate the dimensions and find the player
        for d in self.modLoader.gameRegistry.dimensions:
            for player in self.getWorld(d).players:
                if player.name == username:
                    return player
        return None

    def setPlayer(self, player):
        """
        Set the player on the server
        """
        # If the player does not exist, append them to the required dimension's player list
        if not self.getPlayer(player.name):
            self.getWorld(player.dimension).players.append(player)
            return

        # Fetch the dimension, iterate the players, and replace the corresponding object
        world = self.getWorld(player.dimension)
        for p, play in enumerate(world.players):
            if play.name == player.name:
                world.players[p] = player
                return

    def establishConnection(self, address):
        """
        Connect the default pipeline to the server
        """
        self.packetPipeline.connectToServer(address)

    def getOpenPort(self):
        """
        Return an available port for a custom PacketHandler to use
        """
        self.lastUsedPort += 1
        return self.lastUsedPort

    def processCmdArgs(self, argHandler):
        """
        Process the command line arguments for the game
        """
        lines = [line.strip() for line in open('modlist') if line and line[0] != '#']

        section = None
        side = argHandler.getRuntimeType()
        for line in lines:
            # Switch section here
            if line.startswith('//'):
                line = line[2:]
                if line == 'end':
                    section = None
                else:
                    section = line

            # Schedule the game critical mods to be loaded here
            elif line.startswith('-'):
                if section == 'Server' and side == util.SERVER:
                    self.modLoader.registerModByName(line[1:])
                elif section == 'Client' and side != util.SERVER:
                    self.modLoader.registerModByName(line[1:])

            # Schedule the loading of the extra custom mod
            # if they aren't disabled in the command line.
            elif argHandler.getShouldLoadCustomMods():
                if section == 'Server' and side == util.SERVER:
                    self.modLoader.registerModByName(line[1:])
                elif section == 'Client' and side != util.SERVER:
                    self.modLoader.registerModByName(line[1:])

        if argHandler.getRuntimeType() == util.COMBINED:
            # Fork a new Server process, then set to connect to it immediately
            serverProcess = multiprocessing.Process(target=forkServer, args=(argHandler,))
            serverProcess.daemon = True
            self.child = serverProcess
            serverProcess.start()

            argHandler.results['address'] = socket.getfqdn()

        # Set the world generation seed
        self.modLoader.gameRegistry.seed = argHandler.getSeed()

        # Print a helpful message
        print('Starting Game in {} Mode'.format({util.SERVER : 'SERVER',
                                                 util.CLIENT : 'CLIENT',
                                                 util.COMBINED : 'COMBINED'
                                                }[argHandler.getRuntimeType()]))

def forkServer(argHandler):
    """
    Fork a new process to run the server in the background
    """
    argHandler.results['runtimeType'] = util.SERVER
    serverRuntime = Game(argHandler)
    serverRuntime.run()
