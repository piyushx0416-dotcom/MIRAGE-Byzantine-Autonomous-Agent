// =========================================================================
// MIRAGE: Byzantine Autonomous Agent — MASTER SCRIPT & INTERACTIVE TESTBEDS
// Interactive Trust Simulator, Scenario Profiler, Smooth Zoom & Balanced Audio
// =========================================================================

// Shared AudioContext instance for the page
let globalAudioCtx = null;

function getAudioContext() {
    if (!globalAudioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            globalAudioCtx = new AudioContext();
        }
    }
    if (globalAudioCtx && globalAudioCtx.state === 'suspended') {
        globalAudioCtx.resume();
    }
    return globalAudioCtx;
}

// User Interaction Audio Unlock
function unlockAudio() {
    const ctx = getAudioContext();
    if (ctx && ctx.state === 'suspended') {
        ctx.resume();
    }
}
window.addEventListener('click', unlockAudio, { once: true });
window.addEventListener('touchstart', unlockAudio, { once: true });
window.addEventListener('keydown', unlockAudio, { once: true });

document.addEventListener('DOMContentLoaded', () => {
    // 1. Cinematic Smooth Zoom-In Entrance
    if (typeof gsap !== 'undefined') {
        gsap.fromTo("main.page-container, .login-gateway-container", 
            { 
                opacity: 0, 
                scale: 0.90,
                translateZ: -60,
                transformOrigin: "center center"
            },
            { 
                opacity: 1, 
                scale: 1.0, 
                translateZ: 0,
                duration: 1.0, 
                ease: "power2.out",
                clearProps: "transform"
            }
        );

        gsap.from(".detail-column-card, .scenario-card, .trust-card, .mesh-card, .pipeline-card", {
            opacity: 0,
            y: 25,
            scale: 0.96,
            duration: 0.7,
            stagger: 0.06,
            ease: "power2.out",
            delay: 0.15
        });
    }

    // 2. Cyber HUD Text Decrypt Scramble Effect
    initCyberTextDecrypt();

    // 3. Smooth Medium 1.2s Zoom-In Page Navigation Transitions
    initCinematicZoomTransitions();

    // 4. 5-Column Interactive Project Details Reader Modal
    initProjectDetailReader();

    // 5. Interactive Live Trust & Quarantine Simulator (for quarantine.html)
    initInteractiveTrustSimulator();

    // 6. Interactive Scenario Benchmark Testbed (for telemetry.html)
    initInteractiveScenarioTestbed();

    // 7. Lightbox Modal for Gallery Snapshots
    initSnapshotLightbox();

    // 8. Theme Switcher (Floating Button)
    const themeBtn = document.getElementById('theme-mode-btn');
    const body = document.body;

    const savedTheme = localStorage.getItem('mirage_theme_mode') || 'dark';
    body.setAttribute('data-theme', savedTheme);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const current = body.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', next);
            localStorage.setItem('mirage_theme_mode', next);

            if (window.bgSwarmMaterial) {
                window.bgSwarmMaterial.color.setHex(next === 'dark' ? 0x00ffff : 0x0284c7);
            }
        });
    }

    // 9. Login Gateway Portal — Medium-Paced Supersonic Jet Blast & Forward Warp
    const enterBtn = document.getElementById('btn-enter-system');
    if (enterBtn) {
        enterBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetHref = enterBtn.getAttribute('href');

            // Fire medium-tempo (3.5s) supersonic fighter jet audio
            triggerMediumSupersonicJetFlyby();

            // Smooth forward hyperspace warp transition (1.1s)
            if (typeof gsap !== 'undefined') {
                gsap.to(".login-gateway-container", {
                    scale: 1.35,
                    translateZ: 120,
                    opacity: 0,
                    duration: 1.1,
                    ease: "power2.inOut",
                    onComplete: () => {
                        window.location.href = targetHref;
                    }
                });
            } else {
                setTimeout(() => {
                    window.location.href = targetHref;
                }, 1000);
            }
        });
    }

    // 10. Arrow Keys Pagination Navigation (<kbd>&larr;</kbd> and <kbd>&rarr;</kbd>)
    window.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

        const prevBtn = document.getElementById('page-nav-prev');
        const nextBtn = document.getElementById('page-nav-next');

        if (e.key === 'ArrowRight' && nextBtn) {
            nextBtn.click();
        } else if (e.key === 'ArrowLeft' && prevBtn) {
            prevBtn.click();
        }
    });

    // 11. Ambient Particle Background
    initLightweightBackground();
});

// Cyber Text Decrypt Scramble Effect on Headings
function initCyberTextDecrypt() {
    const titles = document.querySelectorAll('.page-title, .hero-headline, .sec-title');
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_#@*&';

    titles.forEach(el => {
        const originalText = el.innerText;
        let iteration = 0;
        const interval = setInterval(() => {
            el.innerText = originalText
                .split('')
                .map((char, index) => {
                    if (index < iteration || char === ' ' || char === '\n') {
                        return originalText[index];
                    }
                    return chars[Math.floor(Math.random() * chars.length)];
                })
                .join('');

            if (iteration >= originalText.length) {
                clearInterval(interval);
            }
            iteration += 1.8;
        }, 22);
    });
}

// Smooth Medium 1.2s Zoom-In Page Transitions
function initCinematicZoomTransitions() {
    const navButtons = document.querySelectorAll('.page-nav-btn, .module-link');
    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetUrl = btn.getAttribute('href');
            if (!targetUrl || targetUrl.startsWith('#') || targetUrl.startsWith('javascript:')) return;

            e.preventDefault();
            if (typeof gsap !== 'undefined') {
                gsap.to("main.page-container", {
                    scale: 1.16,
                    translateZ: 75,
                    opacity: 0,
                    duration: 1.15,
                    ease: "power2.inOut",
                    onComplete: () => {
                        window.location.href = targetUrl;
                    }
                });
            } else {
                window.location.href = targetUrl;
            }
        });
    });
}

// Interactive Live Trust & Quarantine Simulator (for quarantine.html)
function initInteractiveTrustSimulator() {
    const trustSlider = document.getElementById('sim-trust-slider');
    const decaySlider = document.getElementById('sim-decay-slider');
    const recoverySlider = document.getElementById('sim-recovery-slider');
    const injectBtn = document.getElementById('sim-inject-btn');
    const nodeStatus = document.getElementById('sim-node-status');

    if (!trustSlider || !nodeStatus) return;

    const trustVal = document.getElementById('sim-trust-val');
    const decayVal = document.getElementById('sim-decay-val');
    const recoveryVal = document.getElementById('sim-recovery-val');

    function updateSimUI() {
        const score = parseFloat(trustSlider.value);
        trustVal.textContent = `${Math.round(score)}%`;
        decayVal.textContent = `-${parseFloat(decaySlider.value).toFixed(2)} / cycle`;
        recoveryVal.textContent = `+${parseFloat(recoverySlider.value).toFixed(2)} / cycle`;

        if (score < 45.0) {
            nodeStatus.textContent = "QUARANTINED • CONTAINED IN ISOLATION CORRAL";
            nodeStatus.className = "red";
            trustVal.className = "red";
        } else if (score < 75.0) {
            nodeStatus.textContent = "SUSPICIOUS • UNDER ML OBSERVATION";
            nodeStatus.className = "orange";
            trustVal.className = "orange";
        } else {
            nodeStatus.textContent = "TRUSTED • ACTIVE FORMATION";
            nodeStatus.className = "green";
            trustVal.className = "cyan";
        }
    }

    trustSlider.addEventListener('input', updateSimUI);
    decaySlider.addEventListener('input', updateSimUI);
    recoverySlider.addEventListener('input', updateSimUI);

    if (injectBtn) {
        injectBtn.addEventListener('click', () => {
            let current = parseFloat(trustSlider.value);
            const decay = parseFloat(decaySlider.value) * 18.0;
            current = Math.max(0, current - decay);
            trustSlider.value = current;
            updateSimUI();
        });
    }

    updateSimUI();
}

// Interactive Scenario Benchmark Testbed (for telemetry.html)
function initInteractiveScenarioTestbed() {
    const scenarioCards = document.querySelectorAll('.scenario-card');
    const titleEl = document.getElementById('testbed-title');
    const descTitle = document.getElementById('testbed-desc-title');
    const descText = document.getElementById('testbed-desc-text');
    const accEl = document.getElementById('t-metric-acc');
    const timeEl = document.getElementById('t-metric-time');
    const survEl = document.getElementById('t-metric-surv');
    const codeHeader = document.getElementById('testbed-code-header');
    const codePre = document.getElementById('testbed-code-pre');

    if (scenarioCards.length === 0 || !titleEl) return;

    const scenarioProfiles = {
        "1": {
            title: "SCENARIO 01: BASIC POSITION LIE ATTACK",
            descTitle: "Trigonometric Coordinate Drift Profile",
            descText: "Malicious nodes broadcast sinusoidal coordinate offsets (drift = 120px) while maintaining true formation. Classical BFT detects distance deviations rapidly.",
            acc: "96.8%",
            time: "14.2s",
            surv: "100.0%",
            file: "scenario_01_profile.json",
            json: `{
  "scenario_id": 1,
  "name": "Basic Position Lie Attack",
  "swarm_size": 20,
  "byzantine_nodes": 5,
  "attack_vector": "COORDINATE_SPOOFING",
  "bft_voting_threshold": 60.0,
  "ml_isolation_contamination": 0.25
}`
        },
        "2": {
            title: "SCENARIO 02: COMMUNICATION GOSSIP ATTACK",
            descTitle: "P2P Frame Slander Profile",
            descText: "Rogue drones broadcast falsified peer distance matrices attempting to frame honest drones. ML Isolation Forest isolates bad nodes via neighbor graph analysis.",
            acc: "94.2%",
            time: "18.5s",
            surv: "98.5%",
            file: "scenario_02_profile.json",
            json: `{
  "scenario_id": 2,
  "name": "Communication Attack",
  "swarm_size": 24,
  "byzantine_nodes": 6,
  "attack_vector": "GOSSIP_POISONING",
  "graph_density": 0.42,
  "ml_neighbor_feature_weight": 0.85
}`
        },
        "3": {
            title: "SCENARIO 03: MISSION SABOTAGE ATTACK",
            descTitle: "Waypoint Verification Withholding",
            descText: "Compromised UAVs withhold waypoint scan verification packets while forging completed task logs. Quarantine corrals sever rogue mission claims.",
            acc: "95.6%",
            time: "16.1s",
            surv: "97.8%",
            file: "scenario_03_profile.json",
            json: `{
  "scenario_id": 3,
  "name": "Mission Sabotage Attack",
  "swarm_size": 22,
  "byzantine_nodes": 7,
  "attack_vector": "MISSION_WITHHOLDING",
  "integrity_threshold": 0.70,
  "quarantine_decay_rate": 0.80
}`
        },
        "4": {
            title: "SCENARIO 04: MIXED BYZANTINE ATTACK",
            descTitle: "Multi-Vector Coordinated Assault",
            descText: "Simultaneous multi-vector assault combining position lies, gossip poisoning, mission sabotage, and dynamic evasion across the fleet.",
            acc: "92.4%",
            time: "22.8s",
            surv: "95.2%",
            file: "scenario_04_profile.json",
            json: `{
  "scenario_id": 4,
  "name": "Mixed Byzantine Attack",
  "swarm_size": 26,
  "byzantine_nodes": 8,
  "attack_vector": "MULTI_VECTOR_ASSAULT",
  "bft_ml_fusion_mode": "HYBRID_ARBITRATION",
  "f1_score": 0.938
}`
        },
        "5": {
            title: "SCENARIO 05: HIGH STRESS SWARM TEST",
            descTitle: "High-Density Fleet Stress Limits",
            descText: "Extreme density test with 35 UAVs and 10 malicious agents evaluating memory bandwidth, Isolation Forest scaling, and quarantine corral capacity.",
            acc: "91.2%",
            time: "28.4s",
            surv: "93.6%",
            file: "scenario_05_profile.json",
            json: `{
  "scenario_id": 5,
  "name": "High Stress Test",
  "swarm_size": 35,
  "byzantine_nodes": 10,
  "attack_vector": "HIGH_DENSITY_STRESS",
  "fps_target": 60,
  "containment_throughput": "100%"
}`
        }
    };

    scenarioCards.forEach(card => {
        card.addEventListener('click', () => {
            scenarioCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            const id = card.getAttribute('data-scenario');
            const data = scenarioProfiles[id];
            if (!data) return;

            titleEl.textContent = data.title;
            descTitle.textContent = data.descTitle;
            descText.textContent = data.descText;
            accEl.textContent = data.acc;
            timeEl.textContent = data.time;
            survEl.textContent = data.surv;
            codeHeader.textContent = data.file;
            codePre.textContent = data.json;
        });
    });
}

// 5-Column Project Detail Reader Modal
function initProjectDetailReader() {
    const detailCards = document.querySelectorAll('.detail-column-card');
    const modal = document.getElementById('project-detail-modal');
    if (!modal || detailCards.length === 0) return;

    const modalBody = document.getElementById('modal-body-content');
    const closeBtn = modal.querySelector('.modal-close-btn');
    const backdrop = modal.querySelector('.modal-backdrop');

    const projectData = {
        objective: {
            badge: "PILLAR 01 // OBJECTIVE",
            title: "Autonomous Drone Swarm Byzantine Fault Tolerance",
            desc: "In adversarial drone swarm operations, compromised or malicious UAVs can broadcast falsified GPS coordinates, forge peer communication packets, or sabotage mission waypoints.",
            details: [
                "Guarantees multi-agent consensus resilience up to f < N/3 Byzantine adversaries.",
                "Prevents cascading swarm collisions and mission waypoint abandonment.",
                "Ensures secure peer-to-peer gossip verification across decentralized flight formations."
            ],
            link: "detector.html",
            linkText: "INSPECT DETECTION PIPELINE"
        },
        hybrid: {
            badge: "PILLAR 02 // DUAL ENGINE",
            title: "Hybrid Byzantine Threat Detection Pipeline",
            desc: "Fuses deterministic Euclidean distance voting with high-dimensional Isolation Forest machine learning anomaly analysis to achieve 94.8%+ precision.",
            details: [
                "Classical BFT Engine: Computes pairwise distance outlier deviations from majority centroid.",
                "ML Isolation Forest: Analyzes 7 features including lie distance, centroid deviation, velocity magnitude, and neighbor isolation.",
                "Hybrid Consensus Arbitration: Flags both bold trajectory lies and subtle kinematic evasion."
            ],
            link: "detector.html",
            linkText: "EXPLORE HYBRID DETECTOR"
        },
        trust: {
            badge: "PILLAR 03 // IMMUNE SYSTEM",
            title: "Dynamic Trust Decay & Physical Quarantine",
            desc: "An adaptive self-healing mechanism that dynamically scores node integrity and physically reroutes compromised drones to an isolation perimeter.",
            details: [
                "100.0 Baseline Trust with asymmetric penalization (-0.80/cycle) and recovery (+0.15/cycle).",
                "Quarantine Threshold: Nodes dropping below 45.0 trust are corralled to (SIM_WIDTH-90, HEIGHT-90).",
                "Mesh Link Pruning: Severed communication channels prevent gossip poisoning."
            ],
            link: "quarantine.html",
            linkText: "VIEW QUARANTINE MATRIX"
        },
        scenarios: {
            badge: "PILLAR 04 // BENCHMARKS",
            title: "5 Adversarial Attack Scenarios Suite",
            desc: "A standardized benchmark battery stress-testing the swarm across progressively harsher Byzantine attack vectors.",
            details: [
                "Scenario 01: Basic Position Lie (20 UAVs, 5 Malicious).",
                "Scenario 02: Communication Gossip Attack (24 UAVs, 6 Malicious).",
                "Scenario 03: Mission Sabotage Attack (22 UAVs, 7 Malicious).",
                "Scenario 04: Mixed Byzantine Vector (26 UAVs, 8 Malicious).",
                "Scenario 05: High-Density Swarm Stress Test (35 UAVs, 10 Malicious)."
            ],
            link: "telemetry.html",
            linkText: "VIEW ATTACK SCENARIOS"
        },
        telemetry: {
            badge: "PILLAR 05 // LOGGING",
            title: "Frame-by-Frame CSV Logging & Pandas Analytics",
            desc: "Complete end-to-end data provenance recording full flight telemetry, consensus votes, and detector metrics into standardized CSV datasets.",
            details: [
                "Captures frame, scenario, drone_id, lie_dist, trust_score, and network health.",
                "Integrated analyze_logs.py script for automated Pandas analysis and Matplotlib graphs.",
                "Computes real-time True Positives, False Positives, and F1-Scores across simulation cycles."
            ],
            link: "gallery.html",
            linkText: "VIEW TELEMETRY SNAPSHOTS"
        }
    };

    detailCards.forEach(card => {
        card.addEventListener('click', () => {
            const topic = card.getAttribute('data-topic');
            const data = projectData[topic];
            if (!data) return;

            modalBody.innerHTML = `
                <div class="modal-topic-header">
                    <span class="detail-badge cyan">${data.badge}</span>
                </div>
                <h2 class="modal-topic-title">${data.title}</h2>
                <div class="modal-topic-body">
                    <p>${data.desc}</p>
                    <ul class="modal-bullets">
                        ${data.details.map(d => `<li>&bull; ${d}</li>`).join('')}
                    </ul>
                    <a href="${data.link}" class="modal-nav-link">${data.linkText} &rarr;</a>
                </div>
            `;
            modal.classList.add('active');
        });
    });

    closeBtn.addEventListener('click', () => { modal.classList.remove('active'); });
    backdrop.addEventListener('click', () => { modal.classList.remove('active'); });
}

// Lightbox Modal for Gallery
function initSnapshotLightbox() {
    const galleryImages = document.querySelectorAll('.gallery-zoom-img');
    if (galleryImages.length === 0) return;

    let modal = document.getElementById('snapshot-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'snapshot-modal';
        modal.className = 'snapshot-lightbox-modal';
        modal.innerHTML = `
            <div class="lightbox-backdrop"></div>
            <div class="lightbox-content-box">
                <button class="lightbox-close-btn">&times;</button>
                <img id="lightbox-img" src="" alt="Snapshot Preview">
                <div id="lightbox-caption" class="lightbox-caption-txt"></div>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('.lightbox-close-btn').addEventListener('click', () => {
            modal.classList.remove('active');
        });
        modal.querySelector('.lightbox-backdrop').addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    const modalImg = document.getElementById('lightbox-img');
    const modalCaption = document.getElementById('lightbox-caption');

    galleryImages.forEach(img => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', () => {
            modalImg.src = img.src;
            modalCaption.textContent = img.getAttribute('alt') || 'MIRAGE Simulation Snapshot';
            modal.classList.add('active');
        });
    });
}

// Trigger Medium-Tempo Supersonic Jet Flyby Sound
function triggerMediumSupersonicJetFlyby() {
    // 1. Play Master Audio Element
    const masterAudio = document.getElementById('jet-master-audio');
    if (masterAudio) {
        masterAudio.currentTime = 0;
        masterAudio.volume = 1.0;
        const p1 = masterAudio.play();
        if (p1 !== undefined) {
            p1.catch(() => {});
        }
    }

    // 2. Play Base64 Audio Source
    try {
        const audioSrc = window.JET_FLYBY_BASE64 || 'assets/jet_flyby.wav';
        const b64Audio = new Audio(audioSrc);
        b64Audio.volume = 1.0;
        const p2 = b64Audio.play();
        if (p2 !== undefined) {
            p2.catch(() => {});
        }
    } catch(e) {}

    // 3. Play Balanced Medium 3.5s Web Audio Doppler Synthesizer
    playMediumJetAudio();
}

// Live Balanced 3.5-Second Supersonic Doppler Jet Synthesizer
function playMediumJetAudio() {
    try {
        const ctx = getAudioContext();
        if (!ctx) return;

        const now = ctx.currentTime;
        const duration = 3.5;

        const masterGain = ctx.createGain();
        masterGain.gain.setValueAtTime(1.0, now);
        masterGain.connect(ctx.destination);

        // 1. Dynamic Spooling Doppler Turbine (1.1s spool-up to peak)
        const turbineOsc = ctx.createOscillator();
        const turbineGain = ctx.createGain();
        turbineOsc.type = 'sawtooth';
        turbineOsc.frequency.setValueAtTime(550, now);
        turbineOsc.frequency.exponentialRampToValueAtTime(2100, now + 1.1);
        turbineOsc.frequency.exponentialRampToValueAtTime(220, now + 2.0);
        turbineOsc.frequency.exponentialRampToValueAtTime(50, now + duration);

        turbineGain.gain.setValueAtTime(0.01, now);
        turbineGain.gain.linearRampToValueAtTime(0.7, now + 1.1);
        turbineGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

        turbineOsc.connect(turbineGain);
        turbineGain.connect(masterGain);

        // 2. Supersonic Afterburner Noise Blast
        const bufferSize = Math.floor(ctx.sampleRate * duration);
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            output[i] = Math.random() * 2 - 1;
        }

        const noiseSource = ctx.createBufferSource();
        noiseSource.buffer = noiseBuffer;

        const lowpassFilter = ctx.createBiquadFilter();
        lowpassFilter.type = 'lowpass';
        lowpassFilter.frequency.setValueAtTime(2400, now);
        lowpassFilter.frequency.exponentialRampToValueAtTime(5200, now + 1.15);
        lowpassFilter.frequency.exponentialRampToValueAtTime(180, now + duration);

        const noiseGain = ctx.createGain();
        noiseGain.gain.setValueAtTime(0.03, now);
        noiseGain.gain.linearRampToValueAtTime(0.95, now + 1.15);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + duration);

        noiseSource.connect(lowpassFilter);
        lowpassFilter.connect(noiseGain);
        noiseGain.connect(masterGain);

        // 3. Sub-Bass Sonic Boom Shockwave
        const boomOsc = ctx.createOscillator();
        const boomGain = ctx.createGain();
        boomOsc.type = 'sine';
        boomOsc.frequency.setValueAtTime(150, now + 1.05);
        boomOsc.frequency.exponentialRampToValueAtTime(32, now + 1.9);

        boomGain.gain.setValueAtTime(0.001, now);
        boomGain.gain.setValueAtTime(0.95, now + 1.12);
        boomGain.gain.exponentialRampToValueAtTime(0.001, now + 2.1);

        boomOsc.connect(boomGain);
        boomGain.connect(masterGain);

        turbineOsc.start(now);
        noiseSource.start(now);
        boomOsc.start(now + 1.05);

        turbineOsc.stop(now + duration);
        noiseSource.stop(now + duration);
        boomOsc.stop(now + 2.2);
    } catch (e) {}
}

// Lightweight Ambient Swarm Background
function initLightweightBackground() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 500);
    camera.position.z = 30;

    const renderer = new THREE.WebGLRenderer({ 
        alpha: true, 
        antialias: false,
        powerPreference: "high-performance"
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(1.0);
    container.appendChild(renderer.domElement);

    const count = 120;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 80;
        positions[i + 1] = (Math.random() - 0.5) * 80;
        positions[i + 2] = (Math.random() - 0.5) * 50;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const isLight = document.body.getAttribute('data-theme') === 'light';
    const material = new THREE.PointsMaterial({
        color: isLight ? 0x0284c7 : 0x00ffff,
        size: 0.2,
        transparent: true,
        opacity: 0.35
    });
    window.bgSwarmMaterial = material;

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    function animate() {
        requestAnimationFrame(animate);
        points.rotation.y += 0.0004;
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}
