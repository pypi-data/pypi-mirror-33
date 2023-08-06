"""
The Gui Objects module provides a variety of premade, but lightly customisable graphical elements/objects which can be used to quickly prototype and create graphical interfaces with the M.A.T.A engine.

All elements are initialised through the constructor arguments, and drawn by calling the draw() method on them. All methods can be overridden by subclassing, but it is recommended for these elements to be mostly kept as they are (with the exception of the Button class, which must be overridden to add onClick logic).

Further information on the individual elements is detailed below.
"""

import pygame

from api.gui.gui import *
from api.item import Armour, ItemStack, NullItem

class Scrollbox:
    """
    This element provides a basic scrolling box, which can be drawn to like a Pygame surface, and scrolled using a built-in scroll bar.

    This class only provides a basic ``blit`` method for drawing, rather than the complex drawing functionality normally provided by Pygame. For additional functionality, the ``innerScreen`` field provides a standard Pygame surface for drawing.

    Please note that drawing using any method but the ``blit`` function will prevent the scrollbox from updating the scrolling height.
    """
    def __init__(self, rect):
        #: The current scroll offset of this Scrollbox, in pixels.
        self.scrollValue = 0
        #: The default width and height as a list. Resizing is done from this value.
        self.defaultRect = rect[:2]
        #: The width and height of this Scrollbox at any time.
        self.rect = self.defaultRect
        #: The default x and y position of this Scrollbox. Resizing is done from this value.
        self.defaultPos = rect[2:]
        #: The x and y position of this Scrollbox at any time.
        self.pos = self.defaultPos
        #: The maximum internal scroll height of this element, in pixels.
        #: This value is calculated automatically as elements are drawn into this Scrollbox
        self.maxHeight = 0
        #: The list of Pygame surfaces to be drawn on the next frame.
        #: This list is cleared at the end of each frame.
        self.objects = []
        #: The surface used as the inside of this Scrollbox.
        self.innerScreen = pygame.Surface(self.defaultRect).convert_alpha()

        sliderRect = [self.defaultPos[0] + int(rect[0] * 0.97), self.defaultPos[1] + 30, int(rect[0] * 0.025), rect[1] - 60]
        #: The scrollbar for this Scrollbox.
        self.scrollSlider = Slider(sliderRect, (0, 0, 0))

    def onResize(self, screen):
        """
        Resize this scrollbox to suit ``screen``.
        """
        self.rect = scaleRect(self.defaultRect, screen)
        self.pos = scaleRect(self.defaultPos, screen)
        self.scrollSlider.onResize(screen)

    def draw(self, screen, mousePos):
        """
        Draw this Scrollbox to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.

        Note that calling this function empties the ``objects`` list.
        """
        # Draw the innerscreen
        while self.objects:
            # Iterate the objects, and draw with scroll adjustment applied
            obj, pos = self.objects[0]
            pos = list(pos)
            pos[1] -= self.scrollValue
            self.innerScreen.blit(obj, pos)
            del self.objects[0]

        screen.blit(self.innerScreen, self.pos)

        self.innerScreen = pygame.Surface(self.rect).convert_alpha()

        # Then draw the slider onto it
        self.scrollSlider.draw(screen, mousePos)

        self.scrollValue = int(self.scrollSlider.value * self.maxHeight)

    def blit(self, surface, pos):
        """
        Draw ``surface`` to this scrollbox's inner screen surface, at the position, ``pos``.
        """
        try:
            self.rect[1]
        except AttributeError:
            return

        self.objects.append([surface, pos])
        testMaxHeight = pos[1] + surface.get_height() - self.rect[1]
        if testMaxHeight > self.maxHeight - 10 and testMaxHeight > 0:
            self.maxHeight = testMaxHeight

class ItemSlot:
    """
    This element provides a simple graphical slot for ItemStacks. It displays an Item's image inside a box, and dims when hovered over.

    ItemStacks should be placed into these slots with the setItem method, and all ItemStacks are accepted.
    """
    def __init__(self, game, item, pos, size):
        #: The default x and y position of this ItemSlot. Resizing is done from this value.
        self.defaultPos = [a + 3 for a in pos]
        #: The x and y position of this ItemSlot at any time.
        self.pos = self.defaultPos
        #: The GameRegistry's resource dictionary.
        self.resources = game.modLoader.gameRegistry.resources
        #: The colour for the overlay shown when the ItemSlot is hovered over.
        self.coverColour = (0, 0, 0)
        self.setItem(item)
        #: The Button element of this ItemSlot.
        self.button = Button(list(pos + [size, size]), '', True)

    def setItem(self, item):
        """
        Set the itemstack for this itemslot to ``item``.
        """
        self.item = item
        self.itemImage = self.item.getImage(self.resources)

    def onResize(self, screen):
        """
        Resize this itemslot to suit ``screen``.
        """
        self.button.onResize(screen)
        self.pos = scaleRect(self.defaultPos, screen)
        self.pos[1] += 1

    def draw(self, screen, mousePos):
        """
        Draw this ItemSlot to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.

        Note that calling this function empties the ``objects`` list.
        """
        # Draw the border of the itemslot
        self.button.draw(screen, [0, 0])

        # Draw the item image
        imageSize = [self.button.rect[2] - 5 for a in range(2)]
        if self.itemImage:
            imgRect = screen.blit(pygame.transform.scale(self.itemImage, imageSize), self.pos)

        tagColour = (0, 0, 0)

        if self.button.isHovered(mousePos):
            # Draw a semi transparent square over the itemslot
            square = pygame.Surface(imageSize)
            square.set_alpha(128)
            square.fill(self.coverColour)
            screen.blit(square, self.pos)
            tagColour = (255, 255, 255)

        # Draw the stackSize label
        font = pygame.font.Font('resources/font/main.ttf', imageSize[0]//3)
        text = font.render(str(self.item.stackSize), True, tagColour)
        tagPos = list(self.pos)
        tagPos[1] += imageSize[1] - text.get_height()
        tagPos[0] += text.get_height() * 1/10
        screen.blit(text, tagPos)

class ArmourSlot(ItemSlot):
    """
    This ArmourSlot element subclasses the ItemSlot element, and looks very similar. However, the hover overlay is a dull red, as opposed to gray, and the slot only accepts Armour-type ItemStacks. More details are below.
    """
    def __init__(self, game, item, pos, size):
        super().__init__(game, item, pos, size)
        self.coverColour = (153, 0, 0)

    def setItem(self, item):
        """
        Set the itemstack for this ArmourSlot to ``item``.

        Only ItemStacks containing an item which extends the Armour class can be placed in this slot.
        """
        self.itemImage = None
        self.item = ItemStack(NullItem(), 0)

        if not isinstance(item, Armour) and item.getRegistryName() != 'null_item':
            print('[ERROR] Non-armour item cannot be placed in ArmourSlot')
            return
        super().setItem(item)

class Slider:
    """
    This element is a simple slider. The slider allows a user to adjust the ``value`` field by sliding a circle along it.

    The size of the slider is set by ``rect``, and the colour of the bar of the slider can by controlled by ``colour``. The slider will automatically determine if it is a vertical or horizontal slider based on the value of ``rect``.

    Greater pixel values correspond to greater slider values, so a slider value will increase as the circle is moved downwards on vertical sliders, and rightwards on horizontal sliders.
    """
    def __init__(self, rect, colour):
        #: The default width and height as a list. Resizing is done from this value.
        self.defaultRect = rect
        #: The width and height of this Slider at any time.
        self.rect = self.defaultRect
        #: The percentage of this slider from left to right, or top to bottom. Expressed as a float between 0 and 1.
        self.value = 0

        #: The padding between the draggable bubble and the bar.
        self.pad = rect[2]//2 if rect[2] < rect[3] else rect[3]//2
        #: A boolean representing if this slider is a vertical slider or a horizontal slider.
        self.isVertical = self.pad == rect[2]//2

        if self.isVertical:
            #: The visible bar component of this slider element.
            self.bar = VertBar(rect, colour)
        else:
            self.bar = HorizBar(rect, colour)

    def onResize(self, screen):
        """
        Resize this slider to suit ``screen``.
        """
        self.rect = scaleRect(self.defaultRect, screen)
        self.bar.onResize(screen)

    def draw(self, screen, mousePos):
        """
        Draw this Slider to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        # Update the slider value if the mouse is dragging the circle
        if self.isHovered(mousePos) and pygame.mouse.get_pressed()[0]:
            if self.isVertical:
                self.value = abs(mousePos[1] - self.rect[1])/self.rect[3]
            else:
                self.value = abs(mousePos[0] - self.rect[0])/self.rect[2]

        # Draw the bar
        self.bar.draw(screen, mousePos)

        # Draw the circle over the top of the bar
        if self.isVertical:
            circlePos = [int(self.rect[0] + self.pad), int(self.rect[1] + self.rect[3] * self.value)]
        else:
            circlePos = [int(self.rect[0] + self.rect[2] * self.value), int(self.rect[1] + self.pad)]
        pygame.draw.circle(screen, (255, 255, 255), circlePos, int(self.pad * 1.5))

    def isHovered(self, mousePos):
        """
        Determine if the coords ``mousePos`` are located within the bounds of this slider.

        :returns: True if they are, False if not.
        """
        x, y = mousePos
        if y > self.rect[1] - self.pad and y < self.rect[1] + self.rect[3] + self.pad:
            if x > self.rect[0] - self.pad and x < self.rect[0] + self.rect[2] + self.pad:
                return True
        return False

class HorizBar:
    """
    This element is a simple horizontal percentage bar. The bar overlays a bar of ``colour`` over a grey bar. The width of the coloured bar can be controlled with ``percentage``, and will shrink to the left. An optional label, ``label``, can also be drawn over the bar.

    The maximum size and position of the bar can be controlled by ``rect``, which should be an [x, y, width, height] list.
    """
    def __init__(self, rect, colour, percentage=1, label=''):
        #: The default width. Resizing is done from this value.
        self.defaultWidth = rect[2]
        #: The default height. Resizing is done from this value.
        self.defaultHeight = rect[3]+rect[3]%2
        #: The width of this bar at any time.
        self.width = self.defaultWidth
        #: The height of this bar at any time.
        self.height = self.defaultHeight
        #: The default x and y position of this bar. Resizing is done from this value.
        self.defaultPos = rect[:2]
        #: The x and y position of this bar at any time.
        self.pos = self.defaultPos

        #: The percentage of the bar which is filled in, as a float between 0 and 1.
        self.percentage = percentage
        #: The colour of the bar. Expressed as a 3-element RGB tuple, or a Pygame Color object.
        self.colour = colour
        #: The label shown on the bar. Expressed as a Python string.
        self.label = label

    def onResize(self, screen):
        """
        Resize this bar to suit ``screen``.
        """
        self.pos = scaleRect(self.defaultPos, screen)
        self.width, self.height = scaleRect([self.defaultWidth, self.defaultHeight], screen)

    def draw(self, screen, mousePos):
        """
        Draw this bar to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        lineLength = self.width - self.height

        # Get the left and right points of the bar's circles
        leftPos = [self.pos[0] + self.height//2, self.pos[1] + self.height//2]
        rightPos = [leftPos[0] + lineLength, leftPos[1]]
        # Get the end points of the line
        leftLinePos = [leftPos[0], leftPos[1] - 1]
        rightLinePos = [rightPos[0], rightPos[1] - 1]

        # Draw the grey underbar
        pygame.draw.line(screen, (192, 192, 192), leftLinePos, rightLinePos, self.height)
        pygame.draw.circle(screen, (192, 192, 192), leftPos, self.height//2)
        pygame.draw.circle(screen, (192, 192, 192), rightPos, self.height//2)

        # Draw the bar over the top
        # Get the scaled position of the end of the bar
        scaledRightPos = [leftPos[0] + round(lineLength * self.percentage), rightLinePos[1]]
        pygame.draw.line(screen, self.colour, leftLinePos, scaledRightPos, self.height)
        # Draw the end circles of the bar
        scaledRightPos[1] += 1
        pygame.draw.circle(screen, self.colour, leftPos, self.height//2)
        pygame.draw.circle(screen, self.colour, scaledRightPos, self.height//2)

        # Draw the label
        if self.label:
            font = pygame.font.Font('resources/font/main.ttf', self.height - 4)
            text = font.render(self.label, True, (255, 255, 255))
            pos = [self.pos[0] + 8, self.pos[1]]
            screen.blit(text, pos)

class VertBar(HorizBar):
    """
    The VertBar element is exactly the same as the HorizBar element, but is designed for vertical bars. The VertBar will recede to the bottom of the screen as percentage decreases.
    """
    def draw(self, screen, mousePos):
        """
        Draw this bar to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        lineLength = self.height - self.width

        # Get the top and bottom points of the bar's circles
        topPos = [self.pos[0] + self.width//2, self.pos[1] + self.width//2]
        bottomPos = [topPos[0], topPos[1] + lineLength]
        # Get the end points of the line
        topLinePos = [topPos[0] - 1, topPos[1]]
        bottomLinePos = [bottomPos[0] - 1, bottomPos[1]]

        # Draw the grey underbar
        pygame.draw.line(screen, (192, 192, 192), topLinePos, bottomLinePos, self.width)
        pygame.draw.circle(screen, (192, 192, 192), topPos, self.width//2)
        pygame.draw.circle(screen, (192, 192, 192), bottomPos, self.width//2)

        # Draw the bar over the top
        # Get the scaled position of the end of the bar
        scaledTopPos = [topPos[0] - 1, bottomLinePos[1] - round(lineLength * self.percentage)]
        pygame.draw.line(screen, self.colour, bottomLinePos, scaledTopPos, self.width)
        # Draw the end circles of the bar
        scaledTopPos[0] += 1
        pygame.draw.circle(screen, self.colour, bottomPos, self.width//2)
        pygame.draw.circle(screen, self.colour, scaledTopPos, self.width//2)

        # Draw the label
        if self.label:
            font = pygame.font.Font('resources/font/main.ttf', self.width - 4)
            for c, char in enumerate(self.label):
                text = font.render(self.label, True, (255, 255, 255))
                pos = [self.pos[0], self.pos[1] + 8 + (c * self.width - 4)]
                screen.blit(text, pos)

class Button:
    """
    This element is a simple clickable button. The button can display a label, and will display somewhat greyed out when hovered over. Button click logic can be controlled by overriding the onClick event. When clicked, a button will always run this method.

    The use of multiple buttons in a Gui will be handled by the engine, with the click events only firing one button onClick event at a time. This simple functionality provides an easy way to create form Guis in the M.A.T.A engine.
    """
    def __init__(self, rect, label, isSquare=False, enabled=True):
        #: The default width and height as a list. Resizing is done from this value.
        self.defaultRect = rect
        #: The width and height of this Button at any time.
        self.rect = self.defaultRect

        #: The text shown on the button element, as a Python string.
        self.label = label
        #: The default font object used for rendering the label on this button.
        self.font = pygame.font.Font('resources/font/main.ttf', 30)
        #: A boolean representing whether the button can be clicked or not.
        #: If False, the button will appear greyed out, and will not respond to mouse clicks.
        self.enabled = enabled
        #: A boolean representing whether the button is locked to a square shape.
        #: If True, the button will always appear as a square, even if the window is resized.
        self.isSquare = isSquare

    def onResize(self, screen):
        """
        Resize this button to suit ``screen``.
        """
        self.rect = scaleRect(self.defaultRect, screen)
        if self.isSquare:
            self.rect = self.rect[:2] + [min(self.rect[2:])] * 2

    def draw(self, screen, mousePos):
        """
        Draw this Button to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        colour1 = (65, 55, 40)
        if self.isHovered(mousePos) or not self.enabled:
            colour2 = (138, 114, 84)
        else:
            colour2 = (173, 144, 106)

        # Draw the button
        pygame.draw.rect(screen, colour2, self.rect, 0)
        pygame.draw.rect(screen, colour1, self.rect, 4)

        # Draw the label on the button
        label = self.getLabelObject()
        screen.blit(label, self.getLabelPos(label))

    def getLabelObject(self):
        """
        Return a cropped version of this button's label to fit this button's width.

        :returns: The label text rendered as a Pygame surface.
        """
        label = self.label
        text = self.font.render(label, True, (0, 0, 0))
        while text.get_rect().width + 10 > self.rect[2]:
            label = label[1:]
            text = self.font.render(label, True, (0, 0, 0))
        return text

    def getLabelPos(self, label):
        """
        Return the position to blit ``label`` to onscreen.

        :returns: The x-y coordinates as a 2-element list.
        """
        return [self.rect[0] + self.rect[2]//2 - label.get_rect().width//2, self.rect[1] + self.rect[3]//2 - 20]

    def isHovered(self, mousePos):
        """
        Determine if the coords ``mousePos`` are located within the bounds of this button.

        :returns: True if they are, False if not.
        """
        x, y = mousePos
        if x > self.rect[0] and x < self.rect[0] + self.rect[2]:
            if y > self.rect[1] and y < self.rect[1] + self.rect[3]:
                return True
        return False

    def onClick(self, game):
        """
        Handle a click event on this button.

        This method does nothing, unless overridden by a subclass.
        """
        pass

class TextBox(Button):
    """
    This element is a single-line textbox. The textbox can display a label until text is entered. If the input text overflows, the start of the string will be hidden as overflow.

    The use of multiple textboxes in a Gui will be handled by the engine, with the typed characters only entering one textbox at a time. This simple system provides an easy way to create form Guis in the M.A.T.A engine.
    """
    def __init__(self, rect, label):
        super().__init__(rect, label)
        #: The current input text value of this textbox.
        self.text = ''

    def getLabelObject(self):
        """
        Return a cropped version of this textbox's label to fit, but only if no text has been entered.

        :returns: The label rendered as a Pygame surface, or a blank Pygame surface.
        """
        if not self.text:
            label = self.label
        else:
            label = ''
        text = self.font.render(label, True, (64, 64, 64))
        while text.get_rect().width + 10 > self.rect[2]:
            label = label[1:]
            text = self.font.render(label, True, (64, 64, 64))
        return text

    def getTextObject(self):
        """
        Return a cropped version of this textbox's input text to fit.

        :returns: The label rendered as a Pygame surface.
        """
        label = self.text
        text = self.font.render(label, True, (0, 0, 0))
        while text.get_rect().width + 10 > self.rect[2]:
            label = label[1:]
            text = self.font.render(label, True, (0, 0, 0))
        return text

    def draw(self, screen, mousePos):
        """
        Draw this TextBox to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        super().draw(screen, mousePos)

        # Draw the input text on the button
        label = self.getTextObject()
        screen.blit(label, self.getLabelPos(label))

    def doKeyPress(self, event):
        """
        Handle a key press event on this textbox.

        This method, by default, adds characters to the ``text`` field, or removes them if backspaced.
        """
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key != pygame.K_RETURN:
            self.text += event.unicode

class TextArea:
    """
    Similar to the TextBox element, the TextArea element provides a multi-line text input field for users. Text that is input into this element will automatically wrap to fill multiple lines.

    Size and position are controlled by the ``rect`` argument, and colour is controlled by ``colour``.
    """
    def __init__(self, rect, colour):
        #: The default width and height as a list. Resizing is done from this value.
        self.defaultRect = rect
        #: The width and height of this TextArea at any time.
        self.rect = self.defaultRect

        #: The background colour of the textarea, as a 3-element RGB tuple, or a Pygame Color object.
        self.colour = colour
        #: The text input value of this textarea.
        self.text = ''
        #: The Pygame font object used to render the text inside this textarea.
        self.font = pygame.font.Font('resources/font/main.ttf', 20)

    def onResize(self, screen):
        """
        Resize this textarea to suit ``screen``.
        """
        self.rect = scaleRect(self.defaultRect, screen)

    def draw(self, screen, mousePos):
        """
        Draw this TextArea to the Pygame surface, ``screen``.
        ``mousePos`` is the x and y coordinates of the cursor.
        """
        # Set up the background of the textarea
        background = pygame.Surface(self.rect[2:]).convert_alpha()
        background.fill(pygame.Color(*self.colour))

        # Draw the lines of text
        lines = self.getLines()
        for l, line in enumerate(lines):
            line = self.font.render(line, True, (0, 0, 0))
            background.blit(line, [10, 10 + 20 * l])

        # Draw the textarea to the screen
        screen.blit(background, self.rect[:2])

    def doKeyPress(self, event):
        """
        Handle a key press event on this textbox.
        ``event`` represents the Pygame event of the keypress.
        """
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key != pygame.K_RETURN:
            self.text += event.unicode

    def getLines(self):
        """
        Split the text within this textarea into wrapped lines of text.

        :returns: A list of Python strings.
        """
        lines = []
        i = 0
        text = self.text
        # loop the text and split it into lines
        while text:
            i += 1
            if self.getTextWidth(text[:i]) >= self.rect[2] - 20:
                # Add the line, crop the text and reset the iterator
                lines.append(text[:i - 1])
                text = text[i - 1:]
                i = 0
            elif text[:i] == text:
                # Add a flashing bar to the end of the text entry
                text += '|' if (pygame.time.get_ticks()//300)%2 else ''
                lines.append(text)
                break

        return lines

    def getTextWidth(self, text):
        """
        Return the width of ``text`` as rendered by Pygame.

        :returns: The width of the label rendered as a Pygame surface.
        """
        return self.font.render(text, True, (0, 0, 0)).get_width()
