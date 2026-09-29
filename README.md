# 3D Projects

This repository presents three Computer Graphics and game-programming projects developed in Python with OpenGL-related technologies as part of CSE coursework. The projects explore interactive 2D rendering, 3D scenes, camera systems, and gameplay logic.

## Projects

### [catch_the_diamonds.py](catch_the_diamonds.py) — Catch the Diamonds

#### Overview

A 2D catching game. Move the catcher beneath falling diamonds, build a score, and keep up as the diamonds accelerate after each successful catch.

#### Key Features

- Diamonds fall from the top of the play area and change to a randomly selected color after each catch.
- Successful catches increase the score and falling speed; a missed diamond ends the game.
- Pause, resume, restart, and quit actions are available through keyboard and on-screen mouse controls.
- Game state is managed through a `GameState` object.

#### Graphics / Technical Concepts

- 2D OpenGL rendering with an orthographic projection.
- Custom midpoint-style line rasterization used to draw the diamond, catcher, and interface icons from points.
- Rectangle-overlap collision checks between the falling diamond and catcher.
- Time-based movement using elapsed time between updates.

#### Controls

- Left / Right arrow keys: move the catcher.
- Space: pause or resume.
- Escape: quit.
- Left mouse button on the top-left arrow: restart.
- Left mouse button on the top-center icon: pause or resume.
- Left mouse button on the top-right cross: quit.

### [3d_arena_shooter.py](3d_arena_shooter.py) — 3D Arena Shooter

#### Overview

A 3D arena shooter in which the player moves around a bounded grid, fires at enemies, and tries to survive. Enemies pursue the player, while the score, remaining lives, and missed shots are tracked.

#### Key Features

- Starts with five enemies that move toward the player and pulse in size.
- Player-fired bullets score points on hits; contact with enemies reduces lives, and missed shots count toward game over.
- Includes a toggleable third-person follow camera and a separate orbit-style camera controlled with the arrow keys.
- Cheat mode enables automatic rotation and firing when an enemy is aligned; automatic camera following can also be toggled while cheat mode is active.
- Displays life, score, missed-shot, cheat-mode, and game-over status.
- Press R after game over to reset the player, enemies, and score.

#### Graphics / Technical Concepts

- 3D OpenGL rendering with perspective projection and depth testing.
- Primitive-based object modeling using cubes, spheres, and cylinders.
- Camera positioning with `gluLookAt`, including orbit and player-follow views.
- Transformations for positioning, rotating, and scaling scene objects.
- Distance-based enemy movement and bullet collision checks.
- Game-state tracking for lives, score, missed shots, cheat mode, and game over.

#### Controls

- W / S: move forward / backward relative to the player’s facing direction.
- A / D: rotate the player.
- C: toggle cheat mode.
- V: toggle automatic camera following while cheat mode is enabled.
- Up / Down arrow keys: adjust the orbit camera’s elevation.
- Left / Right arrow keys: rotate the orbit camera.
- Left mouse button: fire.
- Right mouse button: toggle the player-follow camera.
- R: restart after game over.

### [advanced_3d_shooter.py](advanced_3d_shooter.py) — Advanced 3D Shooter

#### Overview

A 3D shooter set in a procedurally populated urban environment. Fight waves of enemies, switch between three weapons, collect health or ammunition drops, and survive as the game’s difficulty increases.

#### Key Features

- Generates buildings and trees in a bounded world, with player and enemy movement constrained by building and world-boundary collision checks.
- Enemies patrol and chase the player; boss enemies can charge and fire a spread of bullets.
- Rifle, shotgun, and sniper weapons have distinct firing rates, damage, speed, range, and ammunition; the shotgun fires multiple spread pellets.
- Health and ammunition pickups can appear when enemies are defeated.
- Wave, score, kills, health, stamina, ammunition, and time-of-day information are shown in the HUD.
- Includes jumping, crouching, stamina-limited dodging, pause/restart, and first- and third-person views.
- Day/night lighting, a night-only flashlight, fog, muzzle flash, and bullet trails contribute to the rendered scene.

#### Graphics / Technical Concepts

- 3D OpenGL rendering with perspective projection, depth testing, and transformations.
- Primitive-based modeling for buildings, trees, characters, weapons, projectiles, and pickups.
- First- and third-person camera setup, mouse-look, OpenGL lighting, spotlight configuration, blending, and fog.
- Collision checks for movement, bullets, enemies, and pickups.
- Object-oriented game systems for players, bullets, enemies, and bosses, with state-based enemy patrol and chase behavior.
- Timed game updates for firing cooldowns, day/night progression, animation, and wave progression.

#### Controls

- W / S: move forward / backward.
- A / D: strafe left / right.
- Left / Right arrow keys: turn; hold Up to jump and Down to crouch.
- Mouse movement: aim. Hold the left mouse button to fire.
- Space: dodge forward.
- 1 / 2 / 3: select rifle / shotgun / sniper. During a level-up prompt, 1 increases maximum health and 2 increases movement speed.
- C: toggle first- and third-person view.
- F: toggle the flashlight (effective at night).
- P: pause; while paused, P resumes, R restarts, and Q quits.
- R: restart the game.
- G / I: toggle god mode / infinite ammunition.

## Technologies

- Python 3 source code.
- PyOpenGL bindings for OpenGL (`OpenGL.GL`), GLU (`OpenGL.GLU`), and GLUT (`OpenGL.GLUT`).
- Python standard-library modules used by the projects: `math`, `random`, `time`, and `sys`.

## Key Concepts Demonstrated

2D and 3D rendering, primitive-based modeling, coordinate transformations, orthographic and perspective projections, camera control, line rasterization, collision detection, animation, keyboard and mouse input, object-oriented game systems, enemy behavior, and game-state management.

## How to Run

Run each Python file separately from a Python environment with PyOpenGL and working OpenGL, GLU, and GLUT support. From the repository directory, launch the desired project with Python, for example:

```text
python catch_the_diamonds.py
```

Substitute either of the other filenames to run a different project. The source files do not specify a Python version or provide dependency-installation instructions; the required OpenGL/GLU/GLUT support must be available in the runtime environment.

## Repository Structure

```text
3D-Projects/
├── README.md
├── catch_the_diamonds.py
├── 3d_arena_shooter.py
└── advanced_3d_shooter.py
```

## Academic Context

Developed as CSE coursework, these projects demonstrate practical work with computer graphics, OpenGL programming, interactive systems, game logic, and 2D/3D rendering.

## Author

**Hossain Md Nayeen Zilkar**
