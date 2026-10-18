/**
 * KidsBook 3D Sound & Synthesizer Engine (Web Audio API)
 * Zero external audio files required: 100% procedurally synthesized in real-time!
 * Safe, copyright-free, fast-loading, and responsive to user touches.
 */

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.lullabyGain = null;
    this.isMuted = false;
    this.isLullabyPlaying = false;
    this.lullabyTimer = null;
    this.currentNoteIndex = 0;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.7, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
      
      this.lullabyGain = this.ctx.createGain();
      this.lullabyGain.gain.setValueAtTime(0.18, this.ctx.currentTime);
      this.lullabyGain.connect(this.masterGain);
    }
    if (this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.masterGain && this.ctx) {
      this.masterGain.gain.setTargetAtTime(this.isMuted ? 0 : 0.7, this.ctx.currentTime, 0.05);
    }
    return this.isMuted;
  }

  // 1. Soft 3D Page Turn Rustle
  playPageTurn() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    
    // Filtered noise buffer for paper rustle
    const bufferSize = this.ctx.sampleRate * 0.25;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.4));
    }
    
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    
    const filter = this.ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(800, t);
    filter.frequency.exponentialRampToValueAtTime(1600, t + 0.15);
    filter.Q.value = 1.8;
    
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.4, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.22);
    
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);
    
    noise.start(t);
  }

  // 2. Playful Bubble Pop
  playPop() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    
    osc.type = "sine";
    osc.frequency.setValueAtTime(400, t);
    osc.frequency.exponentialRampToValueAtTime(850, t + 0.08);
    
    gain.gain.setValueAtTime(0.5, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
    
    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(t);
    osc.stop(t + 0.13);
  }

  // 3. Carrot Crunch Bite
  playCarrotCrunch() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    
    // Low woody pop
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(220, t);
    osc.frequency.exponentialRampToValueAtTime(60, t + 0.08);
    gain.gain.setValueAtTime(0.6, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);
    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(t);
    osc.stop(t + 0.1);
    
    // Crisp click
    const osc2 = this.ctx.createOscillator();
    const gain2 = this.ctx.createGain();
    osc2.type = "square";
    osc2.frequency.setValueAtTime(1200, t + 0.02);
    osc2.frequency.exponentialRampToValueAtTime(400, t + 0.06);
    gain2.gain.setValueAtTime(0.3, t + 0.02);
    gain2.gain.exponentialRampToValueAtTime(0.01, t + 0.07);
    osc2.connect(gain2);
    gain2.connect(this.masterGain);
    osc2.start(t + 0.02);
    osc2.stop(t + 0.08);
  }

  // 4. Water Droplet & Splash
  playWaterSplash() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    
    osc.type = "sine";
    osc.frequency.setValueAtTime(1400, t);
    osc.frequency.exponentialRampToValueAtTime(500, t + 0.15);
    
    gain.gain.setValueAtTime(0.4, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.18);
    
    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(t);
    osc.stop(t + 0.2);
  }

  // 5. Celestial Magic Sparkle (Chimes)
  playSparkle() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    const freqs = [523.25, 659.25, 783.99, 1046.50, 1318.51]; // C5, E5, G5, C6, E6
    
    freqs.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const noteTime = t + idx * 0.06;
      
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, noteTime);
      
      gain.gain.setValueAtTime(0.25, noteTime);
      gain.gain.exponentialRampToValueAtTime(0.001, noteTime + 0.4);
      
      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(noteTime);
      osc.stop(noteTime + 0.45);
    });
  }

  // 6. Bird Chirp
  playBirdChirp() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    
    osc.type = "sine";
    osc.frequency.setValueAtTime(2200, t);
    osc.frequency.linearRampToValueAtTime(3200, t + 0.06);
    osc.frequency.linearRampToValueAtTime(2600, t + 0.12);
    
    gain.gain.setValueAtTime(0.2, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.14);
    
    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(t);
    osc.stop(t + 0.15);
  }

  // 7. Steaming Tea Swirl
  playSteam() {
    this.init();
    if (this.isMuted) return;
    const t = this.ctx.currentTime;
    
    const bufferSize = this.ctx.sampleRate * 0.6;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.sin(Math.PI * i / bufferSize);
    }
    
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    
    const filter = this.ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(2400, t);
    filter.Q.value = 4.0;
    
    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.18, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.55);
    
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);
    noise.start(t);
  }

  // 8. Soothing Bedtime Music Box / Lullaby Synthesizer (Brahms' Lullaby Theme)
  toggleLullaby() {
    this.init();
    this.isLullabyPlaying = !this.isLullabyPlaying;
    
    if (this.isLullabyPlaying) {
      this._startLullabyLoop();
    } else {
      this._stopLullabyLoop();
    }
    return this.isLullabyPlaying;
  }

  _startLullabyLoop() {
    // Brahms Lullaby Melody notes [freq in Hz, duration in seconds]
    const notes = [
      [392.00, 0.4], [392.00, 0.4], [440.00, 0.8], // G4, G4, A4
      [392.00, 0.4], [392.00, 0.4], [440.00, 0.8], // G4, G4, A4
      [392.00, 0.4], [523.25, 0.6], [493.88, 0.4], [440.00, 0.4], [392.00, 0.8], // G4, C5, B4, A4, G4
      [329.63, 0.4], [349.23, 0.4], [392.00, 0.8], // E4, F4, G4
      [329.63, 0.4], [349.23, 0.4], [392.00, 0.8], // E4, F4, G4
      [329.63, 0.4], [392.00, 0.4], [523.25, 0.8], [493.88, 0.6], [440.00, 0.6], [392.00, 1.2]
    ];
    
    this.currentNoteIndex = 0;
    
    const playNext = () => {
      if (!this.isLullabyPlaying || this.isMuted) return;
      const [freq, dur] = notes[this.currentNoteIndex];
      const t = this.ctx.currentTime;
      
      // Warm celesta chime timbre: fundamental + octave overtone
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const noteGain = this.ctx.createGain();
      
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(freq, t);
      
      osc2.type = "triangle";
      osc2.frequency.setValueAtTime(freq * 2, t);
      
      noteGain.gain.setValueAtTime(0.18, t);
      noteGain.gain.exponentialRampToValueAtTime(0.002, t + dur * 1.5);
      
      osc1.connect(noteGain);
      osc2.connect(noteGain);
      noteGain.connect(this.lullabyGain);
      
      osc1.start(t);
      osc2.start(t);
      osc1.stop(t + dur * 1.6);
      osc2.stop(t + dur * 1.6);
      
      this.currentNoteIndex = (this.currentNoteIndex + 1) % notes.length;
      this.lullabyTimer = setTimeout(playNext, (dur + 0.15) * 1000);
    };
    
    playNext();
  }

  _stopLullabyLoop() {
    if (this.lullabyTimer) {
      clearTimeout(this.lullabyTimer);
      this.lullabyTimer = null;
    }
  }
}

export const sound = new SoundEngine();
