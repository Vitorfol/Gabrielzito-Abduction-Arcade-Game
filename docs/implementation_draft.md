# Ideas, Drafts and Future Considerations

This document is a **sandbox** for ideas, optimization strategies, and possible code organization decisions. Nothing in this file is mandatory; it serves as a reference and discussion base for the team.

---

## Optimization Ideas (Computer Graphics Focus)

The following optimizations are aligned with classical Computer Graphics pipelines and may be partially or fully adopted during development:

* **Precomputation of transformation matrices** when objects do not change state
* **Use of 3×3 homogeneous transformation matrices**
* **Efficient custom rendering pipeline** with clear separation of stages
* **Avoid recomputing scanline filling** when polygon geometry is unchanged
* **Bounding boxes** to skip rasterization of unnecessary pixels
* **Manual double buffering** to reduce flickering and tearing
* **Lookup Tables (LUTs)** for sine and cosine values
* **Clipping before rasterization** (Cohen–Sutherland) to reduce workload

Some of these optimizations may be combined with GPU acceleration when appropriate.

---

## CUDA-Related Ideas

* Batch processing of vertex transformations
* Parallel matrix–vector multiplication
* Offloading repetitive numerical computations from CPU to GPU

CUDA usage is considered an **optimization layer**, not a dependency for correctness.

---

## Future Code Structure Ideas (Draft)

The following directory structure is a **preliminary idea** for organizing the source code once implementation begins:

```text
src/
├── main.py            # Application entry point and main loop
├── raster/            # Rasterization algorithms (line, circle, ellipse)
├── transforms/        # Geometric transformations and matrix utilities
├── clipping/          # Cohen–Sutherland clipping implementation
├── game/              # Game logic (claw, objects, menu, states)
└── utils/             # Helper functions, math utilities, LUTs
```

This structure is only a suggestion and may evolve as development progresses.

---

## Notes

* This file exists to avoid losing ideas during early planning stages
* Ideas listed here are **not commitments**
* The team is free to revise, remove, or expand this document at any time
