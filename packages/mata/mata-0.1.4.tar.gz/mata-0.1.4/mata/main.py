"""
2D Game Engine
- Mod Engine
- Networking Engine
- Integrated or Dedicated Server
"""
# Import the Python standard libraries
import sys

# Import the game submodules
import util
import game

if __name__ == "__main__":
    # Collect and handle the command line arguments
    ARG_HANDLER = util.ArgumentHandler(sys.argv[1:])

    # Initialise the game with the mod loader and argument handler
    RUNTIME = game.Game(ARG_HANDLER)
    RUNTIME.run()
