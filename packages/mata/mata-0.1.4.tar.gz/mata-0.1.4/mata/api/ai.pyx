"""
The AI module houses all of the classes used for creating and integrating AI tasks into entities in the M.A.T.A engine.

Entities within the engine can be controlled using custom AITasks. The AITask class in this module provides a framework by which to create these tasks, and the AIHandler provides a simple method for controlling the operation of these tasks.
"""

import time

IDLE = 0
RUNNING = 1

START = 2
CONTINUE = 3
END = 4
SKIP = 5

class AIHandler:
    """
    A controller for AITask scheduling and running within a given entity.

    The Entity class in the api.entity module contains an instance of this class for handling entity AI logic. However, this AIHandler can be employed within any area of code, even within players (e.g. for AFK actions).
    """
    def __init__(self):
        #: A 2D array of the AITasks registered with this AIHandler
        self.registeredAI = [[] for a in range(10)]
        #: The current system time. Used for calculating delta time for each update.
        self.time = time.time()

    def registerAITask(self, task, weight):
        """
        Register an AI task with a certain weighting.

        Low weighting values have priority over high weightings.

        :raises TypeError: If ``weight`` is not an integer.
        :raises ValueError: If ``weight`` is not in range 0-9.
        """
        if not isinstance(weight, int):
            raise TypeError('AI Task weighting is not an integer')
        if -1 < weight < 9:
            self.registeredAI[weight].append(task)
        else:
            raise ValueError('AI Task weighting is not between 0 and 9')

    def runAITick(self, game):
        """
        Run the registered AI tasks for a tick.
        """
        # Calculate the change in time, but clip it to half a second
        deltaTime = min(time.time() - self.time, 500)
        self.time = time.time()

        # Loop each layer and task in order
        for l in range(9, -1, -1):
            for t, task in enumerate(self.registeredAI[l]):
                # Check if the task should run, and run if able
                if task.status == IDLE:
                    shouldRun = self.registeredAI[l][t].shouldStartExecute(game)
                    if shouldRun not in [START, SKIP]:
                        raise TypeError('Returned value is not a valid execution state')

                    if shouldRun == START:
                        self.registeredAI[l][t].startExecution(game)
                        self.registeredAI[l][t].status = RUNNING

                # Check if the task should continue, and run if able
                elif task.status == RUNNING:
                    shouldRun = self.registeredAI[l][t].shouldContinueExecute(game)
                    if shouldRun not in [CONTINUE, SKIP, END]:
                        raise TypeError('Returned value is not a valid execution state')

                    if shouldRun == CONTINUE:
                        self.registeredAI[l][t].continueExecution(game, deltaTime)
                    elif shouldRun == END:
                        self.registeredAI[l][t].endExecution(game)
                        self.registeredAI[l][t].status = IDLE

                else:
                    raise TypeError('Task status is not a valid execution state')

                # Skip the task if it should
                if shouldRun == SKIP:
                    self.registeredAI[l][t].skipExecution(game, deltaTime)

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has a given attribute.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

class AITask:
    """
    A single specialised AI task for use as AI logic in an entity.

    This class should never be instantiated directly, but instead subclassed and customised for each required purpose. The PickupAITask in this module provides a basic example of this class' usage.

    All AITasks should be registered into an AIHandler with an appropriate weighting. Refer to the AIHandler docs above and source code for further information.
    """
    def __init__(self, entity):
        #: The operational status of this AITask (e.g. RUNNING, IDLE)
        self.status = IDLE
        #: The entity which this AITask references
        self.entity = entity

    def shouldStartExecute(self, game):
        """
        Return whether or not the ai task should start running on a given tick.

        :returns: Status code for execution.
        """
        return SKIP

    def shouldContinueExecute(self, game):
        """
        Return whether or not the ai task should continue running on a given tick.

        :returns: Status code for execution.
        """
        return SKIP

    def startExecution(self, game):
        """
        Execute a one-shot task or begin executing a continuous task.
        """
        pass

    def continueExecution(self, game, deltaTime):
        """
        Execute a continuous task for a tick.
        """
        pass

    def endExecution(self, game):
        """
        Execute logic when the task stops execution.
        """
        pass

    def skipExecution(self, game, deltaTime):
        """
        Execute code during a skipped tick.
        """
        pass

    def hasAttribute(self, name):
        """
        Return whether the class (and classes which extend this) has a given attribute.
        """
        try:
            a = self.__getattribute__(name)
            return True
        except AttributeError:
            return False

class PickupAITask(AITask):
    """
    A simple AITask subclass used in Pickup entities for handling collection by nearby players.

    This task gives a Pickup entity a maximum life of 30 seconds, and causes its corresponding itemstack to be given to a player when they approach it.
    """
    def __init__(self, entity):
        super().__init__(entity)

        #: The number of seconds the entity has existed for
        self.lifeTime = 0

    def shouldStartExecute(self, game):
        """
        Return whether or not the ai task should start running on a given tick.
        """
        return START

    def shouldContinueExecute(self, game):
        """
        Return whether or not the ai task should continue running on a given tick.
        """
        return CONTINUE

    def continueExecution(self, game, deltaTime):
        """
        Check for an approaching player, and give itemstack if they are close enough.

        Destroy the Pickup if it has existed for more than 30 seconds.
        """
        self.lifeTime += deltaTime

        # Check for a player coming near, and respond accordingly
        players = game.getWorld(self.entity.dimension).getPlayersNear(self.entity.pos, 1.5)
        if len(players) > 0:
            x, y = self.entity.pos
            distances = [((a.pos[0] - x)**2 + (a.pos[1] - y)**2)**0.5 for a in players]
            closest = players[distances.index(min(distances))]
            closest.inventory.addItemstack(self.entity.getItem())
            self.entity.isDead = True

        # If the pickup has existed for more than 30 seconds
        if self.lifeTime > 30:
            self.entity.isDead = True
