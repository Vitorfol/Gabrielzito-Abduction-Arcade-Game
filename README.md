# Claw Machine Arcade Game (2D)

## Overview

This project implements a **2D Arcade Game** inspired by a classic **claw machine**, developed for the *Computer Graphics* course. The player controls a mechanical claw inside the machine, attempting to grab moving objects while playing under a difficulty level selected at the beginning of the game.

The main goal of the project is to **manually implement core Computer Graphics algorithms**, without relying on high-level graphics libraries, following the academic constraints defined by the course.

---

## Game Concept

* The game is viewed from **inside the claw machine**.
* The claw starts at the **top-center of the screen** and can move freely on the **X and Y axes**.
* Objects move continuously inside the machine.
* The player controls the claw using the keyboard.
* When the player presses **SPACE**, the claw closes and a **viewport transformation** is triggered to emphasize the grabbing action.

### Difficulty Levels

Difficulty is selected in the **initial menu** and directly affects:

* Speed of moving objects
* Number of moving objects inside the machine

The difficulty level remains fixed during gameplay. The player may exit the game at any time by pressing **ESC**, returning to the initial menu.

---

## Controls

* **Arrow Keys**: Move the claw (X/Y plane)
* **Space Bar**: Close the claw / attempt to grab an object
* **Menu Interaction**: Difficulty selection and game control

---

## Technical Constraints

This project strictly follows the course requirements:

* No high-level graphics libraries are used
* Only low-level pixel operations are allowed (e.g., `setPixel`)
* PyGame is used **only** for:

  * Window creation
  * Pixel buffer display
  * Input handling

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
  * Used for all game objects and environment

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
* **Viewport scaling (zoom)** - Applied during claw grab action

### Clipping

* **Cohen-Sutherland line clipping** - [`engine/clipping_utils.py`](src/engine/clipping_utils.py)
  * Used in scene rendering for efficient line drawing

### Visual Features

* **Per-vertex color gradients** - Implemented in rasterization functions
* **Texture mapping** - [`engine/raster.py`](src/engine/raster.py)
  * `paintTexturedPolygon()` - Image-to-matrix texture mapping
  * `paintTexturedEllipse()` - Textured ellipse rendering

### Animation

* Continuous object motion (prizes moving in machine)
* Claw movement and grab animation
* Menu animations (rotating/pulsing elements)

---

## Performance and Optimizations

This project explores **performance-aware design choices**, motivated by the computational cost of matrix-based transformations and rasterization algorithms.

### Adopted and Planned Optimizations

* GPU acceleration for matrix and vector operations using **CUDA**
* Reduction of redundant transformation calculations
* Structured rendering pipeline to minimize per-frame overhead

Further optimization details and design decisions are documented in the `design_notes` file and expanded progressively during development.

---

## Repository Structure

```text
trabalho1/
│
├── README.md
├── requirements.txt
│
├── docs/
│   ├── professor_requirements.txt    # ✅ Course requirements (all implemented)
│   ├── project_requirements.txt      # Game-specific requirements
│   └── implementation_draft.md       # Implementation notes
│
├── src/
│   ├── main.py                       # Entry point - game initialization
│   │
│   ├── engine/                       # 🎨 CG Library (graded components)
│   │   ├── raster.py                 # Line/circle/ellipse rasterization, scanline fill
│   │   ├── transformations.py        # Matrix operations (translate, scale, rotate)
│   │   ├── viewport_utils.py         # World→Window→Viewport transformations
│   │   ├── clipping_utils.py         # Cohen-Sutherland line clipping
│   │   └── collision.py              # Collision detection system
│   │
│   └── game/                         # 🎮 Claw Machine Game
│       ├── game_loop.py              # Main game loop orchestration
│       ├── menu.py                   # Interactive menu system
│       ├── menu_scene.py             # Claw machine scene renderer
│       ├── audio_manager.py          # Sound system
│       ├── fps.py                    # FPS counter display
│       │
│       └── model/                    # Game model (entities & configuration)
│           ├── config.py             # Constants (colors, dimensions, etc.)
│           ├── difficulty.py         # Difficulty system
│           ├── gamestate_enum.py     # Game state enumeration
│           ├── world.py              # Game world orchestrator
│           ├── claw.py               # Claw entity
│           ├── ufo.py                # UFO entity
│           ├── cable.py              # Cable entity
│           └── prize.py              # Prize entities
│
└── assets/
    ├── audio/                        # Sound effects and music
    │   └── soundtrack.ogg
    ├── *.png                         # Game sprites and textures
    └── mocking/                      # Character animation frames
```

**Architecture Principles:**

* **`engine/`**: Pure Computer Graphics algorithms - reusable, game-agnostic primitives (graded portion)
* **`game/`**: Claw Machine-specific logic - imports from `engine/` but never vice-versa
* **`game/model/`**: Game entities, world state, and configuration (MVC model layer)
* **Clean separation**: Easy for professors to evaluate CG implementation independently

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

## Demo Video

A demonstration video of the game execution will be provided here:

> *(Link to be added)*

---

## Team

Developed by a three-member team as part of the Computer Graphics course.

---

## Notes

This project prioritizes **educational clarity**, **algorithmic correctness**, and **manual implementation of graphics concepts**, while also exploring performance optimization techniques beyond the standard curriculum.
