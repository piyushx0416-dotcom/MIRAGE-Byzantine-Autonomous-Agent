// =========================================================================
// MIRAGE ADVANCED 3D TACTICAL FIGHTER JET (HIGH-PERFORMANCE GPU PIPELINE)
// 60-120 FPS Rendering, Optimized Typed Array Particles & RAF Event Throttling
// =========================================================================

function createEnhancedMirageFighterJet() {
    const jetGroup = new THREE.Group();

    // 1. High-Performance GPU Materials
    const stealthMat = new THREE.MeshStandardMaterial({
        color: 0x060b16,
        metalness: 0.9,
        roughness: 0.25,
        flatShading: false
    });

    const panelAccentMat = new THREE.MeshStandardMaterial({
        color: 0x101b30,
        metalness: 0.95,
        roughness: 0.3
    });

    const wireframeCyanMat = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        wireframe: true,
        transparent: true,
        opacity: 0.5
    });
    const wireframeGlowMat = new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        wireframe: true,
        transparent: true,
        opacity: 0.15,
        blending: THREE.AdditiveBlending
    });

    const canopyMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        metalness: 0.3,
        roughness: 0.1,
        transparent: true,
        opacity: 0.8
    });

    const pilotHudMat = new THREE.MeshBasicMaterial({
        color: 0x00ff64,
        wireframe: true
    });

    const flameCoreMat = new THREE.MeshBasicMaterial({
        color: 0x00ffff
    });

    const flameOuterMat = new THREE.MeshBasicMaterial({
        color: 0xb464ff,
        transparent: true,
        opacity: 0.65
    });

    // 2. Nose Cone & Pitot Probe
    const pitotGeo = new THREE.CylinderGeometry(0.015, 0.025, 1.4, 8);
    pitotGeo.rotateX(Math.PI / 2);
    const pitotMesh = new THREE.Mesh(pitotGeo, panelAccentMat);
    pitotMesh.position.z = 4.2;
    jetGroup.add(pitotMesh);

    const noseGeo = new THREE.ConeGeometry(0.55, 3.4, 14);
    noseGeo.rotateX(Math.PI / 2);
    const noseMesh = new THREE.Mesh(noseGeo, stealthMat);
    noseMesh.position.z = 2.0;
    jetGroup.add(noseMesh);

    const wireNose = new THREE.Mesh(noseGeo, wireframeCyanMat);
    wireNose.position.z = 2.0;
    wireNose.scale.set(1.02, 1.02, 1.02);
    jetGroup.add(wireNose);

    // 3. Main Central Fuselage & Dorsal Spine
    const bodyGeo = new THREE.CylinderGeometry(0.65, 0.75, 3.8, 14);
    bodyGeo.rotateX(Math.PI / 2);
    const bodyMesh = new THREE.Mesh(bodyGeo, stealthMat);
    bodyMesh.position.set(0, 0, -0.8);
    jetGroup.add(bodyMesh);

    const wireBody = new THREE.Mesh(bodyGeo, wireframeCyanMat);
    wireBody.position.set(0, 0, -0.8);
    wireBody.scale.set(1.02, 1.02, 1.02);
    jetGroup.add(wireBody);

    const spineGeo = new THREE.BoxGeometry(0.22, 0.28, 4.0);
    const spineMesh = new THREE.Mesh(spineGeo, panelAccentMat);
    spineMesh.position.set(0, 0.54, -0.6);
    jetGroup.add(spineMesh);

    // 4. Cockpit Canopy & Glowing Green Pilot HUD
    const canopyGeo = new THREE.ConeGeometry(0.38, 2.2, 10);
    canopyGeo.rotateX(Math.PI / 2);
    const canopyMesh = new THREE.Mesh(canopyGeo, canopyMat);
    canopyMesh.position.set(0, 0.52, 1.1);
    canopyMesh.scale.set(0.85, 1.0, 1.0);
    jetGroup.add(canopyMesh);

    const hudGeo = new THREE.PlaneGeometry(0.22, 0.18);
    const hudMesh = new THREE.Mesh(hudGeo, pilotHudMat);
    hudMesh.position.set(0, 0.48, 1.35);
    hudMesh.rotation.x = -0.3;
    jetGroup.add(hudMesh);

    // 5. Signature Delta Wings
    const deltaWingShape = new THREE.Shape();
    deltaWingShape.moveTo(0, 1.6);
    deltaWingShape.lineTo(4.2, -2.4);
    deltaWingShape.lineTo(4.1, -2.9);
    deltaWingShape.lineTo(0, -2.7);
    deltaWingShape.lineTo(-4.1, -2.9);
    deltaWingShape.lineTo(-4.2, -2.4);
    deltaWingShape.closePath();

    const extrudeSettings = { depth: 0.08, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: 0.04, bevelThickness: 0.04 };
    const deltaWingGeo = new THREE.ExtrudeGeometry(deltaWingShape, extrudeSettings);
    deltaWingGeo.rotateX(Math.PI / 2);
    const deltaWingMesh = new THREE.Mesh(deltaWingGeo, stealthMat);
    deltaWingMesh.position.set(0, -0.04, 0);
    jetGroup.add(deltaWingMesh);

    const wireWings = new THREE.Mesh(deltaWingGeo, wireframeCyanMat);
    wireWings.position.set(0, -0.04, 0);
    wireWings.scale.set(1.01, 1.01, 1.01);
    jetGroup.add(wireWings);

    // Wingtip Missile Rails
    const railGeo = new THREE.BoxGeometry(0.08, 0.08, 1.5);
    const missileGeo = new THREE.CylinderGeometry(0.055, 0.055, 1.6, 8);
    missileGeo.rotateX(Math.PI / 2);

    [-4.2, 4.2].forEach(x => {
        const rail = new THREE.Mesh(railGeo, panelAccentMat);
        rail.position.set(x, -0.04, -2.5);
        jetGroup.add(rail);

        const missile = new THREE.Mesh(missileGeo, panelAccentMat);
        missile.position.set(x, -0.12, -2.5);
        jetGroup.add(missile);

        const tipGeo = new THREE.ConeGeometry(0.055, 0.28, 8);
        tipGeo.rotateX(Math.PI / 2);
        const tip = new THREE.Mesh(tipGeo, flameCoreMat);
        tip.position.set(x, -0.12, -1.6);
        jetGroup.add(tip);
    });

    // 6. Twin Air-Intakes with Supersonic Shock Cones
    const intakeGeo = new THREE.BoxGeometry(0.46, 0.56, 2.0);
    const shockConeGeo = new THREE.ConeGeometry(0.15, 0.55, 8);
    shockConeGeo.rotateX(Math.PI / 2);

    [-0.82, 0.82].forEach((x, idx) => {
        const intake = new THREE.Mesh(intakeGeo, panelAccentMat);
        intake.position.set(x, -0.04, 0.4);
        intake.rotation.y = idx === 0 ? 0.07 : -0.07;
        jetGroup.add(intake);

        const shockCone = new THREE.Mesh(shockConeGeo, stealthMat);
        shockCone.position.set(x, -0.04, 1.45);
        jetGroup.add(shockCone);
    });

    // 7. Sweeping Vertical Tail Stabilizer
    const finShape = new THREE.Shape();
    finShape.moveTo(0, 0);
    finShape.lineTo(-1.8, 0);
    finShape.lineTo(-1.6, 2.2);
    finShape.lineTo(-0.6, 2.1);
    finShape.closePath();

    const finGeo = new THREE.ExtrudeGeometry(finShape, { depth: 0.06, bevelEnabled: true, bevelSize: 0.02, bevelThickness: 0.02 });
    finGeo.rotateY(Math.PI / 2);
    const finMesh = new THREE.Mesh(finGeo, stealthMat);
    finMesh.position.set(0, 0.42, -1.4);
    jetGroup.add(finMesh);

    const wireFin = new THREE.Mesh(finGeo, wireframeCyanMat);
    wireFin.position.set(0, 0.42, -1.4);
    wireFin.scale.set(1.02, 1.02, 1.02);
    jetGroup.add(wireFin);

    // 8. Exhaust Nozzle & Afterburner Flame
    const exhaustGeo = new THREE.CylinderGeometry(0.52, 0.58, 0.8, 14);
    exhaustGeo.rotateX(Math.PI / 2);
    const exhaustMesh = new THREE.Mesh(exhaustGeo, panelAccentMat);
    exhaustMesh.position.set(0, 0, -2.7);
    jetGroup.add(exhaustMesh);

    const plumeInnerGeo = new THREE.ConeGeometry(0.32, 2.4, 10);
    plumeInnerGeo.rotateX(-Math.PI / 2);
    const plumeInner = new THREE.Mesh(plumeInnerGeo, flameCoreMat);
    plumeInner.position.set(0, 0, -4.0);
    jetGroup.add(plumeInner);

    const plumeOuterGeo = new THREE.ConeGeometry(0.54, 3.4, 10);
    plumeOuterGeo.rotateX(-Math.PI / 2);
    const plumeOuter = new THREE.Mesh(plumeOuterGeo, flameOuterMat);
    plumeOuter.position.set(0, 0, -4.5);
    jetGroup.add(plumeOuter);

    jetGroup.plumeInner = plumeInner;
    jetGroup.plumeOuter = plumeOuter;

    // Pulsing exhaust point light
    const exhaustLight = new THREE.PointLight(0x00ffff, 3, 8);
    exhaustLight.position.set(0, 0, -3.5);
    jetGroup.add(exhaustLight);
    jetGroup.exhaustLight = exhaustLight;

    // Wingtip navigation lights
    const leftWingLight = new THREE.PointLight(0xff3c3c, 1.5, 4);
    leftWingLight.position.set(-4.2, -0.04, -2.5);
    jetGroup.add(leftWingLight);
    const rightWingLight = new THREE.PointLight(0x00ff64, 1.5, 4);
    rightWingLight.position.set(4.2, -0.04, -2.5);
    jetGroup.add(rightWingLight);
    jetGroup.leftWingLight = leftWingLight;
    jetGroup.rightWingLight = rightWingLight;

    // 9. Lightweight Exhaust Particles (GPU Points)
    const particleCount = 80;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleSpeeds = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
        particlePositions[i * 3] = (Math.random() - 0.5) * 0.3;
        particlePositions[i * 3 + 1] = (Math.random() - 0.5) * 0.3;
        particlePositions[i * 3 + 2] = -3.2 - Math.random() * 4.5;
        particleSpeeds[i] = 0.14 + Math.random() * 0.16;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
        color: 0x00ffff,
        size: 0.16,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending
    });

    const exhaustParticles = new THREE.Points(particleGeo, particleMat);
    jetGroup.add(exhaustParticles);
    jetGroup.exhaustParticles = exhaustParticles;
    jetGroup.particleSpeeds = particleSpeeds;

    return jetGroup;
}

// Initialize Interactive 3D Canvas
function initLogin3DStage() {
    const canvas = document.getElementById('login-3d-jet-canvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
    camera.position.set(0, 2.2, 11.2);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ 
        canvas, 
        alpha: true, 
        antialias: true,
        powerPreference: "high-performance"
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

    // Dynamic Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.95);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0x00ffff, 3.2);
    keyLight.position.set(6, 6, 8);
    scene.add(keyLight);

    const rimLight = new THREE.DirectionalLight(0xb464ff, 2.8);
    rimLight.position.set(-6, -4, -6);
    scene.add(rimLight);

    // Create Fighter Jet Model
    const jet = createEnhancedMirageFighterJet();
    jet.position.set(0, 0, 0);
    jet.rotation.set(0.35, -0.45, 0.25);
    scene.add(jet);

    // Physics Variables
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let targetRotationY = -0.45;
    let targetRotationX = 0.35;
    let targetRotationZ = 0.25;
    let velocityY = 0;
    let velocityX = 0;
    let currentZoom = 11.2;
    let targetZoom = 11.2;

    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition.x = e.clientX;
        previousMousePosition.y = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) {
            const normX = (e.clientX / window.innerWidth) - 0.5;
            const normY = (e.clientY / window.innerHeight) - 0.5;
            targetRotationZ = 0.25 + normX * 0.3;
            targetRotationX = 0.35 + normY * 0.2;
            return;
        }

        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        velocityY = deltaX * 0.008;
        velocityX = deltaY * 0.008;

        targetRotationY += velocityY;
        targetRotationX += velocityX;

        previousMousePosition.x = e.clientX;
        previousMousePosition.y = e.clientY;
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        targetZoom += e.deltaY * 0.004;
        targetZoom = Math.max(6.0, Math.min(15.0, targetZoom));
    }, { passive: false });

    // Touch Support
    canvas.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            isDragging = true;
            previousMousePosition.x = e.touches[0].clientX;
            previousMousePosition.y = e.touches[0].clientY;
        }
    });

    window.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        const deltaX = e.touches[0].clientX - previousMousePosition.x;
        const deltaY = e.touches[0].clientY - previousMousePosition.y;

        velocityY = deltaX * 0.008;
        velocityX = deltaY * 0.008;

        targetRotationY += velocityY;
        targetRotationX += velocityX;

        previousMousePosition.x = e.touches[0].clientX;
        previousMousePosition.y = e.touches[0].clientY;
    });

    window.addEventListener('touchend', () => { isDragging = false; });

    let frame = 0;
    function animate() {
        requestAnimationFrame(animate);
        frame++;

        if (!isDragging) {
            // Gentle auto-rotation when idle
            targetRotationY += 0.003;
            targetRotationY += velocityY;
            targetRotationX += velocityX;
            velocityY *= 0.92;
            velocityX *= 0.92;
        }

        jet.rotation.y += (targetRotationY - jet.rotation.y) * 0.12;
        jet.rotation.x += (targetRotationX - jet.rotation.x) * 0.12;
        jet.rotation.z += (targetRotationZ - jet.rotation.z) * 0.1;

        currentZoom += (targetZoom - currentZoom) * 0.08;
        camera.position.z = currentZoom;

        // Pulsating Flame
        if (jet.plumeInner && jet.plumeOuter) {
            const scaleZ = 1.0 + Math.sin(frame * 0.25) * 0.18;
            jet.plumeInner.scale.set(1.0, 1.0, scaleZ);
            jet.plumeOuter.scale.set(1.0, 1.0, scaleZ * 1.1);
        }

        // Exhaust light pulsing
        if (jet.exhaustLight) {
            jet.exhaustLight.intensity = 2 + Math.sin(frame * 0.2) * 1.5;
            jet.exhaustLight.color.setHSL(0.5 + Math.sin(frame * 0.05) * 0.05, 1, 0.5);
        }
        // Wingtip light blink
        if (jet.leftWingLight) {
            jet.leftWingLight.intensity = Math.sin(frame * 0.15) > 0 ? 1.5 : 0.3;
            jet.rightWingLight.intensity = Math.sin(frame * 0.15 + Math.PI) > 0 ? 1.5 : 0.3;
        }

        // Particle Exhaust Trail
        if (jet.exhaustParticles && jet.particleSpeeds) {
            const pos = jet.exhaustParticles.geometry.attributes.position;
            const arr = pos.array;
            const speeds = jet.particleSpeeds;
            for (let i = 0; i < speeds.length; i++) {
                const idx = i * 3 + 2;
                arr[idx] -= speeds[i];
                if (arr[idx] < -10.0) {
                    arr[i * 3] = (Math.random() - 0.5) * 0.3;
                    arr[i * 3 + 1] = (Math.random() - 0.5) * 0.3;
                    arr[idx] = -3.2;
                }
            }
            pos.needsUpdate = true;
        }

        jet.position.y = Math.sin(frame * 0.035) * 0.1;

        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        if (!canvas.clientWidth || !canvas.clientHeight) return;
        camera.aspect = canvas.clientWidth / canvas.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initLogin3DStage();
});
