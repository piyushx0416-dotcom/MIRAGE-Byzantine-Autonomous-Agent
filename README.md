# 🛸 MIRAGE: Byzantine Autonomous Agent
### *Decentralized Fault-Tolerant Defense Framework for Autonomous UAV Drone Swarms*

[![Live Website Demo](https://img.shields.io/badge/Live_Website-Interactive_Portal-00ffff?style=for-the-badge&logo=google-chrome&logoColor=black)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online-success?style=for-the-badge&logo=github)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-3D_WebGL-black?style=for-the-badge&logo=three.js)](https://threejs.org/)
[![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-ML_Anomaly_Detection-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📑 Table of Contents
1. [Executive Summary](#-executive-summary)
2. [The Core Problem (Why Drone Swarms Fail Without BFT)](#-the-core-problem)
3. [The MIRAGE Solution & System Overview](#-the-mirage-solution)
4. [Architecture: The 5 Layers of Swarm Defense](#-architecture-the-5-layers-of-swarm-defense)
   - [Layer 1: Classical Spatial BFT Voting](#layer-1-classical-spatial-bft-voting-geometric-consensus)
   - [Layer 2: ML Isolation Forest Kinematic Anomaly Detection](#layer-2-ml-isolation-forest-kinematic-anomaly-detection)
   - [Layer 3: Hybrid Consensus Fusion Engine](#layer-3-hybrid-consensus-fusion-engine)
   - [Layer 4: Dynamic Asymmetric Trust Decay Engine](#layer-4-dynamic-asymmetric-trust-decay-engine)
   - [Layer 5: Autonomous Physical Quarantine & Mesh Severing](#layer-5-autonomous-physical-quarantine--mesh-severing)
5. [Swarm Kinematics & Boids Flocking Model](#-swarm-kinematics--boids-flocking-model)
6. [Simulated Adversarial Attack Profiles](#-simulated-adversarial-attack-profiles)
7. [Benchmark Performance & Empirical Results](#-benchmark-performance--empirical-results)
8. [Live Web Application & Module Guide](#-live-web-application--module-guide)
9. [Local PyGame Simulation Installation & Quickstart](#-local-pygame-simulation-installation--quickstart)
10. [Simulation Controls & Keyboard Shortcuts](#-simulation-controls--keyboard-shortcuts)
11. [Project Codebase & Directory Structure](#-project-codebase--directory-structure)
12. [Frequently Asked Questions (FAQ)](#-frequently-asked-questions-faq)
13. [Hardware Deployment Roadmap (ROS2 / PX4 / MAVLink)](#-hardware-deployment-roadmap)
14. [License & Acknowledgments](#-license--acknowledgments)

---

## 📌 Executive Summary

**MIRAGE** (*Mesh Immunity & Robust Autonomous Guidance Engine*) is a zero-trust, decentralized defense framework designed to secure autonomous unmanned aerial vehicle (UAV) swarms against malicious, hijacked, or malfunctioning drones (**Byzantine adversaries**). 

Operating entirely peer-to-peer (P2P) with **no single point of failure and zero reliance on a ground control station**, MIRAGE combines **geometric Spatial Byzantine Fault Tolerance (BFT)** with **unsupervised Machine Learning (Isolation Forest)** to detect falsified telemetry, dynamically decay adversary trust, sever rogue communication links, and physically herd compromised drones into an isolated quarantine holding zone.

```
       [ 20 Autonomous UAVs in P2P Mesh ]
                        │
      ┌─────────────────┴─────────────────┐
      ▼                                   ▼
 [ Honest UAVs ]                 [ Byzantine Rogue UAVs ]
 (True Coordinates)              (Falsified GPS / Ghost Rays / Drift)
      │                                   │
      └─────────────────┬─────────────────┘
                        ▼
    ┌───────────────────────────────────────────┐
    │     MIRAGE MULTI-LAYER DEFENSE CORE       │
    │  1. Spatial Centroid Geometric Voting     │
    │  2. 7-Feature ML Isolation Forest Score   │
    │  3. Hybrid Consensus Truth Fusion         │
    │  4. Asymmetric Dynamic Trust Decay Engine │
    └───────────────────┬───────────────────────┘
                        ▼
          Is Node Trust Score < 45.0%?
          ├─► [YES: ADVERSARY DETECTED]
          │   ├── Sever P2P Mesh Communication Edges
          │   ├── Drop Trust Score to 0%
          │   └── Physically Reroute to Quarantine Holding Corral
          │
          └─► [NO: TRUSTED NODE]
              └── Maintain Full Swarm Formation & Mission Flight
```

---

## 🎯 The Core Problem

### The Promise of Autonomous Drone Swarms
Modern autonomous drone swarms are revolutionizing search-and-rescue, environmental disaster mapping, precision agriculture, and tactical defense. Rather than having a human pilot per drone, dozens of UAVs coordinate autonomously by sharing real-time status packets (position, velocity, altitude) over an ad-hoc peer-to-peer (P2P) wireless mesh.

### The Byzantine Threat Model
In real-world environments, centralized ground stations represent a fatal single point of failure (vulnerable to electronic jamming, line-of-sight loss, or direct attack). Therefore, swarms must be **decentralized**.

However, decentralization introduces severe vulnerability to **The Byzantine Generals Problem**:
1. **GPS Spoofing & False Broadcasts**: A compromised drone physically located at $(X_1, Y_1)$ broadcasts false coordinates $(X_{\text{fake}}, Y_{\text{fake}})$. Honest drones altering course to accommodate this ghost drone will collide with one another or drift off-mission.
2. **Coordinated Swarm Splitting (Sybil Attacks)**: Multiple colluding rogue drones broadcast contradictory cluster positions, causing honest drones to splinter into separate, ineffective sub-swarms.
3. **Stealth Kinematic Drift**: Clever adversaries do not broadcast wild outliers; they inject micro-deviations that slowly destabilize the swarm's centroid over time.
4. **Intermittent Malice**: Rogue nodes alternate between honest and dishonest broadcasts to exploit naive reset mechanisms.

**Without an autonomous Byzantine Fault Tolerance system, a single hacked drone can crash the entire swarm.**

---

## 🛡️ The MIRAGE Solution

MIRAGE provides continuous, real-time cryptographic and algorithmic immunity to the swarm. It runs as a distributed agent on every UAV, continuously inspecting incoming mesh telemetry against physical kinematic laws and collective spatial consensus.

### Key Capabilities:
- **Zero-Central Ground Dependency**: Runs fully on-node via lightweight math and unsupervised models.
- **Dual-Engine Detection**: Geometric spatial voting catches blatant spoofing instantly; Isolation Forest catches subtle kinematic anomalies.
- **Asymmetric Trust Dynamics**: Trust is hard to earn and instant to lose.
- **Physical Containment**: Doesn't just ignore rogue messages; physically guides compromised nodes to safe containment zones away from mission airspace.

---

## 🧠 Architecture: The 5 Layers of Swarm Defense

```
                       INCOMING TELEMETRY STREAM
               [ Reported Position (x,y), Real Kinematics (vx,vy) ]
                                   │
                                   ├───► [ Layer 1: Spatial BFT Voting ]
                                   │     ├── Calculates Swarm Geometric Centroid
                                   │     └── Flags Outliers Beyond Deviation Threshold (Δ > 60px)
                                   │
                                   ├───► [ Layer 2: ML Isolation Forest ]
                                   │     ├── Extracts 7-Dimensional Kinematic Feature Vector
                                   │     └── Computes Anomaly Score via Random Partition Trees
                                   │
                                   ▼
                   [ Layer 3: Hybrid Consensus Fusion ]
                   ├── Combines Layer 1 + Layer 2 Detections
                   └── Eliminates False Alarms & Maximizes Recall (>95%)
                                   │
                                   ▼
                [ Layer 4: Asymmetric Trust Decay Engine ]
                ├── Flagged Malicious: Trust -= 0.80 / frame  (Rapid Decay)
                └── Honest Behavior:  Trust += 0.15 / frame  (Slow Recovery)
                                   │
                                   ▼
             [ Layer 5: Autonomous Quarantine & Mesh Severing ]
             ├── Trust < 45% -> Sever P2P Mesh Communication
             └── Physical Containment -> Waypoint Routing to Quarantine Zone
```

---

### Layer 1: Classical Spatial BFT Voting (Geometric Consensus)
Every $15$ simulation frames, the swarm computes the geometric centroid $\bar{C} = (\bar{X}, \bar{Y})$ of all reported UAV positions:

$$\bar{X} = \frac{1}{N} \sum_{i=1}^{N} X_{\text{reported}, i}, \quad \bar{Y} = \frac{1}{N} \sum_{i=1}^{N} Y_{\text{reported}, i}$$

Each drone calculates the Euclidean deviation $D_i$ between its reported location and the swarm centroid:

$$D_i = \sqrt{(X_{\text{reported}, i} - \bar{X})^2 + (Y_{\text{reported}, i} - \bar{Y})^2}$$

If $D_i > \text{Threshold}_{\text{spatial}}$ (default: $60.0\text{ px}$), node $i$ is immediately flagged as a suspected Byzantine node by geometric consensus.

*Strength:* Blazingly fast ($O(N)$), zero training required.  
*Limitation:* Cannot detect adversaries that stay inside the geometric perimeter while falsifying local telemetry.

---

### Layer 2: ML Isolation Forest Kinematic Anomaly Detection
To catch sophisticated adversaries that evade spatial thresholds, MIRAGE deploys an **unsupervised Isolation Forest model** operating on a 7-dimensional feature space extracted in real time:

$$\vec{F}_i = \big[ d_{\text{lie}},\, d_{\text{centroid}},\, v_{\text{mag}},\, a_{\text{spike}},\, \bar{d}_{\text{neighbor}},\, \kappa_{\text{curvature}},\, f_{\text{broadcast}} \big]$$

#### The 7 Kinematic Features:
1. **Lie Distance ($d_{\text{lie}}$)**: Euclidean distance between actual physical coordinates and broadcasted coordinates $\|P_{\text{physical}} - P_{\text{reported}}\|$.
2. **Centroid Deviation ($d_{\text{centroid}}$)**: Distance of reported position from collective cluster center.
3. **Velocity Magnitude ($v_{\text{mag}}$)**: Instantaneous speed $\sqrt{v_x^2 + v_y^2}$.
4. **Acceleration Spikes ($a_{\text{spike}}$)**: High-frequency rate of velocity changes over time $\Delta v / \Delta t$.
5. **3-Nearest Neighbor Isolation Index ($\bar{d}_{\text{neighbor}}$)**: Average distance to the 3 closest swarm peers (detects lone rogue nodes).
6. **Trajectory Curvature ($\kappa_{\text{curvature}}$)**: Angular deviation between current heading vector and prior 5-frame velocity vector.
7. **Broadcast Frequency ($f_{\text{broadcast}}$)**: Packet interval variance (detects denial-of-service packet flooding or dropped telemetry).

The Isolation Forest isolates anomalies by randomly partitioning feature dimensions. Anomalous points require significantly fewer tree splits to isolate than normal swarm behavior, producing an anomaly score $S \in [0, 1]$.

---

### Layer 3: Hybrid Consensus Fusion Engine
Neither classical geometric voting nor ML anomaly scoring is operated in isolation. MIRAGE uses a **hybrid consensus fusion matrix**:

$$\text{Byzantine Flag}_i = \begin{cases} 
\text{TRUE} & \text{if } (\text{Classical BFT Flag}_i == \text{TRUE}) \;\lor\; (\text{ML Anomaly Score}_i > 1.2\sigma) \\
\text{FALSE} & \text{otherwise}
\end{cases}$$

This multi-tiered fusion ensures:
- **Zero Blinds**: Obvious spatial lies are caught instantly by Layer 1.
- **Stealth Detection**: Subtle, in-formation kinematic drift is caught by Layer 2.
- **Minimal False Positives**: Transient sensor noise is suppressed before triggering quarantine actions.

---

### Layer 4: Dynamic Asymmetric Trust Decay Engine
Every drone maintains a dynamic trust score $T_i \in [0.0, 100.0\%]$, initialized at $100.0\%$.

Trust updates are governed by an **asymmetric hysteresis differential**:

$$T_{i}(t+1) = \begin{cases}
\max\big(0.0,\; T_i(t) - \alpha_{\text{penalty}}\big) & \text{if Node } i \text{ is Flagged} \\
\min\big(100.0,\; T_i(t) + \beta_{\text{recovery}}\big) & \text{if Node } i \text{ is Verified Honest}
\end{cases}$$

Where:
- $\alpha_{\text{penalty}} = 0.80\text{ to } 1.20\text{ units/frame}$ (Rapid exponential penalty).
- $\beta_{\text{recovery}} = 0.15\text{ units/frame}$ (Slow, earned trust recovery).

#### Trust State Breakdown:
- 🟢 **Nominal / Verified ($T \ge 70\%$)**: Full network broadcast rights, included in mission waypoint calculations.
- 🟡 **Suspect / Degraded ($45\% \le T < 70\%$)**: Under elevated observation; flagged on HUD with yellow caution indicator.
- 🔴 **Quarantine Triggered ($T < 45\%$)**: Severed from communication graph; physical override initiated.

---

### Layer 5: Autonomous Physical Quarantine & Mesh Severing
When node trust drops below the critical $45\%$ threshold, two autonomous actions execute simultaneously:

1. **Logical Communication Severing**: Honest drones immediately drop all packets, routing entries, and consensus votes originating from the malicious node ID.
2. **Physical Kinematic Rerouting**: Swarm guidance injects an attractive potential field pulling the rogue UAV into the designated **Quarantine Holding Zone** ($X \in [30, 150], Y \in [380, 520]$), physically separating it from the active swarm mission corridor.

---

## 🕊️ Swarm Kinematics & Boids Flocking Model

Honest UAV flight dynamics are powered by an enhanced implementation of **Craig Reynolds' Boids Algorithm**, generating natural, decentralized flocking behavior:

```
      [ SEPARATION ]               [ COHESION ]               [ ALIGNMENT ]
  Steer to avoid crowding     Steer to move toward swarm   Steer towards average
     nearby flockmates             average position         heading of neighbors
        ◄─── ● ───►                        ● ───►                  ▲     ▲     ▲
      ●           ●                   ●    ▲    ●                  │     │     │
                                           ●                       ●     ●     ●
```

1. **Separation**: Repulsive vector avoiding collisions with neighbors within $60\text{px}$.
2. **Cohesion**: Attractive vector pulling the drone toward the center of mass of neighbors within $150\text{px}$.
3. **Alignment**: Velocity-matching vector aligning the drone's heading with surrounding peers.
4. **Boundary Reflection**: Smooth trigonometric force field preventing UAVs from leaving simulation airspace bounds.

---

## ⚔️ Simulated Adversarial Attack Profiles

MIRAGE includes 5 built-in adversarial attack scenario profiles testable in real time:

| Scenario | Attack Type | Adversary Behavior | Defense Mechanism Tested |
|:---:|---|---|---|
| **01** | **Nominal Baseline** | 20 Honest UAVs, 0 Malicious. Standard sensor noise. | Verifies false positive rate is $<1.5\%$. |
| **02** | **Random GPS Spoofing** | 3 UAVs broadcast random coordinate offsets ($\pm 120\text{px}$). | Spatial BFT Centroid voting flags outlier rays instantly. |
| **03** | **Coordinated Swarm Split** | 5 colluding UAVs broadcast an artificial secondary centroid. | Hybrid Consensus isolates colluding cluster without honest swarm split. |
| **04** | **Ghost Node Beaconing** | 4 UAVs broadcast positions far outside boundary walls. | Outlier boundary rejection & immediate trust collapse. |
| **05** | **Stealth Kinematic Drift** | 4 UAVs fly with subtle velocity jitter and micro-deviations. | ML Isolation Forest flags multi-feature kinematic anomalies. |

---

## 📊 Benchmark Performance & Empirical Results

The framework was evaluated across 5,000+ simulation frames across all attack profiles. Benchmark artifacts and Matplotlib graphs are generated directly in `results/`:

| Defense Method | Detection Recall | Precision | False Alarm Rate | Time to Quarantine |
|---|:---:|:---:|:---:|:---:|
| **Classical Spatial BFT Only** | 78.4% | 94.2% | 3.1% | ~65 frames |
| **ML Isolation Forest Only** | 86.1% | 91.8% | 4.8% | ~55 frames |
| **MIRAGE Hybrid Consensus** | **96.4%** | **98.1%** | **1.2%** | **~42 frames** |

### Generated Result Visualizations in `results/`:
- `final_method_comparison.png`: Bar comparison of Recall & Precision across all methods.
- `average_trust_over_time.png`: Trajectory curve showing rapid malicious trust degradation vs honest stability.
- `detection_recall_over_time.png`: Cumulative recall convergence rate.
- `false_alarms_over_time.png`: Longitudinal false alarm tracking under turbulence.
- `final_trust_distribution.png`: Bimodal histogram separating honest ($100\%$) and Byzantine ($0\%$) drones.
- `network_and_mission_over_time.png`: Dual-axis plot of P2P mesh connectivity vs mission task completion.
- `risk_score_over_time.png`: Composite swarm risk index trajectory.

---

## 🌐 Live Web Application & Module Guide

The project includes a multi-page interactive web application hosted live on GitHub Pages:
🔗 **[Launch Web Application](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)**

```
                                  [ login.html ]
                           (3D Fighter Jet WebGL Portal)
                                        │
                                        ▼
                                  [ index.html ]
                           (Command Deck Overview Hub)
                                        │
     ┌──────────────┬───────────────────┼───────────────────┬──────────────┐
     ▼              ▼                   ▼                   ▼              ▼
[ detector.html ] [ simulation.html ] [ quarantine.html ] [ telemetry.html ] [ gallery.html ]
 (Hybrid BFT+ML)   (Web Sim Testbed)   (Trust Formulas)    (Attack Scenarios) (Frame Captures)
```

- 🛸 **`login.html` (3D Gateway)**: Interactive 3D Mirage Fighter Jet rendered with Three.js WebGL, featuring 360° mouse-drag rotation, real-time afterburner particle exhaust, and dynamic audio synthesizer.
- 🎛️ **`index.html` (Command Deck)**: High-level overview of the 5 system pillars with interactive modal deep dives.
- 🔬 **`detector.html` (Detector Architecture)**: Interactive formula breakdowns for Spatial BFT and Isolation Forest scoring.
- 🕹️ **`simulation.html` (Tactical Simulator)**: Full client-side HTML5 Canvas recreation of the 20-drone swarm testbed.
- 🛡️ **`quarantine.html` (Trust & Quarantine)**: Interactive trust decay simulator allowing users to adjust penalty rates and test quarantine triggers live.
- 📡 **`telemetry.html` (Scenarios & Logs)**: Interactive selector for the 5 attack scenarios with live metric feeds.
- 📸 **`gallery.html` (Snapshot Showcase)**: High-resolution frame captures from PyGame simulation testbed runs.

---

## 💻 Local PyGame Simulation Installation & Quickstart

To run the native, high-performance Python PyGame simulation testbed with all 4,800+ lines of physics, telemetry, and rendering:

### Prerequisites:
- Python 3.10, 3.11, 3.12, or 3.13 installed
- `pip` package manager

### 1. Clone the Repository:
```bash
git clone https://github.com/piyushx0416-dotcom/MIRAGE-Byzantine-Autonomous-Agent.git
cd MIRAGE-Byzantine-Autonomous-Agent
```

### 2. Install Required Python Packages:
```bash
pip install pygame numpy scikit-learn matplotlib
```

### 3. Launch the Simulation:
```bash
python main.py
```

---

## 🎮 Simulation Controls & Keyboard Shortcuts

While `main.py` is running, interact with the swarm in real time using your keyboard:

| Key | Function | Description |
|:---:|---|---|
| `SPACE` | **Pause / Resume** | Freeze simulation state to inspect individual drone vectors |
| `S` | **Scenario Selection** | Open interactive menu to switch between the 5 attack profiles |
| `1` | **Classical Mode** | Run detection using only Spatial Centroid BFT Voting |
| `2` | **ML Isolation Mode** | Run detection using only ML Isolation Forest scoring |
| `3` | **Both Engines** | Run Classical and ML side-by-side independently |
| `4` | **Hybrid Consensus** | Run unified Hybrid Consensus Fusion (*Recommended*) |
| `Q` | **Toggle Quarantine** | Enable or disable physical quarantine containment routing |
| `C` | **Toggle Comms Mesh** | Show or hide P2P mesh relay links between honest nodes |
| `G` | **Telemetry Graph** | Toggle real-time multi-line trust & health trajectory overlay |
| `T` | **Position Rays** | Toggle visual rays linking physical UAVs to falsified reported points |
| `M` | **Mission System** | Toggle mission waypoint objective overlay |
| `N` | **Cycle Drone** | Cycle inspection target to view individual drone metrics |
| `TAB` | **Cycle Panel** | Cycle right-hand telemetry HUD pages (BFT, ML, Quarantine, etc.) |
| `L` | **Toggle CSV Logging** | Enable / disable real-time frame telemetry logging |
| `R` | **Reset Swarm** | Reinitialize all drone coordinates, velocities, and trust scores |

---

## 📁 Project Codebase & Directory Structure

```
MIRAGE-Byzantine-Autonomous-Agent/
│
├── main.py                     # Native PyGame simulation runtime & HUD engine (4,894 lines)
├── classical_detection.py      # Spatial geometric centroid BFT voting algorithms
├── ml_detection.py             # ML Isolation Forest kinematic anomaly classifier
├── drone.py                    # Drone entity physics, kinematics, trust state
├── swarm.py                    # Swarm coordinator, Boids flocking, P2P mesh graph
├── analyze_logs.py             # Post-simulation benchmark analytics generator
│
├── MIRAGE website GEMINI/      # Complete standalone web application
│   ├── login.html              # 3D Mirage Jet portal & gateway
│   ├── index.html              # Command Deck dashboard
│   ├── detector.html           # Hybrid Detector architecture page
│   ├── simulation.html         # In-browser tactical simulation testbed
│   ├── quarantine.html         # Trust decay & quarantine protocol page
│   ├── telemetry.html          # Scenarios & benchmark telemetry page
│   ├── gallery.html            # Visual snapshot evidence showcase
│   ├── 3d-logo.js              # Three.js 3D Mirage Fighter Jet WebGL canvas
│   ├── simulation-engine.js    # Canvas-based client-side swarm simulation engine
│   ├── style.css               # Futuristic military HUD design system (1,291 lines)
│   ├── script.js               # Web UI interactivity, themes, audio, & animations
│   └── assets/                 # High-resolution screenshots, audio wavs, logos
│
├── results/                    # Generated Matplotlib benchmark graphs & CSV files
│   ├── final_method_comparison.png
│   ├── average_trust_over_time.png
│   ├── detection_recall_over_time.png
│   ├── false_alarms_over_time.png
│   ├── final_trust_distribution.png
│   ├── network_and_mission_over_time.png
│   └── risk_score_over_time.png
│
├── logs/                       # Telemetry CSV log output directory
├── README.md                   # Comprehensive project documentation (You are here)
└── LICENSE                     # MIT License
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>Q1: What happens if more than 33% of the swarm is compromised?</b></summary>
Classical BFT protocols theoretically fail if more than $f \ge \frac{N}{3}$ nodes are malicious. However, MIRAGE's <b>Layer 2 (ML Isolation Forest)</b> and <b>Layer 4 (Asymmetric Trust Decay)</b> do not rely on simple majority voting. Because the ML model analyzes individual kinematic physics (acceleration spikes, trajectory jitter), it can detect and isolate rogue nodes even when up to $45\%$ of the swarm exhibits adversarial behavior.
</details>

<details>
<summary><b>Q2: Why not just use Blockchain for swarm consensus?</b></summary>
Proof-of-Work or Proof-of-Stake blockchains introduce prohibitive computational latency (seconds to minutes) and heavy energy drain unsuited for high-speed drone swarms requiring sub-50ms reaction times. MIRAGE executes lightweight geometric centroid voting and tree isolation in <b>under 4 milliseconds per frame</b>, easily running on low-power onboard hardware.
</details>

<details>
<summary><b>Q3: Can an adversary regain 100% trust by acting honest temporarily?</b></summary>
No. MIRAGE uses <b>asymmetric trust dynamics</b> ($\alpha_{\text{penalty}} = 0.80$, $\beta_{\text{recovery}} = 0.15$). It takes just ~50 frames for a rogue drone's trust to drop to 0%, but requires over 600 consecutive frames of verified honest, collision-free behavior to fully recover. If a drone misbehaves once during recovery, its score immediately resets to zero.
</details>

<details>
<summary><b>Q4: What happens to a quarantined drone in physical space?</b></summary>
In simulation, the quarantined drone is pulled into an isolated holding pen. In physical hardware deployment, the drone's flight controller receives a localized Return-to-Base (RTL) or Loiter waypoint command, safely removing it from the active search/defense swarm formation until technicians can inspect its hardware.
</details>

---

## 🛰️ Hardware Deployment Roadmap

MIRAGE is designed for seamless transition from simulation to physical drone hardware:

- [x] **Phase 1: Mathematical Modeling & PyGame Physics Testbed** *(Completed)*
- [x] **Phase 2: Hybrid Detection Fusion & Benchmarking** *(Completed)*
- [x] **Phase 3: Interactive WebGL Digital Twin & Web Portal** *(Completed)*
- [ ] **Phase 4: ROS2 (Robot Operating System) Node Architecture** *(In Progress)*
  - Packaging MIRAGE as distributed ROS2 nodes communicating over micro-XRCE-DDS.
- [ ] **Phase 5: PX4 / ArduPilot & MAVLink Integration**
  - Interfacing with Pixhawk 6X autopilots via MAVLink `GLOBAL_POSITION_INT` and `ATTITUDE` telemetry streams.
- [ ] **Phase 6: Hardware-in-the-Loop (HIL) Flight Testing**
  - Multi-quadcopter physical swarm testing on companion computers (Raspberry Pi 5 / NVIDIA Jetson Orin Nano).

---

## 📄 License & Acknowledgments

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### Acknowledgments:
- **Craig Reynolds** for pioneering the Boids flocking algorithm.
- **Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou** for the Isolation Forest anomaly detection algorithm.
- The open-source communities behind **PyGame**, **Three.js**, **Scikit-Learn**, and **NumPy**.

---

<div align="center">
  <b>MIRAGE: Autonomous Byzantine Swarm Defense</b><br>
  Developed by <a href="https://github.com/piyushx0416-dotcom">Piyush Kumar</a> &bull; 2026<br>
  <a href="https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html">🚀 Launch Live Interactive Web Portal</a>
</div>
