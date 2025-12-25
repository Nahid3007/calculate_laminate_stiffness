# Laminate Theory Python Package

A Python package for **classical laminate theory (CLT)** calculations of composite laminates.  
It computes **A, B, D matrices**, effective in-plane stiffness, and detects **symmetric/unsymmetric laminates**.

---

## Features

- Read laminate configuration from a JSON file
- Define orthotropic material properties
- Define individual plies with thickness and orientation
- Compute **ply stiffness matrices (Q, Q̄)** automatically
- Compute **laminate ABD matrices**
- Detect **symmetric vs. unsymmetric laminates**
- Compute **homogenized in-plane laminate properties** (E1, E2, G12, ν12)
- Fully object-oriented and **dataclass-based**
- Logs inputs, matrices, symmetry, and homogenzied properties

---

## Project Structure

```
project_root/
├── src/
│   └── laminate/
│       ├── __init__.py
│       ├── utilities.py
│       ├── material.py
│       ├── ply.py
│       └── laminate.py
├── examples/
│   ├── example.py
│   └── input.json
├── pyproject.toml
└── README.md
```

---

## Development

- All source code is in `src/laminate/`
- Examples and test inputs are in `examples/`
- Use **editable install** to develop and test:

```bash
pip install -e .
```

- Make sure your IDE is using the same virtual environment for proper module resolution.

---

## References

- [NASA Classical Laminate Theory Reference](https://ntrs.nasa.gov/api/citations/19950009349/downloads/19950009349.pdf)

---

## License

