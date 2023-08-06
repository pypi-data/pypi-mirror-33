"""
The Item module holds all of the classes relating to Itemstacks, Inventories, Weapons, and Items.

New Items can be added by overriding the Item class. As can new Weapons. Customised Inventories should override the Inventory class.
"""

import random
from copy import deepcopy

from api import combat

class Inventory:
    """
    The Inventory class holds all of the data of the itemstacks in an inventory.

    It contains stack slots for stacks in the left hand, right hand and armour, as well as two stack lists, one for a hotbar and the other for the main inventory.

    A variety of convenience methods are also provided to perform various transformations and operations on the Inventory.
    """
    def __init__(self):
        #: A dictionary of the items in the inventory.
        #:
        #: The keys, 'left', 'right', and 'armour' correspond to the equipped items.
        #: The key 'main' corresponds to a list of the main section of the inventory.
        self.items = {'left' : ItemStack(NullItem(), 0), 'right' : ItemStack(NullItem(), 0),
                      'armour' : ItemStack(NullItem(), 0), 'hotbar' : [], 'main' : []}
        #: The maximum number of stacks in the main section of the inventory.
        self.maxSize = 999

    def getEquipped(self):
        """
        Get a list of the equipped itemstacks, in the order, left, right, then armour.

        :returns: A list of the equipped itemstacks (Itemstacks may be NullItem itemstacks).
        """
        return [self.items['left'], self.items['right'], self.items['armour']]

    def getItem(self, index):
        """
        Get an itemstack at ``index`` of the main section of the inventory.

        :returns: The itemstack at ``index``, or a NullItem itemstack.
        """
        try:
            return self.items['main'][index]
        except IndexError:
            return ItemStack(NullItem(), 0)

    def toList(self):
        """
        Rearrange the inventory into a single list of itemstacks.

        Note: This method doesn't affect the inventory, it only returns the list.

        :returns: The rearranged list of itemstacks.
        """
        stacks = []
        stacks += self.items['main']
        stacks += self.items['hotbar']
        stacks.append(self.items['left'])
        stacks.append(self.items['right'])
        stacks.append(self.items['armour'])

        return stacks

    @staticmethod
    def fromBytes(game, bytes):
        """
        Convert ``bytes`` into an inventory object.

        :returns: An Inventory object corresponding to the encoded data in ``bytes``.
        """
        # Pull the inventory size of the top of the packet
        invSize = int.from_bytes(bytes[:2], 'big')
        bytes = bytes[2:]

        # Walk the bytestring and get the items
        armourLen = int.from_bytes(bytes[:2], 'big')
        armour = ItemStack.fromBytes(game, bytes[:armourLen + 4])
        bytes = bytes[armourLen + 4:]

        leftLen = int.from_bytes(bytes[:2], 'big')
        left = ItemStack.fromBytes(game, bytes[:leftLen + 4])
        bytes = bytes[leftLen + 4:]

        rightLen = int.from_bytes(bytes[:2], 'big')
        right = ItemStack.fromBytes(game, bytes[:rightLen + 4])
        bytes = bytes[rightLen + 4:]

        hotbar = []
        for a in range(10):
            itemLen = int.from_bytes(bytes[:2], 'big')
            hotbar.append(ItemStack.fromBytes(game, bytes[:itemLen + 4]))
            bytes = bytes[itemLen + 4:]

        main = []
        for a in range(invSize):
            itemLen = int.from_bytes(bytes[:2], 'big')
            main.append(ItemStack.fromBytes(game, bytes[:itemLen + 4]))
            bytes = bytes[itemLen + 4:]

        # Instantiate the inventory
        i = Inventory()
        # Set the values of the inventory
        i.maxSize = invSize
        i.items['armour'] = armour
        i.items['left'] = left
        i.items['right'] = right
        i.items['hotbar'] = hotbar
        i.items['main'] = main

        return i

    def toBytes(self):
        """
        Convert this inventory to a byte string for transmission.

        :returns: A bytestring representation of the inventory and its contents.
        """
        # Convert the equipped stacks
        armour, left, right = [self.items[a].toBytes() for a in ('armour', 'left', 'right')]

        # Then convert the hotbar and main sections
        hotbar = self.items['hotbar']
        hotbar += [ItemStack(NullItem(), 0)] * (10 - len(hotbar))
        main = self.items['main']
        main += [ItemStack(NullItem(), 0)] * (self.maxSize - len(main))

        hotbar = b''.join([a.toBytes() for a in hotbar])
        main = b''.join([a.toBytes() for a in main])

        # Write it all out to a byte string
        return self.maxSize.to_bytes(2, 'big') + armour + left + right + hotbar + main

    def hashInv(self):
        """
        Generate a hash of the contents of this inventory.

        Resulting hash doesn't depend on the order or split of itemstacks.

        :returns: An basic integer hash of the inventory's contents.
        """
        # Duplicate the inventory
        newInv = self.duplicate()

        # Compress everything into a single list and sort
        newInv.items['main'] = newInv.toList()
        newInv.sortGroup('main', compress=True)

        # Separate the list
        itemlist = newInv.items['main']
        itemlist = ['{}|{}'.format(a.getRegistryName(), a.stackSize) for a in itemlist]

        # Hash the list
        return hash(str(itemlist) + str(self.maxSize))

    def duplicate(self):
        """
        Duplicate this inventory and return the copy.

        This is the best way to make a copy the Inventory. Assigning a new variable with:

        new_inv = old_inv

        will not work, and will create two references to the same Inventory (i.e. modifying one will modify the other).

        :returns: A copy of this Inventory object.
        """
        # Initialise the empty inventory
        newInv = Inventory()

        # Copy the each group into a new inventory
        newInv.items['main'] = deepcopy(self.items['main'])
        newInv.items['hotbar'] = deepcopy(self.items['hotbar'])
        newInv.items['left'] = deepcopy(self.items['left'])
        newInv.items['right'] = deepcopy(self.items['right'])
        newInv.items['armour'] = deepcopy(self.items['armour'])

        return newInv

    def sortItems(self, compress=False):
        """
        Collect and sort the entire inventory.

        If ``compress`` is True, all equivalent items will be stacked into one stack, disregarding maximum stack sizes. If False, equivalent items will be split into the minimum number of stacks to fit with maximum stack sizes.
        """
        # Sort the two sections of the inventory separately
        self.sortGroup('hotbar', compress)
        self.sortGroup('main', compress)

    def sortGroup(self, name, compress=False):
        """
        Collect and sort the group with name, ``name``, in this inventory.

        If ``compress`` is True, all equivalent items will be stacked into one stack, disregarding maximum stack sizes. If False, equivalent items will be split into the minimum number of stacks to fit with maximum stack sizes.
        """
        # VVV This is essentially a dodgy version of insertion sort VVV
        newGroup = []
        # Iterate each item, find duplicate stacks and add them together
        for i, itemstack in enumerate(self.items[name]):
            # Iterate the newGroup and try to add the stack to it
            for j, newStack in enumerate(newGroup):
                # If they are the same item type
                if newStack == itemstack:
                    result, carry = itemstack.add(newStack, compress)
                    newGroup[j] = result
                    # Reduce the itemstack and keep trying to fit it in
                    itemstack = carry
                    # If the whole itemstack has been distributed into the new group, move on
                    if not carry:
                        break

            # If the stack could not be merged into existing stacks, make a new stack with the remainder
            if itemstack:
                newGroup.append(itemstack)

        # Sort by item name
        self.items[name] = sorted([a for a in newGroup if a])

    def checkWeapon(self, weapon):
        """
        Check if ``weapon`` is in an equipped itemstack of this inventory.

        :returns: True if ``weapon`` is equipped. False if not.
        """
        return weapon == self.items['left'].getItem() or weapon == self.items['right'].getItem()

    def addItemstack(self, itemstack):
        """
        Add ``itemstack`` to the main section of the inventory.
        """
        if len(self.items['main']) < self.maxSize:
            self.items['main'].append(itemstack)

        else:
            for i, stack in enumerate(self.items['main']):
                if stack.getRegistryName() == itemstack.getRegistryName():
                    result, carry = stack.add(itemstack)
                    if not carry:
                        self.items['main'][i] = result
                        return

                if stack.getRegistryName() == 'null_item':
                    self.items['main'][i] = itemstack
                    return

        print('[ERROR] New Itemstack cannot fit')

    @staticmethod
    def addInventory(inv1, inv2, force=False):
        """
        Create an inventory that is the sum of two inventories, ``inv1`` and ``inv2``.

        If itemstacks overflow and ``force`` is False, an overflow inventory for everything that doesn't fit is also returned.

        :returns: A two element list of the sum inventory and the overflow inventory.
        """
        # Initialise the inventories
        sumInv = Inventory()
        overflowInv = Inventory()
        inv1 = inv1.duplicate()
        inv2 = inv2.duplicate()

        # Fill the first inventory's main section
        # with all of the second inventory's contents
        sumInv.items = inv1.items
        sumInv.items['main'] += inv2.items['hotbar']
        sumInv.items['main'] += inv2.items['main']
        sumInv.items['main'] += [inv2.items['left'], inv2.items['right'], inv2.items['armour']]

        # Sort and stack the itemstacks
        sumInv.sortItems()

        # Check if the inventory needs to overflow
        if not force and len(sumInv.items['main']) > inv1.maxSize:
            # Overflow back into the original second inventory
            overflowInv.items['main'] = sumInv.items['main'][inv1.maxSize:]
            sumInv.items['main'] = sumInv.items['main'][:inv1.maxSize]

        # Sort the inventories
        sumInv.sortItems()
        overflowInv.sortItems()

        return [sumInv, overflowInv]

class PlayerInventory(Inventory):
    """
    The PlayerInventory class is a subclass of the Inventory class, representing a possible default inventory for players.

    It is merely a default Inventory, but limited to 16 itemstack slots in the main inventory. This is considered a common value, usable for many simple games, without any modification.
    """
    def __init__(self):
        super().__init__()
        #: The maximum size of the player's inventory.
        self.maxSize = 16

class ItemStack:
    """
    A class representing a collection of a single type of Item.

    ItemStacks can be sorted, checked for equality, and mathematically manipulated using the limited set of methods supplied.
    """
    def __init__(self, item, size):
        #: The number of items in the itemstack
        self.stackSize = max(size, 0)
        #: The item type in the itemstack
        self.item = item
        if size <= 0:
          self.item = NullItem()

    def __lt__(self, other):
        if other is None:
            return True
        return self.getRegistryName() < other.getRegistryName()

    def __gt__(self, other):
        if other is None:
            return False
        return self.getRegistryName() > other.getRegistryName()

    def __eq__(self, other):
        if not isinstance(other, ItemStack):
            return False
        return self.getRegistryName() == other.getRegistryName()

    def __str__(self):
        return 'ItemStack(item="{}", stackSize={})'.format(self.getRegistryName(), self.stackSize)

    def getOne(self):
        """
        Take one item from this itemstack and return the deiterated itemstack, and the individual item's itemstack.

        :returns: A list containing this itemstack deiterated, and a duplicate itemstack with only one item.
        """
        return [self.__class__(self.getItem(), self.stackSize-1), self.__class__(self.getItem(), 1)]

    def split(self):
        """
        Split the itemstack in half.

        If the stackSize if odd, the second itemstack will have one item more than the first.

        :returns: A tuple containing two itemstacks of half the size of this itemstack.
        """
        stack1 = self.__class__(self.getItem(), self.stackSize//2)
        return (stack1, self.__class__(self.getItem(), self.stackSize-stack1.stackSize))

    def toPickup(self, game, pos):
        """
        Create a Pickup entity at ``pos`` corresponding to this ItemStack.

        :returns: A Pickup entity instance, with position set to ``pos``.
        """
        from api.entity import Pickup
        # Set up the pickup
        pickup = Pickup()
        pickup.setItemstack(self)

        # Generate a randomised position
        x, y = [int(a) for a in pos]
        decimal = round(random.random(), 2)
        pickup.pos = [random.randint(x - 2, x + 2) + decimal, random.randint(y - 2, y + 2) + decimal]

        # Assign it a UUID, and return it
        pickup.uuid = game.modLoader.getUUIDForEntity(pickup)
        return pickup

    @staticmethod
    def fromBytes(game, bytes):
        """
        Convert the bytestring, ``bytes``, into an ItemStack object.

        :returns: ItemStack from parsed bytestring.
        """
        stack = ItemStack(None, 0)
        # Pull the stack size from the data
        stack.stackSize = int.from_bytes(bytes[2:4], 'big')
        bytes = bytes[4:]

        # Get the item from the data
        items = game.modLoader.gameRegistry.items.values()
        resources = game.modLoader.gameRegistry.resources
        stack.item = Item.fromBytes(items, resources, bytes)

        return stack

    def toBytes(self):
        """
        Convert an ItemStack into a bytestring.

        :returns: A bytestring containing the fields of the ItemStack.
        """
        itemBytes = self.item.toBytes()
        return len(itemBytes).to_bytes(2, 'big') + self.stackSize.to_bytes(2, 'big') + itemBytes

    def getValue(self):
        """
        Get the financial value of the ItemStack.

        :returns: The economic value of the ItemStack as an integer.
        """
        return int(self.getItem().getValue() * self.stackSize)

    def getItem(self):
        """
        Get the item of the ItemStack.

        :returns: An Item object corresponding to the Item in this ItemStack.
        """
        return self.item

    def getRegistryName(self):
        """
        Get the registry name of the Item in this ItemStack.

        :returns: The string name of the Item in this ItemStack.
        """
        return self.getItem().getRegistryName()

    def getMaxStackSize(self):
        """
        Get the maximum stack size of this ItemStack.

        :returns: The maximum possible size of the ItemStack as an integer.
        """
        return self.item.getMaxStackSize()

    def getImage(self, resources):
        """
        Return the image of the item in this stack, fetched from ``resources``.

        :returns: A Pygame surface of the Item image.
        """
        return self.item.getImage(resources)

    def add(self, other, forceCompress=False):
        """
        Add ``other`` to this ItemStack.

        If ``forceCompress`` is False, the stack addition will ignore maximum stack size.

        :returns: A two-element list of the summed itemstack, and the carryover in the second stack.
        """
        if not other or self.getRegistryName() != other.getRegistryName():
            return [self, other]

        # Add the stack sizes and assign carryover as required
        sumSize = self.stackSize + other.stackSize
        carrySize = 0
        if not forceCompress and sumSize > self.getMaxStackSize():
            carrySize = sumSize - self.getMaxStackSize()
            sumSize = self.getMaxStackSize()

        # Create the stacks accordingly
        result = ItemStack(self.getItem(), sumSize)
        carryover = None
        if carrySize:
            carryover = ItemStack(self.getItem(), carrySize)

        return [result, carryover]

class Item:
    """

    """
    def __init__(self):
        #: The registry name of the Item object in the GameRegistry.
        self.name = ''
        #: The registry name of the Item image in the GameRegistry.
        self.image = None

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.name == other.name

    def setRegistryName(self, name):
        """
        Set the registry name of this Item in the GameRegistry.
        """
        self.name = name

    def getRegistryName(self):
        """
        Get the registry name of this Item.

        :returns: A string of the registry name of ths Item.
        """
        return self.name

    def getValue(self):
        """
        Get the financial value of this Item.

        This value defaults to 1, and should be overridden in new Items.

        :returns: An integer corresponding to the financial value of one instance of this Item.
        """
        return 1

    def getMaxStackSize(self):
        """
        Get the maximum stack size of this Item.

        :returns: The maximum possible size of this Item as an integer.
        """
        return 1

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has an attribute, ``name``.

        :returns: True if this class has the attribute, False if not.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

    def getImage(self, resources):
        """
        Get the Pygame surface from ``resources`` using the Item's image registry name.

        :raises KeyError: If image has not been registered under that registry name.
        """
        try:
            return resources[self.image]
        except KeyError:
            raise KeyError('Image "{}" has not been registered in the Game Registry'.format(self.image))

    def toBytes(self):
        """
        Get a byte representation of the item.

        :returns: A bytestring containing the data of the Item object.
        """
        className = self.__class__.__name__
        className = len(className).to_bytes(1, 'big') + className.encode()
        image = self.image if isinstance(self.image, str) else ''
        image = len(image).to_bytes(1, 'big') + image.encode()
        itemName = len(self.name).to_bytes(1, 'big') + self.name.encode()
        return itemName + image + className

    def fromBytes(itemClasses, resources, data):
        """
        Convert the ``data`` bytestring to an Item instance.

        :returns: An Item object with all of the fields in the ``data`` string, or NullItem.
        """
        # Get the item name
        itemNameLen = data[0]
        itemName = data[1:1 + itemNameLen].decode()
        data = data[1 + itemNameLen:]

        # Get the item image
        imageLen = data[0]
        image = data[1:imageLen + 1].decode()
        data = data[1 + imageLen:]

        classLen = data[0]
        className = data[1:1 + classLen].decode()
        data = data[1 + classLen:]
        if data:
            # This is a weapon, decode accordingly
            itemTuple = (itemName, image, className)
            return Weapon.fromBytes(itemClasses, resources, data, itemTuple)

        # Iterate the possible classes and look for the matching item class
        for itemClass in itemClasses:
            if itemClass.__name__ == className:
                # Fill in the values for the item, then return it
                item = itemClass()
                item.name = itemName
                item.image = image
                return item

        return NullItem()

class Weapon(Item):
    """
    A class for holding the attributes of a Weapon object. This class extends the Item class, and offers additional values relating to combat and attacks with a Weapon.

    New Weapons can be subclassed from here, and then registered in the GameRegistry for use.
    """
    def __init__(self):
        super().__init__()
        #: The base attack damage of this weapon, as an integer.
        self.attack = 0
        #: The class of attack damage of this weapon. See the api.combat module for possible values.
        self.damageClass = combat.Class.NORMAL
        #: The range of this weapon's attack. See the api.combat module for possible values.
        self.range = combat.Range.MELEE
        #: The maximum knockback distance from this weapon's attack. See the api.combat module for possible values.
        self.knockback = combat.Knockback.KNOCK_NONE
        #: The attack spread of this weapon's attack. See the api.combat module for possible values.
        self.spread = combat.Spread.WIDE_ARC

    def __eq__(self, other):
        if not isinstance(other, Weapon):
            return False
        varComparisons = [
                          self.attack == other.attack,
                          self.range == other.range,
                          self.knockback == other.knockback,
                          self.damageClass == other.damageClass,
                          self.spread == other.spread
                         ]
        return super().__eq__(other) and all(varComparisons)

    def getValue(self):
        """
        Return the economic value of this weapon.

        :returns: The value of the weapon as an integer.
        """
        return 30 * (16 * self.spread**2 + self.knockback**2 + self.damageClass**2 + (self.attack**2)/100)

    def toBytes(self):
        """
        Get a byte representation of the weapon.

        :returns: A bytestring containing the data of the Weapon object.
        """
        # Get the default item bytes
        itemData = super().toBytes()
        # Then append the weapon-specific information to it
        itemData += self.attack.to_bytes(3, 'big') + self.range.to_bytes(4, 'big')
        itemData += self.damageClass.to_bytes(1, 'big')
        itemData += self.knockback.to_bytes(2, 'big')
        return itemData

    def fromBytes(itemClasses, resources, data, itemTuple):
        """
        Convert the ``data`` bytestring to a Weapon instance.

        :returns: A Weapon object with all of the fields in the ``data`` string, or NullItem.
        """
        itemName, image, className = itemTuple

        attack = int.from_bytes(data[:3], 'big')
        attackRange = int.from_bytes(data[3:7], 'big')
        damageClass = data[7]
        knockback = int.from_bytes(data[8:], 'big')

        # Iterate the possible classes and look for the matching item class
        for itemClass in itemClasses:
            if itemClass.__name__ == className:
                # Fill in the values for the item, then return it
                item = itemClass()
                item.name = itemName
                item.image = image
                item.attack = attack
                item.range = attackRange
                item.damageClass = damageClass
                item.knockback = knockback
                return item

        return NullItem()

    def calcDamage(self, game, source, entityList):
        """
        Calculate the damage from this weapon, wielded by entity/player, ``source``, against a list of entities, ``entityList``.
        """
        for entity in entityList:
            damage = self.attack
            # Fire event hooks to modify the damage
            damage = game.fireEvent('onAttack', damage)

            # Import the required classes late, since it crashes up the top
            from api.entity import Damage, Player, Entity
            from api.packets import ResetPlayerPacket

            if isinstance(entity, Player):
                game.getPlayer(entity.name).tickDamage = Damage(damage, source)

            elif isinstance(entity, Entity):
                game.getEntity(entity.uuid).tickDamage = Damage(damage, source)

class Armour(Item):
    """
    This class represents an Armour item. It has no additional properties over an Item by default. They must be added separately.

    This class is simply a rename of the Item class, with no modifications. It is semantically clearer than using an Item, and allows for the Item to be stored in an ArmourSlot.
    """
    pass

class NullItem(Item):
    """
    A special item class used for empty Item objects.

    This class represents a non-Item. A stack of NullItems represents an empty stack, regardless of the stack size.
    """
    def __init__(self):
        self.setRegistryName('null_item')
        #: An empty reference string for this Item's image.
        self.image = None

    def getMaxStackSize(self):
        """
        Get the stack size of the NullItem.

        :returns: An integer, 0, to prevent itemstacks from holding any of these items.
        """
        return 0

    def getImage(self, resources):
        """
        Get the image of the NullItem.

        :returns: None, since the NullItem has no image.
        """
        return self.image
