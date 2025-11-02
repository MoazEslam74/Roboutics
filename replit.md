# Hospital Robot Simulation

## Overview
This is a robotics simulation project that visualizes a hospital robot navigating through a hospital environment with obstacles. The robot can be controlled by clicking on a destination, and it will navigate to that point while avoiding walls and obstacles.

## Project Purpose
- Demonstrates robot navigation and pathfinding concepts
- Provides visual simulation of a hospital robot moving through a structured environment
- Includes collision detection and obstacle avoidance
- Supports interactive target selection via mouse clicks

## Current State
The project is fully functional and ready to run. The main simulation displays a robot that can be directed to move to any location by clicking on the screen. The robot will navigate around obstacles (walls representing hospital rooms) to reach its destination.

## Recent Changes
- **2025-11-02**: Initial import and setup in Replit environment
  - Configured Python 3.11 environment
  - Installed pygame dependency
  - Set up VNC workflow for GUI display
  - Created .gitignore for Python project
  - Documented project structure and setup

## Project Architecture

### Main Components
1. **simulations.py** - Main simulation file located in `Robotics/` directory
   - Pygame-based GUI application
   - Robot movement and pathfinding logic
   - Collision detection system
   - Interactive mouse-based target selection

2. **Robot Assets** - Located in `Robotics/images/`
   - 8 directional robot images (up, down, left, right, and diagonal combinations)
   - Images are loaded and scaled to 40x40 pixels

3. **Labs** - Contains Jupyter notebooks for various robotics concepts:
   - Lab 2: Grid mapping and robotics fundamentals
   - Lab 3: A* pathfinding algorithm with different heuristics (Manhattan, Euclidean, Chebyshev)
   - Lab 4: RRT (Rapidly-exploring Random Tree) path planning

### Key Features
- **Interactive Control**: Click anywhere on the screen to set a target destination
- **Collision Detection**: Robot stops and avoids obstacles
- **Directional Visuals**: Robot sprite changes based on movement direction
- **Fullscreen Support**: Press F11 or M to toggle fullscreen/maximize
- **Hospital Layout**: Simulates a multi-room hospital environment with doors and corridors

### Technical Details
- **Language**: Python 3.11
- **Framework**: Pygame 2.6.1
- **Display**: 700x700 window (resizable)
- **Frame Rate**: 30 FPS
- **Robot Speed**: 4 pixels per frame
- **Obstacle System**: Rectangle-based collision detection

## How to Run
The simulation runs automatically via the configured workflow. The GUI will display in the VNC viewer where you can:
1. View the hospital layout with walls and corridors
2. Click anywhere to set a target destination for the robot
3. Watch the robot navigate to the target while avoiding obstacles
4. Press F11 or M to toggle fullscreen mode

## Project Structure
```
.
├── Robotics/
│   ├── simulations.py          # Main simulation script
│   ├── images/                 # Robot sprite images
│   │   ├── up_robot.png
│   │   ├── down_robot.png
│   │   ├── left_robot.png
│   │   ├── right_robot.png
│   │   └── (4 diagonal images)
│   └── Labs/                   # Educational Jupyter notebooks
│       ├── Lab 2_2/            # Grid mapping
│       ├── Lab 3/              # A* pathfinding
│       └── Lab 4/              # RRT path planning
└── README.md                   # Project title
```

## Dependencies
- Python 3.11
- pygame 2.6.1

## User Preferences
None specified yet.

## Future Enhancement Ideas
- Implement A* or RRT pathfinding algorithms from the labs into the simulation
- Add multiple robots
- Create different hospital layouts
- Add obstacles that can be placed dynamically
- Implement waypoint-based navigation
