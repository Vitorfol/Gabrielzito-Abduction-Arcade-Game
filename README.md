# Gabrielzito Abduction Arcade Game (2D)

## Overview

This project implements a **2D Arcade Game** initially inspired by a classic **claw machine** and themed after a UFO abduction attempt, developed for the *Computer Graphics* course. The player controls a mechanical claw, attempting to grab(abduct) moving objects while playing under a difficulty level selected at the beginning of the game.

The main goal of the project is to **manually implement core Computer Graphics algorithms**, without relying on high-level graphics libraries, following the academic constraints defined by the course.

---

## Demo Video

Watch the game in action:

*You can [download the video](video_demo.mp4) directly.*

---

## Game Concept

* The game is viewed from **inside the claw machine**.
* The UFO and claw start at the **top-center of the screen** and can move freely on the **X axis**.
* Objects move continuously inside the machine.
* The player controls the claw using the keyboard.
* There is a large focus on the arcade style of the game.

### Difficulty Levels

Difficulty is selected in the **initial menu** and directly affects:

* Speed of moving objects
* Number of moving objects inside the machine

The game offers three difficulty levels:

* **EASY**: 1-3 prizes, slower movement (100-150% base speed)
* **NORMAL**: 3-5 prizes, moderate movement (150-250% base speed)
* **HARD**: 5-6 prizes, fast movement (250-350% base speed)

The difficulty level remains fixed during gameplay. The player may exit the game at any time by pressing **ESC**, returning to the initial menu.

---

## Controls

* **Arrow Keys**: Move the claw (X plane)
* **Space Bar**: Close the claw / attempt to grab an object
* **Menu Interaction**: Difficulty selection and game control

---

## Game Features

### Highscore System

* Tracks best completion times for each difficulty level
* Persistent storage in `highscores.txt`
* Display of top times in the main menu

### Audio System

* Background soundtrack with looping music
* Sound effects for game events:
  * UFO/claw movement
  * Successful grab
  * Game over
  * Special character voice lines

### Visual Assets

* **Gabrielzito**: The main character/prize to be grabbed
* Textured sprites for all game entities (claw, UFO, cable)
* Animated character states (movement, caught, mocking)
* Retro arcade-style pixel fonts

---

## Technical Constraints

This project strictly follows the course requirements:

* No high-level graphics libraries are used
* Only basic pixel operations are allowed (e.g., `setPixel`)
* PyGame is used **only** for:

  * Window creation
  * Pixel buffer display
  * Input handling
  * Playing sounds
  * Loading maps for text


All graphical primitives, transformations, and rendering logic are implemented manually.

---

## Implemented Computer Graphics Features

### Rasterization Primitives

* **Line rasterization** (Bresenham) - [`engine/raster.py`](src/engine/raster.py) - `bresenham()`
* **Circle rasterization** - [`engine/raster.py`](src/engine/raster.py) - `draw_circle()`
* **Ellipse rasterization** - [`engine/raster.py`](src/engine/raster.py) - `paintTexturedEllipse()`

### Region Filling

* **Flood Fill** (iterative) - [`engine/raster.py`](src/engine/raster.py) - `flood_fill_iterativo()`
  * Used in opening screen circles
* **Scanline polygon filling** - [`engine/raster.py`](src/engine/raster.py) - `paintPolygon()`
  * Used for most game objects and environment

### Geometric Transformations

All implemented in [`engine/transformations.py`](src/engine/transformations.py):

* **Translation** - `translation(tx, ty)`
* **Scaling** - `scale(sx, sy)`
* **Rotation** - `rotation(theta)`
* **Matrix composition** - `multiply_matrices()`

### Viewing Pipeline

Implemented in [`engine/viewport_utils.py`](src/engine/viewport_utils.py):

* **World → Window transformation**
* **Window → Viewport transformation**
* **Viewport translation**
* **Viewport scaling (zoom)**

### Clipping

* **Cohen-Sutherland line clipping** - [`engine/clipping_utils.py`](src/engine/clipping_utils.py)
  * Used in scene rendering for efficient line drawing

### Visual Features

* **Color gradients** - Implemented in rasterization functions
* **Texture mapping** - [`engine/raster.py`](src/engine/raster.py)
  * `paintTexturedPolygon()` - Image-to-matrix texture mapping
  * `paintTexturedEllipse()` - Textured ellipse rendering

### Animation

* Continuous object motion (prizes moving in machine) and reaction system
* Claw movement and grab animation
* Menu animations (rotating/pulsing elements)

---

## Performance and Optimizations

This project explores **performance-aware design choices**, motivated by the computational cost of matrix-based transformations and rasterization algorithms.

### Adopted Optimizations

* Efficient pixel-level operations using PyGame's PixelArray for direct memory access
* Reduction of redundant transformation calculations
* Structured rendering pipeline to minimize per-frame overhead
* Pure Python implementation with optimizations for software rasterization
---

## Repository Structure

```text
Claw-Machine-Arcade-Game/
│
├── README.md
├── requirements.txt
├── highscores.txt                # Persistent highscore storage
├── video_demo.mp4                # Game demonstration video
│
├── src/
│   ├── main.py                       # Entry point - game initialization
│   │
│   ├── engine/                       # CG Library
│   │   ├── raster.py                 # Line/circle/ellipse rasterization, scanline fill
│   │   ├── transformations.py        # Matrix operations (translate, scale, rotate)
│   │   ├── viewport_utils.py         # World→Window→Viewport transformations
│   │   ├── clipping_utils.py         # Cohen-Sutherland line clipping
│   │   └── collision.py              # Collision detection system
│   │
│   └── game/                         # Claw Machine Game
│       ├── game_loop.py              # Main game loop orchestration
│       ├── menu.py                   # Interactive menu system
│       ├── menu_scene.py             # Claw machine scene renderer
│       ├── audio_manager.py          # Sound system
│       ├── fps.py                    # FPS counter display
│       │
│       └── model/                    # Game model (entities & configuration)
│           ├── config.py             # Constants (colors, dimensions, etc.)
│           ├── difficulty.py         # Difficulty system (EASY/NORMAL/HARD)
│           ├── gamestate_enum.py     # Game state enumeration
│           ├── world.py              # Game world orchestrator
│           ├── claw.py               # Claw entity
│           ├── ufo.py                # UFO entity
│           ├── cable.py              # Cable entity
│           └── prize.py              # Prize entities (Gabrielzito)
│
└── assets/
    ├── audio/                        # Sound effects and music
    │   ├── soundtrack.ogg            # Background music
    │   ├── game-over.ogg
    │   ├── homens-verde.ogg
    │   ├── me-solta.ogg
    │   ├── ufo.ogg
    │   └── vai-comendo.ogg
    │
    ├── gabrielzito/                  # Character textures
    │   ├── caught/                   # Capture animation frames
    │   ├── mocking/                  # Mocking animation frames
    │   ├── movement/                 # Movement animation frames
    │   ├── gabriel-front.png
    │   └── gabriel-side.png
    │
    ├── fonts/                        # Retro fonts
    │   └── Pixeloid_Font_1_0/
    │
    └── *.png                         # Game sprites (claw, UFO, cable, etc.)
```

**Architecture Principles:**

* **`engine/`**: Pure Computer Graphics algorithms - reusable, game-agnostic primitives
* **`game/`**: Claw Machine-specific logic - imports from `engine/`
* **`game/model/`**: Game entities, world state, and configuration

---

## How to Run

### Requirements

```bash
pip install -r requirements.txt
```

### Running the Game

```bash
# From the project root
python src/main.py

# Or in windowed mode (for development)
python src/main.py --window
```

The game starts in fullscreen by default. Use `--window` flag for windowed mode during development.

---

## Notes

This project prioritizes **educational clarity**, **algorithmic correctness**, and **manual implementation of graphics concepts**, while also exploring performance optimization techniques beyond the standard curriculum.
