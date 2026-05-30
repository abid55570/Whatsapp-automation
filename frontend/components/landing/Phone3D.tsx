"use client";

import { Suspense, useLayoutEffect, useMemo, useRef } from "react";
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

const TIMES = ["10:21", "10:21", "10:22", "10:22", "10:23", "10:23"];

function drawChat(ctx: CanvasRenderingContext2D, uc: Showcase) {
  ctx.clearRect(0, 0, CW, CH);
  // WhatsApp chat background
  ctx.fillStyle = "#E9E2DB";
  ctx.fillRect(0, 0, CW, CH);

  // Header (with a top status-bar inset so the Dynamic Island doesn't overlap)
  const statusInset = 64;
  const headH = 150 + statusInset;
  ctx.fillStyle = "#075E54";
  ctx.fillRect(0, 0, CW, headH);
  const ax = 78;
  const ay = statusInset + 88;
  ctx.beginPath();
  ctx.arc(ax, ay, 36, 0, Math.PI * 2);
  ctx.fillStyle = "#cfd8d4";
  ctx.fill();
  ctx.fillStyle = "#075E54";
  ctx.font = "bold 36px Inter, Arial, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(uc.phoneName.charAt(0), ax, ay + 2);
  ctx.textAlign = "left";
  ctx.textBaseline = "top";
  ctx.fillStyle = "#fff";
  ctx.font = "600 37px Inter, Arial, sans-serif";
  ctx.fillText(uc.phoneName, ax + 56, statusInset + 54);
  ctx.fillStyle = "#cdeee4";
  ctx.font = "25px Inter, Arial, sans-serif";
  ctx.fillText("online", ax + 56, statusInset + 98);

  // Messages
  let y = headH + 34;
  const pad = 30;
  const maxW = CW * 0.74;
  const fs = 31;
  const lineH = fs * 1.32;
  const bpx = 24;
  const bpyTop = 16;
  const metaH = 26;

  uc.chat.forEach((m: ChatMsg, idx: number) => {
    const out = m.side === "out";
    ctx.font = `${fs}px Inter, Arial, sans-serif`;
    const lines = wrap(ctx, m.text, maxW - bpx * 2);
    const botH = m.bot ? 32 : 0;
    const textW = Math.max(...lines.map((l) => ctx.measureText(l).width), m.bot ? 170 : 0);
    const bw = Math.min(maxW, Math.max(textW, 120) + bpx * 2);
    const bh = botH + lines.length * lineH + bpyTop + metaH + 12;
    const x = out ? CW - pad - bw : pad;

    // bubble
    roundRect(ctx, x, y, bw, bh, 20);
    ctx.fillStyle = out ? "#D9FDD3" : "#ffffff";
    ctx.shadowColor = "rgba(0,0,0,0.10)";
    ctx.shadowBlur = 5;
    ctx.shadowOffsetY = 2;
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;

    let ty = y + bpyTop;
    if (m.bot) {
      ctx.fillStyle = "#1a9d6c";
      ctx.font = "bold 19px Inter, Arial, sans-serif";
      ctx.fillText("AUTO-REPLY", x + bpx, ty);
      ty += botH;
    }
    ctx.fillStyle = "#111b21";
    ctx.font = `${fs}px Inter, Arial, sans-serif`;
    for (const l of lines) {
      ctx.fillText(l, x + bpx, ty);
      ty += lineH;
    }

    // timestamp + ticks (bottom-right of bubble)
    const time = TIMES[idx % TIMES.length];
    ctx.font = "20px Inter, Arial, sans-serif";
    ctx.fillStyle = "#667781";
    ctx.textAlign = "right";
    const metaRight = x + bw - bpx + (out ? -30 : 0);
    ctx.fillText(time, metaRight, y + bh - metaH - 4);
    if (out) {
      ctx.fillStyle = "#53bdeb"; // blue double-tick
      ctx.font = "22px Inter, Arial, sans-serif";
      ctx.fillText("✓✓", x + bw - bpx + 2, y + bh - metaH - 5);
    }
    ctx.textAlign = "left";

    y += bh + 16;
  });
}

function Model({ progressRef, uc }: { progressRef: MutableRefObject<number>; uc: Showcase }) {
  const { scene } = useGLTF(MODEL);
  const outer = useRef<THREE.Group>(null);
  const inner = useRef<THREE.Group>(null);
  const normRef = useRef(1);
  const centerRef = useRef(new THREE.Vector3());
  const readyRef = useRef(false);

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
    if (ctx) {
      drawChat(ctx, uc);
      texture.needsUpdate = true;
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
  }, [scene, texture, uc, canvas]);

  useFrame(() => {
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
    o.rotation.y = THREE.MathUtils.degToRad(t.r) + BASE_ROT_Y;
    o.rotation.x = BASE_ROT_X;
    o.position.x = mobile ? 0 : t.x;
    o.position.y = mobile ? t.y + mobileYOff : t.y;
    o.scale.setScalar(t.s * (mobile ? mobileScale : 1));
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
  return (
    <Canvas
      className="!absolute inset-0 z-30"
      style={{ pointerEvents: "none", zIndex: 30 }}
      camera={{ position: [0, 0, 9], fov: 35 }}
      gl={{ alpha: true, antialias: true }}
      dpr={[1, 1.6]}
    >
      <ambientLight intensity={0.6} />
      <directionalLight position={[4, 6, 6]} intensity={1.4} />
      <directionalLight position={[-5, -2, -4]} intensity={0.5} />
      <Suspense fallback={null}>
        <Model progressRef={progressRef} uc={uc} />
        <Environment preset="city" />
      </Suspense>
    </Canvas>
  );
}
