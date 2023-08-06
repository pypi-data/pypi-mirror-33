"""
The Biome module stores most of the classes relating to world generation and representation.

The classes here are used to define small scale objects in the world, such as Tiles, Plants and Biomes. The module provides a framework that can be extended to allow for variation in world generation without having to develop complex generation algorithms.

For finer control over world generation, see the api.dimension module.
"""

import random
import math

class Tile:
    """
    The class for representing a Tile type. Each Tile represents one square unit of the world's map area.
    """
    def getImage(self, resources):
        """
        Get the Pygame surface from ``resources`` using the Tile's image reference string.

        :raises KeyError: If image has not been registered under that reference string.
        """
        try:
            return resources['tile_' + self.getTileName()]
        except Exception:
            raise Exception('Selected Resource has not been registered!')

    def setTileName(self, name):
        """
        Set the tile name to ``name``.
        """
        self.name = name

    def getTileName(self):
        """
        Get the name of the Tile as a string
        """
        return self.name

    def getResourceLocation(self):
        """
        Return the relative filesystem path to the Tile's image.
        """
        return 'resources/textures/mods/tiles/{}.png'.format(self.getTileName())

class Plant(Tile):
    """
    The class for representing plants. Each tile can have at most one plant on it, but a plant image can be larger than that of a tile.

    Plants are simply any object which sits "on top of" the ground. This can include anything from trees, chests, fences, rocks, etc.
    """
    pass

class NullPlant(Plant):
    """
    A Plant subclass indicating a lack of plant. It is preferred to have tiles without a plant have their plant set to a NullPlant, rather than None.
    """
    def __init__(self):
        self.setTileName('null_obj')

class Biome:
    """
    The class for representing a block/tile of the world. This class stores the Biome information for each block.

    The Biome stores a list of possible Tile and Plant types that can generate on it, and using this, a biome can be generated quite easily.
    """
    def __init__(self):
        #: A list of possible types of Tiles which can generate in the Biome
        self.tileTypes = []
        #: A list of possible types of Plants which can generate in the Biome
        self.plantTypes = []
        #: A list of possible entity types which can spawn in the Biome
        self.entityTypes = []
        #: A list of possible item types which can spawn in the Biome
        self.itemTypes = []
        #: A list of possible vehicle types which can spawn in the Biome
        self.vehicleTypes = []

        #: The index corresponding to this Biome block's Tile type
        self.tileIndex = -1
        #: The index corresponding to this Biome block's Plant type
        self.plantIndex = -1

        self.initTiles()

    def initTiles(self):
        """
        Initialise the tile and plant type for this Biome block.

        :raises NotImplementedError: If the method has not been overridden in a subclass.
        """
        raise NotImplementedError('This method should be overridden by a subclass')

    def setTileType(self, tileNoise, detailNoise, resources):
        """
        Calculate the tile and plant type for this Biome block using the ``tileNoise`` and ``detailNoise`` values.
        """
        # Initialise the tile and set the type
        if self.tileTypes:
            i = int(tileNoise * len(self.tileTypes))
            self.tileIndex = i
            self.tileTypes[i] = self.tileTypes[i]()

        # Set a plant
        # 0.5 is the minimum threshold for details
        if self.plantTypes:
            # Calculate the plant/detail index
            i = int((2 * detailNoise - 1) * len(self.plantTypes))
            # i = max(0, (20 * detailNoise - 11)//3)
            self.plantIndex = i
            # Then instantiate the detail object
            self.plantTypes[i] = self.plantTypes[i]()

class TileMap:
    """
    The class which holds the block array for a subsection of the world.

    Despite the name, this class holds a 2D array of Biome objects, not Tiles.
    """
    def __init__(self, width, height):
        #: The 2D array for holding the world Biome blocks.
        self.map = [[0 for column in range(width)] for row in range(height)]
