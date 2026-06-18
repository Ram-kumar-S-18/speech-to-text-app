(function () {
  'use strict';

  // --- Custom Select Dropdown for Microphone ---
  const micTrigger = document.getElementById('mic-trigger');
  const micOptionsContainer = document.getElementById('mic-options');
  const micHiddenInput = document.getElementById('mic-select');
  const micTriggerText = document.getElementById('mic-trigger-text');
  const micBtn = document.getElementById('mic');
  const themeBtn = document.getElementById('theme');
  const copyBtn = document.getElementById('btn-copy');
  const clearBtn = document.getElementById('btn-clear');
  const statusBadge = document.getElementById('stat');
  const textBox = document.getElementById('box');
  const timeLabel = document.getElementById('time');
  const correctCheck = document.getElementById('correct-check');

  micTrigger.addEventListener('click', (e) => {
    e.stopPropagation();
    micTrigger.classList.toggle('active');
    micOptionsContainer.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    micTrigger.classList.remove('active');
    micOptionsContainer.classList.remove('show');
  });

  // Device Enumeration
  let selectedMicId = '';
  async function updateMicList() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
        micTriggerText.textContent = 'Mic access not supported';
        return;
      }
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioDevices = devices.filter(device => device.kind === 'audioinput');
      
      micOptionsContainer.innerHTML = '';
      
      if (audioDevices.length === 0) {
        micTriggerText.textContent = 'No microphone found';
        return;
      }
      
      audioDevices.forEach((device, index) => {
        const option = document.createElement('div');
        option.className = 'select-option';
        option.textContent = device.label || `Microphone ${index + 1}`;
        option.setAttribute('data-value', device.deviceId);
        
        if (index === 0 && !selectedMicId) {
          selectedMicId = device.deviceId;
          micTriggerText.textContent = option.textContent;
          micHiddenInput.value = device.deviceId;
          option.classList.add('selected');
        } else if (device.deviceId === selectedMicId) {
          option.classList.add('selected');
        }
        
        option.addEventListener('click', (e) => {
          e.stopPropagation();
          document.querySelectorAll('#mic-options .select-option').forEach(o => o.classList.remove('selected'));
          option.classList.add('selected');
          selectedMicId = device.deviceId;
          micTriggerText.textContent = option.textContent;
          micHiddenInput.value = device.deviceId;
          micTrigger.classList.remove('active');
          micOptionsContainer.classList.remove('show');
        });
        
        micOptionsContainer.appendChild(option);
      });
    } catch (e) {
      console.error('Error listing microphones:', e);
    }
  }

  // Request permission on start, then list devices
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        stream.getTracks().forEach(t => t.stop());
        updateMicList();
      })
      .catch(e => {
        console.error('Mic permission denied on start:', e);
        updateMicList();
      });
  } else {
    console.warn('Mic access not supported in this browser context.');
    updateMicList();
  }

  // --- Theme ---
  let isDark = true;
  function safeSetStorage(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
  }
  function safeGetStorage(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }
  function toggleTheme() {
    isDark = !isDark;
    document.body.classList.toggle('light', !isDark);
    themeBtn.innerHTML = isDark ? '<i class="ri-moon-line"></i>' : '<i class="ri-sun-line"></i>';
    safeSetStorage('theme', isDark ? 'dark' : 'light');
  }
  themeBtn.addEventListener('click', toggleTheme);

  if (safeGetStorage('theme') === 'light') {
    isDark = false;
    document.body.classList.add('light');
    themeBtn.innerHTML = '<i class="ri-sun-line"></i>';
  }

  // --- Premium Wave Visualizer ---
  const viz = document.getElementById('viz');
  const vctx = viz.getContext('2d');
  let animId = null, audioCtx = null, analyser = null, src = null, dataArr = null;
  let idleTime = 0, prevWave = null, smoothAmp = 0;
  let isAnimating = false;

  function resizeViz() {
    const r = viz.getBoundingClientRect();
    viz.width = r.width * devicePixelRatio;
    viz.height = r.height * devicePixelRatio;
    vctx.scale(devicePixelRatio, devicePixelRatio);
    if (!isAnimating) {
      drawCenterline();
    }
  }
  resizeViz();
  window.addEventListener('resize', resizeViz);

  function drawCenterline() {
    const w = viz.width / devicePixelRatio, h = viz.height / devicePixelRatio;
    vctx.clearRect(0, 0, w, h);
    vctx.fillStyle = 'rgba(100, 110, 140, .08)';
    vctx.fillRect(0, h / 2 - 1, w, 2);
  }

  function startAnimating() {
    if (!isAnimating) {
      isAnimating = true;
      tick();
    }
  }

  function startViz(stream) {
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      src = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = .92;
      src.connect(analyser);
      dataArr = new Uint8Array(analyser.frequencyBinCount);
      prevWave = null;
      smoothAmp = 0;
      idleTime = 0;
      startAnimating();
    } catch (e) {
      console.error('Failed to start visualizer:', e);
    }
  }

  function buildWave(data, len, h) {
    const pts = [];
    for (let i = 0; i < len; i++) {
      const t = i / (len - 1);
      const idx = Math.floor(t * (data.length - 1));
      const v = (data[idx] - 128) / 128;
      const y = h / 2 + v * (h * .38);
      pts.push(y);
    }
    return pts;
  }

  function drawFluidWave(w, h, pts, alpha, gradStops, shadow) {
    if (!pts || pts.length < 2) return;
    const len = pts.length;
    
    // ambient occlusion base
    const gradBg = vctx.createLinearGradient(0, 0, 0, h);
    gradBg.addColorStop(0, 'rgba(0,0,0,0)');
    gradBg.addColorStop(.4, 'rgba(0,0,0,.25)');
    gradBg.addColorStop(.6, 'rgba(0,0,0,.25)');
    gradBg.addColorStop(1, 'rgba(0,0,0,0)');
    vctx.fillStyle = gradBg;
    vctx.fillRect(0, 0, w, h);
    
    // horizontal gradient fill
    const grad = vctx.createLinearGradient(0, 0, w, 0);
    for (const [stop, color] of gradStops) {
      grad.addColorStop(stop, color);
    }
    
    // glow layer
    if (shadow) {
      vctx.save();
      vctx.shadowColor = shadow;
      vctx.shadowBlur = 24;
      vctx.beginPath();
      vctx.moveTo(0, h / 2);
      for (let i = 0; i < len; i++) {
        const x = i / (len - 1) * w;
        vctx.lineTo(x, pts[i]);
      }
      vctx.lineTo(w, h / 2);
      vctx.closePath();
      vctx.fillStyle = grad;
      vctx.globalAlpha = alpha * .35;
      vctx.fill();
      vctx.restore();
    }
    
    // main wave fill
    vctx.beginPath();
    vctx.moveTo(0, h / 2);
    for (let i = 0; i < len; i++) {
      const x = i / (len - 1) * w;
      vctx.lineTo(x, pts[i]);
    }
    vctx.lineTo(w, h / 2);
    vctx.closePath();
    vctx.fillStyle = grad;
    vctx.globalAlpha = alpha;
    vctx.fill();
    
    // top stroke for definition
    vctx.beginPath();
    for (let i = 0; i < len; i++) {
      const x = i / (len - 1) * w;
      if (i === 0) vctx.moveTo(x, pts[i]);
      else {
        const cp1x = (i - 0.5) / (len - 1) * w;
        const cp1y = (pts[i - 1] + pts[i]) / 2;
        vctx.quadraticCurveTo(cp1x, cp1y, x, pts[i]);
      }
    }
    vctx.strokeStyle = grad;
    vctx.lineWidth = 2.5;
    vctx.globalAlpha = alpha * .9;
    vctx.shadowColor = shadow || 'transparent';
    vctx.shadowBlur = shadow ? 18 : 0;
    vctx.stroke();
    vctx.shadowBlur = 0;
  }

  function generateIdleWave(len, h) {
    const wave = [];
    for (let i = 0; i < len; i++) {
      const t = i / (len - 1);
      const phase = idleTime * 1.2 + t * Math.PI * 4;
      const amp = .04 + Math.sin(idleTime * .5) * .02;
      wave.push(h / 2 + Math.sin(phase) * h * amp);
    }
    return wave;
  }

  function lerpWave(prev, curr, t) {
    if (!prev || prev.length !== curr.length) return curr;
    const eased = 1 - Math.pow(1 - t, 3);
    return curr.map((v, i) => prev[i] + (v - prev[i]) * eased);
  }

  function tick() {
    animId = requestAnimationFrame(tick);
    const w = viz.width / devicePixelRatio, h = viz.height / devicePixelRatio;
    const steps = 120;
    let wave, active = false, amp = 0;
    
    if (analyser && dataArr) {
      analyser.getByteTimeDomainData(dataArr);
      let sum = 0;
      for (let i = 0; i < dataArr.length; i++) {
        let v = (dataArr[i] - 128) / 128;
        sum += v * v;
      }
      amp = Math.sqrt(sum / dataArr.length);
      active = amp > .03;
      if (active || prevWave) {
        const raw = buildWave(dataArr, steps, h);
        wave = lerpWave(prevWave, raw, .25);
        prevWave = wave;
      } else {
        idleTime += .016;
        wave = generateIdleWave(steps, h);
        prevWave = null;
      }
    } else {
      idleTime += .016;
      wave = generateIdleWave(steps, h);
      prevWave = null;
    }
    
    smoothAmp += ((active ? Math.min(amp * 3, 1) : 0) - smoothAmp) * .12;
    const alpha = .18 + smoothAmp * .65;
    
    vctx.clearRect(0, 0, w, h);
    vctx.shadowBlur = 0;
    
    const stops = [
      [[0, 'rgba(0, 242, 254, 1)'], [.5, 'rgba(255, 0, 110, 1)'], [1, 'rgba(108, 0, 255, 1)']],
      [[0, 'rgba(0, 242, 254, .4)'], [.5, 'rgba(255, 0, 110, .4)'], [1, 'rgba(108, 0, 255, .4)']],
    ];
    
    drawFluidWave(w, h, wave, alpha, stops[0], active ? 'rgba(0, 242, 254, .4)' : null);
    
    const wave2 = wave.map(y => y + (Math.sin(idleTime * 2) * 2));
    drawFluidWave(w, h, wave2, alpha * .25, stops[1], null);
    
    // Check if we should stop the animation frame loop
    const isRecordingActive = !!analyser;
    const isSlightlyActive = smoothAmp > 0.005;
    
    if (!isRecordingActive && !isSlightlyActive) {
      isAnimating = false;
      cancelAnimationFrame(animId);
      animId = null;
      drawCenterline();
    }
  }

  function stopViz() {
    if (animId) {
      cancelAnimationFrame(animId);
      animId = null;
    }
    if (audioCtx) {
      audioCtx.close().catch(() => {});
      audioCtx = null;
      analyser = null;
      src = null;
      dataArr = null;
    }
    prevWave = null;
    smoothAmp = 0;
    isAnimating = false;
    drawCenterline();
  }

  // --- Recording Logic ---
  let mr = null, chunks = [], rec = false;
  async function toggle() {
    const r1 = document.getElementById('r1');
    const r2 = document.getElementById('r2');
    const r3 = document.getElementById('r3');
    
    if (!rec) {
      try {
        const constraints = { audio: { echoCancellation: true, noiseSuppression: true } };
        if (selectedMicId) {
          constraints.audio.deviceId = { exact: selectedMicId };
        }
        const st = await navigator.mediaDevices.getUserMedia(constraints);
        const mt = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
        
        mr = new MediaRecorder(st, { mimeType: mt });
        chunks = [];
        startViz(st);
        
        mr.ondataavailable = e => chunks.push(e.data);
        mr.onstop = async () => {
          st.getTracks().forEach(t => t.stop());
          stopViz();
          
          const blob = new Blob(chunks, { type: mr.mimeType });
          if (blob.size < 1000) {
            statusBadge.textContent = 'Audio too short, try again.';
            micBtn.classList.remove('rec');
            r1.classList.remove('active');
            r2.classList.remove('active');
            r3.classList.remove('active');
            rec = false;
            return;
          }
          
          document.getElementById('sp').classList.add('on');
          statusBadge.textContent = 'Transcribing...';
          micBtn.disabled = true;
          
          const reader = new FileReader();
          reader.onloadend = async () => {
            const b64 = reader.result.split(',')[1];
            const t0 = performance.now();
            try {
              const modelVal = document.getElementById('model-select').value;
              const correctVal = correctCheck.checked;
              
              const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
              const fetchUrl = isLocal ? '/x' : 'https://speech-to-text-app-5kuv.onrender.com/x';
              
              const resp = await fetch(fetchUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ a: b64, model: modelVal, correct: correctVal })
              });
              const d = await resp.json();
              const dt = ((performance.now() - t0) / 1000).toFixed(1);
              if (d.ok) {
                textBox.value = d.text;
                textBox.readOnly = false;
                statusBadge.textContent = 'Done';
                timeLabel.textContent = 'Transcribed in ' + dt + 's';
              } else {
                statusBadge.textContent = 'Error: ' + (d.error || 'unknown');
                timeLabel.textContent = '';
              }
            } catch (e) {
              statusBadge.textContent = 'Error: ' + e.message;
              timeLabel.textContent = '';
            } finally {
              document.getElementById('sp').classList.remove('on');
              micBtn.disabled = false;
              micBtn.classList.remove('rec');
              r1.classList.remove('active');
              r2.classList.remove('active');
              r3.classList.remove('active');
            }
          };
          reader.readAsDataURL(blob);
        };
        
        mr.start();
        rec = true;
        micBtn.classList.add('rec');
        r1.classList.add('active');
        r2.classList.add('active');
        r3.classList.add('active');
        statusBadge.textContent = 'Recording...';
      } catch (e) {
        statusBadge.textContent = 'Mic access: ' + e.message;
      }
    } else {
      if (mr && mr.state !== 'inactive') {
        mr.stop();
      }
      rec = false;
    }
  }

  micBtn.addEventListener('click', toggle);

  copyBtn.addEventListener('click', () => {
    if (!textBox.value) return;
    navigator.clipboard.writeText(textBox.value);
    statusBadge.textContent = 'Copied';
    setTimeout(() => {
      statusBadge.textContent = 'Ready';
    }, 2000);
  });

  clearBtn.addEventListener('click', () => {
    textBox.value = '';
    textBox.readOnly = true;
    timeLabel.textContent = '';
    drawCenterline();
  });

  // Render initial idle visualizer centerline
  drawCenterline();

})();
