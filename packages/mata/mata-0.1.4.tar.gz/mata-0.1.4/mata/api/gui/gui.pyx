"""
The Gui module holds a few container classes for Gui objects to be drawn.

The GUIState is the main object, and holds one Gui and zero or more Overlays.

The Gui class holds gui objects and extra drawing logic for a single Gui.

The Overlay is similar to the Gui, except that it is designed for drawing over a Gui, without completely obscuring it.
"""

import pygame

class GUIState:
    """
    The GUIState class is used to represent the combined Gui and Overlay state for the window at any time.

    Unless only minor changes to the window need to be made (such as adding or removing a single overlay), the Game's GUIState should be changed to adjust the window, as this is logically easier to control and maintain as the game progresses.
    """
    def __init__(self, game):
        self.game = game

        #: The main Gui object for this GUIState.
        self.gui = None
        #: A list of additional overlays to be drawn over the main Gui of this GUIState.
        self.overlays = []

    def onResize(self, screen):
        """
        Resize the Gui and each overlay to suit the Pygame Surface, ``screen``.
        """
        # Resize the gui
        try:
            if self.gui:
                self.gui[1].onResize(screen)
        except AttributeError:
            pass
        # Resize each overlay
        for o, overlay in enumerate(self.overlays):
            try:
                self.overlays[o][1].onResize(screen)
            except AttributeError:
                pass

    def draw(self, mousePos):
        """
        Draw this GUIState to the given screen.

        ``mousePos`` represents the cursor position within the window.
        """
        # Draw the main gui
        if self.gui:
          self.gui[1].draw(mousePos)

        # Draw each of the active overlays
        for id, overlay in self.overlays:
            overlay.drawBackgroundLayer()
        for id, overlay in self.overlays:
            overlay.drawMiddleLayer(mousePos)
        for id, overlay in self.overlays:
            overlay.drawForegroundLayer(mousePos)

    def getButtons(self):
        """
        Return a list of all buttons in this GUIState.

        :returns: A list of Button objects.
        """
        # Get all overlay buttons
        overlayButtons = []
        for id, overlay in self.overlays:
            overlayButtons += overlay.buttons

        # Return the main gui buttons first, then the overlay ones
        return self.gui[1].buttons + overlayButtons

    def getOverlay(self, guiID):
        """
        Get an overlay instance from this GUIState, with an id of ``guiID``.

        :returns: An Overlay instance corresponding to ``guiID``, or None.
        """
        for id, overlay in self.overlays:
            if id == guiID:
                return overlay
        return None

    def openGui(self, guiID, *args):
        """
        Set the open Gui for this GUIState to the Gui with the id, ``guiID``.
        """
        self.gui = [guiID, self.game.modLoader.gameRegistry.guis[guiID](*args)]
        self.gui[1].onResize(pygame.display.get_surface())

    def openOverlay(self, guiID, *args):
        """
        Add an overlay with id, ``guiID``,  to be drawn to the screen.
        """
        if not self.isOverlayOpen(guiID):
            self.overlays.append([guiID, self.game.modLoader.gameRegistry.guis[guiID](*args)])
            self.overlays[-1][1].onResize(pygame.display.get_surface())

    def isOverlayOpen(self, guiID):
        """
        Return whether an overlay with id, ``guiID``, is open in this GUIState.

        :returns: True if overlay is open, False if not.
        """
        for overlay in self.overlays:
            if overlay[0] == guiID:
                return True
        return False

    def closeOverlay(self, guiID):
        """
        Close the overlay with the id, ``guiID``.
        """
        index = None
        for i, overlay in enumerate(self.overlays):
            if overlay[0] == guiID:
                del self.overlays[i]
                return
        print('[WARNING] Overlay is not currently open.')

class Gui:
    """
    The Gui class holds all of the information about drawing a certain screen/interface to the screen.

    This class can be overridden to adjust the logic of each of the draw steps, or drawable gui objects can be added to the corresponding lists to be drawn.

    A Gui can be opened with the openGui() method in the Game class, or by creating a new GUIState and applying the Gui to it.
    """
    def __init__(self):
        #: The Pygame surface of the window.
        self.screen = pygame.display.get_surface()
        #: A list of gui buttons to be drawn to this Gui.
        self.buttons = []
        #: A list of textboxes to be drawn to this Gui.
        self.textboxes = []
        #: A list of value bars to be drawn to this Gui.
        self.bars = []
        #: A list of value sliders to be drawn to this Gui.
        self.valSliders = []
        #: A list of gui itemslots to be drawn to this Gui.
        self.itemSlots = []
        #: A list of miscellaneous additional objects to be drawn to this Gui.
        self.extraItems = []
        #: The index of the currently selected textbox in this Gui.
        #: Keypress events will affect this textbox.
        self.currentTextBox = None

    def onResize(self, screen):
        """
        Resize each gui object in this Gui.
        """
        # Loop every field in the gui
        for field in dir(self):
            value = self.__getattribute__(field)
            # If it is a list, try to resize each object in it.
            if isinstance(value, list):
                for o, obj in enumerate(value):
                    try:
                        value[o].onResize(screen)
                    except AttributeError:
                        pass

    def draw(self, mousePos):
        """
        Draw this Gui to the screen.

        ``mousePos`` represents the cursor coordinates within the window.
        """
        self.screen = pygame.display.get_surface()
        self.drawBackgroundLayer()
        self.drawMiddleLayer(mousePos)
        self.drawForegroundLayer(mousePos)

    def drawBackgroundLayer(self):
        """
        Draw the background layer of this Gui.
        """
        pass

    def drawMiddleLayer(self, mousePos):
        """
        Draw the middleground layer of this Gui.

        ``mousePos`` represents the cursor coordinates within the window.
        """
        for slot in self.itemSlots:
            slot.draw(self.screen, mousePos)
        for item in self.extraItems:
            item.draw(self.screen, mousePos)
        for slider in self.valSliders:
            slider.draw(self.screen, mousePos)

    def drawForegroundLayer(self, mousePos):
        """
        Draw the foreground layer of this Gui.

        ``mousePos`` represents the cursor coordinates within the window.
        """
        for button in self.buttons:
            button.draw(self.screen, mousePos)
        for box in self.textboxes:
            box.draw(self.screen, mousePos)
        for bar in self.bars:
            bar.draw(self.screen, mousePos)

    def addItem(self, item):
        """
        Add ``item`` to be drawn in this Gui.

        :raises Exception: If ``item`` is not a drawable object.
        """
        if 'draw' not in dir(item):
            raise Exception('Invalid Item Being Added To Gui.')
        self.extraItems.append(item)

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has an attribute, called ``name``.

        :returns: True if this object has the attribute, ``name``, False if not.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

    def doKeyPress(self, event):
      """
      Handle a key press event.

      ``event`` is the Pygame SDL event representing the keypress.
      """
      pass

class Overlay(Gui):
    """
    The Overlay class is an unmodified child class of the Gui class, used to represent overlays to the Gui, as opposed to a base Gui.

    While Gui can be used for the exact same purpose, use of the Overlay class is preferred as it is semantically clearer.
    """
    pass

def scaleRect(rect, screen):
    """
    Scale ``rect`` to the size of ``screen``.

    ``rect`` is assumed to be scaled to suit a 1024x768 screen.

    ``rect`` must be either a list containing, [x, y] or [x, y, width, height].

    :returns: A rect list in the same order as ``rect``, but scaled accordingly.
    """
    rect = list(rect)

    w = screen.get_width()
    h = screen.get_height()

    # Calculate the x and y scaling coefficients
    x_coeff = w/1024
    y_coeff = h/768

    # Multiply the x and y positions by the respective coefficients
    try:
        rect[0] *= x_coeff
        rect[1] *= y_coeff
    except IndexError:
        print('[WARNING] Not enough values passed to scaleRect. Things may look strange.')
        return []

    # Attempt to multiply the width and height if the input rect is a full rect, not position
    try:
        rect[2] *= x_coeff
        rect[3] *= y_coeff
    except IndexError:
        pass

    # Floor all of the values and return
    return [int(a) for a in rect]

def scaleVal(val, screen):
    """
    Scale ``val`` to the size of ``screen``.

    ``val`` is multiplied by (width + height)/(1024 + 768)

    :returns: An scaled integer value, scaled accrding to ``screen``.
    """
    w = screen.get_width()
    h = screen.get_height()

    # Calculate the scaling coefficient
    coeff = (w + h)/(1792)

    # Multiply the value by the coefficient
    val *= coeff

    # Floor the value and return
    return int(val)
