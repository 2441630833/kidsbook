/**
 * KidsBook 3D Narration Engine (Web Speech Synthesis API)
 * Provides real-time bilingual read-aloud storytelling with word highlighting.
 */

class NarrationEngine {
  constructor() {
    this.synth = window.speechSynthesis;
    this.currentUtterance = null;
    this.isPlaying = false;
    this.currentLanguage = "cn"; // 'en' or 'cn'
    this.onWordBoundary = null;
    this.onFinished = null;
  }

  isSupported() {
    return 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  }

  speak(text, lang = "cn", onBoundary = null, onEnd = null) {
    if (!this.isSupported()) {
      console.warn("Speech synthesis is not supported on this browser.");
      return;
    }

    this.stop();
    this.isPlaying = true;
    this.currentLanguage = lang;
    this.onWordBoundary = onBoundary;
    this.onFinished = onEnd;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "cn" ? "zh-CN" : "en-US";
    utterance.rate = lang === "cn" ? 0.9 : 0.88; // Relaxed storybook tempo
    utterance.pitch = 1.1; // Friendly warm pitch

    // Choose the best voice available
    const voices = this.synth.getVoices();
    if (voices && voices.length > 0) {
      const match = voices.find(v => 
        (lang === "cn" && (v.lang.includes("zh") || v.lang.includes("cmn"))) ||
        (lang === "en" && (v.lang.includes("en-US") || v.lang.includes("en-GB")))
      );
      if (match) utterance.voice = match;
    }

    utterance.onboundary = (event) => {
      if (this.onWordBoundary) {
        this.onWordBoundary(event.charIndex, event.charLength || 1);
      }
    };

    utterance.onend = () => {
      this.isPlaying = false;
      if (this.onFinished) this.onFinished();
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis event error:", e);
      this.isPlaying = false;
      if (this.onFinished) this.onFinished();
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  pause() {
    if (this.synth.speaking) {
      this.synth.pause();
      this.isPlaying = false;
    }
  }

  resume() {
    if (this.synth.paused) {
      this.synth.resume();
      this.isPlaying = true;
    }
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
      this.isPlaying = false;
    }
  }

  toggle(text, lang, onBoundary, onEnd) {
    if (this.isPlaying) {
      this.stop();
      return false;
    } else {
      this.speak(text, lang, onBoundary, onEnd);
      return true;
    }
  }
}

export const narration = new NarrationEngine();
