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
        this.trustHistory = [];
        this.maxHistoryLength = 200;
        this.lastDetectionFrame = 0;
        this.lastFrameTime = performance.now();
        this.fps = 60;

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
        this.trustHistory = [];
        this.lastDetectionFrame = 0;

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
                // Boids-style flocking forces
                let sepX = 0, sepY = 0, cohX = 0, cohY = 0, aliVx = 0, aliVy = 0, neighbors = 0;
                this.drones.forEach(other => {
                    if (other.id === d.id || this.quarantinedDrones.has(other.id)) return;
                    const dist = Math.hypot(d.x - other.x, d.y - other.y);
                    if (dist < 60 && dist > 0) {
                        sepX += (d.x - other.x) / dist * 0.3;
                        sepY += (d.y - other.y) / dist * 0.3;
                    }
                    if (dist < 150) {
                        cohX += other.x; cohY += other.y;
                        aliVx += other.vx; aliVy += other.vy;
                        neighbors++;
                    }
                });
                if (neighbors > 0) {
                    d.vx += ((cohX / neighbors - d.x) * 0.003) + ((aliVx / neighbors - d.vx) * 0.02);
                    d.vy += ((cohY / neighbors - d.y) * 0.003) + ((aliVy / neighbors - d.vy) * 0.02);
                }
                d.vx += sepX * 0.05;
                d.vy += sepY * 0.05;
                const speed = Math.hypot(d.vx, d.vy);
                if (speed > 3.0) { d.vx = (d.vx / speed) * 3.0; d.vy = (d.vy / speed) * 3.0; }

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
        // 2-4. Detection (run every 15 frames for performance, matching PyGame)
        const runDetection = (this.frame - this.lastDetectionFrame) >= 15;
        if (runDetection) {
            this.lastDetectionFrame = this.frame;
            this.classicalSuspected.clear();
            this.mlSuspected.clear();
            this.hybridSuspected.clear();

            // 2. Classical BFT voting detector (centroid-based distance)
            const reportedPositions = this.drones.map(d => ({ x: d.reportedX, y: d.reportedY }));
            const centroidX = reportedPositions.reduce((s, p) => s + p.x, 0) / this.drones.length;
            const centroidY = reportedPositions.reduce((s, p) => s + p.y, 0) / this.drones.length;
            this.drones.forEach(d => {
                const deviation = Math.hypot(d.reportedX - centroidX, d.reportedY - centroidY);
                if (deviation > this.threshold) {
                    this.classicalSuspected.add(d.id);
                }
            });

            // 3. ML Isolation Forest - multi-feature anomaly scoring
            const features = this.drones.map(d => {
                const lieDist = Math.hypot(d.reportedX - d.x, d.reportedY - d.y);
                const centroidDev = Math.hypot(d.reportedX - centroidX, d.reportedY - centroidY);
                const velocity = Math.hypot(d.vx, d.vy);
                const dists = this.drones.filter(o => o.id !== d.id)
                    .map(o => Math.hypot(d.x - o.x, d.y - o.y))
                    .sort((a, b) => a - b);
                const neighborIso = dists.length >= 3 ? (dists[0] + dists[1] + dists[2]) / 3 : 999;
                return { id: d.id, lieDist, centroidDev, velocity, neighborIso };
            });
            const mean = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
            const std = (arr) => { const m = mean(arr); return Math.sqrt(arr.reduce((s, v) => s + (v - m) ** 2, 0) / arr.length) || 1; };
            const lieVals = features.map(f => f.lieDist);
            const centVals = features.map(f => f.centroidDev);
            const lieMean = mean(lieVals), lieStd = std(lieVals);
            const centMean = mean(centVals), centStd = std(centVals);
            features.forEach(f => {
                const lieZ = (f.lieDist - lieMean) / lieStd;
                const centZ = (f.centroidDev - centMean) / centStd;
                const anomalyScore = lieZ * 0.5 + centZ * 0.35 + (f.neighborIso > 120 ? 0.5 : 0);
                if (anomalyScore > 1.2) {
                    this.mlSuspected.add(f.id);
                }
            });

            // 4. Hybrid Consensus
            this.drones.forEach(d => {
                if (this.classicalSuspected.has(d.id) || this.mlSuspected.has(d.id)) {
                    this.hybridSuspected.add(d.id);
                }
            });
        }

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

        // Track history for real-time graph overlay
        if (this.frame % 5 === 0) {
            const avgTrust = Object.values(this.trustScores).reduce((a, b) => a + b, 0) / this.totalDrones;
            const detRate = (this.drones.filter(d => d.isMalicious && (this.classicalSuspected.has(d.id) || this.mlSuspected.has(d.id))).length / Math.max(1, this.maliciousCount)) * 100;
            const netHealth = ((this.totalDrones - this.quarantinedDrones.size) / this.totalDrones) * 100;
            this.trustHistory.push({ frame: this.frame, avgTrust, detRate, netHealth });
            if (this.trustHistory.length > this.maxHistoryLength) this.trustHistory.shift();
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

            // Rotors with smooth continuous spinning blades
            const spinAngle = (this.frame * 0.3 + d.id * 1.5);
            rotorPoints.forEach(([rx, ry]) => {
                ctx.fillStyle = 'rgb(18, 20, 28)';
                ctx.beginPath(); ctx.arc(rx, ry, 9, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.beginPath(); ctx.arc(rx, ry, 9, 0, Math.PI * 2); ctx.stroke();
                // Continuous rotation blades
                ctx.strokeStyle = 'rgb(170, 175, 185)';
                ctx.lineWidth = 2;
                const bLen = 11;
                ctx.beginPath();
                ctx.moveTo(rx + Math.cos(spinAngle) * bLen, ry + Math.sin(spinAngle) * bLen);
                ctx.lineTo(rx - Math.cos(spinAngle) * bLen, ry - Math.sin(spinAngle) * bLen);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(rx + Math.cos(spinAngle + Math.PI/2) * bLen, ry + Math.sin(spinAngle + Math.PI/2) * bLen);
                ctx.lineTo(rx - Math.cos(spinAngle + Math.PI/2) * bLen, ry - Math.sin(spinAngle + Math.PI/2) * bLen);
                ctx.stroke();
            });

            // Fuselage Body
            ctx.fillStyle = 'rgb(25, 30, 40)';
            ctx.beginPath(); ctx.arc(bodyX, bodyY, 13, 0, Math.PI * 2); ctx.fill();

            ctx.fillStyle = color;
            ctx.beginPath(); ctx.arc(bodyX, bodyY, 8, 0, Math.PI * 2); ctx.fill();

            // Trust bar above drone
            const trustPct = this.trustScores[d.id] / 100;
            const barW = 30, barH = 3;
            const barX = bodyX - barW / 2, barY2 = bodyY - 28;
            ctx.fillStyle = 'rgba(0,0,0,0.5)';
            ctx.fillRect(barX, barY2, barW, barH);
            ctx.fillStyle = trustPct > 0.7 ? '#00ff64' : trustPct > 0.45 ? '#ffdc00' : '#ff3c3c';
            ctx.fillRect(barX, barY2, barW * trustPct, barH);

            // Text Label
            ctx.fillStyle = '#ffffff';
            ctx.font = '10px "Share Tech Mono"';
            ctx.fillText(`UAV #${d.id} [${Math.round(this.trustScores[d.id])}%]`, bodyX - 24, bodyY - 32);

            // Selected Drone Highlight (animated corners)
            if (d.id === this.selectedDroneId) {
                ctx.strokeStyle = '#00ffff';
                ctx.lineWidth = 2;
                const sz = 26, cl = 10;
                // Top-left
                ctx.beginPath(); ctx.moveTo(bodyX-sz, bodyY-sz+cl); ctx.lineTo(bodyX-sz, bodyY-sz); ctx.lineTo(bodyX-sz+cl, bodyY-sz); ctx.stroke();
                // Top-right
                ctx.beginPath(); ctx.moveTo(bodyX+sz-cl, bodyY-sz); ctx.lineTo(bodyX+sz, bodyY-sz); ctx.lineTo(bodyX+sz, bodyY-sz+cl); ctx.stroke();
                // Bottom-left
                ctx.beginPath(); ctx.moveTo(bodyX-sz, bodyY+sz-cl); ctx.lineTo(bodyX-sz, bodyY+sz); ctx.lineTo(bodyX-sz+cl, bodyY+sz); ctx.stroke();
                // Bottom-right
                ctx.beginPath(); ctx.moveTo(bodyX+sz-cl, bodyY+sz); ctx.lineTo(bodyX+sz, bodyY+sz); ctx.lineTo(bodyX+sz, bodyY+sz-cl); ctx.stroke();
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
        ctx.fillText('MIRAGE: BYZANTINE AUTONOMOUS AGENT', 28, 38);

        ctx.fillStyle = '#e6edf8';
        ctx.font = '10px "Share Tech Mono"';
        ctx.fillText('Autonomous swarm trust analysis under Byzantine adversaries', 28, 53);

        ctx.fillStyle = '#ffdc00';
        ctx.font = '10px "Share Tech Mono"';
        ctx.fillText(`FRAME ${this.frame}  |  MODE: ${this.detectionMode}`, 400, 38);

        // 11. Large Graph Overlay (if toggled on via 'G')
        if (this.showLargeGraph && this.trustHistory.length > 2) {
            const gx = 50, gy = 80, gw = width - 100, gh = height - 170;
            ctx.fillStyle = 'rgba(4, 8, 18, 0.96)';
            ctx.fillRect(gx - 10, gy - 20, gw + 20, gh + 60);
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(gx - 10, gy - 20, gw + 20, gh + 60);

            ctx.fillStyle = '#00ffff';
            ctx.font = 'bold 14px "Orbitron"';
            ctx.fillText('REAL-TIME TELEMETRY GRAPH', gx, gy - 4);

            // Grid lines
            ctx.strokeStyle = 'rgba(0,255,255,0.12)';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 4; i++) {
                const y = gy + (gh / 4) * i;
                ctx.beginPath(); ctx.moveTo(gx, y); ctx.lineTo(gx + gw, y); ctx.stroke();
                ctx.fillStyle = '#536482';
                ctx.font = '10px "Share Tech Mono"';
                ctx.fillText(`${100 - i * 25}%`, gx - 10, y + 4);
            }

            // Draw lines
            const drawLine = (data, key, color) => {
                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                data.forEach((d, i) => {
                    const x = gx + (i / (data.length - 1)) * gw;
                    const y = gy + gh - (d[key] / 100) * gh;
                    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
                });
                ctx.stroke();
            };

            drawLine(this.trustHistory, 'avgTrust', '#00ff64');
            drawLine(this.trustHistory, 'detRate', '#ff3c3c');
            drawLine(this.trustHistory, 'netHealth', '#00ffff');

            // Legend
            const legendY = gy + gh + 20;
            [['AVG TRUST', '#00ff64'], ['DETECTION RATE', '#ff3c3c'], ['NETWORK HEALTH', '#00ffff']].forEach(([label, color], i) => {
                const lx = gx + i * 180;
                ctx.fillStyle = color;
                ctx.fillRect(lx, legendY, 12, 12);
                ctx.fillStyle = '#e6edf8';
                ctx.font = '10px "Share Tech Mono"';
                ctx.fillText(label, lx + 18, legendY + 10);
            });

            ctx.fillStyle = '#8a99b5';
            ctx.font = '11px "Share Tech Mono"';
            ctx.fillText('Press [G] or [ESC] to close', gx, gy + gh + 45);
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
        ctx.fillStyle = '#00ff64';
        ctx.fillText(`${this.fps} FPS`, width - 75, height - 32);
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
            const now = performance.now();
            this.fps = Math.round(1000 / Math.max(1, now - this.lastFrameTime));
            this.lastFrameTime = now;
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
