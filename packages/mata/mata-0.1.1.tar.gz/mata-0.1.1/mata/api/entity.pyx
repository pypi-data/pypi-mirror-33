"""
The Entity module contains classes which hold all the major values and logic for entities and players.

All additional entity or player classes should be subclassed from the classes in this module. The EntityBase is the lowest level entity class, and contains all values and methods common to all entities, players, and vehicles. The Entity class contains the additional logic and values used for Non-player entities, whilst the Player class contains the additional logic and values for Player entities.

Vehicles are defined in the Vehicle module.
"""

from api.item import *
from api.ai import AIHandler, PickupAITask

import util

class EntityBase:
    """
    The base class for entities. All entity, vehicle and player classes are subclassed from this class
    """
    def __init__(self):
        #: The name for the entity.
        self.name = ''

        #: The Universally Unique IDentifier (UUID) for the entity.
        self.uuid = 0
        #: The current HP level for the entity.
        self.health = 100
        #: The current position for the entity.
        self.pos = [0, 0]
        #: The previous position for the entity. Usually the position at the last update tick.
        self.lastPos = [0, 0]

        #: The movement speed of the entity in world units-per-second.
        self.speed = 6

        #: Boolean representing if the entity is dead or not. When True, the entity is deleted on the next update tick.
        self.isDead = False
        #: The damage taken by an entity during a tick.
        self.tickDamage = None

        #: A dictionary of the custom properties of an entity.
        self.properties = {}
        #: The dimension which the entity is in.
        self.dimension = 0

        #: The UUID of an entity which the entity is riding.
        self.ridingEntity = None

    def getPos(self):
        """
        Get the position of the entity, rounded to 2 decimal places
        """
        return [round(self.pos[0], 2), round(self.pos[1], 2)]

    def setPos(self, pos):
        """
        Set a new absolute position
        """
        self.lastPos = list(self.pos)
        self.pos = list(pos)

    def getSpeed(self, game):
        """
        Get the movement speed of this entity
        """
        # If riding in a vehicle, use its speed
        if self.ridingEntity:
            return game.getVehicle(self.ridingEntity).getSpeed(self)
        # Otherwise, use the player's speed
        return self.speed

    def setProperty(self, propName, propVal):
        """
        Register the property object, ``propVal``, with the tag, ``propName``.
        """
        self.properties[propName] = propVal

    def getProperty(self, propName):
        """
        Get the property object registered with the tag ``propName``.

        :returns: Property object or None if not registered.
        """
        return self.properties.get(propName)

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has the attribute, ``name``.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

    def isPlayer(self):
        """
        Return whether this object is a player
        """
        return False

class Entity(EntityBase):
    """
    A base class for new entities. It is preferred to create a subclass of this class when adding new entities to the game.
    """
    def __init__(self):
        super().__init__()
        #: The AIHandler instance for the entity.
        self.aiHandler = AIHandler()
        #: The GameRegistry reference string for this entity's image.
        self.image = None

    def __eq__(self, other):
        return isinstance(other, Entity) and self.uuid == other.uuid

    def __str__(self):
        x = super().__repr__()
        return x.split()[-1][:-1] + ' {} {}'.format(self.name, self.uuid)

    def __repr__(self):
        x = super().__repr__()
        return x.split()[-1][:-1] + ' {} {} {}'.format(self.name, self.uuid, self.pos)

    def setRegistryName(self, name):
        """
        Set the GameRegistry reference string which corresponds to this entity to ``name``.
        """
        self.name = name

    def getRegistryName(self):
        """
        Get the GameRegistry reference string for this entity.
        """
        return self.name

    def getImage(self, resources):
        """
        Get the Pygame surface from ``resources`` using the Entity's image reference string.

        :raises KeyError: If image has not been registered under that reference string.
        """
        try:
            return resources[self.image]
        except KeyError:
            raise KeyError('Image "{}" has not been registered in the Game Registry'.format(self.image))

    def setImage(self, image):
        """
        Set the GameRegistry image reference string for the Entity to ``image``
        """
        self.image = image

    def toBytes(self):
        """
        Encode the Entity object into a byte string.
        """
        name = len(self.name).to_bytes(1, 'big') + self.name.encode()
        uuid = self.uuid.to_bytes(8, 'big')
        pos = str(self.getPos()).encode()
        hp = max(0, int(self.health)).to_bytes(4, 'big')
        dimension = self.dimension.to_bytes(2, 'big')

        damage = self.tickDamage.toBytes() if isinstance(self.tickDamage, Damage) else NullDamage().toBytes()

        return name + uuid + pos + hp + dimension + damage + self.__class__.__name__.encode()

    @staticmethod
    def fromBytes(data, entityClassList):
        """
        Decode the given byte string ``data`` into an entity object. The correct entity class must be given in ``entityClassList``.
        """
        # Get the entity name
        nameLength = data[0]
        name = data[1:nameLength + 1].decode().strip()
        data = data[nameLength + 1:]

        # Get the UUID
        uuid = int.from_bytes(data[:8], 'big')
        data = data[8:]

        # Walk the string to find the position value, because we can't just dump float data into the stream -_-
        posBuf = ''
        for character in data:
            posBuf += chr(character)
            if character == ord(']'):
                break
        # Eval it into an array
        pos = eval(posBuf)
        data = data[len(posBuf):]

        # Get the HP and dimension ID
        health = int.from_bytes(data[:4], 'big')
        dimension = int.from_bytes(data[4:6], 'big')
        data = data[6:]

        # Get Damage data
        damAmount = data[:3]
        damType = data[3]
        damLength = data[4]
        damSource = data[5:5 + damLength]
        data = data[5 + damLength:]
        damage = Damage.fromBytes(damType, damSource, damAmount)

        # Then get the entity class
        entityClass = data.decode().strip()

        # Create the entity and fill in its information
        finalEntity = entityClassList.get(entityClass, Entity)()

        finalEntity.setRegistryName(name)
        finalEntity.uuid, finalEntity.pos = uuid, pos
        finalEntity.health, finalEntity.dimension = health, dimension
        finalEntity.tickDamage = damage

        return finalEntity

class Player(EntityBase):
    """
    A base class for storing the player information and handling basic player logic.
    """
    def __init__(self):
        super().__init__()
        #: The current number of experience points the player has.
        self.exp = 0
        #: A list of values for storing the player image. This defaults to a list of (type, hue_shift) tuples.
        self.img = []
        #: The player's Inventory
        self.inventory = PlayerInventory()

        #: A value used for synchronisation.
        #: This value is a boolean of synchronisation status on the client,
        #: but a timestamp of last synchronisation on the server.
        self.synced = False

    def __eq__(self, other):
        return isinstance(other, Player) and self.name == other.name

    def isPlayer(self):
        """
        Return whether this object is a player.
        """
        return True

    def setInventory(self, inv):
        """
        Set the player's inventory to ``inv``.
        """
        self.inventory = inv

    def getInventory(self):
        """
        Get the inventory object in the player.

        :returns: Player's Inventory object or None
        """
        return self.inventory

    def switchDimension(self, dimension, game):
        """
        Switch the current dimension for this player to ``dimension``.
        """
        # Delete the old player
        world = game.getWorld(self.dimension)
        for p, player in enumerate(world.players):
            if player.name == self.name:
                del world.players[p]

        # Set the dimension, and replace it
        self.dimension = dimension
        game.setPlayer(self)

    def setUsername(self, name):
        """
        Set the player username to ``name``.
        """
        self.name = name

    def toBytes(self):
        """
        Get a string representation of the player object.
        """
        name = len(self.name).to_bytes(1, 'big') + self.name.encode()
        pos = str(self.getPos()).encode()
        hp = max(0, int(self.health)).to_bytes(4, 'big')
        exp = max(0, int(self.exp)).to_bytes(4, 'big')
        dimension = self.dimension.to_bytes(2, 'big')

        damage = self.tickDamage.toBytes() if isinstance(self.tickDamage, Damage) else NullDamage().toBytes()

        return name + pos + hp + exp + dimension + damage

    @staticmethod
    def fromBytes(data):
        """
        Get a player object from the bytestring, ``data``.
        """
        # Get the Player name
        nameLength = data[0]
        name = data[1:nameLength + 1].decode().strip()
        data = data[1 + nameLength:]

        # Walk the string to find the position value, because we can't just dump float data into the stream -_-
        posBuf = ''
        for character in data:
            posBuf += chr(character)
            if character == ord(']'):
                break
        # Eval it into an array
        pos = eval(posBuf)
        data = data[len(posBuf):]

        # Get the HP, EXP, and dimension ID
        health = int.from_bytes(data[:4], 'big')
        exp = int.from_bytes(data[4:8], 'big')
        dimension = int.from_bytes(data[8:10], 'big')
        data = data[6:]

        # Get the Damage data
        damAmount = data[:3]
        damType = data[3]
        damLength = data[4]
        damSource = data[5:5 + damLength]
        data = data[5 + damLength:]
        damage = Damage.fromBytes(damType, damSource, damAmount)

        # Restore all the sent values into a new player object
        p = Player()
        p.name = name
        p.pos = pos
        p.health = health
        p.exp = exp
        p.dimension = dimension
        p.tickDamage = damage

        return p

class Pickup(Entity):
    """
    A simple entity which serves as an item pickup for players.
    """
    def __init__(self):
        super().__init__()
        self.health = 2**31
        self.setRegistryName('Pickup')
        self.aiHandler.registerAITask(PickupAITask(self), 0)

        #: The itemstack of the Pickup
        self.stack = None

    def setItemstack(self, stack):
        """
        Set the itemstack of the Pickup to ``stack``.

        :raises AttributeError: If ``stack`` is not a valid ItemStack object.
        """
        if not isinstance(stack, ItemStack):
            print('[WARNING] Invalid item being set for pickup')
        self.setImage(stack.getItem().image)
        self.stack = stack

    def getItem(self):
        """
        Get the itemstack of the Pickup.
        """
        return self.stack

class Damage:
    """
    A base class for damage. This class is used in combat logic to store attacker and damage values.
    """
    def __init__(self, amount, source):
        self.amount = amount
        self.source = source

    def __str__(self):
        return ''

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has an attribute, ``name``.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

    def toBytes(self):
        """
        Encode the data from the Damage class into a byte string.
        """
        # If the source is a non-player, start with a b'u' byte, then the UUID
        if isinstance(self.source, int):
            sourceData = b'u' + b'\x08' + self.source.to_bytes(8, 'big')
        # If the source is a player, start with an b'n' byte, then a length byte, then the username
        else:
            length = len(self.source).to_bytes(1, 'big')
            sourceData = b'n' + length + self.source.encode()
        return self.amount.to_bytes(3, 'big') + sourceData

    @staticmethod
    def fromBytes(type, source, amount):
        """
        Decode the bytes into a Damage object instance.

        Takes three bytestrings, ``type``, ``source`` and ``amount`` which correspond to the Damage source type (player or non-player), Damage source (UUID or username) and Damage amount.
        """
        amount = int.from_bytes(amount, 'big')

        if amount == 0:
            return NullDamage()

        # If the source is a player, decode the bytes to get the username
        if type == ord('n'):
            sourceData = source.decode()
        # Otherwise, convert the raw bits to a 64 bit integer UUID
        else:
            sourceData = int.from_bytes(source, 'big')

        return Damage(amount, sourceData)

class NullDamage(Damage):
    """
    A Damage subclass representing a damage of 0. This class is merely serves as syntactic sugar (it makes code clearer).
    """
    def __init__(self):
        super().__init__(0, '')
