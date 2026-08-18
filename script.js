const CONFIG = {
  to: "我最喜欢的你",
  from: "你的松松子",
  message:
    "如果喜欢可以被量化，那我对你的心动一定持续超频。想把每个普通日子，都升级成和你有关的限定版本。七夕快乐，你永远是我唯一置顶、无限续航的心动信号。",
};

const app = document.querySelector("#app");
const launchButton = document.querySelector("#launch-button");
const roseWrap = document.querySelector("#rose-wrap");
const soundToggle = document.querySelector("#sound-toggle");
const systemStateText = document.querySelector("#system-state-text");
const corePercent = document.querySelector("#core-percent");
const loveMessage = document.querySelector("#love-message");
const toName = document.querySelector("#to-name");
const fromName = document.querySelector("#from-name");
const clickHint = document.querySelector("#click-hint");
const suitLabel = document.querySelector(".suit-label");
const soundtrack = document.querySelector("#qixi-soundtrack");
const canvas = document.querySelector("#particle-canvas");
const ctx = canvas.getContext("2d");

const query = new URLSearchParams(window.location.search);
const content = {
  to: query.get("to")?.trim() || CONFIG.to,
  from: query.get("from")?.trim() || CONFIG.from,
  message: query.get("msg")?.trim() || CONFIG.message,
};

toName.textContent = content.to;
fromName.textContent = content.from;

let isActive = false;
let soundEnabled = false;
let audioContext = null;
let particles = [];
let animationFrame = null;
let viewport = { width: window.innerWidth, height: window.innerHeight, dpr: 1 };

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
soundtrack.volume = 0.74;

function resizeCanvas() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  viewport = { width: window.innerWidth, height: window.innerHeight, dpr };
  canvas.width = Math.round(viewport.width * dpr);
  canvas.height = Math.round(viewport.height * dpr);
  canvas.style.width = `${viewport.width}px`;
  canvas.style.height = `${viewport.height}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function random(min, max) {
  return Math.random() * (max - min) + min;
}

function getRoseCenter() {
  const rect = roseWrap.getBoundingClientRect();
  const assembled = app.classList.contains("is-assembled");
  return {
    x: rect.left + rect.width * (assembled ? 0.51 : 0.784),
    y: rect.top + rect.height * (assembled ? 0.67 : 0.503),
  };
}

class Particle {
  constructor(x, y, options = {}) {
    this.x = x;
    this.y = y;
    this.type = options.type || (Math.random() > 0.42 ? "spark" : "heart");
    this.size = options.size || random(2, 6);
    this.life = 0;
    this.maxLife = options.maxLife || random(70, 150);
    this.vx = options.vx ?? random(-1.8, 1.8);
    this.vy = options.vy ?? random(-3.6, -1.2);
    this.gravity = options.gravity ?? random(0.008, 0.025);
    this.rotation = random(0, Math.PI * 2);
    this.rotationSpeed = random(-0.035, 0.035);
    this.color = options.color || (Math.random() > 0.26 ? "#ff2b8b" : "#44e9ff");
    this.alpha = options.alpha || random(0.55, 1);
    this.twinkle = random(0, Math.PI * 2);
  }

  update() {
    this.life += 1;
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.vx *= 0.994;
    this.rotation += this.rotationSpeed;
    this.twinkle += 0.08;
  }

  draw() {
    const progress = this.life / this.maxLife;
    const opacity = Math.max(0, (1 - progress) * this.alpha);
    const scale = this.type === "heart" ? 1 - progress * 0.35 : 1;

    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.rotation);
    ctx.scale(scale, scale);
    ctx.globalAlpha = opacity;
    ctx.fillStyle = this.color;
    ctx.shadowColor = this.color;
    ctx.shadowBlur = this.type === "spark" ? 9 : 5;

    if (this.type === "heart") {
      const s = this.size;
      ctx.beginPath();
      ctx.moveTo(0, s * 0.42);
      ctx.bezierCurveTo(-s * 1.05, -s * 0.25, -s * 0.72, -s, 0, -s * 0.43);
      ctx.bezierCurveTo(s * 0.72, -s, s * 1.05, -s * 0.25, 0, s * 0.42);
      ctx.fill();
    } else {
      const pulse = 0.72 + Math.sin(this.twinkle) * 0.28;
      ctx.globalAlpha *= pulse;
      ctx.beginPath();
      ctx.arc(0, 0, this.size * 0.42, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  get dead() {
    return this.life >= this.maxLife;
  }
}

function animateParticles() {
  ctx.clearRect(0, 0, viewport.width, viewport.height);
  particles = particles.filter((particle) => !particle.dead);

  particles.forEach((particle) => {
    particle.update();
    particle.draw();
  });

  if (isActive && Math.random() > 0.88 && particles.length < 120) {
    const center = getRoseCenter();
    particles.push(
      new Particle(center.x + random(-60, 60), center.y + random(-20, 55), {
        type: Math.random() > 0.62 ? "heart" : "spark",
        size: random(1.5, 4),
        vx: random(-0.45, 0.45),
        vy: random(-1.25, -0.42),
        maxLife: random(100, 185),
        alpha: random(0.35, 0.75),
      }),
    );
  }

  animationFrame = requestAnimationFrame(animateParticles);
}

function burst(x, y, count = 36) {
  for (let i = 0; i < count; i += 1) {
    const angle = random(0, Math.PI * 2);
    const speed = random(1, 4.7);
    particles.push(
      new Particle(x, y, {
        type: i % 4 === 0 ? "heart" : "spark",
        size: random(2, i % 4 === 0 ? 7 : 4),
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.2,
        gravity: random(0.012, 0.04),
        maxLife: random(65, 135),
      }),
    );
  }
}

function roseBurst() {
  const center = getRoseCenter();
  burst(center.x, center.y, reducedMotion ? 12 : 68);
}

function playAssemblyBursts() {
  const rect = roseWrap.getBoundingClientRect();
  const points = [
    [0.78, 0.5, 36, 80],
    [0.68, 0.58, 20, 780],
    [0.64, 0.61, 22, 1120],
    [0.51, 0.67, 34, 2220],
    [0.51, 0.7, 42, 6670],
    [0.27, 0.68, 24, 7200],
    [0.5, 0.8, 24, 8300],
    [0.4, 0.88, 22, 8900],
    [0.62, 0.88, 22, 9400],
    [0.3, 0.2, 24, 10000],
    [0.7, 0.2, 24, 10500],
    [0.5, 0.17, 30, 11100],
    [0.5, 0.38, 26, 12200],
    [0.62, 0.15, 30, 13300],
    [0.51, 0.67, 64, 15560],
  ];

  points.forEach(([x, y, count, delay]) => {
    window.setTimeout(() => {
      burst(
        rect.left + rect.width * x,
        rect.top + rect.height * y,
        reducedMotion ? 6 : count,
      );
    }, reducedMotion ? 0 : delay);
  });
}

function typeMessage(text) {
  if (reducedMotion) {
    loveMessage.textContent = text;
    loveMessage.classList.add("is-complete");
    return;
  }

  loveMessage.textContent = "";
  loveMessage.classList.remove("is-complete");
  const characters = Array.from(text);
  let index = 0;

  const timer = window.setInterval(() => {
    loveMessage.textContent += characters[index];
    index += 1;
    if (index >= characters.length) {
      window.clearInterval(timer);
      loveMessage.classList.add("is-complete");
    }
  }, 58);
}

function animateCorePercent() {
  if (reducedMotion) {
    corePercent.textContent = "100%";
    return;
  }

  const start = performance.now();
  const duration = 15560;

  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    corePercent.textContent = `${String(Math.round(eased * 100)).padStart(2, "0")}%`;
    if (progress < 1) requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);
}

function createAudioContext() {
  if (!audioContext) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return null;
    audioContext = new AudioCtx();
  }
  if (audioContext.state === "suspended") audioContext.resume();
  return audioContext;
}

function tone(frequency, start, duration, volume = 0.035, type = "sine") {
  const audio = createAudioContext();
  if (!audio) return;

  const oscillator = audio.createOscillator();
  const gain = audio.createGain();
  const filter = audio.createBiquadFilter();

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, audio.currentTime + start);
  filter.type = "lowpass";
  filter.frequency.value = 1800;

  gain.gain.setValueAtTime(0.0001, audio.currentTime + start);
  gain.gain.exponentialRampToValueAtTime(volume, audio.currentTime + start + 0.035);
  gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + start + duration);

  oscillator.connect(filter);
  filter.connect(gain);
  gain.connect(audio.destination);
  oscillator.start(audio.currentTime + start);
  oscillator.stop(audio.currentTime + start + duration + 0.05);
}

function playHeartTone() {
  if (!soundEnabled) return;
  tone(523.25, 0, 0.42, 0.025);
  tone(659.25, 0.08, 0.55, 0.018);
}

function updateSoundControl() {
  soundToggle.classList.toggle("is-on", soundEnabled);
  soundToggle.setAttribute("aria-label", soundEnabled ? "关闭声音" : "开启声音");
  soundToggle.querySelector(".sound-label").textContent = soundEnabled ? "SOUND ON" : "SOUND OFF";
}

async function playSoundtrack(restart = false) {
  if (!soundEnabled) return false;
  if (restart || soundtrack.ended) soundtrack.currentTime = 0;

  try {
    await soundtrack.play();
    return true;
  } catch (error) {
    // A scripted ?open=1 launch has no user gesture, so browsers may reject it.
    soundEnabled = false;
    updateSoundControl();
    return false;
  }
}

function setSound(enabled, { replay = false } = {}) {
  soundEnabled = enabled;
  updateSoundControl();

  if (enabled) {
    createAudioContext();
    if (isActive) {
      playSoundtrack(replay || soundtrack.ended);
    }
  } else {
    soundtrack.pause();
  }
}

function activate(withSound = true) {
  if (isActive) {
    pulseRose();
    return;
  }

  isActive = true;
  app.classList.add("is-active");
  roseWrap.setAttribute("aria-label", "正在组装的 Hello Kitty 心动战甲");
  systemStateText.textContent = "ARMOR ASSEMBLING";
  suitLabel.textContent = "KAWAII ARMOR // ASSEMBLING";
  animateCorePercent();
  playAssemblyBursts();

  if (withSound) {
    soundEnabled = true;
    updateSoundControl();
    createAudioContext();
    playSoundtrack(true);
  }

  window.setTimeout(roseBurst, reducedMotion ? 0 : 120);
  window.setTimeout(
    () => {
      systemStateText.textContent = "LOVE CORE LINKED";
      suitLabel.textContent = "CORE LINKED // SUIT SCAN";
    },
    reducedMotion ? 0 : 2750,
  );
  window.setTimeout(
    () => {
      systemStateText.textContent = "ARMOR DEPLOYING";
      suitLabel.textContent = "KAWAII ARMOR // DEPLOYING";
    },
    reducedMotion ? 0 : 6650,
  );
  window.setTimeout(
    () => {
      app.classList.add("is-assembled");
      systemStateText.textContent = "KAWAII ARMOR ONLINE";
      suitLabel.textContent = "KAWAII ARMOR // ONLINE";
      roseWrap.setAttribute("aria-label", "已经完成的 Hello Kitty 心动战甲，点击可发送心动信号");
      roseBurst();
    },
    reducedMotion ? 0 : 15560,
  );
  window.setTimeout(() => typeMessage(content.message), reducedMotion ? 0 : 16200);
}

function pulseRose(event) {
  if (!isActive) return;
  const point = event
    ? { x: event.clientX, y: event.clientY }
    : getRoseCenter();

  app.classList.remove("is-pulsing");
  void app.offsetWidth;
  app.classList.add("is-pulsing");
  window.setTimeout(() => app.classList.remove("is-pulsing"), 720);

  burst(point.x, point.y, reducedMotion ? 8 : 28);
  playHeartTone();
  clickHint.style.opacity = "0";
}

launchButton.addEventListener("click", () => activate(true));
roseWrap.addEventListener("click", (event) => {
  if (isActive) {
    pulseRose(event);
  } else {
    activate(true);
  }
});

roseWrap.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  if (isActive) {
    pulseRose();
  } else {
    activate(true);
  }
});

soundToggle.addEventListener("click", () => setSound(!soundEnabled, { replay: true }));

window.addEventListener("pointermove", (event) => {
  document.documentElement.style.setProperty("--cursor-x", `${event.clientX}px`);
  document.documentElement.style.setProperty("--cursor-y", `${event.clientY}px`);
});

window.addEventListener("resize", resizeCanvas);

resizeCanvas();
animateParticles();

if (query.get("complete") === "1") {
  isActive = true;
  app.classList.add("is-active", "is-assembled", "force-complete");
  corePercent.textContent = "100%";
  systemStateText.textContent = "KAWAII ARMOR ONLINE";
  suitLabel.textContent = "KAWAII ARMOR // ONLINE";
  loveMessage.textContent = content.message;
  loveMessage.classList.add("is-complete");
} else if (query.get("open") === "1") {
  window.setTimeout(() => activate(false), 500);
}

window.addEventListener("beforeunload", () => {
  if (animationFrame) cancelAnimationFrame(animationFrame);
  soundtrack.pause();
  if (audioContext) audioContext.close();
});
