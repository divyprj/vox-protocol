/**
 * VOX//PROTOCOL — Neural Voice Studio Client Application
 * Production-Grade Reactive Frontend Controller
 */

// Application State
const state = {
  activeTab: 'studio',
  voices: [],
  selectedVoice: null,
  activeFilterLang: 'all',
  activeFilterGender: 'all',
  searchQuery: '',
  currentAudio: null,
  history: [],
  previewAudio: null,
  currentlyPlayingPreviewId: null,
  isGenerating: false,
  autoTranslate: true,
  activeTranslation: null,
  useOriginal: false,
  transDebounceTimer: null,
};

// Prompt Presets
const TEMPLATES = {
  tech_explainer: "Neural voice synthesis leverages deep diffusion transformers and mel-spectrogram vocoders to generate photorealistic human acoustics at sub-hundred millisecond latencies.",
  saas_promo: "Welcome to VOX Protocol. Unleash production-ready neural speech for your games, AI agents, podcasts, and video voiceovers with instant API integration.",
  hindi_dialogue: "नमस्ते! वॉक्स प्रोटोकॉल में आपका स्वागत है। हमारी अत्याधुनिक एआई आवाज़ तकनीक आपके प्रोजेक्ट्स को सजीव और प्रभावशाली बनाती है।",
  customer_agent: "Thank you for calling Web3Task Global Support. I am your autonomous AI concierge. How can I assist you with your platform integration today?",
  audiobook_epic: "The ancient citadel stood silent beneath the perpetual twilight of the northern rim, its titanium gates sealed for ten thousand years awaiting the chosen architect."
};

// DOM References
const elements = {
  // Navigation
  tabs: document.querySelectorAll('.nav-tab'),
  views: document.querySelectorAll('.tab-view'),
  libraryCountBadge: document.getElementById('library-count-badge'),

  // Script Editor & Translation
  textInput: document.getElementById('text-input'),
  charCount: document.getElementById('char-count'),
  wordCount: document.getElementById('word-count'),
  clearTextBtn: document.getElementById('clear-text-btn'),
  templateDropdown: document.getElementById('template-dropdown'),
  autoTranslateToggle: document.getElementById('auto-translate-toggle'),
  detectedLangBadge: document.getElementById('detected-lang-badge'),
  translationPreviewCard: document.getElementById('translation-preview-card'),
  transTargetLabel: document.getElementById('trans-target-label'),
  transPipelineTag: document.getElementById('trans-pipeline-tag'),
  transText: document.getElementById('trans-text'),
  transLoadingOverlay: document.getElementById('trans-loading-overlay'),
  toggleOriginalBtn: document.getElementById('toggle-original-btn'),
  toggleOriginalText: document.getElementById('toggle-original-text'),
  copyTransBtn: document.getElementById('copy-trans-btn'),
  manualTranslateBtn: document.getElementById('manual-translate-btn'),
  manualTranslateLabel: document.getElementById('manual-translate-label'),

  // Tuning Sliders
  speedSlider: document.getElementById('speed-slider'),
  speedVal: document.getElementById('speed-val'),
  pitchSlider: document.getElementById('pitch-slider'),
  pitchVal: document.getElementById('pitch-val'),
  volumeSlider: document.getElementById('volume-slider'),
  volumeVal: document.getElementById('volume-val'),
  resetTuningBtn: document.getElementById('reset-tuning-btn'),

  // Generation
  generateBtn: document.getElementById('generate-btn'),
  generateIcon: document.getElementById('generate-icon'),
  generateBtnText: document.getElementById('generate-btn-text'),

  // Voice Catalog
  voiceSearchInput: document.getElementById('voice-search-input'),
  langPills: document.querySelectorAll('.pill'),
  genderBtns: document.querySelectorAll('.gender-btn'),
  voiceCardsContainer: document.getElementById('voice-cards-container'),

  // Active Player
  activePlayerCard: document.getElementById('active-player-card'),
  playerLangBadge: document.getElementById('player-lang-badge'),
  playerTitle: document.getElementById('player-title'),
  playerVoiceName: document.getElementById('player-voice-name'),
  playerSpecs: document.getElementById('player-specs'),
  waveformCanvas: document.getElementById('waveform-canvas'),
  mainAudioElement: document.getElementById('main-audio-element'),
  playPauseBtn: document.getElementById('play-pause-btn'),
  playIcon: document.getElementById('play-icon'),
  currTime: document.getElementById('curr-time'),
  totalTime: document.getElementById('total-time'),
  scrubberTrack: document.getElementById('scrubber-track'),
  scrubberProgress: document.getElementById('scrubber-progress'),
  playerMuteBtn: document.getElementById('player-mute-btn'),
  muteIcon: document.getElementById('mute-icon'),
  downloadMp3Btn: document.getElementById('download-mp3-btn'),
  copyTextBtn: document.getElementById('copy-text-btn'),

  // Library
  historyTbody: document.getElementById('history-tbody'),
  librarySearch: document.getElementById('library-search'),
  libraryEmptyState: document.getElementById('library-empty-state'),

  // Analytics & Benchmark
  metricLatency: document.getElementById('metric-latency'),
  metricRtf: document.getElementById('metric-rtf'),
  metricSpeedup: document.getElementById('metric-speedup'),
  metricAudioSeconds: document.getElementById('metric-audio-seconds'),
  metricTotalGenerations: document.getElementById('metric-total-generations'),
  metricChars: document.getElementById('metric-chars'),
  benchmarkSamplesSelect: document.getElementById('benchmark-samples-select'),
  runBenchmarkBtn: document.getElementById('run-benchmark-btn'),
  benchmarkStatusBadge: document.getElementById('benchmark-status-badge'),
  benchmarkProgressBarWrap: document.getElementById('benchmark-progress-bar-wrap'),
  benchmarkProgressFill: document.getElementById('benchmark-progress-fill'),
  benchmarkSummaryStrip: document.getElementById('benchmark-summary-strip'),
  benchSampleCount: document.getElementById('bench-sample-count'),
  benchMeanLat: document.getElementById('bench-mean-lat'),
  benchRtf: document.getElementById('bench-rtf'),
  benchSpeedup: document.getElementById('bench-speedup'),
  benchThroughput: document.getElementById('bench-throughput'),
  benchmarkTbody: document.getElementById('benchmark-tbody'),

  // Preview Audio
  globalPreviewAudio: document.getElementById('global-preview-audio'),
  toastContainer: document.getElementById('toast-container'),
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupEditorListeners();
  setupTuningListeners();
  setupPlayerListeners();
  setupVoiceFilterListeners();
  setupLibraryListeners();
  setupAnalyticsListeners();

  // Load Initial Data
  await fetchVoices();
  await fetchHistory();
  await fetchAnalytics();

  // Set default prompt
  if (!elements.textInput.value) {
    elements.textInput.value = TEMPLATES.tech_explainer;
    updateTextStats();
  }

  // Refresh Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  initWaveformVisualizer();
});

/* ==================== NAVIGATION ==================== */
function setupNavigation() {
  elements.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetTab = tab.dataset.tab;
      state.activeTab = targetTab;

      elements.tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      elements.views.forEach(v => {
        v.classList.remove('active');
        if (v.id === `view-${targetTab}`) {
          v.classList.add('active');
        }
      });

      if (targetTab === 'library') {
        fetchHistory();
      } else if (targetTab === 'analytics') {
        fetchAnalytics();
      }

      if (window.lucide) lucide.createIcons();
    });
  });
}

/* ==================== SCRIPT EDITOR & TRANSLATION ==================== */
function setupEditorListeners() {
  elements.textInput.addEventListener('input', () => {
    updateTextStats();
    if (state.autoTranslate) {
      scheduleTranslation(550);
    }
  });

  elements.autoTranslateToggle.addEventListener('change', (e) => {
    state.autoTranslate = e.target.checked;
    if (state.autoTranslate) {
      elements.manualTranslateBtn.classList.add('hidden');
      scheduleTranslation(100);
      showToast('Auto-Translate enabled: script adapts to voice language.');
    } else {
      elements.manualTranslateBtn.classList.remove('hidden');
      updateManualTranslateLabel();
      elements.translationPreviewCard.classList.add('hidden');
      showToast('Auto-Translate paused. Manual translation button enabled.');
    }
  });

  elements.manualTranslateBtn.addEventListener('click', () => {
    triggerTranslation(true);
  });

  elements.toggleOriginalBtn.addEventListener('click', () => {
    state.useOriginal = !state.useOriginal;
    if (state.useOriginal) {
      elements.toggleOriginalBtn.classList.add('active');
      elements.toggleOriginalText.textContent = 'Using Original';
      elements.transText.style.opacity = '0.4';
      showToast('Synthesis set to use original input script.');
    } else {
      elements.toggleOriginalBtn.classList.remove('active');
      elements.toggleOriginalText.textContent = 'Use Original';
      elements.transText.style.opacity = '1.0';
      showToast('Synthesis set to use translated script.');
    }
  });

  elements.copyTransBtn.addEventListener('click', () => {
    const text = elements.transText.innerText.trim();
    if (text) {
      navigator.clipboard.writeText(text).then(() => {
        showToast('Translated script copied to clipboard!');
      });
    }
  });

  elements.transText.addEventListener('input', () => {
    if (state.activeTranslation) {
      state.activeTranslation.translated_text = elements.transText.innerText.trim();
    }
  });

  elements.clearTextBtn.addEventListener('click', () => {
    elements.textInput.value = '';
    updateTextStats();
    elements.translationPreviewCard.classList.add('hidden');
    state.activeTranslation = null;
    elements.detectedLangBadge.textContent = 'Auto-Detect';
    elements.detectedLangBadge.classList.remove('active-detect');
    elements.textInput.focus();
  });

  elements.templateDropdown.addEventListener('change', (e) => {
    const key = e.target.value;
    if (key && TEMPLATES[key]) {
      elements.textInput.value = TEMPLATES[key];
      updateTextStats();
      if (key === 'hindi_dialogue') {
        selectVoiceByLocale('hi-IN');
      } else if (state.autoTranslate) {
        scheduleTranslation(200);
      }
    }
    e.target.value = '';
  });

  // Shortcut Ctrl/Cmd + Enter to synthesize
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      if (state.activeTab === 'studio' && !state.isGenerating) {
        handleSynthesis();
      }
    }
  });

  elements.generateBtn.addEventListener('click', handleSynthesis);
}

function updateTextStats() {
  const text = elements.textInput.value;
  elements.charCount.textContent = text.length.toLocaleString();
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  elements.wordCount.textContent = words.toLocaleString();

  if (text.length > 5000) {
    elements.charCount.style.color = '#ff6b6b';
  } else {
    elements.charCount.style.color = '';
  }
}

/* ==================== ACOUSTIC TUNING ==================== */
function setupTuningListeners() {
  elements.speedSlider.addEventListener('input', (e) => {
    elements.speedVal.textContent = `${parseFloat(e.target.value).toFixed(2)}x`;
  });

  elements.pitchSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value, 10);
    elements.pitchVal.textContent = `${val >= 0 ? '+' : ''}${val} Hz`;
  });

  elements.volumeSlider.addEventListener('input', (e) => {
    elements.volumeVal.textContent = `${e.target.value}%`;
  });

  elements.resetTuningBtn.addEventListener('click', () => {
    elements.speedSlider.value = 1.0;
    elements.speedVal.textContent = '1.0x';
    elements.pitchSlider.value = 0;
    elements.pitchVal.textContent = '0 Hz';
    elements.volumeSlider.value = 100;
    elements.volumeVal.textContent = '100%';
    showToast('Acoustic parameters reset to studio defaults.');
  });
}

/* ==================== VOICE CATALOG ==================== */
async function fetchVoices() {
  try {
    const res = await fetch('/api/voices');
    if (!res.ok) throw new Error('Failed to load voice catalog');
    state.voices = await res.json();

    // Default select Jenny (US Female)
    const defaultVoice = state.voices.find(v => v.id === 'en-US-JennyNeural') || state.voices[0];
    if (defaultVoice) {
      state.selectedVoice = defaultVoice;
    }

    renderVoiceCards();
  } catch (err) {
    console.error(err);
    elements.voiceCardsContainer.innerHTML = `
      <div class="empty-state">
        <i data-lucide="alert-triangle"></i>
        <h3>Failed to load voices</h3>
        <p>Ensure backend server is running.</p>
      </div>`;
    if (window.lucide) lucide.createIcons();
  }
}

function setupVoiceFilterListeners() {
  // Search
  elements.voiceSearchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    renderVoiceCards();
  });

  // Language pills
  elements.langPills.forEach(pill => {
    pill.addEventListener('click', () => {
      elements.langPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeFilterLang = pill.dataset.lang;
      renderVoiceCards();
    });
  });

  // Gender toggle
  elements.genderBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.genderBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeFilterGender = btn.dataset.gender;
      renderVoiceCards();
    });
  });
}

function renderVoiceCards() {
  const filtered = state.voices.filter(v => {
    // Language check
    if (state.activeFilterLang !== 'all') {
      if (!v.language.toLowerCase().includes(state.activeFilterLang.toLowerCase())) {
        return false;
      }
    }
    // Gender check
    if (state.activeFilterGender !== 'all') {
      if (v.gender.toLowerCase() !== state.activeFilterGender.toLowerCase()) {
        return false;
      }
    }
    // Search query
    if (state.searchQuery) {
      const q = state.searchQuery;
      const haystack = `${v.name} ${v.language} ${v.country} ${v.id}`.toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    elements.voiceCardsContainer.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <i data-lucide="filter"></i>
        <p>No voices match current filters.</p>
      </div>`;
    if (window.lucide) lucide.createIcons();
    return;
  }

  elements.voiceCardsContainer.innerHTML = filtered.map(v => {
    const isSelected = state.selectedVoice && state.selectedVoice.id === v.id;
    const isPlayingPreview = state.currentlyPlayingPreviewId === v.id;
    const genderClass = v.gender.toLowerCase() === 'female' ? 'female' : 'male';

    return `
      <div class="voice-card ${isSelected ? 'selected' : ''}" data-id="${v.id}">
        <div class="card-left">
          <div class="card-flag">${v.flag || '🌐'}</div>
          <div class="card-meta">
            <div class="card-name">${v.name}</div>
            <div class="card-sub">
              <span>${v.language}</span>
              <span class="gender-tag ${genderClass}">${v.gender}</span>
            </div>
          </div>
        </div>
        <button class="card-preview-btn ${isPlayingPreview ? 'playing' : ''}" data-id="${v.id}" title="Preview Voice (3s)">
          <i data-lucide="${isPlayingPreview ? 'square' : 'play'}"></i>
        </button>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();

  // Attach card click handlers
  elements.voiceCardsContainer.querySelectorAll('.voice-card').forEach(card => {
    card.addEventListener('click', (e) => {
      // If clicking preview button, handle preview only
      if (e.target.closest('.card-preview-btn')) return;

      const voiceId = card.dataset.id;
      const voice = state.voices.find(v => v.id === voiceId);
      if (voice) {
        state.selectedVoice = voice;
        elements.voiceCardsContainer.querySelectorAll('.voice-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        // Update player badge
        elements.playerLangBadge.textContent = `${voice.flag} ${voice.language} (${voice.country})`;
        elements.playerVoiceName.textContent = `${voice.name} (${voice.gender})`;
        updateManualTranslateLabel();

        // Trigger auto-translation if enabled
        if (state.autoTranslate) {
          scheduleTranslation(200);
        }
      }
    });
  });

  // Attach preview button click handlers
  elements.voiceCardsContainer.querySelectorAll('.card-preview-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const voiceId = btn.dataset.id;
      toggleVoicePreview(voiceId);
    });
  });
}

function selectVoiceByLocale(localePrefix) {
  const match = state.voices.find(v => v.locale.startsWith(localePrefix));
  if (match) {
    state.selectedVoice = match;
    renderVoiceCards();
    elements.playerLangBadge.textContent = `${match.flag} ${match.language} (${match.country})`;
    elements.playerVoiceName.textContent = `${match.name} (${match.gender})`;
  }
}

async function toggleVoicePreview(voiceId) {
  if (state.currentlyPlayingPreviewId === voiceId) {
    // Stop playback
    elements.globalPreviewAudio.pause();
    state.currentlyPlayingPreviewId = null;
    renderVoiceCards();
    return;
  }

  try {
    state.currentlyPlayingPreviewId = voiceId;
    renderVoiceCards();

    elements.globalPreviewAudio.src = `/api/preview/${voiceId}`;
    await elements.globalPreviewAudio.play();

    elements.globalPreviewAudio.onended = () => {
      state.currentlyPlayingPreviewId = null;
      renderVoiceCards();
    };

    elements.globalPreviewAudio.onerror = () => {
      state.currentlyPlayingPreviewId = null;
      renderVoiceCards();
      showToast('Could not load voice preview audio.', 'error');
    };
  } catch (err) {
    console.error(err);
    state.currentlyPlayingPreviewId = null;
    renderVoiceCards();
  }
}

/* ==================== TRANSLATION PIPELINE ==================== */
function updateManualTranslateLabel() {
  if (state.selectedVoice) {
    elements.manualTranslateLabel.textContent = `Translate to ${state.selectedVoice.language} ${state.selectedVoice.flag}`;
  }
}

function scheduleTranslation(delay = 450) {
  clearTimeout(state.transDebounceTimer);
  state.transDebounceTimer = setTimeout(() => {
    triggerTranslation();
  }, delay);
}

async function triggerTranslation(force = false) {
  const text = elements.textInput.value.trim();
  if (!text) {
    elements.translationPreviewCard.classList.add('hidden');
    state.activeTranslation = null;
    return;
  }
  if (!state.selectedVoice) return;

  const targetLang = state.selectedVoice.language;

  // Show card and loading state
  elements.translationPreviewCard.classList.remove('hidden');
  elements.transLoadingOverlay.classList.remove('hidden');

  try {
    const res = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        target_lang: targetLang
      })
    });

    if (!res.ok) throw new Error('Translation failed');
    const data = await res.json();
    state.activeTranslation = data;

    elements.transTargetLabel.textContent = `${state.selectedVoice.flag} ${data.target_lang_name.toUpperCase()} · AUTO-TRANSLATED`;
    elements.transPipelineTag.textContent = data.pipeline.length > 0 ? data.pipeline.join(' • ') : 'Direct Voice Matching';
    elements.transText.innerText = data.translated_text;

    elements.detectedLangBadge.textContent = `${data.source_lang_name}`;
    elements.detectedLangBadge.classList.add('active-detect');

    state.useOriginal = false;
    elements.toggleOriginalBtn.classList.remove('active');
    elements.toggleOriginalText.textContent = 'Use Original';
    elements.transText.style.opacity = '1.0';

  } catch (err) {
    console.error('Translation error:', err);
    elements.transTargetLabel.textContent = 'Translation Notice';
    elements.transPipelineTag.textContent = 'Using original text';
    elements.transText.innerText = text;
  } finally {
    elements.transLoadingOverlay.classList.add('hidden');
  }
}

/* ==================== SPEECH SYNTHESIS ==================== */
async function handleSynthesis() {
  const rawText = elements.textInput.value.trim();
  if (!rawText) {
    showToast('Please enter text to synthesize.', 'error');
    elements.textInput.focus();
    return;
  }

  if (!state.selectedVoice) {
    showToast('Please select a voice from the catalog.', 'error');
    return;
  }

  // Determine text to synthesize (translated or original)
  let textToSynthesize = rawText;
  let isTranslated = false;
  if (state.activeTranslation && !state.useOriginal) {
    const customTrans = elements.transText.innerText.trim();
    if (customTrans) {
      textToSynthesize = customTrans;
      isTranslated = true;
    }
  }

  setGeneratingState(true);

  const payload = {
    text: textToSynthesize,
    voice_id: state.selectedVoice.id,
    speed: parseFloat(elements.speedSlider.value),
    pitch: parseInt(elements.pitchSlider.value, 10),
    volume: parseInt(elements.volumeSlider.value, 10),
  };

  const startTime = performance.now();

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Synthesis failed');
    }

    const data = await res.json();
    state.currentAudio = data;

    // Load into player workstation
    loadAudioIntoPlayer(data);

    // Update library count and telemetry
    fetchHistory();
    fetchAnalytics();

    const clientLatency = Math.round(performance.now() - startTime);
    const rtf = (data.latency_ms / 1000.0) / data.duration_seconds;
    showToast(`Synthesized ${isTranslated ? 'translated speech' : 'speech'} in ${data.latency_ms} ms (RTF: ${rtf.toFixed(2)}x)!`, 'success');

  } catch (err) {
    console.error(err);
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    setGeneratingState(false);
  }
}

function setGeneratingState(isBusy) {
  state.isGenerating = isBusy;
  elements.generateBtn.disabled = isBusy;
  if (isBusy) {
    elements.generateIcon.setAttribute('data-lucide', 'loader-2');
    elements.generateIcon.classList.add('spinner');
    elements.generateBtnText.textContent = 'Synthesizing Audio...';
  } else {
    elements.generateIcon.setAttribute('data-lucide', 'sparkles');
    elements.generateIcon.classList.remove('spinner');
    elements.generateBtnText.textContent = 'Synthesize Speech';
  }
  if (window.lucide) lucide.createIcons();
}

/* ==================== WORKSTATION AUDIO PLAYER ==================== */
function setupPlayerListeners() {
  const audio = elements.mainAudioElement;

  elements.playPauseBtn.addEventListener('click', () => {
    if (!audio.src) return;
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  });

  audio.addEventListener('play', () => {
    elements.playIcon.setAttribute('data-lucide', 'pause');
    if (window.lucide) lucide.createIcons();
  });

  audio.addEventListener('pause', () => {
    elements.playIcon.setAttribute('data-lucide', 'play');
    if (window.lucide) lucide.createIcons();
  });

  audio.addEventListener('timeupdate', () => {
    if (!audio.duration) return;
    elements.currTime.textContent = formatTime(audio.currentTime);
    const pct = (audio.currentTime / audio.duration) * 100;
    elements.scrubberProgress.style.width = `${pct}%`;
  });

  audio.addEventListener('loadedmetadata', () => {
    elements.totalTime.textContent = formatTime(audio.duration);
    elements.playPauseBtn.disabled = false;
    elements.downloadMp3Btn.disabled = false;
  });

  audio.addEventListener('ended', () => {
    elements.playIcon.setAttribute('data-lucide', 'play');
    elements.scrubberProgress.style.width = '0%';
    if (window.lucide) lucide.createIcons();
  });

  // Scrubber click to seek
  elements.scrubberTrack.addEventListener('click', (e) => {
    if (!audio.duration) return;
    const rect = elements.scrubberTrack.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const seekTime = (clickX / width) * audio.duration;
    audio.currentTime = seekTime;
  });

  // Mute toggle
  elements.playerMuteBtn.addEventListener('click', () => {
    audio.muted = !audio.muted;
    if (audio.muted) {
      elements.muteIcon.setAttribute('data-lucide', 'volume-x');
    } else {
      elements.muteIcon.setAttribute('data-lucide', 'volume-2');
    }
    if (window.lucide) lucide.createIcons();
  });

  // Download MP3
  elements.downloadMp3Btn.addEventListener('click', () => {
    if (!state.currentAudio || !state.currentAudio.audio_url) return;
    const a = document.createElement('a');
    a.href = state.currentAudio.audio_url;
    a.download = `VOX_${state.currentAudio.voice_name}_${Date.now()}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('Downloading MP3 audio file...');
  });

  // Copy Text
  elements.copyTextBtn.addEventListener('click', () => {
    if (!state.currentAudio || !state.currentAudio.text) return;
    navigator.clipboard.writeText(state.currentAudio.text).then(() => {
      showToast('Script copied to clipboard!');
    });
  });
}

function loadAudioIntoPlayer(item, autoPlay = true) {
  state.currentAudio = item;
  elements.playerTitle.textContent = item.text.length > 55 ? item.text.substring(0, 52) + '...' : item.text;
  elements.playerVoiceName.textContent = `${item.voice_name} (${item.gender})`;
  elements.playerSpecs.textContent = `${item.latency_ms || item.duration_seconds} ms latency • ${formatBytes(item.file_size_bytes)}`;
  elements.playerLangBadge.textContent = `${item.language}`;

  elements.mainAudioElement.src = item.audio_url;
  elements.playPauseBtn.disabled = false;
  elements.downloadMp3Btn.disabled = false;

  if (autoPlay) {
    elements.mainAudioElement.play().catch(e => console.warn('Auto-play blocked by browser policy:', e));
  }
}

function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function formatBytes(bytes) {
  if (!bytes) return '0 KB';
  return `${(bytes / 1024).toFixed(1)} KB`;
}

/* ==================== WAVEFORM VISUALIZER ==================== */
function initWaveformVisualizer() {
  const canvas = elements.waveformCanvas;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const audio = elements.mainAudioElement;

  function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  const barCount = 64;

  function renderWaveform() {
    requestAnimationFrame(renderWaveform);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const isPlaying = !audio.paused && !audio.ended && audio.currentTime > 0;
    const progressPct = audio.duration ? (audio.currentTime / audio.duration) : 0;
    const activeBarIndex = Math.floor(progressPct * barCount);

    const barWidth = (canvas.width / barCount) - 2;

    for (let i = 0; i < barCount; i++) {
      let heightMultiplier;
      if (isPlaying) {
        // Dynamic simulated wave frequencies
        const freq = Math.sin((i * 0.2) + (performance.now() * 0.008)) * 0.4 + 0.6;
        heightMultiplier = freq * (0.3 + 0.7 * Math.sin(i * 0.15));
      } else {
        // Static ambient waveform preview
        heightMultiplier = 0.25 + 0.5 * Math.sin(i * 0.2);
      }

      const barHeight = Math.max(6, heightMultiplier * (canvas.height * 0.8));
      const x = i * (barWidth + 2);
      const y = (canvas.height - barHeight) / 2;

      // Color active bars with lime accent, remaining with dark slate
      if (i <= activeBarIndex && audio.currentTime > 0) {
        ctx.fillStyle = '#d5ff63';
      } else {
        ctx.fillStyle = '#222938';
      }

      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, 2);
      ctx.fill();
    }
  }

  renderWaveform();
}

/* ==================== LIBRARY (GENERATION HISTORY) ==================== */
function setupLibraryListeners() {
  elements.librarySearch.addEventListener('input', () => {
    renderHistoryTable();
  });
}

async function fetchHistory() {
  try {
    const res = await fetch('/api/history?limit=100');
    if (!res.ok) throw new Error('Failed to fetch history');
    state.history = await res.json();

    elements.libraryCountBadge.textContent = state.history.length;
    renderHistoryTable();
  } catch (err) {
    console.error(err);
  }
}

function renderHistoryTable() {
  const query = elements.librarySearch.value.toLowerCase().trim();
  const filtered = state.history.filter(item => {
    if (!query) return true;
    return `${item.text} ${item.voice_name} ${item.language} ${item.gender}`.toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    elements.historyTbody.innerHTML = '';
    elements.libraryEmptyState.classList.remove('hidden');
    return;
  }

  elements.libraryEmptyState.classList.add('hidden');

  elements.historyTbody.innerHTML = filtered.map(item => {
    const createdStr = item.created_at ? new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--';
    const genderClass = item.gender.toLowerCase() === 'female' ? 'female' : 'male';

    return `
      <tr data-id="${item.id}">
        <td>
          <button class="action-icon-btn history-play-btn" data-id="${item.id}" title="Play in Workstation">
            <i data-lucide="play"></i>
          </button>
        </td>
        <td>
          <div class="transcript-cell" title="${escapeHtml(item.text)}">${escapeHtml(item.text)}</div>
        </td>
        <td><strong>${item.voice_name}</strong></td>
        <td>${item.language}</td>
        <td><span class="gender-tag ${genderClass}">${item.gender}</span></td>
        <td><code>${item.duration_seconds.toFixed(1)}s</code></td>
        <td><code>${createdStr}</code></td>
        <td>
          <div class="table-actions">
            <a href="${item.audio_url}" download="VOX_${item.voice_name}_${item.id}.mp3" class="action-icon-btn" title="Download Audio">
              <i data-lucide="download"></i>
            </a>
            <button class="action-icon-btn danger history-del-btn" data-id="${item.id}" title="Delete Record">
              <i data-lucide="trash-2"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();

  // Attach Play & Delete handlers
  elements.historyTbody.querySelectorAll('.history-play-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      const item = state.history.find(h => h.id === id);
      if (item) {
        // Switch to Studio tab and load audio
        elements.tabs[0].click();
        loadAudioIntoPlayer(item, true);
        showToast(`Loaded "${item.voice_name}" audio into player.`);
      }
    });
  });

  elements.historyTbody.querySelectorAll('.history-del-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      if (!confirm('Are you sure you want to delete this audio clip?')) return;
      try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        if (res.ok) {
          showToast('Audio clip deleted.');
          fetchHistory();
          fetchAnalytics();
        }
      } catch (err) {
        console.error(err);
      }
    });
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ==================== ANALYTICS & BENCHMARKS ==================== */
function setupAnalyticsListeners() {
  elements.runBenchmarkBtn.addEventListener('click', handleRunBenchmark);
}

async function fetchAnalytics() {
  try {
    const res = await fetch('/api/analytics');
    if (!res.ok) return;
    const data = await res.json();

    elements.metricLatency.textContent = `${data.mean_latency_ms.toFixed(1)} ms`;
    elements.metricRtf.textContent = `${data.mean_rtf.toFixed(3)}x`;
    elements.metricSpeedup.textContent = `${data.realtime_speedup.toFixed(1)}x faster than real-time`;
    elements.metricAudioSeconds.textContent = `${data.total_audio_seconds.toFixed(1)} s`;
    elements.metricTotalGenerations.textContent = `${data.total_generations} sessions recorded`;
    elements.metricChars.textContent = data.total_characters_processed.toLocaleString();
  } catch (err) {
    console.error(err);
  }
}

async function handleRunBenchmark() {
  const sampleCount = parseInt(elements.benchmarkSamplesSelect.value, 10) || 10;

  elements.runBenchmarkBtn.disabled = true;
  elements.benchmarkStatusBadge.innerHTML = `<span class="status-chip running">Running ${sampleCount} Model Evaluations...</span>`;
  elements.benchmarkProgressBarWrap.classList.remove('hidden');
  elements.benchmarkProgressFill.style.width = '20%';

  // Animate progress simulation
  let progress = 20;
  const interval = setInterval(() => {
    if (progress < 85) {
      progress += 5;
      elements.benchmarkProgressFill.style.width = `${progress}%`;
    }
  }, 400);

  try {
    const res = await fetch(`/api/benchmark?sample_count=${sampleCount}`, {
      method: 'POST'
    });

    clearInterval(interval);
    elements.benchmarkProgressFill.style.width = '100%';

    if (!res.ok) throw new Error('Benchmark run failed');
    const data = await res.json();

    // Populate summary strip
    elements.benchmarkSummaryStrip.classList.remove('hidden');
    elements.benchSampleCount.textContent = `${data.sample_count} Prompts`;
    elements.benchMeanLat.textContent = `${data.mean_latency_ms} ms`;
    elements.benchRtf.textContent = `${data.global_rtf}x`;
    elements.benchSpeedup.textContent = `${data.realtime_speedup}x RT`;
    elements.benchThroughput.textContent = `${data.character_throughput_per_sec} char/s`;

    // Populate benchmark table
    elements.benchmarkTbody.innerHTML = data.samples.map(s => `
      <tr>
        <td><code>${s.id}</code></td>
        <td class="transcript-cell" title="${escapeHtml(s.text)}">${escapeHtml(s.text)}</td>
        <td><strong>${s.language}</strong></td>
        <td><code>${s.voice}</code></td>
        <td><code>${s.duration_seconds.toFixed(2)}s</code></td>
        <td><code>${s.latency_ms.toFixed(0)} ms</code></td>
        <td><strong style="color: var(--accent);">${s.rtf}x</strong></td>
        <td><span class="gender-tag male">${s.speedup}x</span></td>
      </tr>
    `).join('');

    elements.benchmarkStatusBadge.innerHTML = `<span class="status-chip ready">Sweep Completed (100% Success)</span>`;
    showToast(`Benchmark completed across ${data.sample_count} prompts (RTF: ${data.global_rtf}x)!`, 'success');

    // Update global platform metrics
    fetchAnalytics();

  } catch (err) {
    clearInterval(interval);
    console.error(err);
    elements.benchmarkStatusBadge.innerHTML = `<span class="status-chip" style="color: #ff6b6b;">Benchmark Failed</span>`;
    showToast(`Benchmark failed: ${err.message}`, 'error');
  } finally {
    elements.runBenchmarkBtn.disabled = false;
    setTimeout(() => {
      elements.benchmarkProgressBarWrap.classList.add('hidden');
      elements.benchmarkProgressFill.style.width = '0%';
    }, 1200);
  }
}

/* ==================== TOAST NOTIFICATIONS ==================== */
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const iconName = type === 'success' ? 'check-circle' : 'alert-circle';
  toast.innerHTML = `
    <i data-lucide="${iconName}"></i>
    <span>${message}</span>
  `;

  elements.toastContainer.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
