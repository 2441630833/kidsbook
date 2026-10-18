/**
 * KidsBook 3D Main Application Controller
 * Orchestrates 3D scene, UI state, bilingual switching, narration, and bedtime soothing mode.
 */

import { STORY_METADATA, CHAPTERS, OTHER_PUBLIC_DOMAIN_BOOKS } from './storyData.js';
import { Storybook3DScene } from './scene3d.js';
import { sound } from './audio.js';
import { narration } from './narration.js';

class KidsBookApp {
  constructor() {
    this.currentChapterIndex = 0;
    this.currentLanguage = "cn"; // 'cn' or 'en'
    this.isBedtimeMode = false;
    this.isAutoplay = false;
    this.scene3d = null;
    
    this.touchStartX = 0;
    this.touchStartY = 0;
  }

  init() {
    const canvasContainer = document.getElementById("canvas-container");
    this.scene3d = new Storybook3DScene(canvasContainer);

    this.bindUI();
    this.bindGestures();
    this.renderLibraryModal();
    this.updateChapter(0);
  }

  bindUI() {
    // Navigation buttons
    document.getElementById("btn-prev").addEventListener("click", () => this.prevChapter());
    document.getElementById("btn-next").addEventListener("click", () => this.nextChapter());

    // Language toggle
    const langBtn = document.getElementById("btn-lang");
    langBtn.addEventListener("click", () => {
      this.currentLanguage = this.currentLanguage === "cn" ? "en" : "cn";
      langBtn.textContent = this.currentLanguage === "cn" ? "EN / 中文" : "中文 / EN";
      this.renderStoryText();
      sound.playPop();
    });

    // Read to Me (Narration)
    const readBtn = document.getElementById("btn-narrate");
    readBtn.addEventListener("click", () => {
      const chapter = CHAPTERS[this.currentChapterIndex];
      const text = this.currentLanguage === "cn" ? chapter.text_cn : chapter.text_en;
      
      const isSpeaking = narration.toggle(
        text,
        this.currentLanguage,
        (charIndex, charLength) => this.highlightSpokenWord(charIndex, charLength),
        () => {
          this.clearWordHighlights();
          readBtn.classList.remove("active");
          if (this.isAutoplay && this.currentChapterIndex < CHAPTERS.length - 1) {
            setTimeout(() => this.nextChapter(), 1200);
          }
        }
      );

      if (isSpeaking) {
        readBtn.classList.add("active");
        sound.playSparkle();
      } else {
        readBtn.classList.remove("active");
        this.clearWordHighlights();
      }
    });

    // Bedtime Mode
    const bedtimeBtn = document.getElementById("btn-bedtime");
    bedtimeBtn.addEventListener("click", () => {
      this.isBedtimeMode = !this.isBedtimeMode;
      document.body.classList.toggle("bedtime-theme", this.isBedtimeMode);
      bedtimeBtn.classList.toggle("active", this.isBedtimeMode);
      this.scene3d.setBedtimeMode(this.isBedtimeMode);
      sound.toggleLullaby();
    });

    // Sound Mute
    const soundBtn = document.getElementById("btn-sound");
    soundBtn.addEventListener("click", () => {
      const isMuted = sound.toggleMute();
      soundBtn.classList.toggle("muted", isMuted);
      soundBtn.title = isMuted ? "Unmute" : "Mute";
    });

    // Library Modal
    const libBtn = document.getElementById("btn-library");
    const libModal = document.getElementById("library-modal");
    const libClose = document.getElementById("library-close");
    
    libBtn.addEventListener("click", () => {
      libModal.classList.add("visible");
      sound.playPop();
    });
    
    libClose.addEventListener("click", () => {
      libModal.classList.remove("visible");
    });
    
    libModal.addEventListener("click", (e) => {
      if (e.target === libModal) libModal.classList.remove("visible");
    });

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") this.prevChapter();
      if (e.key === "ArrowRight") this.nextChapter();
      if (e.key === " ") {
        e.preventDefault();
        document.getElementById("btn-narrate").click();
      }
    });

    // Chapter Indicator Dots
    const dotsContainer = document.getElementById("chapter-dots");
    dotsContainer.innerHTML = "";
    CHAPTERS.forEach((ch, idx) => {
      const dot = document.createElement("button");
      dot.className = "dot" + (idx === 0 ? " active" : "");
      dot.title = ch.title_cn;
      dot.addEventListener("click", () => this.updateChapter(idx));
      dotsContainer.appendChild(dot);
    });
  }

  bindGestures() {
    window.addEventListener("touchstart", (e) => {
      this.touchStartX = e.touches[0].clientX;
      this.touchStartY = e.touches[0].clientY;
    }, { passive: true });

    window.addEventListener("touchend", (e) => {
      const diffX = e.changedTouches[0].clientX - this.touchStartX;
      const diffY = e.changedTouches[0].clientY - this.touchStartY;
      
      // Horizontal swipe detected
      if (Math.abs(diffX) > 60 && Math.abs(diffY) < 80) {
        if (diffX < 0) {
          this.nextChapter();
        } else {
          this.prevChapter();
        }
      }
    }, { passive: true });
  }

  prevChapter() {
    if (this.currentChapterIndex > 0) {
      this.updateChapter(this.currentChapterIndex - 1);
    }
  }

  nextChapter() {
    if (this.currentChapterIndex < CHAPTERS.length - 1) {
      this.updateChapter(this.currentChapterIndex + 1);
    }
  }

  updateChapter(index) {
    narration.stop();
    document.getElementById("btn-narrate").classList.remove("active");
    this.clearWordHighlights();

    this.currentChapterIndex = index;
    const chapter = CHAPTERS[index];

    // 1. Show instant illustration backdrop & loading badge
    const backdrop = document.getElementById("scene-backdrop");
    const loader = document.getElementById("scene-loader");
    const loaderStatus = document.getElementById("loader-status");
    if (backdrop && chapter.preview) {
      backdrop.style.backgroundImage = `url('${chapter.preview}')`;
      backdrop.classList.remove("faded");
    }
    if (loader) {
      if (loaderStatus) {
        loaderStatus.textContent = this.currentLanguage === "cn" ? "正在翻开立体画卷..." : "Opening 3D pop-up page...";
      }
      loader.classList.remove("hidden");
    }

    // 2. Update 3D diorama
    this.scene3d.loadChapter(chapter, () => {
      if (loader) loader.classList.add("hidden");
      if (backdrop) backdrop.classList.add("faded");
    });

    // 3. Update Text UI
    this.renderStoryText();

    // 4. Update Buttons & Dots
    document.getElementById("btn-prev").disabled = index === 0;
    document.getElementById("btn-next").disabled = index === CHAPTERS.length - 1;

    const dots = document.querySelectorAll("#chapter-dots .dot");
    dots.forEach((d, i) => d.classList.toggle("active", i === index));

    // 5. Render interactive clues pill
    this.renderInteractivePills(chapter);
  }

  renderStoryText() {
    const chapter = CHAPTERS[this.currentChapterIndex];
    const isCn = this.currentLanguage === "cn";

    document.getElementById("chapter-title").textContent = isCn ? chapter.title_cn : chapter.title_en;
    document.getElementById("chapter-subtitle").textContent = isCn ? chapter.subtitle_cn : chapter.subtitle_en;
    
    const text = isCn ? chapter.text_cn : chapter.text_en;
    const textEl = document.getElementById("story-text");
    
    // Wrap words/characters in spans for narration highlight
    if (isCn) {
      // Wrap sentences or clauses
      textEl.innerHTML = text.split('').map((char, i) => `<span data-idx="${i}">${char}</span>`).join('');
    } else {
      let charCount = 0;
      textEl.innerHTML = text.split(' ').map((word) => {
        const span = `<span data-idx="${charCount}">${word}</span> `;
        charCount += word.length + 1;
        return span;
      }).join('');
    }
  }

  renderInteractivePills(chapter) {
    const pillsContainer = document.getElementById("interactive-pills");
    pillsContainer.innerHTML = "";
    
    chapter.interactive_hints.forEach(hint => {
      const pill = document.createElement("div");
      pill.className = "interactive-pill";
      pill.innerHTML = `✨ <span>${this.currentLanguage === "cn" ? hint.name_cn : hint.name_en}</span>`;
      pill.addEventListener("click", () => {
        // Find corresponding mesh in scene
        const target = this.scene3d.clickableMeshes.find(m => 
          m.name.toLowerCase().includes(hint.id)
        );
        if (target) {
          this.scene3d.triggerObjectInteraction(target);
        } else {
          sound.playSparkle();
        }
      });
      pillsContainer.appendChild(pill);
    });
  }

  highlightSpokenWord(charIndex, charLength) {
    const textEl = document.getElementById("story-text");
    const spans = textEl.querySelectorAll("span");
    
    spans.forEach(span => {
      const idx = parseInt(span.getAttribute("data-idx"), 10);
      if (idx >= charIndex && idx < charIndex + charLength + 2) {
        span.classList.add("highlighted");
      } else {
        span.classList.remove("highlighted");
      }
    });
  }

  clearWordHighlights() {
    const textEl = document.getElementById("story-text");
    if (textEl) {
      textEl.querySelectorAll("span.highlighted").forEach(s => s.classList.remove("highlighted"));
    }
  }

  renderLibraryModal() {
    const container = document.getElementById("library-list");
    container.innerHTML = "";

    // Featured current book
    const currentCard = document.createElement("div");
    currentCard.className = "book-card active";
    currentCard.innerHTML = `
      <div class="book-badge">NOW READING</div>
      <img src="${STORY_METADATA.cover_image}" class="book-thumb" alt="Cover" />
      <div class="book-info">
        <h3>${this.currentLanguage === "cn" ? STORY_METADATA.title_cn : STORY_METADATA.title_en}</h3>
        <p class="book-author">By ${STORY_METADATA.author_en} (${STORY_METADATA.published_year})</p>
        <span class="book-tag ip-clear">100% Public Domain</span>
      </div>
    `;
    container.appendChild(currentCard);

    // Other Public domain books
    OTHER_PUBLIC_DOMAIN_BOOKS.forEach(b => {
      const card = document.createElement("div");
      card.className = "book-card";
      card.innerHTML = `
        <div class="book-thumb placeholder-thumb">📖</div>
        <div class="book-info">
          <h3>${this.currentLanguage === "cn" ? b.title_cn : b.title_en}</h3>
          <p class="book-author">${b.author} (${b.year})</p>
          <p class="book-desc">${this.currentLanguage === "cn" ? b.desc_cn : b.desc_en}</p>
          <span class="book-tag">${b.status}</span>
        </div>
      `;
      container.appendChild(card);
    });
  }
}

// Safe Bootstrap on DOM load or immediate if already interactive
function startApp() {
  if (!window.kidsBook) {
    try {
      window.kidsBook = new KidsBookApp();
      window.kidsBook.init();
      console.log("KidsBook 3D successfully initialized!");
    } catch (err) {
      console.error("KidsBook 3D initialization error:", err);
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", startApp);
} else {
  startApp();
}
