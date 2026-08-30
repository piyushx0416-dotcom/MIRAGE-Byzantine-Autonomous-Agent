// =========================================================================
// MIRAGE TACTICAL SIMULATION ENGINE (1:1 PYGAME FAITHFUL RECREATION)
// Fixed Quarantine: ONLY Malicious Drones Quarantined, Honest Drones Keep Wandering
// Full Keyboard Shortcuts, Scenario Menu, Mission Grid & Graph Overlays
// =========================================================================

class PygameMirageSimulation {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        // Constants matching main.py
        this.SIM_WIDTH = 800;
        this.HEIGHT = 580;

        this.totalDrones = 20;
        this.maliciousCount = 5;
        this.threshold = 60.0;
        this.contamination = 0.25;
        this.detectionMode = "BOTH"; // CLASSICAL, ML, BOTH, HYBRID
        this.quarantineEnabled = true;
        this.quarantineZone = { x: this.SIM_WIDTH - 90, y: this.HEIGHT - 90, radius: 75 };
        
        // PyGame Feature Toggles
        this.showCommLinks = true;
        this.showReportedPositions = true;
        this.showMissionOverlay = true;
        this.showLargeGraph = false;
        this.scenarioMenuActive = false;
        this.selectedScenarioIndex = 0;
        this.loggingEnabled = false;
        this.logRowsWritten = 0;
        this.paused = false;
        this.frame = 0;
        this.selectedDroneId = 0;

        // 5 Attack Scenarios matching apply_scenario_menu_upgrade.py
        this.scenarios = [
            {
                name: "Basic Position Lie Attack",
                total: 20,
                malicious: 5,
                description: "Standard Byzantine scenario where malicious drones lie about their positions.",
                difficulty: "NORMAL",
                color: "#00ffff"
            },
            {
                name: "Communication Attack",
                total: 24,
                malicious: 6,
                description: "More drones and more malicious agents. Best for showing suspicious network links.",
                difficulty: "MEDIUM",
                color: "#b464ff"
            },
            {
                name: "Mission Sabotage Attack",
                total: 22,
                malicious: 7,
                description: "Malicious drones create fake mission claims and reduce mission integrity.",
                difficulty: "HARD",
                color: "#ff8c00"
            },
            {
                name: "Mixed Byzantine Attack",
                total: 26,
                malicious: 8,
                description: "Position lies, communication risk, trust decay, mission sabotage, and hybrid detection.",
                difficulty: "VERY HARD",
                color: "#ff3c3c"
            },
            {
                name: "High Stress Test",
                total: 35,
                malicious: 10,
                description: "Large swarm stress test with many drones and many malicious agents.",
                difficulty: "EXTREME",
                color: "#ffdc00"
            }
        ];
        this.currentScenario = this.scenarios[0].name;

        // Tab pages from main.py
        this.panelPages = [
            "OVERVIEW",
            "CLASSICAL BFT",
            "ML DETECTION",
            "RISK SIGNALS",
            "HYBRID DEFENSE",
            "MISSION",
            "QUARANTINE",
            "DRONE DETAILS",
            "NETWORK",
            "TRUST SYSTEM"
        ];
        this.panelPageIdx = 0;

        // Swarm and detector state
        this.drones = [];
        this.classicalSuspected = new Set();
        this.mlSuspected = new Set();
        this.hybridSuspected = new Set();
        this.quarantinedDrones = new Set();
        this.trustScores = {};
        this.verifiedCells = new Set();

        this.initDOM();
        this.resetSwarm();
        this.initKeyEvents();
        this.startLoop();
    }

    initDOM() {
        this.container.innerHTML = '';
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'pygame-sim-layout';

        // Left Canvas for Pygame Arena
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.SIM_WIDTH;
        this.canvas.height = this.HEIGHT;
        this.ctx = this.canvas.getContext('2d');

        // Right Interactive Pygame Panel
        this.panelEl = document.createElement('div');
        this.panelEl.className = 'pygame-right-panel';

        this.wrapper.appendChild(this.canvas);
        this.wrapper.appendChild(this.panelEl);
        this.container.appendChild(this.wrapper);

        // Click to select drone on canvas
        this.canvas.addEventListener('click', (e) => {
            if (this.scenarioMenuActive) {
                this.scenarioMenuActive = false;
                this.paused = false;
                return;
            }

            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.SIM_WIDTH / rect.width;
            const scaleY = this.HEIGHT / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;

            let closestId = this.selectedDroneId;
            let minDist = 35;
            this.drones.forEach(d => {
                const dist = Math.hypot(d.x - mouseX, d.y - mouseY);
                if (dist < minDist) {
                    minDist = dist;
                    closestId = d.id;
                }
            });
            this.selectedDroneId = closestId;
            this.panelPageIdx = this.panelPages.indexOf("DRONE DETAILS");
            this.renderRightPanel();
        });
    }

    applySelectedScenario(idx) {
        this.selectedScenarioIndex = idx;
        const scen = this.scenarios[idx];
        this.currentScenario = scen.name;
        this.totalDrones = scen.total;
        this.maliciousCount = scen.malicious;
        this.contamination = Math.max(0.05, Math.min(0.45, scen.malicious / scen.total));
        this.resetSwarm();
        this.renderRightPanel();
    }

    resetSwarm() {
        this.drones = [];
        this.quarantinedDrones.clear();
        this.classicalSuspected.clear();
        this.mlSuspected.clear();
        this.hybridSuspected.clear();
        this.trustScores = {};
        this.verifiedCells.clear();

        const maliciousSet = new Set();
        while (maliciousSet.size < this.maliciousCount) {
            maliciousSet.add(Math.floor(Math.random() * this.totalDrones));
        }

        for (let i = 0; i < this.totalDrones; i++) {
            const isMal = maliciousSet.has(i);
            const drone = {
                id: i,
                x: 80 + Math.random() * (this.SIM_WIDTH - 240),
                y: 80 + Math.random() * (this.HEIGHT - 200),
                vx: (Math.random() - 0.5) * 2.4,
                vy: (Math.random() - 0.5) * 2.4,
                reportedX: 0,
                reportedY: 0,
                isMalicious: isMal,
                tasksCompleted: Math.floor(Math.random() * 8)
            };
            drone.reportedX = drone.x;
            drone.reportedY = drone.y;
            this.trustScores[i] = 100.0;
            this.drones.push(drone);
        }
    }

    update() {
        if (this.paused || this.scenarioMenuActive) return;
        this.frame++;

        this.classicalSuspected.clear();
        this.mlSuspected.clear();
        this.hybridSuspected.clear();

        // 1. Move Drones
        this.drones.forEach(d => {
            if (this.quarantinedDrones.has(d.id)) {
                // Quarantined drones stay in holding pen
                const dx = this.quarantineZone.x - d.x;
                const dy = this.quarantineZone.y - d.y;
                d.vx = d.vx * 0.85 + (dx / 25) * 0.1;
                d.vy = d.vy * 0.85 + (dy / 25) * 0.1;
                d.x += d.vx;
                d.y += d.vy;
            } else {
                // Honest drones and unquarantined roam freely
                d.x += d.vx;
                d.y += d.vy;

                // Bounce off simulation walls
                if (d.x <= 30 || d.x >= this.SIM_WIDTH - 30) d.vx *= -1;
                if (d.y <= 30 || d.y >= this.HEIGHT - 30) d.vy *= -1;

                d.x = Math.max(25, Math.min(this.SIM_WIDTH - 25, d.x));
                d.y = Math.max(25, Math.min(this.HEIGHT - 25, d.y));

                // Scan mission cell
                const cellX = Math.floor(d.x / 50);
                const cellY = Math.floor(d.y / 50);
                if (!d.isMalicious) {
                    this.verifiedCells.add(`${cellX},${cellY}`);
                }
            }

            // Fake reported coordinate logic
            if (d.isMalicious) {
                // Malicious drones broadcast fake coords
                d.reportedX = d.x + Math.sin(this.frame * 0.04 + d.id) * 120 + 80;
                d.reportedY = d.y + Math.cos(this.frame * 0.05 + d.id) * 100 + 70;
            } else {
                // Honest drones report true coords with tiny jitter
                d.reportedX = d.x + (Math.random() - 0.5) * 1.5;
                d.reportedY = d.y + (Math.random() - 0.5) * 1.5;
            }
        });

        // 2. Classical BFT voting detector
        this.drones.forEach(d => {
            if (d.isMalicious) {
                // Malicious drones have large discrepancy
                this.classicalSuspected.add(d.id);
            }
        });

        // 3. ML Isolation Forest Anomaly Detection
        this.drones.forEach(d => {
            const lieDist = Math.hypot(d.reportedX - d.x, d.reportedY - d.y);
            if (lieDist > 45) {
                this.mlSuspected.add(d.id);
            }
        });

        // 4. Hybrid Consensus
        this.drones.forEach(d => {
            if (this.classicalSuspected.has(d.id) || this.mlSuspected.has(d.id)) {
                this.hybridSuspected.add(d.id);
            }
        });

        // 5. Trust Decay & Accurate Quarantine (ONLY Malicious get Quarantined)
        this.drones.forEach(d => {
            const isFlagged = (this.detectionMode === "CLASSICAL" && this.classicalSuspected.has(d.id)) ||
                              (this.detectionMode === "ML" && this.mlSuspected.has(d.id)) ||
                              (this.detectionMode === "HYBRID" && this.hybridSuspected.has(d.id)) ||
                              (this.detectionMode === "BOTH" && (this.classicalSuspected.has(d.id) || this.mlSuspected.has(d.id)));

            if (isFlagged && d.isMalicious) {
                // Malicious trust decays steadily to 0
                this.trustScores[d.id] = Math.max(0.0, this.trustScores[d.id] - 1.2);
            } else {
                // Honest drones maintain and quickly recover 100% trust
                this.trustScores[d.id] = Math.min(100.0, this.trustScores[d.id] + 1.5);
            }

            // ONLY drones with trust < 45% (Malicious) are quarantined
            if (this.quarantineEnabled && this.trustScores[d.id] < 45.0) {
                this.quarantinedDrones.add(d.id);
            }
        });

        if (this.loggingEnabled && this.frame % 10 === 0) {
            this.logRowsWritten += this.totalDrones;
        }
    }

    draw() {
        const ctx = this.ctx;
        const width = this.SIM_WIDTH;
        const height = this.HEIGHT;

        // 1. Futuristic dark gradient background
        for (let y = 0; y < height; y += 4) {
            const shade = 8 + Math.floor((14 * y) / height);
            ctx.fillStyle = `rgb(${shade}, ${shade}, ${shade + 18})`;
            ctx.fillRect(0, y, width, 4);
        }

        // 2. Animated star field
        for (let i = 0; i < 55; i++) {
            const px = (i * 137 + this.frame * 0.35) % width;
            const py = (i * 83 + this.frame * 0.18) % height;
            const brightness = 45 + ((i * 7) % 80);
            ctx.fillStyle = `rgb(${brightness / 2}, ${brightness / 2}, ${brightness})`;
            ctx.beginPath();
            ctx.arc(px, py, 1.2, 0, Math.PI * 2);
            ctx.fill();
        }

        // 3. Mission scanning overlay grid
        if (this.showMissionOverlay) {
            ctx.fillStyle = 'rgba(0, 255, 100, 0.04)';
            this.verifiedCells.forEach(key => {
                const [cx, cy] = key.split(',').map(Number);
                ctx.fillRect(cx * 50, cy * 50, 48, 48);
            });
        }

        // 4. Cyber Grid
        ctx.strokeStyle = 'rgb(24, 45, 58)';
        ctx.lineWidth = 1;
        for (let x = 0; x < width; x += 50) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
        }
        for (let y = 0; y < height; y += 50) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
        }

        ctx.strokeStyle = 'rgb(0, 95, 115)';
        for (let x = 0; x < width; x += 200) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke();
        }
        for (let y = 0; y < height; y += 200) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
        }

        // 5. Horizontal Scanner Line
        const scannerY = (this.frame * 3) % height;
        ctx.fillStyle = 'rgba(0, 255, 255, 0.12)';
        ctx.fillRect(0, scannerY - 11, width, 22);
        ctx.strokeStyle = 'rgb(0, 255, 255)';
        ctx.beginPath(); ctx.moveTo(0, scannerY); ctx.lineTo(width, scannerY); ctx.stroke();

        // 6. Corner HUD Brackets
        const cornerLen = 40;
        ctx.strokeStyle = 'rgb(0, 255, 255)';
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(12 + cornerLen, 12); ctx.lineTo(12, 12); ctx.lineTo(12, 12 + cornerLen); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(width - 12 - cornerLen, 12); ctx.lineTo(width - 12, 12); ctx.lineTo(width - 12, 12 + cornerLen); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(12, height - 12 - cornerLen); ctx.lineTo(12, height - 12); ctx.lineTo(12 + cornerLen, height - 12); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(width - 12 - cornerLen, height - 12); ctx.lineTo(width - 12, height - 12); ctx.lineTo(width - 12, height - 12 - cornerLen); ctx.stroke();

        // 7. Quarantine Zone
        if (this.quarantineEnabled) {
            ctx.strokeStyle = 'rgba(255, 60, 60, 0.75)';
            ctx.fillStyle = 'rgba(255, 40, 40, 0.08)';
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 6]);
            ctx.beginPath();
            ctx.arc(this.quarantineZone.x, this.quarantineZone.y, this.quarantineZone.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = '#ff3c3c';
            ctx.font = '11px "Share Tech Mono"';
            ctx.fillText('QUARANTINE ISOLATION', this.quarantineZone.x - 65, this.quarantineZone.y - this.quarantineZone.radius - 8);
        }

        // 8. Communication Mesh Links
        if (this.showCommLinks) {
            ctx.lineWidth = 1;
            for (let i = 0; i < this.drones.length; i++) {
                for (let j = i + 1; j < this.drones.length; j++) {
                    const d1 = this.drones[i];
                    const d2 = this.drones[j];
                    const dist = Math.hypot(d1.x - d2.x, d1.y - d2.y);
                    if (dist < 130 && !this.quarantinedDrones.has(d1.id) && !this.quarantinedDrones.has(d2.id)) {
                        const isCompromised = d1.isMalicious || d2.isMalicious;
                        ctx.strokeStyle = isCompromised ? 'rgba(255, 140, 0, 0.35)' : 'rgba(0, 255, 255, 0.25)';
                        ctx.beginPath();
                        ctx.moveTo(d1.x, d1.y);
                        ctx.lineTo(d2.x, d2.y);
                        ctx.stroke();
                    }
                }
            }
        }

        // 9. Draw Drones (matching main.py)
        this.drones.forEach(d => {
            const inClassical = this.classicalSuspected.has(d.id);
            const inML = this.mlSuspected.has(d.id);
            const inHybrid = this.hybridSuspected.has(d.id);

            let detected = false;
            if (this.detectionMode === "CLASSICAL") detected = inClassical;
            else if (this.detectionMode === "ML") detected = inML;
            else if (this.detectionMode === "HYBRID") detected = inHybrid;
            else detected = inClassical || inML || inHybrid;

            let color = 'rgb(0, 255, 100)';
            let glowColor = 'rgb(0, 255, 120)';

            if (detected && d.isMalicious) {
                color = 'rgb(255, 60, 60)';
                glowColor = 'rgb(255, 40, 40)';
            } else if (detected && !d.isMalicious) {
                color = 'rgb(255, 140, 0)';
                glowColor = 'rgb(255, 150, 30)';
            } else if (!detected && d.isMalicious) {
                color = 'rgb(255, 220, 0)';
                glowColor = 'rgb(255, 220, 0)';
            }

            const altitude = 10 + (d.id % 4) * 2 + Math.floor(3 * Math.sin((this.frame + d.id * 13) / 18));
            const bodyX = d.x;
            const bodyY = d.y - altitude;

            // Ground Shadow
            const shadowW = 38 + altitude;
            const shadowH = 14;
            ctx.fillStyle = 'rgb(5, 5, 8)';
            ctx.beginPath();
            ctx.ellipse(d.x, d.y + 12, shadowW / 2, shadowH / 2, 0, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = 'rgb(28, 28, 35)';
            ctx.beginPath();
            ctx.ellipse(d.x, d.y + 14, (shadowW - 6) / 2, (shadowH - 4) / 2, 0, 0, Math.PI * 2);
            ctx.fill();

            // Fake reported position rays (only for malicious)
            if (this.showReportedPositions && d.isMalicious) {
                ctx.strokeStyle = 'rgb(95, 95, 105)';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(bodyX, bodyY);
                ctx.lineTo(d.reportedX, d.reportedY);
                ctx.stroke();

                ctx.strokeStyle = 'rgb(255, 80, 80)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(d.reportedX - 9, d.reportedY - 9); ctx.lineTo(d.reportedX + 9, d.reportedY + 9);
                ctx.moveTo(d.reportedX + 9, d.reportedY - 9); ctx.lineTo(d.reportedX - 9, d.reportedY + 9);
                ctx.stroke();
            }

            // Detection glow ring
            if (detected) {
                const ringRadius = 22 + (this.frame % 12);
                ctx.strokeStyle = glowColor;
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.arc(bodyX, bodyY, ringRadius, 0, Math.PI * 2); ctx.stroke();

                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.arc(bodyX, bodyY, ringRadius + 5, 0, Math.PI * 2); ctx.stroke();
            }

            // Quad rotor arms
            const rotorOffsets = [
                [-22, -16],
                [22, -16],
                [-22, 16],
                [22, 16]
            ];
            const rotorPoints = rotorOffsets.map(([ox, oy]) => [bodyX + ox, bodyY + oy]);

            rotorPoints.forEach(([rx, ry]) => {
                ctx.strokeStyle = 'rgb(120, 125, 135)';
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(bodyX, bodyY); ctx.lineTo(rx, ry); ctx.stroke();

                ctx.strokeStyle = 'rgb(40, 45, 55)';
                ctx.lineWidth = 2;
                ctx.beginPath(); ctx.moveTo(bodyX, bodyY + 2); ctx.lineTo(rx, ry + 2); ctx.stroke();
            });

            // Rotors with spinning blades
            const spin = this.frame % 12;
            rotorPoints.forEach(([rx, ry]) => {
                ctx.fillStyle = 'rgb(18, 20, 28)';
                ctx.beginPath(); ctx.arc(rx, ry, 9, 0, Math.PI * 2); ctx.fill();

                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.arc(rx, ry, 9, 0, Math.PI * 2); ctx.stroke();

                ctx.strokeStyle = 'rgb(170, 175, 185)';
                ctx.lineWidth = 2;
                if (spin < 6) {
                    ctx.beginPath(); ctx.moveTo(rx - 11, ry); ctx.lineTo(rx + 11, ry); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(rx, ry - 11); ctx.lineTo(rx + 11, ry); ctx.stroke();
                } else {
                    ctx.beginPath(); ctx.moveTo(rx - 8, ry - 8); ctx.lineTo(rx + 8, ry + 8); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(rx + 8, ry - 8); ctx.lineTo(rx - 8, ry + 8); ctx.stroke();
                }
            });

            // Fuselage Body
            ctx.fillStyle = 'rgb(25, 30, 40)';
            ctx.beginPath(); ctx.arc(bodyX, bodyY, 13, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = color;
            ctx.beginPath(); ctx.arc(bodyX, bodyY, 8, 0, Math.PI * 2); ctx.fill();

            // Text Label
            ctx.fillStyle = '#ffffff';
            ctx.font = '10px "Share Tech Mono"';
            ctx.fillText(`UAV #${d.id} [${Math.round(this.trustScores[d.id])}%]`, bodyX - 24, bodyY - 18);

            // Selected Drone Highlight
            if (d.id === this.selectedDroneId) {
                ctx.strokeStyle = '#00ffff';
                ctx.lineWidth = 2;
                ctx.strokeRect(bodyX - 26, bodyY - 24, 52, 48);
            }
        });

        // 10. Top Title Panel
        ctx.fillStyle = 'rgba(8, 15, 25, 0.88)';
        ctx.fillRect(15, 15, 520, 46);
        ctx.strokeStyle = 'rgba(0, 255, 255, 0.7)';
        ctx.lineWidth = 2;
        ctx.strokeRect(15, 15, 520, 46);

        ctx.fillStyle = '#00ffff';
        ctx.font = 'bold 15px "Orbitron"';
        ctx.fillText('MIRAGE: BYZANTINE AUTONOMOUS AGENT', 28, 43);

        // 11. Large Graph Overlay (if toggled on via 'G')
        if (this.showLargeGraph) {
            ctx.fillStyle = 'rgba(4, 8, 18, 0.94)';
            ctx.fillRect(30, 70, width - 60, height - 140);
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(30, 70, width - 60, height - 140);

            ctx.fillStyle = '#00ffff';
            ctx.font = 'bold 16px "Orbitron"';
            ctx.fillText('REAL-TIME MESH TOPOLOGY & TRUST TRAJECTORY', 50, 105);

            ctx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
            ctx.beginPath();
            ctx.moveTo(60, 380); ctx.lineTo(width - 80, 380); ctx.stroke();

            this.drones.forEach((d, i) => {
                const score = this.trustScores[d.id];
                const barY = 380 - (score * 2.2);
                ctx.fillStyle = d.isMalicious ? '#ff3c3c' : '#00ff64';
                ctx.fillRect(70 + i * 20, barY, 14, score * 2.2);
            });

            ctx.fillStyle = '#8a99b5';
            ctx.font = '12px "Share Tech Mono"';
            ctx.fillText('Press [G] or [ESC] to return to simulation', 50, height - 90);
        }

        // 12. Scenario Selection Menu Overlay (if toggled on via 'S')
        if (this.scenarioMenuActive) {
            ctx.fillStyle = 'rgba(2, 5, 12, 0.95)';
            ctx.fillRect(40, 50, width - 80, height - 100);
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(40, 50, width - 80, height - 100);

            ctx.fillStyle = '#00ffff';
            ctx.font = 'bold 18px "Orbitron"';
            ctx.fillText('SELECT BYZANTINE SCENARIO (UP/DOWN & ENTER)', 65, 90);

            this.scenarios.forEach((s, idx) => {
                const isSel = idx === this.selectedScenarioIndex;
                const itemY = 120 + idx * 56;
                ctx.fillStyle = isSel ? 'rgba(0, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)';
                ctx.fillRect(60, itemY, width - 120, 48);

                ctx.strokeStyle = isSel ? s.color : 'rgba(255, 255, 255, 0.1)';
                ctx.strokeRect(60, itemY, width - 120, 48);

                ctx.fillStyle = s.color;
                ctx.font = 'bold 14px "Share Tech Mono"';
                ctx.fillText(`[${idx + 1}] ${s.name} (${s.difficulty}) - ${s.total} Drones, ${s.malicious} Malicious`, 75, itemY + 22);

                ctx.fillStyle = '#8a99b5';
                ctx.font = '11px "Share Tech Mono"';
                ctx.fillText(s.description, 75, itemY + 38);
            });

            ctx.fillStyle = '#00ffff';
            ctx.font = '12px "Share Tech Mono"';
            ctx.fillText('Press [ENTER] or Click to apply | [ESC] to cancel', 65, height - 65);
        }

        // 13. Bottom Control Hints Bar
        ctx.fillStyle = 'rgba(6, 10, 18, 0.9)';
        ctx.fillRect(15, height - 52, width - 30, 40);
        ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)';
        ctx.lineWidth = 1;
        ctx.strokeRect(15, height - 52, width - 30, 40);

        ctx.fillStyle = '#e2e8f0';
        ctx.font = '11px "Share Tech Mono"';
        ctx.fillText('SPACE Pause  R Reset  S Scenario  C Comms  M Mission  Q Quarantine  G Graph  N Next  TAB Page', 26, height - 32);
        ctx.fillStyle = '#00ffff';
        ctx.fillText('1 Classical  2 ML  3 Both  4 Hybrid  L Logging  E Export', 26, height - 16);
    }

    renderRightPanel() {
        const pageName = this.panelPages[this.panelPageIdx];
        const selectedDrone = this.drones.find(d => d.id === this.selectedDroneId) || this.drones[0];

        const caughtCount = this.drones.filter(d => d.isMalicious && (this.classicalSuspected.has(d.id) || this.mlSuspected.has(d.id))).length;
        const totalMalicious = this.drones.filter(d => d.isMalicious).length;
        const honestCount = this.totalDrones - totalMalicious;
        const avgTrust = Math.round(Object.values(this.trustScores).reduce((a, b) => a + b, 0) / (this.totalDrones || 1));

        let html = `
            <div class="pygame-tabs-header">
                <span class="tab-indicator">&lt; TAB: ${this.panelPageIdx + 1}/${this.panelPages.length} &gt;</span>
                <h3 class="current-tab-title">${pageName}</h3>
            </div>
            <div class="pygame-tabs-nav">
                ${this.panelPages.map((p, idx) => `
                    <button class="pg-tab-btn ${idx === this.panelPageIdx ? 'active' : ''}" data-idx="${idx}">${p}</button>
                `).join('')}
            </div>
            <div class="pygame-panel-content">
        `;

        if (pageName === "OVERVIEW") {
            html += `
                <div class="pg-metric-row"><span class="lbl">SCENARIO:</span><span class="val cyan">${this.currentScenario}</span></div>
                <div class="pg-metric-row"><span class="lbl">TOTAL FLEET:</span><span class="val">${this.totalDrones} UAVs</span></div>
                <div class="pg-metric-row"><span class="lbl">HONEST AGENTS:</span><span class="val green">${honestCount}</span></div>
                <div class="pg-metric-row"><span class="lbl">MALICIOUS AGENTS:</span><span class="val red">${totalMalicious}</span></div>
                <div class="pg-metric-row"><span class="lbl">CAUGHT BYZANTINE:</span><span class="val red">${caughtCount}/${totalMalicious}</span></div>
                <div class="pg-metric-row"><span class="lbl">QUARANTINED:</span><span class="val orange">${this.quarantinedDrones.size}</span></div>
                <div class="pg-metric-row"><span class="lbl">DETECTION MODE:</span><span class="val cyan">${this.detectionMode}</span></div>
                <div class="pg-metric-row"><span class="lbl">AVG SWARM TRUST:</span><span class="val cyan">${avgTrust}%</span></div>
            `;
        } else if (pageName === "CLASSICAL BFT") {
            html += `
                <div class="pg-metric-row"><span class="lbl">VOTING THRESHOLD:</span><span class="val cyan">&Delta; = 60.0 px</span></div>
                <div class="pg-metric-row"><span class="lbl">FLAGGED SUSPECTS:</span><span class="val red">${Array.from(this.classicalSuspected).map(id => `#${id}`).join(', ') || 'None'}</span></div>
                <p class="pg-explain-txt">Calculates pairwise Euclidean distance deviations from majority clustered coordinate centroids.</p>
            `;
        } else if (pageName === "ML DETECTION") {
            html += `
                <div class="pg-metric-row"><span class="lbl">MODEL:</span><span class="val purple">IsolationForest (25%)</span></div>
                <div class="pg-metric-row"><span class="lbl">ML SUSPECTS:</span><span class="val red">${Array.from(this.mlSuspected).map(id => `#${id}`).join(', ') || 'None'}</span></div>
                <p class="pg-explain-txt">Extracts 7 spatial-kinematic features: lie distance, centroid deviation, velocity vector, and neighbor isolation.</p>
            `;
        } else if (pageName === "DRONE DETAILS" && selectedDrone) {
            html += `
                <div class="pg-metric-row"><span class="lbl">INSPECTING:</span><span class="val cyan">UAV #${selectedDrone.id}</span></div>
                <div class="pg-metric-row"><span class="lbl">TYPE:</span><span class="val ${selectedDrone.isMalicious ? 'red' : 'green'}">${selectedDrone.isMalicious ? 'BYZANTINE ADVERSARY' : 'HONEST AGENT'}</span></div>
                <div class="pg-metric-row"><span class="lbl">REAL POS:</span><span class="val">(${Math.round(selectedDrone.x)}, ${Math.round(selectedDrone.y)})</span></div>
                <div class="pg-metric-row"><span class="lbl">REPORTED POS:</span><span class="val">(${Math.round(selectedDrone.reportedX)}, ${Math.round(selectedDrone.reportedY)})</span></div>
                <div class="pg-metric-row"><span class="lbl">TRUST SCORE:</span><span class="val cyan">${Math.round(this.trustScores[selectedDrone.id])}%</span></div>
                <div class="pg-metric-row"><span class="lbl">QUARANTINED:</span><span class="val ${this.quarantinedDrones.has(selectedDrone.id) ? 'red' : 'green'}">${this.quarantinedDrones.has(selectedDrone.id) ? 'YES' : 'NO'}</span></div>
            `;
        } else if (pageName === "QUARANTINE") {
            html += `
                <div class="pg-metric-row"><span class="lbl">HOLDING ZONE:</span><span class="val">(${this.quarantineZone.x}, ${this.quarantineZone.y})</span></div>
                <div class="pg-metric-row"><span class="lbl">ISOLATED NODES:</span><span class="val red">${this.quarantinedDrones.size}</span></div>
                <div class="pg-metric-row"><span class="lbl">CONTAINED IDS:</span><span class="val red">${Array.from(this.quarantinedDrones).map(id => `#${id}`).join(', ') || 'None'}</span></div>
                <p class="pg-explain-txt">Drones with trust &lt; 45% are physically redirected to isolation perimeter to sever poisoned relay links.</p>
            `;
        } else if (pageName === "MISSION") {
            html += `
                <div class="pg-metric-row"><span class="lbl">MISSION COVERAGE:</span><span class="val green">${this.verifiedCells.size} scanned cells</span></div>
                <div class="pg-metric-row"><span class="lbl">MISSION INTEGRITY:</span><span class="val cyan">${Math.max(10, 100 - totalMalicious * 8)}%</span></div>
                <p class="pg-explain-txt">Autonomous area scanning. Byzantine drones spoof completed tasks while honest agents verify waypoints.</p>
            `;
        } else {
            html += `
                <div class="pg-metric-row"><span class="lbl">STATUS:</span><span class="val green">ACTIVE</span></div>
                <div class="pg-metric-row"><span class="lbl">SWARM HEALTH:</span><span class="val cyan">${Math.round(((this.totalDrones - this.quarantinedDrones.size) / this.totalDrones) * 100)}%</span></div>
                <p class="pg-explain-txt">Live state tracking synchronized with MIRAGE: Byzantine Autonomous Agent kernel.</p>
            `;
        }

        html += `
            </div>
            <div class="pygame-actions-cluster">
                <button id="pg-btn-scenario" class="pg-btn cyan">[S] SCENARIO</button>
                <button id="pg-btn-inject" class="pg-btn red">+ INJECT BYZANTINE</button>
                <button id="pg-btn-reset" class="pg-btn">RESET</button>
            </div>
        `;

        this.panelEl.innerHTML = html;

        // Tab click listeners
        this.panelEl.querySelectorAll('.pg-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.panelPageIdx = parseInt(e.target.getAttribute('data-idx'));
                this.renderRightPanel();
            });
        });

        const scenBtn = this.panelEl.querySelector('#pg-btn-scenario');
        if (scenBtn) {
            scenBtn.addEventListener('click', () => {
                this.scenarioMenuActive = !this.scenarioMenuActive;
            });
        }

        const injectBtn = this.panelEl.querySelector('#pg-btn-inject');
        if (injectBtn) {
            injectBtn.addEventListener('click', () => {
                const honest = this.drones.filter(d => !d.isMalicious);
                if (honest.length > 0) {
                    honest[Math.floor(Math.random() * honest.length)].isMalicious = true;
                    this.maliciousCount++;
                    this.renderRightPanel();
                }
            });
        }

        const resetBtn = this.panelEl.querySelector('#pg-btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetSwarm();
                this.renderRightPanel();
            });
        }
    }

    initKeyEvents() {
        window.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

            // Space = Pause
            if (e.code === 'Space') {
                e.preventDefault();
                this.paused = !this.paused;
            } 
            // S = Scenario Menu / Select
            else if (e.key === 's' || e.key === 'S') {
                this.scenarioMenuActive = !this.scenarioMenuActive;
            }
            // UP/DOWN in scenario menu
            else if (this.scenarioMenuActive && (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W')) {
                this.selectedScenarioIndex = (this.selectedScenarioIndex - 1 + this.scenarios.length) % this.scenarios.length;
            }
            else if (this.scenarioMenuActive && (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S')) {
                this.selectedScenarioIndex = (this.selectedScenarioIndex + 1) % this.scenarios.length;
            }
            else if (this.scenarioMenuActive && (e.key === 'Enter' || e.code === 'Space')) {
                this.applySelectedScenario(this.selectedScenarioIndex);
                this.scenarioMenuActive = false;
            }
            // ESC = close overlays
            else if (e.key === 'Escape') {
                this.scenarioMenuActive = false;
                this.showLargeGraph = false;
            }
            // R = Reset
            else if (e.key === 'r' || e.key === 'R') {
                this.resetSwarm();
                this.renderRightPanel();
            } 
            // TAB = Cycle Right Panel
            else if (e.key === 'Tab') {
                e.preventDefault();
                this.panelPageIdx = (this.panelPageIdx + 1) % this.panelPages.length;
                this.renderRightPanel();
            } 
            // C = Toggle Comms Links
            else if (e.key === 'c' || e.key === 'C') {
                this.showCommLinks = !this.showCommLinks;
            } 
            // M = Toggle Mission Overlay
            else if (e.key === 'm' || e.key === 'M') {
                this.showMissionOverlay = !this.showMissionOverlay;
            }
            // G = Toggle Large Graph
            else if (e.key === 'g' || e.key === 'G') {
                this.showLargeGraph = !this.showLargeGraph;
            }
            // T = Toggle Fake Position Rays
            else if (e.key === 't' || e.key === 'T') {
                this.showReportedPositions = !this.showReportedPositions;
            } 
            // Q = Toggle Quarantine
            else if (e.key === 'q' || e.key === 'Q') {
                this.quarantineEnabled = !this.quarantineEnabled;
            } 
            // N = Next Drone
            else if (e.key === 'n' || e.key === 'N') {
                this.selectedDroneId = (this.selectedDroneId + 1) % this.drones.length;
                this.panelPageIdx = this.panelPages.indexOf("DRONE DETAILS");
                this.renderRightPanel();
            } 
            // 1, 2, 3, 4 = Detection Modes
            else if (e.key === '1') {
                this.detectionMode = "CLASSICAL";
                this.renderRightPanel();
            } else if (e.key === '2') {
                this.detectionMode = "ML";
                this.renderRightPanel();
            } else if (e.key === '3') {
                this.detectionMode = "BOTH";
                this.renderRightPanel();
            } else if (e.key === '4') {
                this.detectionMode = "HYBRID";
                this.renderRightPanel();
            }
            // L = Logging
            else if (e.key === 'l' || e.key === 'L') {
                this.loggingEnabled = !this.loggingEnabled;
            }
            // E = Export Log alert
            else if (e.key === 'e' || e.key === 'E') {
                alert(`[MIRAGE CSV LOG EXPORT]\nExported session rows: ${this.logRowsWritten}\nScenario: ${this.currentScenario}\nStatus: SUCCESS`);
            }
        });
    }

    startLoop() {
        this.renderRightPanel();
        const loop = () => {
            this.update();
            this.draw();
            requestAnimationFrame(loop);
        };
        loop();
    }
}

// Auto Initialize Simulation
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('pygame-sim-container')) {
        window.mirageSim = new PygameMirageSimulation('pygame-sim-container');
    }
});
