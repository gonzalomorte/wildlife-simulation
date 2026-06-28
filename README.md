# 🦅 Wildlife Simulation

> A Pygame-based predator–prey ecosystem simulator built on the Boids flocking algorithm, extended with energy dynamics, refuge mechanics, and a full experiment framework.

This project was developed as a coursework assignment for **Advanced Topics in Artificial Intelligence** at the [Wrocław University of Science and Technology](https://pwr.edu.pl/en/) (Politechnika Wrocławska). It explores how classical collective-behaviour rules interact with survival pressures — starvation, predation, and resource scarcity — and provides a reproducible pipeline for running and analysing parameter-sweep experiments.

---

## Authors

| Name | GitHub |
|------|--------|
| Gonzalo Morte Gómez | [@gonzalomorte](https://github.com/gonzalomorte) |
| Jose Daniel Moya Moreno | [@josedanielmoya](https://github.com/josedanielmoya) |
| Álvaro Rivera Moreno | [@AlvaroRiveraMoreno](https://github.com/AlvaroRiveraMoreno) |

---

## Table of Contents

- [🦅 Wildlife Simulation](#-wildlife-simulation)
  - [Authors](#authors)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Running the Simulation](#running-the-simulation)
    - [Interactive Mode](#interactive-mode)
    - [CLI Parameters](#cli-parameters)
    - [Available Maps](#available-maps)
    - [Headless / Batch Mode](#headless--batch-mode)
  - [Experiment Framework](#experiment-framework)
    - [Boids Parameter Tuning](#boids-parameter-tuning)
    - [Refuge Capacity \& Food Ratio Experiments](#refuge-capacity--food-ratio-experiments)
    - [Analysing Results](#analysing-results)
  - [Architecture](#architecture)
    - [Steering Forces](#steering-forces)
    - [Energy System](#energy-system)
    - [Refuge System](#refuge-system)
    - [Simulation Loop Phases](#simulation-loop-phases)
  - [Visualisation](#visualisation)
  - [Logging](#logging)

---

## Background

The simulation is rooted in Craig Reynolds' **Boids** model (1987), which reproduces the emergent flocking behaviour of birds using three local rules applied to each agent:

| Rule | Description |
|------|-------------|
| **Separation** | Steer away from neighbours to avoid crowding |
| **Alignment** | Match the average heading of the local flock |
| **Cohesion** | Move toward the average position of the local flock |

On top of these classic rules, this project introduces a fully coupled **ecological layer**:

- Boids (prey) deplete energy continuously and must forage for food items scattered across the map.
- Predators hunt boids, gaining energy from each kill and wandering when satiated.
- Refuges act as sanctuaries where boids are invisible and immune to predators, but capacity-limited.
- Starvation eliminates any agent — boid or predator — whose energy reaches zero.

The result is a dynamic, emergent ecosystem where the three Boids weights, food availability, and refuge capacity interact to determine whether prey, predators, or both survive.

---

## Features

- Real-time Pygame visualisation with bird-shaped sprites, energy bars, and an animated predator glow.
- Interactive sliders to adjust separation, alignment, and cohesion weights live during the simulation.
- Optional visual overlays: velocity arrows and perception-radius circles.
- 11 hand-crafted maps plus a random-generation fallback.
- CLI-driven headless mode for high-throughput batch experiments.
- CSV experiment logger and a tick-by-tick stats logger.
- Ready-to-run batch scripts for parameter sweeps with parallel execution.
- Analysis scripts producing time-series evolution plots and summary statistics with Matplotlib/Seaborn.

---

## Project Structure

```
wildlife-simulation/
│
├── wildlife-simulation-code/          # Simulation source code
│   ├── main.py                        # Entry point & CLI argument parser
│   ├── core/
│   │   ├── vector.py                  # 2D vector arithmetic (Vec2)
│   │   ├── boid.py                    # Prey agent (movement, energy, stuck detection)
│   │   ├── predator.py                # Predator agent (hunt, chase, wander)
│   │   ├── food.py                    # Food item and related constants
│   │   ├── refuge.py                  # Safe zone with capacity management
│   │   ├── obstacle.py                # Circular obstacle
│   │   ├── simulation.py              # Simulation engine (steering, phases, logging)
│   │   ├── map_loader.py              # JSON map loader
│   │   ├── experiment_logger.py       # CSV logger for batch experiments
│   │   ├── stats_logger.py            # Per-tick CSV logger
│   │   ├── slider.py                  # Interactive slider UI element
│   │   └── checkbox.py                # Toggle checkbox UI element
│   ├── ui/
│   │   └── render.py                  # Pygame drawing routines
│   └── maps/
│       └── maps.json                  # All 11 predefined map configurations
│
├── tunning_boids_parameter-experiment-files/   # Boids weight sweep experiments
│   ├── run_parallel.sh                         # GNU Parallel batch runner
│   ├── command_run_parallel.txt                # Command reference
│   ├── separation/                             # Separation weight results & plotter
│   ├── alignment/                              # Alignment weight results & plotter
│   └── cohesion/                               # Cohesion weight results & plotter
│
├── refuge_and_food_experiments/       # Refuge capacity & food ratio experiments
│   ├── run_experiments.py             # Parallel batch runner (Python ProcessPoolExecutor)
│   ├── analyze_experiments.py         # Analysis & visualisation script
│   └── plots/                         # Pre-generated result plots
│       ├── refuge_capacity_experiments/
│       └── food-boid_ratio/
│
├── wildlife-simulation_presentation.pdf
└── wildlife-simulation_presentation.pptx
```

---

## Requirements

- **Python 3.9+**
- **pygame** — simulation window and rendering
- **pandas** — experiment data handling
- **matplotlib** — result plots
- **seaborn** — styled statistical plots
- **GNU parallel** *(optional)* — for the shell-based boids parameter sweep

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/gonzalomorte/wildlife-simulation.git
cd wildlife-simulation

# 2. Install Python dependencies
pip install pygame pandas matplotlib seaborn

# 3. (Optional) Install GNU parallel for boids parameter tuning
# On Debian/Ubuntu:
sudo apt install parallel
# On macOS with Homebrew:
brew install parallel
```

No additional setup is required — the simulation reads maps from the bundled `wildlife-simulation-code/maps/maps.json`.

---

## Running the Simulation

All commands below assume you are in the repository root (`wildlife-simulation/`).

### Interactive Mode

Launch the simulation with the default map and GUI:

```bash
python wildlife-simulation-code/main.py
```

This opens a 1200 × 800 window with 10 boids and 1 predator on map 10 ("Balanced Quads").

### CLI Parameters

| Argument | Type | Default | Description |
|---|---|---|---|
| `-map INDEX` | int (0–10) | `10` | Map to load (see [Available Maps](#available-maps)) |
| `-sep VALUE` | float (0–3) | `1.25` | Separation steering weight |
| `-ali VALUE` | float (0–3) | `1.75` | Alignment steering weight |
| `-coh VALUE` | float (0–3) | `2.00` | Cohesion steering weight |
| `--refuge-capacity VALUE` | int | `10` | Max boids per refuge |
| `--food-ratio VALUE` | float | `0.70` | Food items relative to boid count |
| `--duration SECONDS` | int | — | Auto-stop the simulation after N seconds |
| `--headless` | flag | — | Disable the window (faster for batch runs) |
| `--run-id ID` | int | — | Enable CSV logging and assign a run identifier |
| `--log-file PATH` | str | `experiments.csv` | Output path for the CSV log |

**Examples:**

```bash
# Run the "Maze" map with custom Boids weights
python wildlife-simulation-code/main.py -map 5 -sep 0.5 -ali 2.0 -coh 1.5

# Run headless for 60 seconds and log results
python wildlife-simulation-code/main.py --headless --duration 60 --run-id 1 --log-file results/run.csv

# Use a small refuge (capacity 3) and scarce food
python wildlife-simulation-code/main.py -map 2 --refuge-capacity 3 --food-ratio 0.3
```

### Available Maps

| ID | Name | Description |
|----|------|-------------|
| 0 | Open Field | Minimal obstacles, wide open space |
| 1 | Forest Clearing | Multiple medium obstacles scattered around |
| 2 | Canyon | Two large obstacles creating a narrow passage |
| 3 | Dense Forest | Many small obstacles creating a complex environment |
| 4 | Corner Refuge | Obstacles in corners with a central refuge |
| 5 | Maze | Strategic obstacle placement creating maze-like paths |
| 6 | Island | Large central obstacle with refuges on the sides |
| 7 | Scattered | Random-sized obstacles spread across the map |
| 8 | Twin Valleys | Two separated areas with obstacles between them |
| 9 | Edge Barriers | Obstacles along edges forcing movement toward the centre |
| 10 | Balanced Quads *(default)* | Two obstacles and two refuges across quadrants |

Omitting `-map` uses map 10. To generate two random obstacles and one random refuge instead, edit the `Simulation` constructor to pass `map_index=None`.

### Headless / Batch Mode

Headless mode is activated automatically when `--run-id` is provided, or explicitly via `--headless`. It sets `SDL_VIDEODRIVER=dummy` before importing Pygame, so no display server is required — useful for remote servers and CI environments.

---

## Experiment Framework

> **Note:** the experiment scripts call `main.py` with a relative path, so they must be invoked from inside the `wildlife-simulation-code/` directory. Enter it once before running any of the commands below:
>
> ```bash
> cd wildlife-simulation-code
> ```

### Boids Parameter Tuning

Located in `tunning_boids_parameter-experiment-files/`. Each of the three Boids weights (separation, alignment, cohesion) was swept independently across values `{0.00, 0.25, 0.50, ..., 3.00}` with 5 replicates each and a 120-second duration, using **GNU Parallel** for concurrency:

```bash
bash ../tunning_boids_parameter-experiment-files/run_parallel.sh > parallel.log 2>&1 &
```

The script fixes the other two weights at their defaults (`sep=1.25`, `ali=1.75`) while varying the target weight. All runs use map 5 ("Maze"). Raw results and pre-generated analysis plots are stored under `separation/`, `alignment/`, and `cohesion/`, each with its own `plotter.py`.

### Refuge Capacity & Food Ratio Experiments

Located in `refuge_and_food_experiments/`. Two parameter sweeps were run with 15 replicates each on map 10 ("Balanced Quads"), using Python's `ProcessPoolExecutor` for parallel execution:

| Set | Varied parameter | Values tested | Fixed parameter |
|-----|-----------------|---------------|-----------------|
| **A** | Refuge capacity | 2, 4, 6, 8, 10 | Food ratio = 0.7 |
| **B** | Food ratio | 0.1, 0.5, 1.0, 1.5, 2.0 | Refuge capacity = 6 |

```bash
# Run both experiment sets (75 simulations total, 4 parallel workers)
python ../refuge_and_food_experiments/run_experiments.py

# Run only Set A (refuge capacity)
python ../refuge_and_food_experiments/run_experiments.py --set A

# Run only Set B (food ratio)
python ../refuge_and_food_experiments/run_experiments.py --set B
```

Each run spawns `main.py` as a subprocess in headless mode. Results are saved to timestamped CSV files under `simulation_logs/`.

### Analysing Results

```bash
# Analyse all available CSVs (auto-discovers timestamped files)
python ../refuge_and_food_experiments/analyze_experiments.py

# Analyse a specific experiment set
python ../refuge_and_food_experiments/analyze_experiments.py --set A
python ../refuge_and_food_experiments/analyze_experiments.py --set B

# Analyse a specific CSV file
python ../refuge_and_food_experiments/analyze_experiments.py --file simulation_logs/experiments_refuge_capacity_20260120_161715.csv
```

The script outputs:

- **Per-value time-series plots** — mean boids alive and mean predators alive over time for each tested parameter value.
- **Final-means plot** — mean final population of both species across parameter values.
- **Summary dashboard** — a 2×2 grid showing success rate, final boid count distribution, time-to-extinction, and outcome breakdown (success / failure / inconclusive).

Outcome categories are defined as:

| Outcome | Condition |
|---------|-----------|
| **Success** | Predators starve; at least one boid survives |
| **Failure** | All boids go extinct |
| **Inconclusive** | Both populations survive the time limit |

---

## Architecture

### Steering Forces

Every simulation step, the `Simulation` class computes up to six steering forces for each active boid and combines them into a single limited acceleration vector:

```
force = sep × separation
      + ali × alignment
      + coh × cohesion
      + obstacle_avoidance_weight × obstacle_avoidance
      + refuge_searching          (weight implicit)
      + food_seeking_weight × food_seeking
```

If the obstacle-avoidance component exceeds a priority threshold (`0.3 × max_force`), all other forces are discarded and only avoidance is applied — preventing boids from flying into trees while chasing food or fleeing predators.

Predators receive only two forces: obstacle avoidance and a `hunt` force that steers toward the nearest visible, unprotected boid. When satiated or with no valid target, they wander with a smoothly perturbed angle.

All vectors use the custom `Vec2` class, which supports arithmetic operators, normalisation, magnitude limiting (`limit`), and magnitude assignment (`set_magnitude`) — matching Reynolds' original formulation.

### Energy System

Both boids and predators carry a food/energy value in `[0, 100]`. Energy is consumed every frame by two components:

- **Basal metabolism** — a constant drain of 1 unit per second (`1/60` per frame at 60 FPS).
- **Kinetic cost** — proportional to speed², so a boid moving at maximum speed consumes twice as much energy as one standing still.

Boids replenish energy by eating `Food` items spawned across the map (capped by a `SATIETY_THRESHOLD` of 85 to prevent overeating while fleeing). Predators replenish by killing boids (+15 energy per kill) and stop hunting when they are too full to absorb the energy gain. Any agent whose energy reaches zero is permanently removed.

### Refuge System

Refuges are circular safe zones with a configurable capacity (default 10). The entry/exit logic runs every step:

- A boid outside a refuge that is sufficiently fed (`food > 50`) and within the refuge's radius will enter it if there is space.
- A boid inside a refuge whose food drops to or below the threshold exits and resumes foraging.
- While inside, a boid does not move, is excluded from neighbour calculations, and cannot be killed by predators.
- Predators ignore boids flagged as `in_refuge` when choosing targets.

### Simulation Loop Phases

Each call to `Simulation.step()` executes six ordered phases to avoid sequential bias:

1. **Energy update** — decrement food for all boids and predators.
2. **Refuge management** — process all refuge entries and exits.
3. **Food spawning & eating** — try to spawn food up to the configured ratio; boids eat nearby items.
4. **Boid steering** — compute all six forces for every active boid; apply simultaneously.
5. **Predator update** — compute and apply hunting/wandering forces for each predator; kill boids within `KILL_RADIUS = 10`.
6. **Cleanup & logging** — remove starved agents; record step metrics.

The simulation auto-terminates when either species reaches zero.

---

## Visualisation

The Pygame renderer (`ui/render.py`) draws every entity as a directional, velocity-aligned sprite:

| Entity | Sprite | Colour |
|--------|--------|--------|
| Boid (calm) | Small bird shape | Blue / teal |
| Boid (targeted) | Small bird shape | Yellow |
| Predator | Large hawk/eagle shape | Dark red / brown |
| Food | Small filled circle | Yellow-green |
| Obstacle | Layered circles with texture | Forest green |
| Refuge | Layered circles with occupancy counter | Dark grey/brown |

Each agent displays a colour-coded energy bar (green → red as energy drops). When a predator can eat (not satiated), a pulsing red glow is drawn around it.

The control panel in the top-left corner provides:

- **Three sliders** (`sep`, `ali`, `coh`) — drag to adjust the corresponding Boids weight in real time. Disabled during logged experiments to keep parameters fixed.
- **Two checkboxes** — toggle velocity-direction arrows and perception-radius circles for all agents.

---

## Logging

Two independent loggers record data during a run:

**`ExperimentLogger`** — activated by `--run-id`. Appends one row per second to a shared CSV with the columns:

```
run_id, map_id, initial_boids, initial_predators,
refuge_capacity, food_ratio, timestamp_sec,
boids_alive, predators_alive
```

**`StatsLogger`** — always active. Writes per-tick data to individual CSV files, capturing higher-resolution metrics including `boids_in_refuge`, `boids_eaten`, `avg_boid_food_level`, flock cohesion statistics, and more.

At the end of every run, a summary is printed to stdout:

```
Simulation summary
Ended because    : extinction
Runtime          : 47.32s
Steps            : 2839
Boids start/alive: 10 -> 0
Boids eaten      : 3
Boids starved    : 7
Predators start/alive: 1 -> 0
Predators starved    : 1
```

---

*Developed for Advanced Topics in Artificial Intelligence — Wrocław University of Science and Technology.*