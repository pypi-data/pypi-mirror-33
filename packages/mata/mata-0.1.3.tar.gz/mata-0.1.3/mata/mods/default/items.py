"""
items.py
A module with definitions of all the default items for MATA
"""
from api.item import *
from api import combat

class Dirt(Item):
    def __init__(self):
        super().__init__()
        self.setRegistryName('Dirt')
        self.image = 'tile_dirt'

    def getValue(self):
        return 0.1

class Gold(Item):
    def __init__(self):
        super().__init__()
        self.setRegistryName('Gold')
        self.image = 'tile_sand'#'item_gold'

    def getMaxStackSize(self):
        return 900

class Sword(Weapon):
    def __init__(self):
        super().__init__()
        self.setRegistryName('Steel Sword')
        self.image = 'tile_water'#'weapon_steel_sword'
        self.attack = 10
        self.spread = combat.Spread.MID_ARC
        self.range = combat.Range.MELEE
        self.damageClass = combat.Class.NORMAL
        self.knockback = combat.Knockback.KNOCK_WEAK

class Teeth(Weapon):
    """
    An unobtainable weapon used for entity attack calculations
    """
    def __init__(self):
        super().__init__()
        self.setRegistryName('Teeth Weapon')
        self.attack = 5
        self.spread = combat.Spread.FULL_ARC
        self.range = combat.Range.MELEE
        self.damageClass = combat.Class.LIFE
        self.knockback = combat.Knockback.KNOCK_NONE
