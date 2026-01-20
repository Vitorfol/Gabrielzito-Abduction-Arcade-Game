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

* Line rasterization
* Circle rasterization
* Ellipse rasterization

### Region Filling

* Flood Fill / Boundary Fill (opening screen)
* Scanline polygon filling (game objects and environment)

### Transformations

* Translation
* Scaling
* Rotation

### Rendering Pipeline

* World coordinates → Window transformation
* Window → Viewport transformation (including zoom)
* Cohen–Sutherland line clipping

### Visual Features

* Per-vertex color gradients
* Texture mapping using image-to-matrix loading

### Animation

* Continuous object motion
* Claw movement and grab animation

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
claw-machine-arcade/
│
├── README.md
├── requirements.txt
│
├── docs/
│   ├── professor_requirements.txt
│   ├── project_requirements.txt
│   └── design_notes.md
│
├── src/
│   └── (source code)
│
└── assets/
    └── (textures and image resources)
```

---

## How to Run (Preview)

Detailed instructions will be provided once implementation begins.

General steps:

```bash
pip install -r requirements.txt
python src/main.py
```

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
