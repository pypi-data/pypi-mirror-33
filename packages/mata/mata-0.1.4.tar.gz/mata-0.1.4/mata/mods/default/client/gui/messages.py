from api.gui.gui import *
from api.gui.objects import *
from mods.default.client.gui.extras import *

class MessageScreen(Gui):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.backImg = pygame.image.load('resources/textures/background.png').convert()

    def drawBackgroundLayer(self):
        w = self.screen.get_width()
        h = self.screen.get_height()

        self.screen.blit(pygame.transform.scale(self.backImg, [w, h]), [0, 0])

    def drawMiddleLayer(self, mousePos):
        w = self.screen.get_width()
        h = self.screen.get_height()

        font = pygame.font.Font('resources/font/main.ttf', 40)
        text = font.render(self.message, True, (0, 0, 0))
        self.screen.blit(text, [w//2 - text.get_rect().width//2, h//2 - 54])

class DimLoadingScreen(MessageScreen):
    def __init__(self, message, game):
        super().__init__(message)
        self.game = game

    def drawForegroundLayer(self, mousePos):
        super().drawForegroundLayer(mousePos)

        pygame.display.flip()

        dimension = self.game.getDimension(self.game.player.dimension)
        dimension.generate(self.game.player.pos, self.game.modLoader.gameRegistry)

        self.game.restoreGui()

class DisconnectMessage(MessageScreen):
    def __init__(self, message):
        super().__init__(message)

        self.buttons = [MenuButton([300, 500, 424, 80])]

class LoadingScreen(MessageScreen):
    def __init__(self):
        super().__init__('Loading...')
