"use client";

import { Suspense, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { MutableRefObject } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useGLTF, Environment } from "@react-three/drei";
import * as THREE from "three";
import type { Showcase, ChatMsg } from "./content";

// Compressed (meshopt + WebP, 1.5 MB) — drei's useGLTF auto-wires the decoders.
const MODEL = "/models/iphone17.opt.glb";
useGLTF.preload(MODEL);

const BASE_ROT_Y = Math.PI;
const BASE_ROT_X = 0;
const TARGET_HEIGHT = 4.2;

// Scroll keyframes: p (0..1) -> x offset, rotationY (deg), scale multiplier.
const KF = [
  { p: 0.0, x: 0, y: -2.4, r: -16, s: 0.82 }, // hero: centered, lower, bigger
  { p: 0.035, x: 0, y: 0, r: -16, s: 1.2 }, // rise + zoom to center immediately on scroll
  { p: 0.065, x: 0, y: 0, r: 170, s: 1.22 }, // mid 360 spin (close-up kept brief)
  { p: 0.1, x: 2.2, y: 0, r: 344, s: 1.15 }, // arrive RIGHT — use-case 1 (restaurant)
  { p: 0.26, x: 2.2, y: 0, r: 344, s: 1.15 }, // HOLD right (equal-length holds)
  { p: 0.345, x: -2.2, y: 0, r: 376, s: 1.15 }, // glide to LEFT — use-case 2
  { p: 0.505, x: -2.2, y: 0, r: 376, s: 1.15 }, // HOLD left
  { p: 0.59, x: 2.2, y: 0, r: 344, s: 1.15 }, // glide to RIGHT — use-case 3
  { p: 0.75, x: 2.2, y: 0, r: 344, s: 1.15 }, // HOLD right
  { p: 0.84, x: -2.2, y: 0, r: 376, s: 1.15 }, // glide to LEFT — use-case 4
  { p: 1.0, x: -2.2, y: 0, r: 376, s: 1.15 }, // HOLD left
];

function sampleKF(p: number) {
  if (p <= KF[0].p) return KF[0];
  for (let i = 0; i < KF.length - 1; i++) {
    const a = KF[i];
    const b = KF[i + 1];
    if (p >= a.p && p <= b.p) {
      const t = (p - a.p) / (b.p - a.p);
      return {
        x: THREE.MathUtils.lerp(a.x, b.x, t),
        y: THREE.MathUtils.lerp(a.y, b.y, t),
        r: THREE.MathUtils.lerp(a.r, b.r, t),
        s: THREE.MathUtils.lerp(a.s, b.s, t),
      };
    }
  }
  return KF[KF.length - 1];
}

// ----- Chat -> canvas texture (painted onto the phone's OLED screen) -----
const CW = 660;
const CH = 1430;

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function wrap(ctx: CanvasRenderingContext2D, text: string, maxW: number) {
  const words = text.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const test = line ? line + " " + w : w;
    if (ctx.measureText(test).width > maxW && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

const TIMES = ["10:18", "10:19", "10:20", "10:21", "10:22", "10:23", "10:24", "10:25"];

function drawChat(ctx: CanvasRenderingContext2D, uc: Showcase, pfp: HTMLImageElement | null) {
  ctx.clearRect(0, 0, CW, CH);
  // WhatsApp wallpaper
  ctx.fillStyle = "#E5DDD5";
  ctx.fillRect(0, 0, CW, CH);

  const statusInset = 64;
  const headH = statusInset + 132;

  // ---------- Header ----------
  ctx.fillStyle = "#075E54";
  ctx.fillRect(0, 0, CW, headH);

  // back chevron
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 6;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  const cy = statusInset + 64;
  ctx.beginPath();
  ctx.moveTo(40, cy - 16);
  ctx.lineTo(24, cy);
  ctx.lineTo(40, cy + 16);
  ctx.stroke();

  // avatar (photo, clipped to a circle; falls back to initial)
  const ar = 42;
  const ax = 100;
  const ay = statusInset + 64;
  ctx.save();
  ctx.beginPath();
  ctx.arc(ax, ay, ar, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();
  if (pfp && pfp.width > 0) {
    const s = Math.max((ar * 2) / pfp.width, (ar * 2) / pfp.height);
    const iw = pfp.width * s;
    const ih = pfp.height * s;
    ctx.drawImage(pfp, ax - iw / 2, ay - ih / 2, iw, ih);
  } else {
    ctx.fillStyle = "#cfd8d4";
    ctx.fillRect(ax - ar, ay - ar, ar * 2, ar * 2);
    ctx.fillStyle = "#075E54";
    ctx.font = "bold 42px Inter, Arial, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(uc.phoneName.charAt(0), ax, ay + 2);
  }
  ctx.restore();

  // name + online
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";
  ctx.fillStyle = "#fff";
  ctx.font = "600 41px Inter, Arial, sans-serif";
  ctx.fillText(uc.phoneName, ax + ar + 24, statusInset + 56);
  ctx.fillStyle = "#bfe6da";
  ctx.font = "26px Inter, Arial, sans-serif";
  ctx.fillText("online", ax + ar + 24, statusInset + 98);

  // 3-dot menu
  ctx.fillStyle = "#cfe8e0";
  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    ctx.arc(CW - 44, statusInset + 40 + i * 22, 5, 0, Math.PI * 2);
    ctx.fill();
  }

  // ---------- Input bar (bottom) ----------
  const inputH = 124;
  const inputY = CH - inputH;
  const pillX = 24;
  const pillH = inputH - 44;
  const pillY = inputY + 20;
  const pillW = CW - pillX - 116;
  roundRect(ctx, pillX, pillY, pillW, pillH, pillH / 2);
  ctx.fillStyle = "#ffffff";
  ctx.fill();
  // emoji icon inside pill
  const ex = pillX + 38;
  const ey = pillY + pillH / 2;
  ctx.strokeStyle = "#8696a0";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(ex, ey, 18, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "#8696a0";
  ctx.beginPath();
  ctx.arc(ex - 6, ey - 5, 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(ex + 6, ey - 5, 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(ex, ey + 2, 9, 0.15 * Math.PI, 0.85 * Math.PI);
  ctx.stroke();
  ctx.fillStyle = "#9aa6ad";
  ctx.font = "29px Inter, Arial, sans-serif";
  ctx.textBaseline = "middle";
  ctx.fillText("Message", ex + 36, ey + 1);
  ctx.textBaseline = "top";
  // send/mic circle
  const sc = CW - 56;
  const scy = inputY + inputH / 2;
  ctx.beginPath();
  ctx.arc(sc, scy, 42, 0, Math.PI * 2);
  ctx.fillStyle = "#00a884";
  ctx.fill();
  ctx.fillStyle = "#fff";
  roundRect(ctx, sc - 9, scy - 24, 18, 30, 9);
  ctx.fill();
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(sc, scy, 16, 0.15 * Math.PI, 0.85 * Math.PI);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(sc, scy + 16);
  ctx.lineTo(sc, scy + 26);
  ctx.moveTo(sc - 12, scy + 26);
  ctx.lineTo(sc + 12, scy + 26);
  ctx.stroke();

  // ---------- Messages (measure, then bottom-align so the chat fills) ----------
  const pad = 26;
  const maxW = CW * 0.76;
  const fs = 32;
  const lineH = fs * 1.34;
  const bpx = 26;
  const bpyTop = 18;
  const metaH = 30;
  const gap = 20;

  const items = uc.chat.map((m) => {
    ctx.font = `${fs}px Inter, Arial, sans-serif`;
    const lines = wrap(ctx, m.text, maxW - bpx * 2);
    const botH = m.bot ? 38 : 0;
    const textW = Math.max(...lines.map((l) => ctx.measureText(l).width), m.bot ? 200 : 0);
    const bw = Math.min(maxW, Math.max(textW, 120) + bpx * 2);
    const bh = botH + lines.length * lineH + bpyTop + metaH + 14;
    return { m, lines, botH, bw, bh };
  });

  const totalH = items.reduce((s, it) => s + it.bh + gap, 0) - gap;
  const chipH = 46;
  const areaTop = headH + 28;
  const areaBottom = inputY - 22;
  let y = Math.max(areaTop + chipH + 26, areaBottom - totalH);

  // date chip, sitting just above the first message
  const chipText = "TODAY";
  ctx.font = "bold 23px Inter, Arial, sans-serif";
  const chipW = ctx.measureText(chipText).width + 48;
  const chipX = (CW - chipW) / 2;
  const chipY = y - chipH - 22;
  roundRect(ctx, chipX, chipY, chipW, chipH, 16);
  ctx.fillStyle = "rgba(225,245,235,0.95)";
  ctx.fill();
  ctx.fillStyle = "#54656f";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(chipText, CW / 2, chipY + chipH / 2 + 1);
  ctx.textAlign = "left";
  ctx.textBaseline = "top";

  items.forEach((it, idx) => {
    const out = it.m.side === "out";
    const x = out ? CW - pad - it.bw : pad;

    // bubble
    roundRect(ctx, x, y, it.bw, it.bh, 22);
    ctx.fillStyle = out ? "#DCF8C6" : "#ffffff";
    ctx.shadowColor = "rgba(0,0,0,0.12)";
    ctx.shadowBlur = 6;
    ctx.shadowOffsetY = 2;
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
    // little tail
    ctx.beginPath();
    if (out) {
      ctx.moveTo(x + it.bw - 4, y + 4);
      ctx.lineTo(x + it.bw + 16, y);
      ctx.lineTo(x + it.bw - 4, y + 30);
    } else {
      ctx.moveTo(x + 4, y + 4);
      ctx.lineTo(x - 16, y);
      ctx.lineTo(x + 4, y + 30);
    }
    ctx.closePath();
    ctx.fillStyle = out ? "#DCF8C6" : "#ffffff";
    ctx.fill();

    let ty = y + bpyTop;
    if (it.m.bot) {
      ctx.fillStyle = "#1fa463";
      ctx.font = "bold 21px Inter, Arial, sans-serif";
      ctx.fillText("WHATLY • AUTO-REPLY", x + bpx, ty);
      ty += it.botH;
    }
    ctx.fillStyle = "#111b21";
    ctx.font = `${fs}px Inter, Arial, sans-serif`;
    for (const l of it.lines) {
      ctx.fillText(l, x + bpx, ty);
      ty += lineH;
    }

    // timestamp + ticks
    const time = TIMES[idx % TIMES.length];
    ctx.font = "22px Inter, Arial, sans-serif";
    ctx.fillStyle = "#667781";
    ctx.textAlign = "right";
    const metaRight = x + it.bw - bpx + (out ? -34 : 0);
    ctx.fillText(time, metaRight, y + it.bh - metaH - 2);
    if (out) {
      ctx.fillStyle = "#53bdeb";
      ctx.font = "24px Inter, Arial, sans-serif";
      ctx.fillText("✓✓", x + it.bw - bpx + 4, y + it.bh - metaH - 3);
    }
    ctx.textAlign = "left";

    y += it.bh + gap;
  });
}

function Model({ progressRef, uc }: { progressRef: MutableRefObject<number>; uc: Showcase }) {
  const { scene } = useGLTF(MODEL);
  const outer = useRef<THREE.Group>(null);
  const inner = useRef<THREE.Group>(null);
  const normRef = useRef(1);
  const centerRef = useRef(new THREE.Vector3());
  const readyRef = useRef(false);
  // Smoothed (damped) transform so the device glides toward its scroll target
  // instead of tracking the wheel 1:1 — the premium, weighted feel.
  const dampRef = useRef({ x: 0, y: 0, s: 1, init: false });
  // Cache of loaded chat-header avatars, keyed by url.
  const pfpCache = useRef(new Map<string, HTMLImageElement>());

  const canvas = useMemo(() => {
    const c = document.createElement("canvas");
    c.width = CW;
    c.height = CH;
    return c;
  }, []);
  const texture = useMemo(() => {
    const t = new THREE.CanvasTexture(canvas);
    t.colorSpace = THREE.SRGBColorSpace;
    t.flipY = false;
    // The screen UVs are mirrored — flip the texture horizontally to match.
    t.wrapS = THREE.RepeatWrapping;
    t.repeat.x = -1;
    t.offset.x = 1;
    t.anisotropy = 8;
    return t;
  }, [canvas]);

  // Draw the chat + bind it to the screen synchronously before paint, so the
  // display is never blank once the phone appears (and redraws on use-case change).
  useLayoutEffect(() => {
    const ctx = canvas.getContext("2d");
    let cancelled = false;
    if (ctx) {
      // Draw immediately (with the avatar if it's already cached), then load it
      // in the background and repaint once when it arrives.
      const cached = pfpCache.current.get(uc.pfp) ?? null;
      drawChat(ctx, uc, cached);
      texture.needsUpdate = true;
      if (!cached && uc.pfp) {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => {
          if (cancelled) return;
          pfpCache.current.set(uc.pfp, img);
          drawChat(ctx, uc, img);
          texture.needsUpdate = true;
        };
        img.src = uc.pfp;
      }
    }
    scene.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (!mesh.isMesh) return;
      const mat = mesh.material as THREE.MeshStandardMaterial & { name?: string };
      const name = mat?.name || "";
      if (name.toUpperCase().startsWith("OLED")) {
        // Flat, unlit screen: black diffuse (so lighting can't add glare) +
        // the chat as an emissive map shown at true brightness.
        mat.color = new THREE.Color(0x000000);
        mat.map = null;
        mat.emissive = new THREE.Color(0xffffff);
        mat.emissiveMap = texture;
        mat.emissiveIntensity = 1.1;
        mat.metalness = 0;
        mat.roughness = 1;
        mat.toneMapped = false;
        mat.transparent = false;
        mat.opacity = 1;
        mat.needsUpdate = true;
      } else if (name === "Glass" || /frosted/i.test(name)) {
        // Remove the cover glass over the display so there's no reflection/glare.
        mesh.visible = false;
      }
    });
    return () => {
      cancelled = true;
    };
  }, [scene, texture, uc, canvas]);

  useFrame((_, delta) => {
    const o = outer.current;
    const inn = inner.current;
    if (!o || !inn) return;

    // Measure + normalize, retrying each frame until the (meshopt) geometry is
    // actually decoded — so we never lock in a wrong/tiny scale or flash it.
    if (!readyRef.current) {
      inn.scale.setScalar(1);
      inn.position.set(0, 0, 0);
      const box = new THREE.Box3().setFromObject(scene);
      const size = box.getSize(new THREE.Vector3());
      if (size.y > 0.001 && Number.isFinite(size.y)) {
        normRef.current = TARGET_HEIGHT / size.y;
        centerRef.current.copy(box.getCenter(new THREE.Vector3()));
        readyRef.current = true;
      } else {
        o.visible = false;
        return;
      }
    }
    o.visible = true;
    const n = normRef.current;
    inn.scale.setScalar(n);
    inn.position.set(-centerRef.current.x * n, -centerRef.current.y * n, -centerRef.current.z * n);

    const p = progressRef.current ?? 0;
    const t = sampleKF(p);
    // Responsive: on phones, center the device (no side offset). During the hero
    // it sits centred & peeks from the bottom; as the journey enters use-case
    // mode (~p 0.05->0.1) it smoothly drops into the lower half + shrinks, so the
    // taller use-case card has the top half to itself and never overlaps it.
    const mobile = typeof window !== "undefined" && window.innerWidth < 768;
    const ucFactor = THREE.MathUtils.clamp((p - 0.05) / 0.05, 0, 1);
    const mobileYOff = -0.3 - 1.9 * ucFactor; // -0.3 (hero) -> -2.2 (use-cases, lower)
    const mobileScale = 0.78 - 0.05 * ucFactor; // 0.78 (hero) -> 0.73 (use-cases, larger)
    const targetX = mobile ? 0 : t.x;
    const targetY = mobile ? t.y + mobileYOff : t.y;
    const targetS = t.s * (mobile ? mobileScale : 1);

    // Seed the damped state on the first ready frame to avoid an opening swing.
    const d = dampRef.current;
    if (!d.init) {
      d.x = targetX;
      d.y = targetY;
      d.s = targetS;
      d.init = true;
    }
    const dt = Math.min(delta, 1 / 30); // clamp so tab-switches don't jump
    const lambda = 7; // higher = snappier, lower = floatier
    d.x = THREE.MathUtils.damp(d.x, targetX, lambda, dt);
    d.y = THREE.MathUtils.damp(d.y, targetY, lambda, dt);
    d.s = THREE.MathUtils.damp(d.s, targetS, lambda, dt);

    // Rotation stays exact so the 360° spin reads crisp.
    o.rotation.y = THREE.MathUtils.degToRad(t.r) + BASE_ROT_Y;
    o.rotation.x = BASE_ROT_X;
    o.position.x = d.x;
    o.position.y = d.y;
    o.scale.setScalar(d.s);
  });

  return (
    <group ref={outer} visible={false}>
      <group ref={inner}>
        <primitive object={scene} />
      </group>
    </group>
  );
}

export default function Phone3D({
  progressRef,
  uc,
}: {
  progressRef: MutableRefObject<number>;
  uc: Showcase;
}) {
  const wrapRef = useRef<HTMLDivElement>(null);
  // Stop rendering the WebGL scene whenever the journey is scrolled off-screen
  // — frees the GPU for the entire lower half of the page.
  const [active, setActive] = useState(true);
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setActive(e.isIntersecting), {
      rootMargin: "120px",
    });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div ref={wrapRef} className="absolute inset-0 z-30">
      <Canvas
        className="!absolute inset-0"
        style={{ pointerEvents: "none" }}
        camera={{ position: [0, 0, 9], fov: 35 }}
        gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}
        dpr={[1, 1.25]}
        frameloop={active ? "always" : "never"}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[4, 6, 6]} intensity={1.4} />
        <directionalLight position={[-5, -2, -4]} intensity={0.5} />
        <Suspense fallback={null}>
          <Model progressRef={progressRef} uc={uc} />
          <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  );
}
