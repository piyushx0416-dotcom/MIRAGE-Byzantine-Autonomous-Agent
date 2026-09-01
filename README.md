# 🛸 MIRAGE: Byzantine Autonomous Agent
### *Autonomous Drone Swarm Defense Against Rogue & Compromised Nodes*

[![Live Website Demo](https://img.shields.io/badge/Live_Website-Interactive_Portal-00ffff?style=for-the-badge&logo=google-chrome&logoColor=black)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online-success?style=for-the-badge&logo=github)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 🌟 Quick Links
- 🌐 **[Live Interactive Web App](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)** *(Explore the 3D Jet, Command Deck, and in-browser Simulation)*
- 🕹️ **[Run PyGame Simulation Locally](#-getting-started-run-in-3-steps)**
- 🧠 **[How MIRAGE Works (Simple Explanation)](#-the-problem--how-mirage-solves-it)**

---

## ❓ The Problem & How MIRAGE Solves It

### 🎯 The Problem
Imagine a team of **20 autonomous drones** flying together on a search-and-rescue or defense mission. To stay coordinated without relying on a vulnerable central ground tower, the drones talk directly to each other (**Peer-to-Peer Mesh**).

**What happens if an enemy hijacks or hacks 3 of those drones?**
- These rogue drones (**Byzantine nodes**) start broadcasting **fake GPS coordinates** or falsified telemetry.
- If honest drones believe the lies, they crash into each other, break formation, or fail their mission.

### 🛡️ The MIRAGE Solution
**MIRAGE** (*Mesh Immunity & Robust Autonomous Guidance Engine*) is a zero-trust decentralized defense system. It enables the drone swarm to **automatically identify lying drones, drop their trust scores to zero, cut them off from the network, and physically herd them into a quarantine zone**—all in real time, with no central human controller needed.

```
       [ Drone Broadcasts Telemetry ]
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
 [ Layer 1: Spatial BFT ]   [ Layer 2: Machine Learning ]
 (Did it lie about GPS?)     (Is its flight behavior abnormal?)
       └────────────┬────────────┘
                    ▼
     [ Layer 3: Hybrid Consensus Fusion ]
                    │
         Is the drone Byzantine?
         ├─► YES: Trust decays rapidly (T -> 0)
         │        Mesh communication severed
         │        Rogue UAV forced into Quarantine Corral
         │
         └─► NO : Trust score maintained / verified
                  Full swarm mission continues safely
```

---

## 🧠 Core Architecture (5 Layers of Defense)

| Layer | Component | What It Does in Simple Words |
|---|---|---|
| **1** | **Classical Spatial BFT Voting** | Geometric centroid distance voting. Drones cross-check reported positions against the swarm majority cluster. If a drone claims to be somewhere impossible, it gets flagged. |
| **2** | **ML Isolation Forest Anomaly Detection** | An unsupervised Machine Learning model analyzing 7 kinematic features (velocity jitter, trajectory curvature, sudden acceleration, neighbor distance). Catches sneaky or subtle attackers that geometric rules miss. |
| **3** | **Hybrid Consensus Fusion** | Combines Layer 1 + Layer 2 into a single unified consensus decision. Achieves **>95% recall** with near-zero false alarms. |
| **4** | **Dynamic Asymmetric Trust Decay** | Every drone has a trust score ($0 - 100\%$). A flagged drone loses trust fast ($-0.80$ penalty per cycle). Trust recovery is slow ($+0.15$) and requires proven honest behavior. |
| **5** | **Physical Autonomous Quarantine** | When a drone's trust drops below **45%**, its communication links are severed, and it is physically escorted into a designated containment zone away from the active swarm. |

---

## 🚀 Live Web Portal Overview

You can test and view every aspect of the project directly in your browser:

- 🛩️ **[3D Fighter Jet Gateway (`login.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/login.html)**: Interactive 3D Mirage aircraft with real-time lighting and sound.
- 🎛️ **[Command Deck (`index.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/index.html)**: High-level overview of the 5 system pillars and architecture.
- 🔬 **[Hybrid Detector (`detector.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/detector.html)**: Deep dive into the BFT math & ML feature space.
- 🎮 **[Tactical Simulation (`simulation.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/simulation.html)**: Interactive swarm simulator with real-time coordinate broadcasting and outlier detection.
- 🛡️ **[Trust & Quarantine (`quarantine.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/quarantine.html)**: Asymmetric trust formulas, holding corral mechanics, and state machine.
- 📊 **[Scenarios & Telemetry (`telemetry.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/telemetry.html)**: Benchmark profiles (Random Lie, Coordinated Split, Ghost Swarm).
- 📸 **[Snapshot Evidence Gallery (`gallery.html`)](https://piyushx0416-dotcom.github.io/MIRAGE-Byzantine-Autonomous-Agent/gallery.html)**: High-resolution frame captures from the live simulation runtime.

---

## 💻 Getting Started (Run in 3 Steps)

Experience the full native simulation with real physics, flocking behavior, and HUD overlays:

### Step 1: Clone the Repository
```bash
git clone https://github.com/piyushx0416-dotcom/MIRAGE-Byzantine-Autonomous-Agent.git
cd MIRAGE-Byzantine-Autonomous-Agent
```

### Step 2: Install Dependencies
```bash
pip install pygame numpy scikit-learn matplotlib
```

### Step 3: Launch the Simulation
```bash
python main.py
```

---

## 🎮 PyGame Simulation Controls & Hotkeys

While the simulation is running, use these keyboard shortcuts to test different attack scenarios and view telemetry:

| Hotkey | Action | Description |
|:---:|---|---|
| `SPACE` | **Pause / Resume** | Freeze simulation frames for close analysis |
| `S` | **Scenario Menu** | Select from 5 attack scenarios (GPS spoofing, Sybil attacks, etc.) |
| `1` | **Classical BFT Only** | Enable geometric spatial voting |
| `2` | **ML Isolation Forest** | Enable machine learning anomaly detection |
| `3` | **Both Engines** | Run Classical and ML in parallel |
| `4` | **Hybrid Consensus** | Combined fusion mode (*Recommended*) |
| `Q` | **Toggle Quarantine** | Enable/disable physical containment holding zone |
| `C` | **Toggle Comms Mesh** | Show/hide peer-to-peer communication relay links |
| `G` | **Telemetry Graph** | Open real-time trust score and network health graph overlay |
| `T` | **Position Rays** | Toggle display of fake vs real coordinate vectors |
| `N` | **Next Drone** | Cycle through drones to inspect individual telemetry |
| `R` | **Reset Swarm** | Reinitialize all UAV coordinates, trust scores, and states |

---

## ⚔️ Attack Scenarios Handled by MIRAGE

1. **Random GPS Drift**: Individual compromised UAVs broadcast slightly offset coordinates to slip under radar.
2. **Coordinated Split (Sybil Attack)**: Multiple rogue drones coordinate to broadcast a false centroid to split the honest swarm.
3. **Ghost Node Broadcast**: Rogue drones broadcast positions outside physical arena bounds to trigger false search paths.
4. **Intermittent Adversary**: Malicious drones alternate between honest and dishonest broadcasts to avoid continuous penalties.
5. **High-Velocity Kinematic Anomaly**: Rogue drones exhibit erratic velocity or acceleration spikes indicating hijacked control loops.

---

## 📁 Repository Structure

```
MIRAGE-Byzantine-Autonomous-Agent/
│
├── main.py                     # Native PyGame simulation runtime (4,800+ lines)
├── classical_detection.py      # Spatial geometric centroid BFT voting algorithms
├── ml_detection.py             # ML Isolation Forest kinematic anomaly classifier
├── drone.py                    # Drone entity, kinematics, trust state, physics
├── swarm.py                    # Swarm coordinator, Boids flocking, P2P mesh
├── analyze_logs.py             # Performance benchmark analysis scripts
│
├── MIRAGE website GEMINI/      # Full interactive website source files
│   ├── login.html              # 3D Mirage Jet portal & gateway
│   ├── index.html              # Command Deck dashboard
│   ├── detector.html           # Hybrid Detector architecture page
│   ├── simulation.html         # In-browser tactical simulation testbed
│   ├── quarantine.html         # Trust decay & quarantine protocol page
│   ├── telemetry.html          # Scenarios & benchmark telemetry page
│   ├── gallery.html            # Visual snapshot evidence showcase
│   ├── 3d-logo.js              # Three.js 3D Mirage Fighter Jet engine
│   ├── simulation-engine.js    # Canvas-based swarm simulation engine
│   ├── style.css               # Futuristic military HUD design system
│   └── script.js               # UI interactivity, themes, audio, & animations
│
├── results/                    # Generated benchmark graphs & evaluation CSVs
└── README.md                   # Project documentation
```

---

## 🔬 Research & Evaluation Highlights

- **Recall Rate**: $>95\%$ malicious node detection across all attack profiles.
- **False Alarm Rate**: $<2\%$ false positive rate under noisy real-world kinematic drift.
- **Containment Time**: Average time to quarantine $<45$ simulation frames after attack initiation.
- **Network Resilience**: Honest swarm maintains $>90\%$ mission formation integrity even when up to $30\%$ of nodes are compromised.

---

## 🤝 Contributing & License

Contributions, issues, and feature requests are welcome!
This project is open source and available under the [MIT License](LICENSE).
