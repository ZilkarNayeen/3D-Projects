# 3D Projects

This repository presents three Computer Graphics and game-programming projects developed in Python with OpenGL-related technologies as part of CSE coursework. The projects explore interactive 2D rendering, 3D scenes, camera systems, and gameplay logic.

## Projects

### Catch the Diamonds

**File:** `22201172_Hossain Md Nayeen Zilkar_Assignment2.py`

#### Overview

A 2D catching game where the player moves a catcher beneath falling diamonds, builds a score, and responds to increasing diamond speed after successful catches.

#### Key Features

* Diamonds fall from the top of the play area and change to a randomly selected color after each catch.
* Successful catches increase the score and falling speed; a missed diamond ends the game.
* Pause, resume, restart, and quit actions are available through keyboard and on-screen mouse controls.
* Game state is managed through a `GameState` object.

#### Graphics / Technical Concepts

* 2D OpenGL rendering with an orthographic projection.
* Custom midpoint-style line rasterization used to draw the diamond, catcher, and interface icons from points.
* Rectangle-overlap collision checks between the falling diamond and catcher.
* Time-based movement using elapsed time between updates.

#### Controls

* **Left / Right Arrow:** Move the catcher.
* **Space:** Pause or resume.
* **Escape:** Quit.
* **Left mouse button on the top-left arrow:** Restart.
* **Left mouse button on the top-center icon:** Pause or resume.
* **Left mouse button on the top-right cross:** Quit.

### 3D Arena Shooter

**File:** `22201172_Hossain Md Nayeen Zilkar_Assignment3.py`

#### Overview

A 3D arena shooter in which the player moves around a bounded grid, fires at enemies, and tries to survive. Enemies pursue the player while the score, remaining lives, and missed shots are tracked.

#### Key Features

* Starts with five enemies that move toward the player and pulse in size.
* Player-fired bullets score points on hits; contact with enemies reduces lives, and missed shots count toward game over.
* Includes a toggleable third-person follow camera and a separate orbit-style camera controlled with the arrow keys.
* Cheat mode enables automatic rotation and firing when an enemy is aligned.
* Automatic camera following can also be toggled while cheat mode is active.
* Displays life, score, missed-shot, cheat-mode, and game-over status.
* Press `R` after game over to reset the player, enemies, and score.

#### Graphics / Technical Concepts

* 3D OpenGL rendering with perspective projection and depth testing.
* Primitive-based object modeling using cubes, spheres, and cylinders.
* Camera positioning with `gluLookAt`, including orbit and player-follow views.
* Transformations for positioning, rotating, and scaling scene objects.
* Distance-based enemy movement and bullet collision checks.
* Game-state tracking for lives, score, missed shots, cheat mode, and game over.

#### Controls

* **W / S:** Move forward / backward relative to the player's facing direction.
* **A / D:** Rotate the player.
* **C:** Toggle cheat mode.
* **V:** Toggle automatic camera following while cheat mode is enabled.
* **Up / Down Arrow:** Adjust the orbit camera's elevation.
* **Left / Right Arrow:** Rotate the orbit camera.
* **Left mouse button:** Fire.
* **Right mouse button:** Toggle the player-follow camera.
* **R:** Restart after game over.

### Advanced 3D Shooter

**File:** `423.py`

#### Overview

A 3D shooter set in a procedurally populated urban environment. Fight waves of enemies, switch between three weapons, collect health or ammunition drops, and survive as the game's difficulty increases.

#### Key Features

* Generates buildings and trees in a bounded world, with player and enemy movement constrained by building and world-boundary collision checks.
* Enemies patrol and chase the player; boss enemies can charge and fire a spread of bullets.
* Rifle, shotgun, and sniper weapons have distinct firing rates, damage, speed, range, and ammunition.
* The shotgun fires multiple spread pellets.
* Health and ammunition pickups can appear when enemies are defeated.
* Wave, score, kills, health, stamina, ammunition, and time-of-day information are shown in the HUD.
* Includes jumping, crouching, stamina-limited dodging, pause/restart, and first- and third-person views.
* Day/night lighting, a night-only flashlight, fog, muzzle flash, and bullet trails contribute to the rendered scene.

#### Graphics / Technical Concepts

* 3D OpenGL rendering with perspective projection, depth testing, and transformations.
* Primitive-based modeling for buildings, trees, characters, weapons, projectiles, and pickups.
* First- and third-person camera setup and mouse-look.
* OpenGL lighting, spotlight configuration, blending, and fog.
* Collision checks for movement, bullets, enemies, and pickups.
* Object-oriented game systems for players, bullets, enemies, and bosses.
* State-based enemy patrol and chase behavior.
* Timed game updates for firing cooldowns, day/night progression, animation, and wave progression.

#### Controls

* **W / S:** Move forward / backward.
* **A / D:** Strafe left / right.
* **Left / Right Arrow:** Turn.
* **Up Arrow:** Jump.
* **Down Arrow:** Crouch.
* **Mouse movement:** Aim.
* **Left mouse button:** Fire.
* **Space:** Dodge forward.
* **1 / 2 / 3:** Select rifle / shotgun / sniper.
* **1 / 2 during level-up:** Increase maximum health / movement speed.
* **C:** Toggle first- and third-person view.
* **F:** Toggle the flashlight at night.
* **P:** Pause or resume.
* **R:** Restart the game.
* **Q:** Quit while paused.
* **G:** Toggle god mode.
* **I:** Toggle infinite ammunition.

## Technologies

* Python 3 source code.
* PyOpenGL bindings for OpenGL (`OpenGL.GL`), GLU (`OpenGL.GLU`), and GLUT (`OpenGL.GLUT`).
* Python standard-library modules including `math`, `random`, `time`, and `sys`.

## Key Concepts Demonstrated

* 2D and 3D rendering
* Primitive-based modeling
* Coordinate transformations
* Orthographic and perspective projections
* Camera control
* Line rasterization
* Collision detection
* Animation
* Keyboard and mouse input
* Object-oriented game systems
* Enemy behavior
* Game-state management

## How to Run

Run each Python file separately from a Python environment with PyOpenGL and working OpenGL, GLU, and GLUT support.

From the repository directory, launch the desired project with Python:

```text
python "22201172_Hossain Md Nayeen Zilkar_Assignment2.py"
```

Substitute the filename to run either of the other projects.

The source files do not specify a Python version or provide dependency-installation instructions. The required OpenGL, GLU, and GLUT support must therefore be available in the runtime environment.

## Repository Structure

```text
3D-Projects/
├── 22201172_Hossain Md Nayeen Zilkar_Assignment2.py
├── 22201172_Hossain Md Nayeen Zilkar_Assignment3.py
└── 423.py
```

## Academic Context

Developed as CSE coursework, these projects demonstrate practical work with computer graphics, OpenGL programming, interactive systems, game logic, and 2D/3D rendering.

## Author

**Hossain Md Nayeen Zilkar**
