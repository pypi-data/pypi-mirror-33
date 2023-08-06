"""
The Combat module holds enumeration classes for each attribute of a weapon.

Further information about each enumeration is listed under each class definition below.
"""
from enum import IntEnum

class Class(IntEnum):
  """
  An enumeration for weapon damage classes.

  Higher values are more powerful.
  """
  NORMAL = 0
  FIRE = 1
  ICE = 2
  LIFE = 3
  UNDEAD = 4
  MAGIC = 5

class Range(IntEnum):
  """
  An enumeration for weapon range.

  The values are equal to the range of the weapon, in tiles.
  """
  MELEE = 1
  BIG_MELEE = 3
  SHORT_RANGED = 10

  INFINITE = 0 # 0 means no limits

class Spread(IntEnum):
  """
  An enumeration for weapon attack spread.

  Values are between 0.1 - 1 and represent the amount of a circle the attack spreads.

  0.1 is a 36 degree arc (18 to each side), 1 is a complete revolution (attack in every direction simultaneously).
  """
  THIN_ARC = 0.1
  MID_ARC = 0.25
  WIDE_ARC = 0.33
  SEMI_ARC = 0.5
  FULL_ARC = 1

class Knockback(IntEnum):
  """
  An enumeration for knockback of a weapon's attack.

  The values are equal to the maximum knockback of an attack, in tiles.
  """
  KNOCK_NONE = 0
  KNOCK_WEAK = 1
  KNOCK_STRONG = 5
  KNOCK_INFINITE = 65000
