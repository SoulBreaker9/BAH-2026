// ==========================================================================
// BAH 2026 — APP LOGIC
// ==========================================================================

// --------------------------------------------------------------------------
// MODULE 1: CURSOR SYSTEM
// --------------------------------------------------------------------------
const cur = document.getElementById('cur');
const ring = document.getElementById('cur-ring');
let mx = 0, my = 0, rx = 0, ry = 0;

document.addEventListener('mousemove', e => {
  mx = e.clientX;
  my = e.clientY;
});

function animCursor() {
  rx += (mx - rx) * 0.15;
  ry += (my - ry) * 0.15;
  if(cur) cur.style.cssText += `;left:${mx}px;top:${my}px`;
  if(ring) ring.style.cssText += `;left:${rx}px;top:${ry}px`;
  requestAnimationFrame(animCursor);
}
animCursor();

document.querySelectorAll('button, a, .pipe-box, .m-card, .t-card, .vis-btn, .dash-card').forEach(el => {
  el.addEventListener('mouseenter', () => {
    if(cur) { cur.style.width = '18px'; cur.style.height = '18px'; }
    if(ring) { ring.style.width = '52px'; ring.style.height = '52px'; }
  });
  el.addEventListener('mouseleave', () => {
    if(cur) { cur.style.width = '10px'; cur.style.height = '10px'; }
    if(ring) { ring.style.width = '34px'; ring.style.height = '34px'; }
  });
});

// --------------------------------------------------------------------------
// MODULE 2: MISSION CLOCK
// --------------------------------------------------------------------------
const t0 = Date.now();
setInterval(() => {
  const s = Math.floor((Date.now() - t0) / 1000);
  const mtime = document.getElementById('mtime');
  if(mtime) {
    mtime.textContent = `T+${String(Math.floor(s/3600)).padStart(2,'0')}:${String(Math.floor((s%3600)/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
  }
}, 1000);

// --------------------------------------------------------------------------
// MODULE 3: THREE.JS MOON SCENE
// --------------------------------------------------------------------------
const canvas = document.getElementById('moonCanvas');
if (canvas && typeof THREE !== 'undefined') {
  
  // 1. Scene Setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 0, 7);
  
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // 2. Lighting
  const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
  dirLight.position.set(-5, 3, 5);
  scene.add(dirLight);

  const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
  scene.add(ambientLight);
  
  const hemiLight = new THREE.HemisphereLight(0x4fc3f7, 0x020409, 0.2);
  scene.add(hemiLight);

  // 3. Moon Texture & Material
  const textureLoader = new THREE.TextureLoader();
  const moonTexture = textureLoader.load(MOON_TEXTURE_B64);
  
  // Custom Shader to enhance the texture and add ice glow
  const moonMaterial = new THREE.MeshStandardMaterial({
    map: moonTexture,
    roughness: 0.8,
    metalness: 0.1,
  });

  // Inject custom GLSL to add south polar ice shimmer on top of the texture
  moonMaterial.onBeforeCompile = (shader) => {
    shader.uniforms.time = { value: 0 };
    shader.fragmentShader = shader.fragmentShader.replace(
      '#include <common>',
      `
      #include <common>
      uniform float time;
      
      // Noise function for ice scatter
      float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float noise(vec2 p) {
        vec2 i = floor(p), f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
      }
      `
    );
    
    shader.fragmentShader = shader.fragmentShader.replace(
      '#include <dithering_fragment>',
      `
      #include <dithering_fragment>
      
      // Calculate polar mask (south pole)
      float pole = smoothstep(-0.6, -0.95, vNormal.y);
      
      // Add ice shimmer effect
      float n = noise(vUv * 150.0 + time * 0.1);
      float shimmer = (0.5 + 0.5 * sin(time * 2.0 + n * 10.0));
      
      // Ice color
      vec3 iceColor = vec3(0.3, 0.8, 1.0);
      
      // Blend ice over texture
      gl_FragColor.rgb = mix(gl_FragColor.rgb, iceColor, pole * shimmer * 0.7);
      
      // Add subtle blue atmospheric rim
      float rim = 1.0 - max(dot(vNormal, normalize(vViewPosition)), 0.0);
      gl_FragColor.rgb += vec3(0.05, 0.15, 0.3) * pow(rim, 3.0) * 0.8;
      `
    );
    moonMaterial.userData.shader = shader;
  };

  const moonGeometry = new THREE.SphereGeometry(2, 64, 64);
  const moon = new THREE.Mesh(moonGeometry, moonMaterial);
  // Tilt the moon slightly
  moon.rotation.x = 0.2;
  moon.rotation.z = -0.1;
  scene.add(moon);

  // 4. Star Field
  const starGeo = new THREE.BufferGeometry();
  const starCount = 8000;
  const starPos = new Float32Array(starCount * 3);
  for(let i=0; i < starCount*3; i++) {
    starPos[i] = (Math.random() - 0.5) * 40;
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
  
  const starMat = new THREE.PointsMaterial({
    color: 0x88ccff,
    size: 0.05,
    transparent: true,
    opacity: 0.6
  });
  const stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

  // 5. Controls
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.enablePan = false;
  controls.enableZoom = false; // Disable zooming so scroll works on the page
  controls.autoRotate = true;
  controls.autoRotateSpeed = 0.5;

  // 6. Scroll & Mouse Parallax
  let scrollY = 0;
  let targetCamZ = 7;
  let targetCamY = 0;
  
  window.addEventListener('scroll', () => {
    scrollY = window.scrollY;
    // Zoom in and move camera down as user scrolls down
    const scrollFactor = Math.min(scrollY / window.innerHeight, 1.0);
    targetCamZ = 7 - (scrollFactor * 3);
    targetCamY = -(scrollFactor * 1.5);
  });

  let smx = 0, smy = 0;
  document.addEventListener('mousemove', e => {
    smx = (e.clientX / window.innerWidth - 0.5) * 2;
    smy = -(e.clientY / window.innerHeight - 0.5) * 2;
  });

  // 7. Animation Loop
  const clock = new THREE.Clock();
  
  function animateMoon() {
    requestAnimationFrame(animateMoon);
    
    const delta = clock.getDelta();
    const time = clock.getElapsedTime();
    
    if (moonMaterial.userData.shader) {
      moonMaterial.userData.shader.uniforms.time.value = time;
    }
    
    // Smooth camera scroll and parallax
    camera.position.z += (targetCamZ - camera.position.z) * 0.05;
    camera.position.y += (targetCamY - camera.position.y) * 0.05;
    
    camera.position.x += (smx * 0.5 - camera.position.x) * 0.05;
    
    // Rotate starfield slowly
    stars.rotation.y = time * 0.02;
    
    controls.update();
    renderer.render(scene, camera);
  }
  
  animateMoon();

  // Resize handler
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

// --------------------------------------------------------------------------
// MODULE 4: RADAR POLAR CHART (Canvas 2D)
// --------------------------------------------------------------------------
(function initRadar() {
  const c = document.getElementById('radarC');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W = 600, H = 600, cx = 300, cy = 300, R = 220;
  
  let angle = 0;

  // Simulated CPR data (bumpy circle)
  const cprData = Array.from({length: 360}, (_, i) => {
    const base = 0.8 + 0.6 * Math.sin(i * Math.PI / 55) + 0.4 * Math.cos(i * Math.PI / 38);
    return Math.max(0.2, Math.min(2.0, base + (Math.random() - 0.5) * 0.12));
  });
  
  // Smooth data
  const smooth = cprData.map((_, i) => {
    let s = 0; for(let j = -3; j <= 3; j++) s += cprData[(i + j + 360) % 360];
    return s / 7;
  });

  function draw() {
    ctx.clearRect(0, 0, W, H);

    // Grid rings
    [0.25, 0.5, 0.75, 1].forEach(f => {
      ctx.beginPath(); ctx.arc(cx, cy, R * f, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0,255,136,${f === 1 ? 0.2 : 0.08})`;
      ctx.lineWidth = f === 1 ? 1.5 : 1; ctx.stroke();
      ctx.fillStyle = 'rgba(0,255,136,.3)';
      ctx.font = '10px Courier New';
      ctx.fillText((f * 2).toFixed(1), cx + R * f + 4, cy + 4);
    });

    // Axes
    for(let a = 0; a < 360; a += 30) {
      const rad = a * Math.PI / 180;
      ctx.beginPath(); ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(rad) * R, cy + Math.sin(rad) * R);
      ctx.strokeStyle = 'rgba(0,255,136,.06)'; ctx.stroke();
    }

    // Threshold ring CPR=1.0 (R*0.5)
    ctx.beginPath(); ctx.arc(cx, cy, R * 0.5, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,107,53,.6)'; ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]); ctx.stroke(); ctx.setLineDash([]);

    // CPR polygon
    ctx.beginPath();
    smooth.forEach((v, i) => {
      const rad = i * Math.PI / 180, r = R * (v / 2) * 0.92;
      i === 0 ? ctx.moveTo(cx + Math.cos(rad) * r, cy + Math.sin(rad) * r) : ctx.lineTo(cx + Math.cos(rad) * r, cy + Math.sin(rad) * r);
    });
    ctx.closePath();
    const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, R);
    grd.addColorStop(0, 'rgba(79,195,247,.2)'); grd.addColorStop(1, 'rgba(0,255,136,.05)');
    ctx.fillStyle = grd; ctx.fill();
    ctx.strokeStyle = 'rgba(79,195,247,.8)'; ctx.lineWidth = 2; ctx.stroke();

    // Ice hotspot highlight
    const ig = ctx.createRadialGradient(cx + 20, cy + 60, 0, cx + 20, cy + 60, 45);
    ig.addColorStop(0, 'rgba(79,195,247,.5)'); ig.addColorStop(1, 'rgba(79,195,247,0)');
    ctx.beginPath(); ctx.arc(cx + 20, cy + 60, 45, 0, Math.PI * 2);
    ctx.fillStyle = ig; ctx.fill();

    // Sweep arc trail
    const sweepRad = angle * Math.PI / 180;
    ctx.save(); ctx.translate(cx, cy);
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.arc(0, 0, R, (angle - 70) * Math.PI / 180, sweepRad);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0,255,136,.08)'; ctx.fill();
    ctx.restore();

    // Sweep line
    const sg = ctx.createLinearGradient(cx, cy, cx + Math.cos(sweepRad) * R, cy + Math.sin(sweepRad) * R);
    sg.addColorStop(0, 'rgba(0,255,136,0)'); sg.addColorStop(1, 'rgba(0,255,136,1)');
    ctx.beginPath(); ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(sweepRad) * R, cy + Math.sin(sweepRad) * R);
    ctx.strokeStyle = sg; ctx.lineWidth = 2; ctx.stroke();

    // Center dot & Compass
    ctx.beginPath(); ctx.arc(cx, cy, 4, 0, Math.PI * 2); ctx.fillStyle = '#00FF88'; ctx.fill();
    ctx.fillStyle = 'rgba(0,255,136,.6)'; ctx.font = '12px Courier New';
    ctx.fillText('N', cx - 4, cy - R - 12); ctx.fillText('S', cx - 4, cy + R + 20);
    ctx.fillText('E', cx + R + 12, cy + 4); ctx.fillText('W', cx - R - 24, cy + 4);

    angle = (angle + 1.2) % 360;
    requestAnimationFrame(draw);
  }
  
  // Start animation when visible
  const obs = new IntersectionObserver(e => {
    if(e[0].isIntersecting) { draw(); obs.disconnect(); }
  });
  obs.observe(c);
})();


// --------------------------------------------------------------------------
// MODULE 4.5: SENSOR FUSION DIAGRAM (Canvas 2D)
// --------------------------------------------------------------------------
(function initFusion() {
  const c = document.getElementById('fusionC');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W = 600, H = 600;

  function draw() {
    ctx.clearRect(0,0,W,H);
    const t = Date.now() / 1000;

    // Draw central node
    ctx.beginPath(); ctx.arc(300, 300, 55, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(0,255,136,0.1)'; ctx.fill();
    ctx.strokeStyle = '#00FF88'; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 12px Courier New'; ctx.textAlign = 'center';
    ctx.fillText('ICE DETECTED', 300, 304);

    // Draw pulsing rings around center
    const pulse = (t % 2) / 2;
    ctx.beginPath(); ctx.arc(300, 300, 55 + pulse*100, 0, Math.PI*2);
    ctx.strokeStyle = `rgba(0,255,136,${1-pulse})`; ctx.stroke();

    // Data streams (DFSAR L-Band, S-Band, OHRC, IIRS)
    const nodes = [
      {x: 100, y: 150, c: '#00FF88', label: 'DFSAR L-BAND'},
      {x: 500, y: 150, c: '#FF6B35', label: 'DFSAR S-BAND'},
      {x: 100, y: 450, c: '#FFD700', label: 'IIRS SPECTRA'},
      {x: 500, y: 450, c: '#4FC3F7', label: 'OHRC ALBEDO'}
    ];

    nodes.forEach((n, i) => {
      // Draw line to center
      ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(300, 300);
      ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 1; ctx.stroke();
      
      // Moving packet
      const packetT = ((t + i*0.4) % 1.5) / 1.5;
      const px = n.x + (300 - n.x) * packetT;
      const py = n.y + (300 - n.y) * packetT;
      ctx.beginPath(); ctx.arc(px, py, 5, 0, Math.PI*2);
      ctx.fillStyle = n.c; ctx.fill();
      ctx.shadowBlur = 15; ctx.shadowColor = n.c; ctx.fill(); ctx.shadowBlur = 0;

      // Node circle
      ctx.beginPath(); ctx.arc(n.x, n.y, 35, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(255,255,255,0.03)'; ctx.fill();
      ctx.strokeStyle = n.c; ctx.stroke();
      
      // Label
      ctx.fillStyle = '#fff'; ctx.font = 'bold 11px Courier New';
      ctx.fillText(n.label, n.x, n.y + 55);
    });

    requestAnimationFrame(draw);
  }

  const obs = new IntersectionObserver(e => {
    if(e[0].isIntersecting) { draw(); obs.disconnect(); }
  });
  obs.observe(c);
})();


// --------------------------------------------------------------------------
// MODULE 5: LUNAR MAP (Canvas 2D)
// --------------------------------------------------------------------------
(function initMap() {
  const c = document.getElementById('mapC');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W = 600, H = 600;
  
  // Perlin noise substitute for terrain
  function hash(x, y) { return Math.sin(x * 12.9898 + y * 78.233) * 43758.5453 % 1; }
  function noise(x, y) {
    const ix = Math.floor(x), iy = Math.floor(y);
    const fx = x - ix, fy = y - iy;
    return (
      hash(ix, iy) * (1 - fx) * (1 - fy) +
      hash(ix + 1, iy) * fx * (1 - fy) +
      hash(ix, iy + 1) * (1 - fx) * fy +
      hash(ix + 1, iy + 1) * fx * fy
    );
  }

  // Pre-render terrain to offscreen canvas
  const offC = document.createElement('canvas');
  offC.width = W; offC.height = H;
  const oCtx = offC.getContext('2d');
  const imgData = oCtx.createImageData(W, H);
  
  for(let y=0; y<H; y++) {
    for(let x=0; x<W; x++) {
      let v = noise(x*0.01, y*0.01) * 0.5 + noise(x*0.05, y*0.05) * 0.25 + noise(x*0.1, y*0.1) * 0.125;
      
      // Add craters
      const c1 = Math.hypot(x-400, y-350);
      if(c1 < 120) {
        const d = c1/120;
        v -= (1-d)*0.5 * Math.sin(d*Math.PI*3);
      }
      
      const c2 = Math.hypot(x-150, y-150);
      if(c2 < 60) {
        const d = c2/60;
        v -= (1-d)*0.4 * Math.sin(d*Math.PI*2);
      }

      v = Math.max(0, Math.min(1, v + 0.3));
      
      const idx = (y * W + x) * 4;
      const cVal = Math.floor(v * 255);
      imgData.data[idx] = cVal * 0.8;
      imgData.data[idx+1] = cVal * 0.8;
      imgData.data[idx+2] = cVal * 0.9;
      imgData.data[idx+3] = 255;
      
      // Overlay dark PSR shadow
      if(c1 < 100 && y > 300) {
        imgData.data[idx] *= 0.1;
        imgData.data[idx+1] *= 0.1;
        imgData.data[idx+2] *= 0.2;
      }
    }
  }
  oCtx.putImageData(imgData, 0, 0);

  let pathProgress = 0;
  
  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.drawImage(offC, 0, 0);

    // Hazard Heatmap overlay
    ctx.fillStyle = 'rgba(255, 51, 102, 0.15)'; // Red danger
    ctx.beginPath(); ctx.arc(250, 200, 80, 0, Math.PI*2); ctx.fill();
    ctx.beginPath(); ctx.arc(450, 150, 60, 0, Math.PI*2); ctx.fill();

    // Crater target highlight (ice pulse)
    const p = (Date.now() % 2000) / 2000;
    ctx.beginPath(); ctx.arc(400, 350, 40 + p*30, 0, Math.PI*2);
    ctx.strokeStyle = `rgba(79,195,247,${1-p})`; ctx.lineWidth = 2; ctx.stroke();
    
    // Path points
    const pts = [
      {x: 100, y: 100}, {x: 150, y: 250}, {x: 300, y: 280}, 
      {x: 350, y: 400}, {x: 400, y: 350}
    ];

    // Draw path
    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    let totalDist = 0;
    for(let i=1; i<pts.length; i++) {
      totalDist += Math.hypot(pts[i].x - pts[i-1].x, pts[i].y - pts[i-1].y);
    }
    
    let curDist = 0;
    let targetDist = pathProgress * totalDist;
    
    for(let i=1; i<pts.length; i++) {
      const d = Math.hypot(pts[i].x - pts[i-1].x, pts[i].y - pts[i-1].y);
      if(curDist + d > targetDist) {
        const ratio = (targetDist - curDist) / d;
        ctx.lineTo(pts[i-1].x + (pts[i].x - pts[i-1].x) * ratio, pts[i-1].y + (pts[i].y - pts[i-1].y) * ratio);
        break;
      } else {
        ctx.lineTo(pts[i].x, pts[i].y);
      }
      curDist += d;
    }
    
    ctx.strokeStyle = '#00FF88'; ctx.lineWidth = 3; 
    ctx.setLineDash([8, 6]); ctx.lineDashOffset = -Date.now() / 20;
    ctx.stroke(); ctx.setLineDash([]);

    // Landing site
    ctx.beginPath(); ctx.arc(100, 100, 8, 0, Math.PI*2);
    ctx.fillStyle = '#FFD700'; ctx.fill();
    ctx.fillStyle = '#fff'; ctx.font = 'bold 12px Courier New';
    ctx.fillText('LANDING ZONE', 115, 105);

    if(pathProgress < 1) pathProgress += 0.005;
    requestAnimationFrame(draw);
  }

  const obs = new IntersectionObserver(e => {
    if(e[0].isIntersecting) { draw(); obs.disconnect(); }
  });
  obs.observe(c);
})();


// --------------------------------------------------------------------------
// MODULE 6: SUBSURFACE DIAGRAM (Canvas 2D)
// --------------------------------------------------------------------------
(function initSubsurface() {
  const c = document.getElementById('subsurfaceC');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W = 600, H = 600;
  
  function draw() {
    ctx.clearRect(0,0,W,H);
    
    // Background gradient
    const bg = ctx.createLinearGradient(0,0,0,H);
    bg.addColorStop(0, '#111'); bg.addColorStop(0.3, '#222'); bg.addColorStop(1, '#000');
    ctx.fillStyle = bg; ctx.fillRect(0,0,W,H);
    
    // Time
    const t = Date.now() / 1000;
    
    // Ice layer (pulsing)
    const iceY = 300, iceH = 150;
    const pulse = 0.5 + 0.5 * Math.sin(t * 3);
    const ig = ctx.createLinearGradient(0, iceY, 0, iceY + iceH);
    ig.addColorStop(0, `rgba(79,195,247,${0.2 + pulse*0.2})`);
    ig.addColorStop(0.5, `rgba(79,195,247,${0.6 + pulse*0.3})`);
    ig.addColorStop(1, `rgba(79,195,247,0.1)`);
    ctx.fillStyle = ig; ctx.fillRect(0, iceY, W, iceH);
    
    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for(let y=0; y<H; y+=50) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
    
    // Depth labels
    ctx.fillStyle = 'rgba(255,255,255,0.4)'; ctx.font = '12px Courier New';
    ctx.fillText('0m — SURFACE', 10, 20);
    ctx.fillText('2m — REGOLITH', 10, 220);
    ctx.fillText('3m — ICE LENS DETECTED', 10, 320);
    ctx.fillText('5m — BEDROCK', 10, 520);
    
    // Radar pulse going down
    const pY = (t * 200) % H;
    ctx.beginPath(); ctx.moveTo(0, pY); ctx.lineTo(W, pY);
    ctx.strokeStyle = 'rgba(0,255,136,0.8)'; ctx.lineWidth = 2; ctx.stroke();
    
    // Backscatter pulse coming up (only if pulse is past ice)
    if(pY > iceY) {
      const upY = iceY - (pY - iceY);
      if(upY > 0) {
        ctx.beginPath(); ctx.moveTo(0, upY); ctx.lineTo(W, upY);
        ctx.strokeStyle = 'rgba(79,195,247,0.6)'; ctx.lineWidth = 2; ctx.stroke();
      }
    }
    
    requestAnimationFrame(draw);
  }
  
  const obs = new IntersectionObserver(e => {
    if(e[0].isIntersecting) { draw(); obs.disconnect(); }
  });
  obs.observe(c);
})();

// --------------------------------------------------------------------------
// MODULE 7: A* PATHFINDER (Canvas 2D)
// --------------------------------------------------------------------------
(function initAlgo() {
  const c = document.getElementById('algoC');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W = 600, H = 600;
  const cols = 30, rows = 30;
  const w = W / cols, h = H / rows;
  
  let grid = new Array(cols);
  let openSet = [], closedSet = [], path = [];
  let start, end;
  let running = false;
  
  function Spot(i, j) {
    this.i = i; this.j = j;
    this.f = 0; this.g = 0; this.h = 0;
    this.neighbors = []; this.previous = undefined;
    // 20% chance of hazard
    this.wall = Math.random() < 0.2;
    // Keep start and end clear
    if((i===0 && j===0) || (i===cols-1 && j===rows-1)) this.wall = false;
    
    this.addNeighbors = function(g) {
      let i = this.i, j = this.j;
      if (i < cols - 1) this.neighbors.push(g[i + 1][j]);
      if (i > 0) this.neighbors.push(g[i - 1][j]);
      if (j < rows - 1) this.neighbors.push(g[i][j + 1]);
      if (j > 0) this.neighbors.push(g[i][j - 1]);
    }
  }
  
  function setup() {
    for (let i = 0; i < cols; i++) {
      grid[i] = new Array(rows);
      for (let j = 0; j < rows; j++) grid[i][j] = new Spot(i, j);
    }
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) grid[i][j].addNeighbors(grid);
    }
    start = grid[0][0]; end = grid[cols - 1][rows - 1];
    start.wall = false; end.wall = false;
    openSet = [start]; closedSet = []; path = [];
    running = true;
  }
  
  function heuristic(a, b) { return Math.abs(a.i - b.i) + Math.abs(a.j - b.j); }
  
  function draw() {
    ctx.clearRect(0,0,W,H);
    
    if (running) {
      if (openSet.length > 0) {
        let winner = 0;
        for (let i = 0; i < openSet.length; i++) {
          if (openSet[i].f < openSet[winner].f) winner = i;
        }
        let current = openSet[winner];
        
        if (current === end) { running = false; }
        
        openSet.splice(winner, 1);
        closedSet.push(current);
        
        let neighbors = current.neighbors;
        for (let i = 0; i < neighbors.length; i++) {
          let neighbor = neighbors[i];
          if (!closedSet.includes(neighbor) && !neighbor.wall) {
            let tempG = current.g + 1;
            let newPath = false;
            if (openSet.includes(neighbor)) {
              if (tempG < neighbor.g) { neighbor.g = tempG; newPath = true; }
            } else {
              neighbor.g = tempG; newPath = true;
              openSet.push(neighbor);
            }
            if (newPath) {
              neighbor.h = heuristic(neighbor, end);
              neighbor.f = neighbor.g + neighbor.h;
              neighbor.previous = current;
            }
          }
        }
        
        path = [];
        let temp = current;
        path.push(temp);
        while (temp.previous) { path.push(temp.previous); temp = temp.previous; }
        
      } else {
        running = false; // no solution
      }
    }
    
    // Draw grid
    for(let i=0; i<cols; i++) {
      for(let j=0; j<rows; j++) {
        const spot = grid[i][j];
        ctx.fillStyle = spot.wall ? 'rgba(255, 51, 102, 0.4)' : 'rgba(2,4,9,0)';
        if(closedSet.includes(spot)) ctx.fillStyle = 'rgba(0,255,136,0.15)';
        if(openSet.includes(spot)) ctx.fillStyle = 'rgba(0,255,136,0.3)';
        
        ctx.fillRect(i*w, j*h, w-1, h-1);
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        ctx.strokeRect(i*w, j*h, w-1, h-1);
      }
    }
    
    // Draw path
    ctx.beginPath();
    for(let i=0; i<path.length; i++) {
      const p = path[i];
      ctx.lineTo(p.i*w + w/2, p.j*h + h/2);
    }
    ctx.strokeStyle = '#00FF88'; ctx.lineWidth = 4; ctx.stroke();
    
    // Start/End points
    ctx.fillStyle = '#FFD700'; ctx.fillRect(start.i*w, start.j*h, w, h);
    ctx.fillStyle = '#4FC3F7'; ctx.fillRect(end.i*w, end.j*h, w, h);
    
    if(running) requestAnimationFrame(draw);
  }
  
  setup();
  
  const restartBtn = document.getElementById('btn-restart-algo');
  if(restartBtn) restartBtn.addEventListener('click', () => {
    setup(); draw();
  });
  
  const obs = new IntersectionObserver(e => {
    if(e[0].isIntersecting && !running) { setup(); draw(); obs.disconnect(); }
  });
  obs.observe(c);
})();

// --------------------------------------------------------------------------
// MODULE 8: LOADER
// --------------------------------------------------------------------------
(function loader(){
  const bar = document.getElementById('lbar');
  const txt = document.getElementById('ltxt');
  if(!bar || !txt) return;
  
  const msgs = ['LOADING CHANDRAYAAN-2 DATA...', 'INITIALIZING DFSAR PROCESSOR...', 'MAPPING FAUSTINI PSR...', 'CALIBRATING CPR THRESHOLDS...', 'MISSION SYSTEMS READY'];
  let pct = 0, mi = 0;
  
  const iv = setInterval(()=>{
    pct += Math.random()*4 + 2;
    if(pct > 100) pct = 100;
    bar.style.width = pct + '%';
    
    const idx = Math.min(Math.floor(pct / 21), 4);
    if(idx !== mi) { mi = idx; txt.textContent = msgs[mi]; }
    
    if(pct >= 100) {
      clearInterval(iv);
      setTimeout(() => {
        const ldr = document.getElementById('loader');
        ldr.style.opacity = '0';
        setTimeout(() => {
          ldr.style.display = 'none';
          launchAnimations();
        }, 800);
      }, 400);
    }
  }, 40);
})();

// --------------------------------------------------------------------------
// MODULE 9: SCROLL ANIMATIONS
// --------------------------------------------------------------------------
function animEl(el, delay=0) {
  if(!el) return;
  setTimeout(() => {
    el.style.transition = 'opacity .8s ease, transform .8s ease';
    el.classList.add('visible');
  }, delay);
}

function launchAnimations() {
  // Hero sequence
  animEl(document.getElementById('ey'), 100);
  animEl(document.getElementById('h1'), 300);
  animEl(document.getElementById('hs'), 500);
  animEl(document.getElementById('ba'), 700);
  animEl(document.getElementById('ca'), 900);
  
  const sh = document.getElementById('sh');
  if(sh) { sh.style.transition = 'opacity 1s ease 1s'; sh.style.opacity = '1'; }
  
  const sb = document.getElementById('sb');
  if(sb) { sb.style.transition = 'opacity 1s ease 1.5s'; sb.style.opacity = '1'; }

  // Count-up stats
  setTimeout(() => {
    document.querySelectorAll('.stat-v[data-c]').forEach(el => {
      const target = parseFloat(el.dataset.c), dec = parseInt(el.dataset.d)||0;
      let cur = 0; const step = target/60;
      const iv = setInterval(() => {
        cur = Math.min(cur+step, target);
        el.textContent = cur.toFixed(dec);
        if(cur >= target) clearInterval(iv);
      }, 16);
    });
  }, 1500);

  // IntersectionObserver for all elements
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if(e.isIntersecting) {
        e.target.classList.add('visible');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.m-card, .pipe-step, .r-metric, .algo-li, .t-card, .tl-item, .split-visual, .dash-card').forEach((el, i) => {
    if(!el.style.transitionDelay) {
      el.style.transitionDelay = (i % 4) * 0.15 + 's';
    }
    obs.observe(el);
  });

  // Radar bar fills
  const radarObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if(e.isIntersecting) {
        setTimeout(() => {
          if(document.getElementById('rf1')) document.getElementById('rf1').style.width = '62%';
          if(document.getElementById('rf2')) document.getElementById('rf2').style.width = '69%';
          if(document.getElementById('rf3')) document.getElementById('rf3').style.width = '99.4%';
          if(document.getElementById('rf4')) document.getElementById('rf4').style.width = '46%';
          if(document.getElementById('rf5')) document.getElementById('rf5').style.width = '59%';
        }, 300);
        radarObs.disconnect();
      }
    });
  }, { threshold: 0.3 });
  
  const radarSec = document.getElementById('radar-sec');
  if(radarSec) radarObs.observe(radarSec);
  const subSec = document.getElementById('subsurface-sec');
  if(subSec) radarObs.observe(subSec);
}

// --------------------------------------------------------------------------
// MODULE 8: LIVE DATA INJECTION FROM PYTHON PIPELINE
// --------------------------------------------------------------------------
fetch('assets/mission_report.json')
  .then(res => res.json())
  .then(data => {
    // 1. Radar Polarimetry
    const cprEls = document.querySelectorAll('.m-cpr .r-val');
    cprEls.forEach(el => el.innerText = data.cpr_threshold.toFixed(2));
    
    const dopEls = document.querySelectorAll('.m-dop .r-val');
    dopEls.forEach(el => el.innerText = data.dop_threshold.toFixed(2));
    
    const iceProbEls = document.querySelectorAll('.m-ice .r-val');
    iceProbEls.forEach(el => el.innerText = data.ice_probability.toFixed(1) + '%');
    
    // 2. Terrain Subsurface 
    const depthEls = document.querySelectorAll('.m-dep .r-val');
    depthEls.forEach(el => el.innerText = data.ice_depth_m.toFixed(1) + 'm');
    
    // 3. Dashboard specific updates if they exist
    const hazCards = document.querySelectorAll('.dash-card');
    hazCards.forEach(card => {
      if(card.innerText.includes('HAZARD')) {
        const valEl = card.querySelector('.dc-val');
        if(valEl) valEl.innerText = data.hazard_pixels_avoided.toLocaleString();
      }
      if(card.innerText.includes('VOLUME')) {
        const valEl = card.querySelector('.dc-val');
        if(valEl) valEl.innerText = (data.total_ice_volume_m3 / 1000000).toFixed(2) + 'M';
      }
    });
  })
  .catch(err => console.error("Could not load mission_report.json", err));
