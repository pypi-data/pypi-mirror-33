"""
The Vehicle module holds the class for creating Vehicles in the M.A.T.A engine.

Vehicle is subclassed from the EntityBase class, and all vehicles being created should ideally be subclassed from the Vehicle class.

For further details about EntityBase functionality, see the api.entity module page.
"""

from api.entity import EntityBase, Player

class Vehicle(EntityBase):
    """
    The base class for Vehicles in the engine. Vehicles should be subclassed from this class to ensure compatibility with engine logic.
    """
    def __init__(self):
        super().__init__()
        #: The health of the vehicle. Defaults to infinity to prevent destruction from attacks.
        self.health = float('inf')
        #: A dictionary holding the entities and players riding the vehicle
        self.riders = {'driver' : None, 'other' : []}
        #: A GameRegistry reference string for the Vehicle's image
        self.image = None

        #: A boolean symbolising the existence status of the vehicle.
        #: If True, the vehicle will be deleted from the world in the next update tick.
        self.isDestroyed = False

    def __eq__(self, other):
        return isinstance(other, Vehicle) and self.uuid == other.uuid

    def mountRider(self, entity, game):
        """
        Attempt to add a rider, ``entity``, to this vehicle.

        :returns: True is successful, False otherwise
        """
        # Check if a valid entity
        if not isinstance(entity, EntityBase):
            print('[WARNING] Invalid rider for vehicle')
            return False
        # Check for rider quantity overflow
        if len(self.riders['other']) + int(bool(self.riders['driver'])) >= self.getMaxRiders():
            return False
        # Check if rider is mounted to another vehicle
        if entity.ridingEntity:
            game.getVehicle(entity.ridingEntity).unmountRider(entity)

        # If everything is ok, mount the entity in the appropriate position
        game.getPlayer(entity.name).setPos(self.pos)

        if entity.name in self.riders['other'] or self.riders['driver'] == entity.name:
            return False
        if not self.riders['driver']:
            self.riders['driver'] = entity.name
        else:
            self.riders['other'].append(entity.name)
        entity.ridingEntity = self.uuid
        return True

    def unmountRider(self, entity):
        """
        Attempt to remove ``entity`` from the vehicle.
        """
        # Check the main driver
        driver = self.riders.get('driver')
        if entity.name == driver:
            self.riders['driver'] = None
            return
        # Iterate the other connected riders, compare the entity and remove it if possible
        for r, rider in enumerate(self.riders['other']):
            if entity.name == rider:
                self.riders['other'].pop(r)
                entity.ridingEntity = None
                return

    def getSpeed(self, rider):
        """
        Get the movement speed of the entity ``rider`` riding this vehicle.
        """
        # If the rider is a player
        # Return the speed, multiplied by 1 or 0 for whether player is the driver
        return self.speed * int(self.isDriver(rider))

    def getMaxRiders(self):
        """
        Return the maximum number of riders this vehicle can hold.
        """
        return 1

    def isDriver(self, obj):
        """
        Return if the given entity, ``obj``, is the driver.
        """
        if obj.isPlayer():
            return obj.name == self.riders['driver']
        else:
            return obj.uuid == self.riders['driver']

    def isPassenger(self, obj):
        """
        Return if the given entity, ``obj``, is a passenger.
        """
        if obj.isPlayer():
            return obj.name in self.riders['other']
        else:
            return obj.uuid in self.riders['other']

    def onVehicleUpdate(self, game):
        """
        Update the vehicle.
        """
        # Lock the vehicle to the driver and lock passengers to the vehicle
        if self.riders['driver'] is not None:
            self.pos = list(game.getPlayer(self.riders['driver']).pos)
        for ridername in self.riders['other']:
            game.getPlayer(ridername).pos = list(self.pos)

    def hasAttribute(self, name):
          """
          Return whether the class (and classes which extend this) has the attribute, ``name``.
          """
          try:
              a = self.__getattribute__(name)
              return True
          except AttributeError:
              return False

    def setRegistryName(self, name):
        """
        Set the GameRegistry reference string which corresponds to this vehicle to ``name``.
        """
        self.name = name

    def getRegistryName(self):
        """
        Get the GameRegistry reference string for this vehicle.
        """
        return self.name

    def getImage(self, resources):
        """
        Get the Pygame surface from ``resources`` using the Vehicle's image reference string.

        :raises KeyError: If image has not been registered under that reference string.
        """
        try:
            return resources[self.image]
        except KeyError:
            raise KeyError('Image "{}" has not been registered in the Game Registry'.format(self.image))

    def setImage(self, image):
        """
        Set the GameRegistry image reference string for the Vehicle to ``image``
        """
        self.image = image

    def toBytes(self):
        """
        Encode the Vehicle object into a byte string.
        """
        return (str([self.__class__.__name__, self.name, self.uuid, self.pos, self.riders]).replace(', ', ',')).encode()

    @staticmethod
    def fromBytes(vBytes, vehicleClassList):
        """
        Decode the given byte string ``data`` into a vehicle object. The correct vehicle class must be given in ``vehicleClassList``.
        """
        # Get the class and the props by eval
        vehicleClass, *vehicleProps = eval(vBytes)
        finalVehicle = vehicleClassList.get(vehicleClass, Vehicle)()

        # After instantiating class, set attributes
        finalVehicle.setRegistryName(vehicleProps[0])
        finalVehicle.uuid = vehicleProps[1]
        finalVehicle.pos = vehicleProps[2]
        finalVehicle.riders = vehicleProps[3]

        return finalVehicle
