/**
 * KidsBook 3D Scene Engine
 * Manages Three.js scene, lighting, 3D pop-up book diorama transitions,
 * floating magical particles, and interactive object clicking.
 */

import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { sound } from './audio.js';

export class Storybook3DScene {
  constructor(canvasContainer) {
    this.container = canvasContainer;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.loader = new GLTFLoader();
    
    this.currentChapterGroup = null;
    this.currentChapterIndex = 0;
    this.isTransitioning = false;
    this.isBedtimeMode = false;
    
    this.sunLight = null;
    this.ambientLight = null;
    this.warmGlowLight = null;
    this.particleSystem = null;
    this.particleCount = 60;
    
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.clickableMeshes = [];
    
    this.cachedModels = {};
    this.clock = new THREE.Clock();
    
    this.init();
  }

  init() {
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x241d1a);
    this.scene.fog = new THREE.FogExp2(0x241d1a, 0.08);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, 3.8, 5.2);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.container.appendChild(this.renderer.domElement);

    // 4. Orbit Controls (Tuned for kid-friendly interaction)
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.maxPolarAngle = Math.PI / 2 - 0.05; // Don't flip below floor
    this.controls.minDistance = 2.5;
    this.controls.maxDistance = 9.0;
    this.controls.target.set(0, 0.4, 0);

    // 5. Lighting
    this.setupLighting();

    // 6. Floating Magical Dust / Firefly Particles
    this.setupParticles();

    // 7. Event Listeners
    window.addEventListener('resize', () => this.onWindowResize());
    this.renderer.domElement.addEventListener('pointerdown', (e) => this.onPointerDown(e));

    // 8. Start Render Loop
    this.animate();
  }

  setupLighting() {
    this.ambientLight = new THREE.AmbientLight(0xfff3e6, 0.65);
    this.scene.add(this.ambientLight);

    this.sunLight = new THREE.DirectionalLight(0xfffaed, 2.2);
    this.sunLight.position.set(4, 7, 5);
    this.sunLight.castShadow = true;
    this.sunLight.shadow.mapSize.width = 1024;
    this.sunLight.shadow.mapSize.height = 1024;
    this.sunLight.shadow.camera.near = 0.5;
    this.sunLight.shadow.camera.far = 20;
    this.sunLight.shadow.camera.left = -4;
    this.sunLight.shadow.camera.right = 4;
    this.sunLight.shadow.camera.top = 4;
    this.sunLight.shadow.camera.bottom = -4;
    this.sunLight.shadow.bias = -0.001;
    this.scene.add(this.sunLight);

    this.warmGlowLight = new THREE.PointLight(0xffaa44, 2.5, 8);
    this.warmGlowLight.position.set(0, 1.2, 0);
    this.scene.add(this.warmGlowLight);
  }

  setupParticles() {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.particleCount * 3);
    const scales = new Float32Array(this.particleCount);

    for (let i = 0; i < this.particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 6;
      positions[i * 3 + 1] = Math.random() * 3.5 + 0.2;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 6;
      scales[i] = Math.random() * 0.8 + 0.4;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));

    // Canvas particle texture
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    grad.addColorStop(0, 'rgba(255, 240, 180, 1)');
    grad.addColorStop(0.4, 'rgba(255, 200, 100, 0.6)');
    grad.addColorStop(1, 'rgba(255, 200, 100, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 32, 32);
    const pTexture = new THREE.CanvasTexture(canvas);

    const material = new THREE.PointsMaterial({
      size: 0.15,
      map: pTexture,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    this.particleSystem = new THREE.Points(geometry, material);
    this.scene.add(this.particleSystem);
  }

  loadChapter(chapterData, onLoaded = null) {
    if (this.isTransitioning) return;
    this.isTransitioning = true;
    sound.playPageTurn();

    const modelPath = chapterData.model;
    const doTransition = (newModelScene) => {
      // 1. Pop out current chapter
      if (this.currentChapterGroup) {
        this.animatePopOut(this.currentChapterGroup, () => {
          this.scene.remove(this.currentChapterGroup);
          this.insertNewChapter(newModelScene, chapterData, onLoaded);
        });
      } else {
        this.insertNewChapter(newModelScene, chapterData, onLoaded);
      }
    };

    if (this.cachedModels[modelPath]) {
      const cloned = this.cachedModels[modelPath].clone(true);
      doTransition(cloned);
    } else {
      this.loader.load(
        modelPath,
        (gltf) => {
          this.cachedModels[modelPath] = gltf.scene;
          const cloned = gltf.scene.clone(true);
          doTransition(cloned);
        },
        undefined,
        (err) => {
          console.error("Failed to load model:", modelPath, err);
          this.isTransitioning = false;
        }
      );
    }
  }

  insertNewChapter(modelScene, chapterData, onLoaded) {
    this.clickableMeshes = [];
    modelScene.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        this.clickableMeshes.push(child);
      }
    });

    this.currentChapterGroup = new THREE.Group();
    this.currentChapterGroup.add(modelScene);
    this.currentChapterGroup.scale.set(0.001, 0.001, 0.001);
    this.currentChapterGroup.position.set(0, 0, 0);
    this.scene.add(this.currentChapterGroup);

    // Update lighting based on chapter
    if (chapterData.lighting) {
      this.sunLight.intensity = chapterData.lighting.sun_intensity;
      this.sunLight.color.setHex(chapterData.lighting.sun_color);
      this.ambientLight.intensity = chapterData.lighting.ambient;
      this.warmGlowLight.color.setHex(chapterData.lighting.warm_glow);
    }

    // Pop-in spring animation
    this.animatePopIn(this.currentChapterGroup, () => {
      this.isTransitioning = false;
      sound.playSparkle();
      if (onLoaded) onLoaded();
    });
  }

  animatePopIn(group, onDone) {
    let t = 0;
    const duration = 0.65;
    const startPos = -0.4;
    const endPos = 0.0;
    
    const tick = () => {
      t += 0.035;
      const progress = Math.min(t / duration, 1.0);
      // Spring elastic overshoot curve
      const s = Math.sin(-13.0 * (progress + 1.0) * Math.PI / 2) * Math.pow(2.0, -10.0 * progress) + 1.0;
      
      group.scale.set(s, s, s);
      group.position.y = startPos + (endPos - startPos) * progress;

      if (progress < 1.0) {
        requestAnimationFrame(tick);
      } else {
        group.scale.set(1, 1, 1);
        group.position.y = 0;
        if (onDone) onDone();
      }
    };
    tick();
  }

  animatePopOut(group, onDone) {
    let t = 0;
    const duration = 0.35;
    const tick = () => {
      t += 0.05;
      const progress = Math.min(t / duration, 1.0);
      const ease = Math.pow(progress, 2);
      const s = 1.0 - ease;
      
      group.scale.set(s, s, s);
      group.position.y = -0.3 * ease;

      if (progress < 1.0) {
        requestAnimationFrame(tick);
      } else {
        if (onDone) onDone();
      }
    };
    tick();
  }

  onPointerDown(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.clickableMeshes, false);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      this.triggerObjectInteraction(hit);
    }
  }

  triggerObjectInteraction(mesh) {
    // Determine sound and bounce animation
    const name = mesh.name.toLowerCase();
    if (name.includes('carrot')) {
      sound.playCarrotCrunch();
    } else if (name.includes('water') || name.includes('can')) {
      sound.playWaterSplash();
    } else if (name.includes('bird') || name.includes('robin')) {
      sound.playBirdChirp();
    } else if (name.includes('tea') || name.includes('mug') || name.includes('cup')) {
      sound.playSteam();
    } else if (name.includes('lantern') || name.includes('candle') || name.includes('star')) {
      sound.playSparkle();
    } else {
      sound.playPop();
    }

    // Interactive scale bounce on clicked mesh
    const originalScale = mesh.scale.clone();
    let frame = 0;
    const bounce = () => {
      frame++;
      const s = 1.0 + Math.sin(frame * 0.4) * 0.25 * Math.exp(-frame * 0.1);
      mesh.scale.set(originalScale.x * s, originalScale.y * s, originalScale.z * s);
      if (frame < 25) {
        requestAnimationFrame(bounce);
      } else {
        mesh.scale.copy(originalScale);
      }
    };
    bounce();
  }

  setBedtimeMode(isBedtime) {
    this.isBedtimeMode = isBedtime;
    if (isBedtime) {
      this.scene.background = new THREE.Color(0x0e111a);
      this.scene.fog.color = new THREE.Color(0x0e111a);
      this.ambientLight.intensity = 0.25;
      this.sunLight.intensity = 0.4;
      this.sunLight.color.setHex(0x5577bb);
      this.warmGlowLight.intensity = 4.0;
    } else {
      this.scene.background = new THREE.Color(0x241d1a);
      this.scene.fog.color = new THREE.Color(0x241d1a);
      this.ambientLight.intensity = 0.65;
      this.sunLight.intensity = 2.2;
      this.sunLight.color.setHex(0xfffaed);
      this.warmGlowLight.intensity = 2.5;
    }
  }

  onWindowResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    const delta = this.clock.getDelta();
    const elapsedTime = this.clock.getElapsedTime();

    // Subtle floating particles motion
    if (this.particleSystem) {
      const pos = this.particleSystem.geometry.attributes.position.array;
      for (let i = 0; i < this.particleCount; i++) {
        pos[i * 3 + 1] += Math.sin(elapsedTime * 1.5 + i) * 0.003;
        pos[i * 3] += Math.cos(elapsedTime * 0.8 + i) * 0.002;
      }
      this.particleSystem.geometry.attributes.position.needsUpdate = true;
    }

    // Subtle breathing animation for active chapter diorama
    if (this.currentChapterGroup && !this.isTransitioning) {
      this.currentChapterGroup.position.y = Math.sin(elapsedTime * 1.8) * 0.025;
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
