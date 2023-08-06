"""
The Properties module defines a framework for storing additional values in entities, vehicles and the world.

The Property class acts as a container for variables. These objects are defined by the arguments passed into their constructors and from here should be set duplicated and set in each object that is to use them.
"""

class Property:
    """
    A class for defining customisable properties for entities.

    Due to limitations in Python, Pygame Surface objects should not be used in this class, lest duplication become impossible.
    """
    def __init__(self, **kwargs):
        """
        This constructor only accepts keyword arguments (e.g. itemID=4, randomList=[1, 2, 3]), and defines mirroring attributes in the Property instance.

        For example:

          >>> prop = Property(field1='hello')
          >>> print(prop.field1)
          hello
        
        """
        for val in kwargs.items():
            self.__setattr__(*val)
