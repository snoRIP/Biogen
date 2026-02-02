# 🧪 Bio-Gen Pro: Evolutionary Neural Laboratory

Welcome to **Bio-Gen Pro**, a high-performance evolutionary simulation where agents with neural network brains survive, reproduce, and evolve in a dynamic environment.

## 🚀 Features
- **Neural Evolution:** Every agent has a brain (Neural Network) that processes senses and controls movement.
- **Genetic DNA:** Traits like speed, sense radius, and aggression are passed to offspring with mutations.
- **Scientific Cyberpunk UI:** Real-time performance profiling, population analytics, and neural core inspection.
- **Optimized Engine:** Uses Spatial Partitioning and Level of Detail (LOD) to handle hundreds of agents smoothly.

---

## 🛠 Project Structure
The project is organized into a clean, modular architecture:

- **`core/`**: The "heart" of the simulation.
  - `agent.py`: Logic for individual creatures.
  - `brain.py`: Neural Network implementation.
  - `simulation.py`: Global simulation controller.
  - `world.py`: Resources and environment objects.
  - `spatial_grid.py`: Performance optimization for proximity checks.
- **`ui/`**: Visualization and interaction.
  - `manager.py`: HUD and Inspector rendering.
  - `camera.py`: Smooth camera movement and zoom.
  - `render_utils.py`: Graphics and glow effects.
- **`utils/`**: Helper modules.
  - `config.py`: Tweakable simulation constants.
- **`tests/`**: Automated unit tests to ensure stability.
- **`main.py`**: The main entry point to launch the laboratory.

---

## 🚦 How to Run

### 1. Prerequisites
Ensure you have Python 3.8+ installed. You will need the `pygame` library.

```bash
pip install -r requirements.txt
```

### 2. Launch the Simulation
Run the following command from the project root:

```bash
python main.py
```

### 3. Controls
- **Mouse Wheel**: Zoom in/out (centered on cursor).
- **Right-Click + Drag**: Pan the camera.
- **Left-Click**: Select an agent to inspect its brain.
- **Space**: Pause / Resume simulation.
- **1, 2, 3**: Change simulation speed (1x, 2x, 5x).
- **R**: Reset camera view.

---

## 🧪 Running Tests
To verify the core logic, run the test suite:

```bash
python -m unittest tests/test_simulation.py
```

---

## 🧬 Archetypes
- **Gatherers (Green):** Focused on survival and efficient resource gathering.
- **Hunters (Red):** Predatory agents that attack others when hungry.
- **Explorers (Purple):** Fast-moving agents with high exploration drive.

Enjoy your research in the Bio-Gen Pro Laboratory!
