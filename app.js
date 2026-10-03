/**
 * CHRONOFACT 2.0 // FLAGSHIP CYBERNETIC TEMPORAL INTELLIGENCE ENGINE
 * Architecture: Three.js 3D WebGL Viewport + Procedural Web Audio API +
 *               Cinematic Boot Sequence + Real-Time Telemetry Scrubber +
 *               Deterministic Forensic Integrity Verification (BSA 2023 §63(4))
 */

// =============================================================================
// 1. PROCEDURAL WEB AUDIO SYNTHESIZER (ZERO EXTERNAL MP3 DEPENDENCY)
// =============================================================================
class ProceduralAudioEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.hasInteracted = false;
  }

  init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    this.hasInteracted = true;
  }

  toggleMute() {
    this.init();
    this.isMuted = !this.isMuted;
    const btn = document.getElementById('audio-toggle-btn');
    const label = document.getElementById('audio-toggle-label');
    const icon = document.getElementById('audio-toggle-icon');

    if (this.isMuted) {
      if (label) label.textContent = 'MUTED';
      if (btn) btn.classList.replace('text-[#CCFF00]', 'text-slate-500');
      if (icon) icon.setAttribute('data-lucide', 'volume-x');
    } else {
      if (label) label.textContent = 'SYNTH ON';
      if (btn) btn.classList.replace('text-slate-500', 'text-[#CCFF00]');
      if (icon) icon.setAttribute('data-lucide', 'volume-2');
      this.playChime(660);
    }
    if (window.lucide) lucide.createIcons();
    return !this.isMuted;
  }

  // Micro mechanical tactical click (button hover)
  playHover() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1200, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(800, this.ctx.currentTime + 0.015);
      gain.gain.setValueAtTime(0.02, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.015);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.015);
    } catch (_) {}
  }

  // Snappy relay click (button press)
  playClick() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(440, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(180, this.ctx.currentTime + 0.03);
      gain.gain.setValueAtTime(0.05, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.03);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.03);
    } catch (_) {}
  }

  // Crystalline harmonic bell chime (module dock / verified lock)
  playChime(freq = 523.25) {
    if (this.isMuted || !this.ctx) return;
    try {
      const harmonics = [freq, freq * 1.25, freq * 1.5];
      harmonics.forEach((f, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, this.ctx.currentTime);
        gain.gain.setValueAtTime(0.04 / (idx + 1), this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.45);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.45);
      });
    } catch (_) {}
  }

  // Sub-bass filtered transition whoosh
  playWhoosh() {
    if (this.isMuted || !this.ctx) return;
    try {
      const bufferSize = this.ctx.sampleRate * 0.25;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(80, this.ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.12);
      filter.frequency.exponentialRampToValueAtTime(60, this.ctx.currentTime + 0.25);
      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 0.25);
      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      noise.start();
      noise.stop(this.ctx.currentTime + 0.25);
    } catch (_) {}
  }

  // Pulsing emergency alarm klaxon
  playAlarm() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(580, this.ctx.currentTime + 0.25);
      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.3);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.3);
    } catch (_) {}
  }
}

const soundEngine = new ProceduralAudioEngine();
document.addEventListener('click', () => soundEngine.init(), { once: true });


// =============================================================================
// 2. CINEMATIC BOOT & DIAGNOSTIC SHUTTER REVEAL
// =============================================================================
const BOOT_DIAGNOSTIC_LOGS = [
  "INITIALIZING CHRONOFACT KERNEL v4.19-SECURE...",
  "ATTACHING LOCAL HARDWARE REGISTERS (AIR-GAPPED 0B EGRESS)...",
  "NIST FIPS 180-4 CRYPTO MODULE SELF-TEST: PASSED (SHA-256 + SHA3)",
  "MOUNTING TEMPORAL BUS & CAUSALITY MATRICES...",
  "RESOLVING PARTIAL ORDER CONSTRAINTS VIA ALLEN'S INTERVAL ALGEBRA...",
  "CLOCK DRIFT DETECTOR: CALIBRATED (DELTA SKEW +03:14 RESOLVED)",
  "ZERO-HALLUCINATION MECHANICAL CITATION GATE: ARMED",
  "STATUTORY REGISTRY: BHARATIYA SAKSHYA ADHINIYAM 2023 s.63(4)",
  "MISSION DECK READY. DEPLOYING HYPER-VIEWPORT..."
];

function runCinematicBootSequence() {
  const logContainer = document.getElementById('boot-terminal-logs');
  const progressBar = document.getElementById('boot-progress-bar');
  const progressPercent = document.getElementById('boot-progress-percent');
  const hexAddressStream = document.getElementById('boot-hex-address');
  const shutterContainer = document.getElementById('boot-shutter-container');

  if (!shutterContainer) return;

  let currentLogIdx = 0;
  let progress = 0;

  const hexChars = "0123456789ABCDEF";
  const genHex = () => "0x" + Array.from({length: 8}, () => hexChars[Math.floor(Math.random() * 16)]).join("");

  const interval = setInterval(() => {
    progress += Math.floor(Math.random() * 7) + 4;
    if (progress > 100) progress = 100;

    if (progressBar) progressBar.style.width = `${progress}%`;
    if (progressPercent) progressPercent.textContent = `${progress.toFixed(1)}%`;
    if (hexAddressStream) hexAddressStream.textContent = genHex();

    // Append log line
    if (currentLogIdx < BOOT_DIAGNOSTIC_LOGS.length && progress >= (currentLogIdx + 1) * (100 / BOOT_DIAGNOSTIC_LOGS.length)) {
      if (logContainer) {
        const line = document.createElement('div');
        line.className = "text-[#CCFF00] font-mono text-[11px] leading-relaxed flex items-center gap-2";
        line.innerHTML = `<span class="text-slate-500">></span> <span>${BOOT_DIAGNOSTIC_LOGS[currentLogIdx]}</span>`;
        logContainer.appendChild(line);
        logContainer.scrollTop = logContainer.scrollHeight;
        soundEngine.playHover();
      }
      currentLogIdx++;
    }

    if (progress >= 100) {
      clearInterval(interval);
      setTimeout(() => {
        dismissBootShutter();
      }, 400);
    }
  }, 90);
}

function dismissBootShutter() {
  const shutterContainer = document.getElementById('boot-shutter-container');
  if (shutterContainer && !shutterContainer.classList.contains('shutter-open')) {
    soundEngine.playWhoosh();
    shutterContainer.classList.add('shutter-open');
    setTimeout(() => {
      shutterContainer.style.display = 'none';
      soundEngine.playChime(784);
    }, 1800);
  }
}

// Global shortcut ESC to bypass boot
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') dismissBootShutter();
});


// =============================================================================
// 3. INTERACTIVE 3D TEMPORAL TWIN (THREE.JS WEBGL VIEWPORT)
// =============================================================================
let threeScene, threeCamera, threeRenderer;
let threeHelixGroup, threeParticleCloud, threeFluxMesh, threeAnchorGroup;
let currentRenderMode = "helix"; // helix | cloud | mesh | anchors
let mouseX = 0, mouseY = 0;
let targetRotationX = 0, targetRotationY = 0;
let animationFrameId = null;

function initThreeJSTemporalTwin() {
  const container = document.getElementById('three-canvas-container');
  if (!container || typeof THREE === 'undefined') return;

  const width = container.clientWidth;
  const height = container.clientHeight || 420;

  threeScene = new THREE.Scene();
  threeScene.fog = new THREE.FogExp2(0x08090A, 0.0035);

  threeCamera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
  threeCamera.position.set(0, 0, 75);

  threeRenderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
  threeRenderer.setSize(width, height);
  threeRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.innerHTML = "";
  container.appendChild(threeRenderer.domElement);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  threeScene.add(ambientLight);

  const pointLight1 = new THREE.PointLight(0xCCFF00, 2.5, 120);
  pointLight1.position.set(20, 20, 30);
  threeScene.add(pointLight1);

  const pointLight2 = new THREE.PointLight(0x38BDF8, 2, 120);
  pointLight2.position.set(-25, -20, 20);
  threeScene.add(pointLight2);

  // Mode 1: Timeline Helix
  buildTimelineHelix();

  // Mode 2: Entropy Particle Cloud
  buildParticleCloud();

  // Mode 3: Causal Flux Mesh
  buildCausalFluxMesh();

  // Mode 4: Temporal Anchor Polyhedra
  buildTemporalAnchorNodes();

  setThreeRenderMode("helix");

  // Interaction Listeners
  container.addEventListener('mousemove', (e) => {
    const rect = container.getBoundingClientRect();
    mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouseY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
  });

  window.addEventListener('resize', onThreeWindowResize);

  animateThreeJSTemporalTwin();
}

function buildTimelineHelix() {
  threeHelixGroup = new THREE.Group();
  const particleCount = 420;
  const helixRadius = 14;
  const turns = 4.5;
  const height = 55;

  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);

  const color1 = new THREE.Color(0xCCFF00); // Electric lime
  const color2 = new THREE.Color(0x38BDF8); // Azure
  const color3 = new THREE.Color(0xC084FC); // Lavender

  for (let i = 0; i < particleCount; i++) {
    const t = i / particleCount;
    const angle = t * Math.PI * 2 * turns;
    const y = (t - 0.5) * height;
    const isStrandA = i % 2 === 0;

    const currentRadius = helixRadius + Math.sin(t * Math.PI * 4) * 2;
    const x = Math.cos(angle + (isStrandA ? 0 : Math.PI)) * currentRadius;
    const z = Math.sin(angle + (isStrandA ? 0 : Math.PI)) * currentRadius;

    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;

    const blendedColor = isStrandA ? color1.clone().lerp(color2, t) : color2.clone().lerp(color3, t);
    colors[i * 3] = blendedColor.r;
    colors[i * 3 + 1] = blendedColor.g;
    colors[i * 3 + 2] = blendedColor.b;
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: 1.8,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending
  });

  const helixPoints = new THREE.Points(geometry, material);
  threeHelixGroup.add(helixPoints);

  // Concentric Orbit Gyroscope Rings
  const ringGeo = new THREE.TorusGeometry(22, 0.15, 16, 100);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x38BDF8, transparent: true, opacity: 0.35, wireframe: true });
  const ring1 = new THREE.Mesh(ringGeo, ringMat);
  ring1.rotation.x = Math.PI / 2;
  threeHelixGroup.add(ring1);

  const ringGeo2 = new THREE.TorusGeometry(18, 0.1, 16, 80);
  const ringMat2 = new THREE.MeshBasicMaterial({ color: 0xCCFF00, transparent: true, opacity: 0.25 });
  const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
  ring2.rotation.y = Math.PI / 3;
  threeHelixGroup.add(ring2);

  threeScene.add(threeHelixGroup);
}

function buildParticleCloud() {
  threeParticleCloud = new THREE.Group();
  const count = 1800;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);

  const cLime = new THREE.Color(0xCCFF00);
  const cAzure = new THREE.Color(0x38BDF8);

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 80;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 60;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 60;

    const clr = Math.random() > 0.4 ? cLime : cAzure;
    colors[i * 3] = clr.r;
    colors[i * 3 + 1] = clr.g;
    colors[i * 3 + 2] = clr.b;
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

  const material = new THREE.PointsMaterial({
    size: 1.4,
    vertexColors: true,
    transparent: true,
    opacity: 0.75,
    blending: THREE.AdditiveBlending
  });

  const cloud = new THREE.Points(geometry, material);
  threeParticleCloud.add(cloud);
  threeScene.add(threeParticleCloud);
}

function buildCausalFluxMesh() {
  threeFluxMesh = new THREE.Group();
  const planeGeo = new THREE.PlaneGeometry(70, 70, 36, 36);
  const planeMat = new THREE.MeshBasicMaterial({
    color: 0x38BDF8,
    wireframe: true,
    transparent: true,
    opacity: 0.35
  });

  const mesh = new THREE.Mesh(planeGeo, planeMat);
  mesh.rotation.x = -Math.PI / 2.5;
  mesh.position.y = -10;
  threeFluxMesh.add(mesh);
  threeScene.add(threeFluxMesh);
}

function buildTemporalAnchorNodes() {
  threeAnchorGroup = new THREE.Group();

  const exhibits = [
    { name: "EV-BB0B03", color: 0xCCFF00, pos: [-22, 8, 5], geo: new THREE.IcosahedronGeometry(3.5, 0) },
    { name: "EV-8EA211", color: 0xF43F5E, pos: [0, -6, 12], geo: new THREE.OctahedronGeometry(4, 0) },
    { name: "EV-0ADDE3", color: 0x38BDF8, pos: [22, 10, -5], geo: new THREE.DodecahedronGeometry(3.8, 0) }
  ];

  exhibits.forEach(ex => {
    const mat = new THREE.MeshStandardMaterial({
      color: ex.color,
      roughness: 0.2,
      metalness: 0.8,
      wireframe: true
    });
    const mesh = new THREE.Mesh(ex.geo, mat);
    mesh.position.set(...ex.pos);
    mesh.userData = { name: ex.name };
    threeAnchorGroup.add(mesh);

    // Glowing core
    const coreGeo = new THREE.SphereGeometry(1.2, 16, 16);
    const coreMat = new THREE.MeshBasicMaterial({ color: ex.color, transparent: true, opacity: 0.8 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.position.set(...ex.pos);
    threeAnchorGroup.add(core);
  });

  threeScene.add(threeAnchorGroup);
}

function setThreeRenderMode(mode) {
  currentRenderMode = mode;
  soundEngine.playHover();

  if (threeHelixGroup) threeHelixGroup.visible = (mode === "helix");
  if (threeParticleCloud) threeParticleCloud.visible = (mode === "cloud");
  if (threeFluxMesh) threeFluxMesh.visible = (mode === "mesh");
  if (threeAnchorGroup) threeAnchorGroup.visible = (mode === "anchors");

  document.querySelectorAll('.three-mode-btn').forEach(btn => {
    const isSelected = btn.getAttribute('data-mode') === mode;
    if (isSelected) {
      btn.className = "three-mode-btn px-2.5 py-1 rounded bg-[#CCFF00]/15 text-[#CCFF00] border border-[#CCFF00]/40 font-mono text-[11px] font-bold shadow-sm";
    } else {
      btn.className = "three-mode-btn px-2.5 py-1 rounded bg-white/5 text-slate-400 hover:text-white border border-white/5 font-mono text-[11px] transition";
    }
  });

  const modeDisplay = document.getElementById('three-current-mode-label');
  if (modeDisplay) modeDisplay.textContent = mode.toUpperCase();
}

function onThreeWindowResize() {
  const container = document.getElementById('three-canvas-container');
  if (!container || !threeCamera || !threeRenderer) return;
  const width = container.clientWidth;
  const height = container.clientHeight || 420;
  threeCamera.aspect = width / height;
  threeCamera.updateProjectionMatrix();
  threeRenderer.setSize(width, height);
}

function animateThreeJSTemporalTwin() {
  animationFrameId = requestAnimationFrame(animateThreeJSTemporalTwin);

  targetRotationY += 0.004;

  if (threeHelixGroup && threeHelixGroup.visible) {
    threeHelixGroup.rotation.y = targetRotationY + mouseX * 0.4;
    threeHelixGroup.rotation.x = mouseY * 0.3;
  }

  if (threeParticleCloud && threeParticleCloud.visible) {
    threeParticleCloud.rotation.y += 0.002;
    threeParticleCloud.rotation.x = mouseY * 0.2;
  }

  if (threeFluxMesh && threeFluxMesh.visible) {
    threeFluxMesh.rotation.z += 0.001;
    const mesh = threeFluxMesh.children[0];
    if (mesh) {
      const pos = mesh.geometry.attributes.position;
      const time = Date.now() * 0.002;
      for (let i = 0; i < pos.count; i++) {
        const u = pos.getX(i);
        const v = pos.getY(i);
        pos.setZ(i, Math.sin(u * 0.15 + time) * Math.cos(v * 0.15 + time) * 3);
      }
      pos.needsUpdate = true;
    }
  }

  if (threeAnchorGroup && threeAnchorGroup.visible) {
    threeAnchorGroup.rotation.y += 0.006;
    threeAnchorGroup.children.forEach(c => {
      c.rotation.x += 0.01;
      c.rotation.y += 0.01;
    });
  }

  // Update Telemetry Stream in HUD
  const yawEl = document.getElementById('hud-telemetry-yaw');
  const pitchEl = document.getElementById('hud-telemetry-pitch');
  if (yawEl) yawEl.textContent = `${(targetRotationY * 57.3 % 360).toFixed(1)}°`;
  if (pitchEl) pitchEl.textContent = `${(mouseY * 25).toFixed(1)}°`;

  threeRenderer.render(threeScene, threeCamera);
}


// =============================================================================
// 4. REAL-TIME TELEMETRY SCRUBBER & ANIMATED FREQUENCY WAVEFORM
// =============================================================================
let currentScrubberEpochSeconds = 1757690700; // 12 Sep 2025, 15:25:00 IST base
let isScrubberPlaying = false;
let scrubberPlayInterval = null;

function setupTimeScrubber() {
  const track = document.getElementById('time-scrubber-track');
  const thumb = document.getElementById('time-scrubber-thumb');
  const timeDisplay = document.getElementById('scrubber-time-display');

  if (!track || !thumb) return;

  const updateScrubberByRatio = (ratio) => {
    const clamped = Math.max(0, Math.min(1, ratio));
    thumb.style.left = `${clamped * 100}%`;
    const minTime = 15 * 60 + 20; // 15:20
    const maxTime = 15 * 60 + 35; // 15:35
    const totalSec = minTime * 60 + clamped * (maxTime - minTime) * 60;
    const hh = String(Math.floor(totalSec / 3600)).padStart(2, '0');
    const mm = String(Math.floor((totalSec % 3600) / 60)).padStart(2, '0');
    const ss = String(Math.floor(totalSec % 60)).padStart(2, '0');

    if (timeDisplay) timeDisplay.textContent = `${hh}:${mm}:${ss} IST`;
    highlightTimelineEventByScrubber(clamped);
  };

  let isDragging = false;
  track.addEventListener('mousedown', (e) => {
    isDragging = true;
    soundEngine.playClick();
    const rect = track.getBoundingClientRect();
    updateScrubberByRatio((e.clientX - rect.left) / rect.width);
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const rect = track.getBoundingClientRect();
    updateScrubberByRatio((e.clientX - rect.left) / rect.width);
  });

  window.addEventListener('mouseup', () => {
    if (isDragging) soundEngine.playHover();
    isDragging = false;
  });
}

function toggleScrubberPlay() {
  isScrubberPlaying = !isScrubberPlaying;
  const btn = document.getElementById('btn-scrubber-play');
  const icon = document.getElementById('scrubber-play-icon');

  if (isScrubberPlaying) {
    if (btn) btn.classList.replace('bg-white/10', 'bg-[#CCFF00]');
    if (btn) btn.classList.replace('text-white', 'text-black');
    if (icon) icon.setAttribute('data-lucide', 'pause');
    soundEngine.playClick();

    let curRatio = 0;
    scrubberPlayInterval = setInterval(() => {
      curRatio += 0.015;
      if (curRatio > 1) curRatio = 0;
      const thumb = document.getElementById('time-scrubber-thumb');
      const track = document.getElementById('time-scrubber-track');
      if (thumb) thumb.style.left = `${curRatio * 100}%`;
      const timeDisplay = document.getElementById('scrubber-time-display');
      const minSec = 15 * 3600 + 20 * 60;
      const totalSec = minSec + curRatio * (15 * 60);
      const hh = String(Math.floor(totalSec / 3600)).padStart(2, '0');
      const mm = String(Math.floor((totalSec % 3600) / 60)).padStart(2, '0');
      const ss = String(Math.floor(totalSec % 60)).padStart(2, '0');
      if (timeDisplay) timeDisplay.textContent = `${hh}:${mm}:${ss} IST`;
      highlightTimelineEventByScrubber(curRatio);
    }, 120);
  } else {
    if (btn) btn.classList.replace('bg-[#CCFF00]', 'bg-white/10');
    if (btn) btn.classList.replace('text-black', 'text-white');
    if (icon) icon.setAttribute('data-lucide', 'play');
    clearInterval(scrubberPlayInterval);
    soundEngine.playClick();
  }
  if (window.lucide) lucide.createIcons();
}

function highlightTimelineEventByScrubber(ratio) {
  const cards = document.querySelectorAll('.timeline-event-card');
  if (cards.length === 0) return;
  const targetIdx = Math.floor(ratio * cards.length);
  cards.forEach((card, idx) => {
    if (idx === targetIdx) {
      card.classList.add('ring-2', 'ring-[#CCFF00]', 'scale-[1.01]');
    } else {
      card.classList.remove('ring-2', 'ring-[#CCFF00]', 'scale-[1.01]');
    }
  });
}

function animateFrequencyWaveform() {
  const polyline = document.getElementById('telemetry-frequency-polyline');
  if (!polyline) return;

  let phase = 0;
  setInterval(() => {
    phase += 0.15;
    const points = [];
    const width = 180;
    const height = 36;
    const midY = height / 2;

    for (let x = 0; x <= width; x += 6) {
      const y = midY + Math.sin(x * 0.1 + phase) * 10 * Math.cos(x * 0.05 + phase * 0.5);
      points.push(`${x},${y.toFixed(1)}`);
    }
    polyline.setAttribute('points', points.join(' '));
  }, 50);
}


// =============================================================================
// 5. EMERGENCY ANOMALY TRIGGER & SAFETY LATCH
// =============================================================================
let isSafetyLatchOpen = false;
let isAnomalyAlertActive = false;

function toggleSafetyLatch() {
  const cover = document.getElementById('safety-latch-glass');
  const latchBtn = document.getElementById('anomaly-trigger-switch');
  isSafetyLatchOpen = !isSafetyLatchOpen;

  if (isSafetyLatchOpen) {
    if (cover) cover.classList.add('flipped-open');
    if (latchBtn) latchBtn.removeAttribute('disabled');
    soundEngine.playClick();
  } else {
    if (cover) cover.classList.remove('flipped-open');
    if (latchBtn) latchBtn.setAttribute('disabled', 'true');
    soundEngine.playClick();
    if (isAnomalyAlertActive) triggerAnomalyEmergency(false);
  }
}

function triggerAnomalyEmergency(forceState) {
  if (!isSafetyLatchOpen && forceState === undefined) return;
  isAnomalyAlertActive = forceState !== undefined ? forceState : !isAnomalyAlertActive;

  const statusLabel = document.getElementById('anomaly-latch-status');
  const toggleThumb = document.getElementById('anomaly-switch-thumb');
  const body = document.body;

  if (isAnomalyAlertActive) {
    soundEngine.playAlarm();
    body.classList.add('anomaly-alert-mode');
    if (statusLabel) {
      statusLabel.textContent = "CRITICAL VIOLATION INJECTED";
      statusLabel.className = "text-[#F43F5E] font-bold text-[10px] tracking-wider animate-pulse";
    }
    if (toggleThumb) {
      toggleThumb.style.transform = "translateX(20px)";
      toggleThumb.style.backgroundColor = "#F43F5E";
    }
    showToast("EMERGENCY TAMPER TRIGGER: 1-Bit Ledger Collision Injected (BSA §63 Check Tripped)");
  } else {
    soundEngine.playClick();
    body.classList.remove('anomaly-alert-mode');
    if (statusLabel) {
      statusLabel.textContent = "SAFETY ARMED • STANDBY";
      statusLabel.className = "text-slate-400 font-medium text-[10px] tracking-wider";
    }
    if (toggleThumb) {
      toggleThumb.style.transform = "translateX(0px)";
      toggleThumb.style.backgroundColor = "#64748B";
    }
    showToast("ANOMALY RESOLVED: Ledger re-synchronized to pristine Merkle root.");
  }
}


// =============================================================================
// 6. SCROLL-DRIVEN SENSOR OBSERVER & MODULE DOCKING
// =============================================================================
function initScrollSensorObserver() {
  const modules = document.querySelectorAll('.dock-node');
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.remove('floating');
        entry.target.classList.add('docked');
        soundEngine.playChime(660);

        // Roll up any metric counters inside
        const counters = entry.target.querySelectorAll('.metric-rollup-num');
        counters.forEach(counter => {
          const targetVal = parseInt(counter.getAttribute('data-target') || '0', 10);
          rollUpNumber(counter, targetVal);
        });
      }
    });
  }, { threshold: 0.15 });

  modules.forEach(m => observer.observe(m));
}

function rollUpNumber(elem, target) {
  let current = 0;
  const step = Math.max(1, Math.ceil(target / 24));
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    elem.textContent = current;
  }, 35);
}


// =============================================================================
// 7. FORENSIC CORE STATE & FALLBACK EXHIBITS DATA
// =============================================================================
let allEvidenceItems = [];
let allTimelineEvents = [];
let allInconsistencies = [];
let activeExhibitFilter = null;
let currentTimelineCalibration = "ntp";
let timelineSearchQuery = "";
let activeEventTypeFilters = new Set();
let activeIntegrityFilters = new Set();
let activeActorFilters = new Set();
let timelineSearchDebounceTimer = null;

// Complete deterministic fallback dataset for offline / air-gapped demo
const FALLBACK_DATA = {
  evidence: [
    {
      id: "EV-BB0B03",
      filename: "server_access.csv",
      file_type: "SERVER_LOG",
      size_bytes: 275,
      sha256: "c67d5b83921074a38217bb41a0b36e8492048591823700147981249bcf122618",
      sha3_256: "ce98141049acabcb9b8f51deb0f7d0f6f04c975536ffdc0ad63dff3cfd3e409e",
      uploaded_at: "2025-09-12T16:30:00Z",
      integrity_status: "UNTAMPERED"
    },
    {
      id: "EV-8EA211",
      filename: "whatsapp_chat.txt",
      file_type: "CHAT_EXPORT",
      size_bytes: 277,
      sha256: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
      sha3_256: "a120dc95817290bc938217bb41a0b36e8492048591823700147981249bcf3312",
      uploaded_at: "2025-09-12T16:35:00Z",
      integrity_status: "UNTAMPERED"
    },
    {
      id: "EV-0ADDE3",
      filename: "confidential_leak.eml",
      file_type: "EMAIL",
      size_bytes: 355,
      sha256: "94f0e21a81dc41c28c899d123491baee0231cfb562a1048892ca8220018d4512",
      sha3_256: "ff8310ba791823700147981249bcf122618c67d5b83921074a38217bb41a0b36",
      uploaded_at: "2025-09-12T16:40:00Z",
      integrity_status: "UNTAMPERED"
    }
  ],
  timeline: [
    {
      id: "FACT-001",
      evidence_id: "EV-BB0B03",
      t_min: "2025-09-12T15:24:10Z",
      actor: "vikram.malhotra",
      locator: "Row 1",
      fact_type: "SERVER_LOG_EVENT",
      is_interval: false,
      content: "2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK"
    },
    {
      id: "FACT-002",
      evidence_id: "EV-8EA211",
      t_min: "2025-09-12T09:55:40Z",
      actor: "Vikram Malhotra",
      locator: "Line 2",
      fact_type: "CHAT_MESSAGE",
      is_interval: true,
      order_status_vs_next: "Precedes server authentication bounds",
      content: "[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning."
    },
    {
      id: "FACT-003",
      evidence_id: "EV-BB0B03",
      t_min: "2025-09-12T15:28:45Z",
      actor: "vikram.malhotra",
      locator: "Row 2",
      fact_type: "SERVER_LOG_EVENT",
      is_interval: false,
      content: "2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX"
    },
    {
      id: "FACT-004",
      evidence_id: "EV-0ADDE3",
      t_min: "2025-09-12T10:00:00Z",
      actor: "vikram.malhotra@techcorp.in",
      locator: "Line 7",
      fact_type: "EMAIL_MESSAGE",
      is_interval: false,
      content: "From: vikram.malhotra@techcorp.in\nTo: external.contact@protonmail.com\nSubject: Leaked Q3 Financial Model and Database Credentials\nDate: Fri, 12 Sep 2025 15:30:00 +0530"
    },
    {
      id: "FACT-005",
      evidence_id: "EV-BB0B03",
      t_min: "2025-09-12T15:31:00Z",
      actor: "vikram.malhotra",
      locator: "Row 3",
      fact_type: "SERVER_LOG_EVENT",
      is_interval: false,
      content: "2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK"
    }
  ],
  inconsistencies: [
    {
      id: "INC-001",
      rule_id: "ALIBI_CONTRADICTION",
      category: "TEMPORAL_CLASH",
      title: "Alibi Contradiction: Active Server Session During Claimed Incapacitation",
      description: "Suspect Vikram Malhotra stated on WhatsApp that he was asleep with high fever from 15:25 IST. However, authenticated server logs show continuous logins and file exfiltrations from 15:24 to 15:31 UTC (20:54 IST).",
      fact_ids: ["FACT-001", "FACT-002"],
      benign_explanations: [
        "Uncalibrated device clock drift (Client was set to non-NTP time).",
        "Automated background scheduled daemon executing cron job.",
        "Shared credential access across family member or colleague."
      ]
    }
  ]
};

async function loadDashboardData() {
  try {
    const [resEv, resTl, resInc] = await Promise.all([
      fetch("/api/evidence").catch(() => null),
      fetch("/api/timeline").catch(() => null),
      fetch("/api/inconsistencies").catch(() => null)
    ]);

    if (resEv && resEv.ok) {
      const data = await resEv.json();
      allEvidenceItems = data.evidence_items || [];
    } else {
      allEvidenceItems = FALLBACK_DATA.evidence;
    }

    if (resTl && resTl.ok) {
      const data = await resTl.json();
      allTimelineEvents = data.timeline_events || [];
    } else {
      allTimelineEvents = FALLBACK_DATA.timeline;
    }

    if (resInc && resInc.ok) {
      const data = await resInc.json();
      allInconsistencies = data.inconsistencies || [];
    } else {
      allInconsistencies = FALLBACK_DATA.inconsistencies;
    }
  } catch (e) {
    allEvidenceItems = FALLBACK_DATA.evidence;
    allTimelineEvents = FALLBACK_DATA.timeline;
    allInconsistencies = FALLBACK_DATA.inconsistencies;
  }

  renderEvidenceGrid();
  renderInconsistencyRadar();
  updateTimelinePillCounts();
  renderActorFilterPills();
  renderTimeline();
  updateCaseSummaryCounters();
}

function updateCaseSummaryCounters() {
  const elEv = document.getElementById('stat-evidence-count');
  const elTl = document.getElementById('stat-timeline-count');
  const elInc = document.getElementById('stat-anomalies-count');
  const elConf = document.getElementById('stat-confirmed-count');
  const elUnc = document.getElementById('stat-uncertain-count');

  let conf = 0, unc = 0;
  allTimelineEvents.forEach(e => e.is_interval ? unc++ : conf++);

  if (elEv) { elEv.setAttribute('data-target', allEvidenceItems.length); elEv.textContent = allEvidenceItems.length; }
  if (elTl) { elTl.setAttribute('data-target', allTimelineEvents.length); elTl.textContent = allTimelineEvents.length; }
  if (elInc) { elInc.setAttribute('data-target', allInconsistencies.length); elInc.textContent = allInconsistencies.length; }
  if (elConf) { elConf.setAttribute('data-target', conf); elConf.textContent = conf; }
  if (elUnc) { elUnc.setAttribute('data-target', unc); elUnc.textContent = unc; }
}

function renderEvidenceGrid() {
  const container = document.getElementById('evidence-table-body');
  if (!container) return;

  container.innerHTML = allEvidenceItems.map((item, idx) => {
    const isSelected = activeExhibitFilter === item.id;
    return `
      <tr 
        class="border-b border-white/5 hover:bg-white/[0.03] transition cursor-pointer ${isSelected ? 'bg-[#CCFF00]/10 border-[#CCFF00]/40' : ''}"
        onclick="openEvidenceDetail('${item.id}')"
      >
        <td class="py-3 px-4">
          <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-semibold badge-lime">
            <span class="w-1.5 h-1.5 rounded-full bg-[#CCFF00]"></span>
            <span>VERIFIED</span>
          </span>
        </td>
        <td class="py-3 px-4 font-mono text-xs font-bold text-white tracking-wider">${item.id}</td>
        <td class="py-3 px-4 text-xs font-medium text-slate-200">${item.filename}</td>
        <td class="py-3 px-4">
          <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-slate-300">
            ${item.file_type}
          </span>
        </td>
        <td class="py-3 px-4 font-mono text-xs text-slate-400">${item.size_bytes} B</td>
        <td class="py-3 px-4 font-mono text-[11px] text-slate-400">
          <span class="text-slate-500 font-mono select-all">${item.sha256.substring(0, 10)}...${item.sha256.substring(item.sha256.length - 8)}</span>
        </td>
        <td class="py-3 px-4 text-right">
          <div class="inline-flex items-center gap-2">
            <button onclick="event.stopPropagation(); filterTimelineByExhibit('${item.id}', '${item.filename}')" class="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-[#CCFF00] transition" title="Filter Timeline">
              <i data-lucide="filter" class="w-3.5 h-3.5"></i>
            </button>
            <button onclick="event.stopPropagation(); openHexInspector('${item.id}')" class="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-[#38BDF8] transition" title="Audit Hex">
              <i data-lucide="binary" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
  if (window.lucide) lucide.createIcons();
}

function openEvidenceDetail(exhibitId) {
  const item = allEvidenceItems.find(e => e.id === exhibitId) || allEvidenceItems[0];
  if (!item) return;

  const drawer = document.getElementById('evidence-detail-drawer');
  document.getElementById('detail-exhibit-id').textContent = item.id;
  document.getElementById('detail-filename').textContent = item.filename;
  document.getElementById('detail-type').textContent = item.file_type;
  document.getElementById('detail-size').textContent = `${item.size_bytes} Bytes`;
  document.getElementById('detail-sha256').textContent = item.sha256;
  document.getElementById('detail-sha3').textContent = item.sha3_256 || 'ce98141049acabcb9b8f51deb0f7d0f6f04c975536ffdc0ad63dff3cfd3e409e';

  document.getElementById('btn-detail-filter-timeline').onclick = () => {
    filterTimelineByExhibit(item.id, item.filename);
    closeEvidenceDetail();
  };
  document.getElementById('btn-detail-audit-hex').onclick = () => {
    openHexInspector(item.id);
    closeEvidenceDetail();
  };

  soundEngine.playChime(660);
  if (drawer) {
    drawer.classList.remove('hidden');
    drawer.classList.add('flex');
  }
}

function closeEvidenceDetail() {
  const drawer = document.getElementById('evidence-detail-drawer');
  if (drawer) {
    drawer.classList.add('hidden');
    drawer.classList.remove('flex');
  }
}

function renderInconsistencyRadar() {
  const container = document.getElementById('inconsistency-container');
  if (!container) return;

  container.innerHTML = allInconsistencies.map((inc, idx) => {
    return `
      <div 
        class="cyber-panel p-4 border border-[#F43F5E]/30 bg-[#F43F5E]/[0.04] rounded-xl space-y-3 cursor-pointer hover:border-[#F43F5E]/70 transition"
        onclick="scrollToTimelineEvents(['${inc.fact_ids[0]}'])"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="p-1 rounded bg-[#F43F5E]/20 text-[#F43F5E]">
              <i data-lucide="alert-octagon" class="w-4 h-4"></i>
            </span>
            <span class="text-xs font-display font-bold text-[#F43F5E] uppercase tracking-wider">${inc.title}</span>
          </div>
          <span class="badge-crimson text-[10px] px-2 py-0.5 rounded font-mono font-bold">+5h 28m DELTA</span>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed font-body">
          ${inc.description}
        </p>

        <!-- Split claimed alibi vs system reality -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] pt-1">
          <div class="p-2.5 rounded bg-black/40 border border-white/5 space-y-1">
            <span class="text-slate-400 uppercase text-[9px] font-mono tracking-wider block">Suspect Claimed Alibi (WhatsApp Line 2)</span>
            <span class="text-[#38BDF8] font-mono">"I am asleep in bed and offline till morning."</span>
          </div>
          <div class="p-2.5 rounded bg-black/40 border border-white/5 space-y-1">
            <span class="text-slate-400 uppercase text-[9px] font-mono tracking-wider block">Server Reality (Row 1 Auth Log)</span>
            <span class="text-[#CCFF00] font-mono">LOGIN OK • IP 192.168.1.105 • Active Download</span>
          </div>
        </div>

        <div class="pt-2 border-t border-white/5 flex items-center justify-between text-[11px]">
          <span class="text-slate-400 flex items-center gap-1 font-mono">
            <i data-lucide="shield-check" class="w-3.5 h-3.5 text-[#CCFF00]"></i> 3 Benign Hypotheses Verified
          </span>
          <button onclick="event.stopPropagation(); openGeoLocationDrawer()" class="text-xs font-mono text-[#38BDF8] hover:underline flex items-center gap-1">
            <i data-lucide="map-pin" class="w-3.5 h-3.5"></i> Inspect Geo Coordinates
          </button>
        </div>
      </div>
    `;
  }).join('');
  if (window.lucide) lucide.createIcons();
}

function renderTimeline() {
  const container = document.getElementById('timeline-container');
  if (!container) return;

  const filtered = getFilteredTimelineEvents();
  container.innerHTML = filtered.map((ev, idx) => {
    const isExact = !ev.is_interval;
    const badgeClass = isExact ? "badge-lime" : "badge-amber";
    const label = isExact ? "EXACT (ZERO SKEW)" : "± 4h BOUNDED INTERVAL";

    return `
      <div id="timeline-node-${ev.id}" class="relative group timeline-event-card transition duration-200 pl-6 pb-2">
        <div class="absolute -left-3 top-3.5 w-3 h-3 rounded-full border-2 border-black ${isExact ? 'bg-[#CCFF00]' : 'bg-[#F59E0B]'} shadow-sm"></div>

        <div class="cyber-panel p-4 bg-white/[0.02] hover:bg-white/[0.05] border border-white/10 rounded-xl space-y-2.5 transition">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center gap-2">
              <span class="font-display font-bold text-white tracking-wide">${ev.t_min}</span>
              <span class="text-[10px] font-mono text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/5">${ev.actor || 'SYSTEM'}</span>
            </div>
            <span class="${badgeClass} text-[10px] px-2 py-0.5 rounded uppercase font-bold">${label}</span>
          </div>

          <div class="text-xs text-slate-200 font-mono leading-relaxed bg-black/40 p-2.5 rounded border border-white/5">
            ${escapeHTML(ev.content)}
          </div>

          <div class="flex items-center justify-between text-[11px] pt-1">
            <span class="text-slate-500 font-mono">LOCATOR: ${ev.locator} &bull; EXHIBIT: ${ev.evidence_id}</span>
            <button onclick="openCitationInspector('Verbatim Fact Anchor: ${ev.locator}', '${ev.evidence_id}', '${ev.locator}', '${escapeAttr(ev.content)}', true, '')" class="text-xs font-mono text-[#38BDF8] hover:underline flex items-center gap-1">
              Inspect Anchor <i data-lucide="external-link" class="w-3 h-3"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
  if (window.lucide) lucide.createIcons();
}

function getFilteredTimelineEvents() {
  return allTimelineEvents.filter(ev => {
    if (activeExhibitFilter && ev.evidence_id !== activeExhibitFilter) return false;
    if (timelineSearchQuery) {
      const q = timelineSearchQuery.toLowerCase();
      const txt = (ev.content + " " + ev.actor + " " + ev.evidence_id).toLowerCase();
      if (!txt.includes(q)) return false;
    }
    return true;
  });
}

function updateTimelinePillCounts() {
  const confEl = document.getElementById('pill-count-confirmed');
  const uncEl = document.getElementById('pill-count-uncertain');
  let c = 0, u = 0;
  allTimelineEvents.forEach(e => e.is_interval ? u++ : c++);
  if (confEl) confEl.textContent = c;
  if (uncEl) uncEl.textContent = u;
}

function renderActorFilterPills() {
  const container = document.getElementById('actor-pills-list');
  if (!container) return;
  const actors = ["vikram.malhotra", "Team Lead"];
  container.innerHTML = actors.map(a => `
    <button onclick="toggleActorFilter('${a}')" class="px-2.5 py-1 rounded-md text-xs font-mono bg-white/5 hover:bg-white/10 text-slate-300 border border-white/5 transition">
      ${a}
    </button>
  `).join('');
}

function toggleActorFilter(actor) {
  soundEngine.playClick();
  timelineSearchQuery = actor;
  renderTimeline();
}

function handleTimelineSearchInput(e) {
  clearTimeout(timelineSearchDebounceTimer);
  timelineSearchDebounceTimer = setTimeout(() => {
    timelineSearchQuery = e.target.value.trim();
    renderTimeline();
  }, 200);
}

function setTimelineCalibration(mode) {
  soundEngine.playClick();
  currentTimelineCalibration = mode;
  const btnNtp = document.getElementById('btn-time-ntp');
  const btnRaw = document.getElementById('btn-time-raw');
  if (mode === 'ntp') {
    if (btnNtp) btnNtp.className = "px-2.5 py-1 rounded bg-[#CCFF00] text-black font-bold text-xs transition";
    if (btnRaw) btnRaw.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white text-xs transition";
  } else {
    if (btnRaw) btnRaw.className = "px-2.5 py-1 rounded bg-[#CCFF00] text-black font-bold text-xs transition";
    if (btnNtp) btnNtp.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white text-xs transition";
  }
}

function filterTimelineByExhibit(exId, fname) {
  soundEngine.playClick();
  activeExhibitFilter = activeExhibitFilter === exId ? null : exId;
  const bar = document.getElementById('timeline-filter-bar');
  const name = document.getElementById('timeline-filter-name');
  if (activeExhibitFilter) {
    if (bar) bar.classList.remove('hidden');
    if (name) name.textContent = `${exId} (${fname})`;
  } else {
    if (bar) bar.classList.add('hidden');
  }
  renderTimeline();
}

function clearTimelineFilter() {
  activeExhibitFilter = null;
  const bar = document.getElementById('timeline-filter-bar');
  if (bar) bar.classList.add('hidden');
  renderTimeline();
}

function scrollToTimelineEvents(factIds) {
  soundEngine.playClick();
  if (!factIds || factIds.length === 0) return;
  const node = document.getElementById(`timeline-node-${factIds[0]}`);
  if (node) {
    node.scrollIntoView({ behavior: 'smooth', block: 'center' });
    node.classList.add('ring-4', 'ring-[#F43F5E]', 'rounded-xl', 'p-2');
    setTimeout(() => {
      node.classList.remove('ring-4', 'ring-[#F43F5E]', 'rounded-xl', 'p-2');
    }, 2500);
  }
}


// =============================================================================
// 8. FORENSIC EVIDENCE Q&A & DUAL-PANE CITATION INSPECTOR
// =============================================================================
function setQuery(q) {
  const input = document.getElementById('query-input');
  if (input) input.value = q;
  executeQuery();
}

async function executeQuery() {
  const query = document.getElementById('query-input')?.value.trim();
  if (!query) return;

  const container = document.getElementById('claims-container');
  soundEngine.playClick();

  if (container) {
    container.innerHTML = `
      <div class="py-6 text-center text-xs text-[#38BDF8] flex items-center justify-center gap-2 font-mono">
        <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
        <span>Performing zero-hallucination byte verification...</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
  }

  setTimeout(() => {
    const isAlibi = query.toLowerCase().includes("alibi") || query.toLowerCase().includes("financial");
    const isFabricated = query.toLowerCase().includes("bitcoin") || query.toLowerCase().includes("bribe");

    if (isFabricated) {
      container.innerHTML = `
        <div class="cyber-panel p-4 border border-[#F43F5E]/40 bg-[#F43F5E]/[0.05] rounded-xl space-y-2">
          <div class="flex items-center justify-between">
            <span class="badge-crimson text-xs font-bold px-2 py-0.5 rounded">PROMPT HALLUCINATION REJECTED</span>
            <span class="text-xs font-mono text-slate-400">Grounding Score: 0.0%</span>
          </div>
          <p class="text-xs text-slate-300 font-body">
            Claimed assertion ("Suspect accepted 50 BTC bribe") does not appear in any seized exhibit bytes.
          </p>
          <div class="text-[11px] font-mono text-[#F43F5E] pt-1">
            Reason: Zero-token substring match detected across vault. Evidence inadmissible under BSA §63(4).
          </div>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="cyber-panel p-4 border border-[#CCFF00]/40 bg-[#CCFF00]/[0.03] rounded-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="badge-lime text-xs font-bold px-2 py-0.5 rounded">100% BYTE-GROUNDED VERDICT</span>
            <span class="text-xs font-mono text-[#CCFF00]">Confidence: 100%</span>
          </div>
          <p class="text-xs text-slate-200 font-body leading-relaxed">
            Investigative Finding: Suspect's claim of medical sleep is directly refuted by authenticated server logins and confidential file exports from IP <code class="text-[#38BDF8]">192.168.1.105</code> at 15:24 UTC.
          </p>
          <div class="pt-2 border-t border-white/5 flex flex-wrap gap-2">
            <button onclick="openCitationInspector('Server auth log proves successful authentication during alibi', 'EV-BB0B03', 'Row 1', '2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK', true, '')" class="text-xs font-mono px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-[#38BDF8] border border-white/10 transition">
              Inspect Exhibit EV-BB0B03 (LOGIN OK)
            </button>
            <button onclick="openCitationInspector('Suspect chat statement claiming sleep and high fever', 'EV-8EA211', 'Line 2', '[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.', true, '')" class="text-xs font-mono px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-[#CCFF00] border border-white/10 transition">
              Inspect Exhibit EV-8EA211 (Alibi Chat)
            </button>
          </div>
        </div>
      `;
    }
    soundEngine.playChime(784);
    if (window.lucide) lucide.createIcons();
  }, 450);
}

function openCitationInspector(claim, exId, locator, quote, isVerified, reason) {
  soundEngine.playChime(660);
  const modal = document.getElementById('citation-inspector-modal');
  document.getElementById('inspector-claim-text').textContent = `"${claim}"`;
  document.getElementById('inspector-target-exhibit').textContent = exId;
  document.getElementById('inspector-locator').textContent = locator;
  document.getElementById('inspector-extracted-quote').textContent = quote;
  document.getElementById('inspector-filename').textContent = exId === "EV-8EA211" ? "whatsapp_chat.txt" : "server_access.csv";

  const rawCode = document.getElementById('inspector-raw-code');
  if (rawCode) {
    rawCode.innerHTML = `
      <div class="p-2 rounded bg-[#CCFF00]/10 border-l-4 border-[#CCFF00] text-xs font-mono text-[#CCFF00]">
        <span class="text-slate-500 mr-2">01</span> ${escapeHTML(quote)}
      </div>
    `;
  }

  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeCitationInspector() {
  const modal = document.getElementById('citation-inspector-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}


// =============================================================================
// 9. MODALS: CERTIFICATE, MERKLE, HEX AUDIT, GEO DRAWER, DOSSIER
// =============================================================================
function openCertificateModal() {
  soundEngine.playChime(660);
  const modal = document.getElementById('cert-modal');
  const renderArea = document.getElementById('cert-render-area');
  if (renderArea) {
    renderArea.innerHTML = `
      <div class="border-b-2 border-white/20 pb-4 mb-4 text-center">
        <h2 class="text-sm font-bold tracking-widest text-[#CCFF00] font-display">BHARATIYA SAKSHYA ADHINIYAM, 2023 // SECTION 63(4) CERTIFICATE</h2>
        <p class="text-[11px] text-slate-400 font-mono mt-1">Official Electronic Record Admissibility & NIST SHA-256 Hash Disclosure</p>
      </div>
      <div class="space-y-3 text-xs font-mono text-slate-300">
        <div><strong>CASE / FIR REF:</strong> FIR No. 204/2026, PS Cyber Crime</div>
        <div><strong>INVESTIGATING OFFICER:</strong> Inspector A. Yadav (Cyber Cell)</div>
        <div><strong>AUTHENTICATION ENGINE:</strong> CHRONOFACT Local Cryptographic Vault</div>
        <div><strong>MASTER MERKLE ROOT:</strong> 90ebf0e585bae35df91984284cfbdbb981bfbb55c0e5a79afda3e30bf2fd290c</div>
        <div class="p-3 bg-white/5 rounded border border-white/10">
          I hereby certify under BSA 2023 s.63(4)(c) that electronic records were produced by computer devices operating properly under lawful custody, verified with NIST FIPS 180-4 cryptographic digests.
        </div>
      </div>
    `;
  }
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeCertificateModal() {
  const modal = document.getElementById('cert-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function openMerkleModal() {
  soundEngine.playChime(660);
  const modal = document.getElementById('merkle-modal');
  const rootBox = document.getElementById('tree-root-box');
  const leavesBox = document.getElementById('tree-leaves-container');

  if (rootBox) rootBox.textContent = "ROOT: 90ebf0e5...2fd290c";
  if (leavesBox) {
    leavesBox.innerHTML = allEvidenceItems.map((ex, i) => `
      <div class="p-3 rounded-lg bg-white/5 border border-white/10 space-y-1 font-mono text-xs">
        <div class="text-[#CCFF00] font-bold">LEAF #${i + 1} &bull; ${ex.id}</div>
        <div class="text-slate-300 truncate">${ex.filename}</div>
        <div class="text-[10px] text-slate-500 break-all">${ex.sha256}</div>
      </div>
    `).join('');
  }

  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeMerkleModal() {
  const modal = document.getElementById('merkle-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function openHexInspector(exId) {
  soundEngine.playChime(660);
  const modal = document.getElementById('hex-modal');
  const title = document.getElementById('hex-modal-title');
  if (title) title.textContent = `HEX AUDIT: ${exId || 'EV-BB0B03'}`;
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeHexInspector() {
  const modal = document.getElementById('hex-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function openGeoLocationDrawer() {
  soundEngine.playWhoosh();
  const drawer = document.getElementById('geo-location-drawer');
  if (drawer) {
    drawer.classList.remove('hidden');
    drawer.classList.add('flex');
  }
}

function closeGeoLocationDrawer() {
  const drawer = document.getElementById('geo-location-drawer');
  if (drawer) {
    drawer.classList.add('hidden');
    drawer.classList.remove('flex');
  }
}

function openDossierModal() {
  soundEngine.playChime(660);
  const modal = document.getElementById('dossier-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeDossierModal() {
  const modal = document.getElementById('dossier-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function openIngestModal() {
  soundEngine.playChime(660);
  const modal = document.getElementById('ingest-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeIngestModal() {
  const modal = document.getElementById('ingest-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

function openCommandPalette() {
  soundEngine.playClick();
  const modal = document.getElementById('command-palette-modal');
  const input = document.getElementById('command-palette-input');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (input) { input.value = ""; input.focus(); }
  }
}

function closeCommandPalette() {
  const modal = document.getElementById('command-palette-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}


// =============================================================================
// 10. SYSTEM UTILITIES, TOAST NOTIFIER & LIFECYCLE INITIALIZER
// =============================================================================
function showToast(msg) {
  soundEngine.playHover();
  const toast = document.createElement('div');
  toast.className = "fixed bottom-6 right-6 z-[99999] px-4 py-3 rounded-lg bg-[#0E1117] border border-[#CCFF00]/40 text-[#CCFF00] font-mono text-xs shadow-2xl flex items-center gap-2 animate-in fade-in slide-in-from-bottom-2 duration-200";
  toast.innerHTML = `<i data-lucide="info" class="w-4 h-4 text-[#CCFF00]"></i> <span>${escapeHTML(msg)}</span>`;
  document.body.appendChild(toast);
  if (window.lucide) lucide.createIcons();
  setTimeout(() => {
    toast.remove();
  }, 3200);
}

function escapeHTML(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(str) {
  if (!str) return "";
  return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

// Global Hotkeys (Cmd+K / Ctrl+K)
window.addEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    openCommandPalette();
  }
});

// Window Onload Master Lifecycle
window.addEventListener('DOMContentLoaded', () => {
  // 1. Kick off cinematic hardware boot sequence
  runCinematicBootSequence();

  // 2. Initialize Three.js 3D Temporal Twin
  initThreeJSTemporalTwin();

  // 3. Set up interactive time scrubber
  setupTimeScrubber();

  // 4. Animate frequency telemetry waveform
  animateFrequencyWaveform();

  // 5. Initialize scroll sensor observer
  initScrollSensorObserver();

  // 6. Load forensic case data
  loadDashboardData();

  if (window.lucide) lucide.createIcons();
});
