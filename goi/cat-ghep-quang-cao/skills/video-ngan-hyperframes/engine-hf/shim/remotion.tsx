// Lớp thay thế gói "remotion" khi dựng bằng HyperFrames.
// Mã cảnh (engine/src/MoHinh.tsx) giữ nguyên, chỉ đổi nơi lấy khung hình:
// HyperFrames phát sự kiện hf-seek với giây hiện tại, ta vẽ lại React theo khung đó.
// Chỉ cài những hàm MoHinh.tsx dùng: AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame.
import React, {createContext, useContext, useId} from 'react';

export const FPS = 30;
export const KhungCtx = createContext(0);
type Doan = {tu: number; dai: number};
const DoanCtx = createContext<Doan>({tu: 0, dai: 1e9});

export const useCurrentFrame = () => useContext(KhungCtx) - useContext(DoanCtx).tu;
export const staticFile = (p: string) => `assets/${p.replace(/^\/+/, '')}`;

export const AbsoluteFill: React.FC<{style?: React.CSSProperties; children?: React.ReactNode}> = ({style, children}) => (
  <div style={{position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', ...style}}>{children}</div>
);

// Cảnh luôn được dựng sẵn (để mọi <video> có mặt ngay khi trang tải), ngoài khoảng thời gian thì ẩn.
export const Sequence: React.FC<{from?: number; durationInFrames?: number; layout?: string; children?: React.ReactNode}> = ({from = 0, durationInFrames = 1e9, children}) => {
  const tong = useContext(KhungCtx);
  const cha = useContext(DoanCtx);
  const tu = cha.tu + from;
  const hien = tong >= tu && tong < tu + durationInFrames;
  return (
    <DoanCtx.Provider value={{tu, dai: durationInFrames}}>
      <div style={{display: hien ? 'contents' : 'none'}}>{children}</div>
    </DoanCtx.Provider>
  );
};

export const Img: React.FC<React.ImgHTMLAttributes<HTMLImageElement>> = (p) => <img {...p} />;

// Video do HyperFrames tự lấy khung: khai đủ data-start, data-duration, data-media-start, không tự play hay tua.
export const OffthreadVideo: React.FC<{src: string; startFrom?: number; muted?: boolean; style?: React.CSSProperties}> = ({src, startFrom = 0, style}) => {
  const d = useContext(DoanCtx);
  const id = 'v' + useId().replace(/[^a-zA-Z0-9]/g, '');
  return (
    <video id={id} className="clip" src={src} muted playsInline preload="auto"
      data-start={(d.tu / FPS).toFixed(3)} data-duration={(Math.min(d.dai, 1e6) / FPS).toFixed(3)} data-media-start={(startFrom / FPS).toFixed(3)}
      style={style} />
  );
};

type MoRong = 'clamp' | 'extend' | 'identity';
export function interpolate(x: number, vao: number[], ra: number[], o: {extrapolateLeft?: MoRong; extrapolateRight?: MoRong; easing?: (t: number) => number} = {}): number {
  const ease = o.easing ?? ((t: number) => t);
  let i = 0;
  while (i < vao.length - 2 && x > vao[i + 1]) i++;
  const [a, b] = [vao[i], vao[i + 1]];
  let t = b === a ? 1 : (x - a) / (b - a);
  if (t < 0) {
    if ((o.extrapolateLeft ?? 'extend') === 'clamp') t = 0;
    else if (o.extrapolateLeft === 'identity') return x;
  }
  if (t > 1) {
    if ((o.extrapolateRight ?? 'extend') === 'clamp') t = 1;
    else if (o.extrapolateRight === 'identity') return x;
  }
  const e = t >= 0 && t <= 1 ? ease(t) : t;
  return ra[i] + (ra[i + 1] - ra[i]) * e;
}

// Lò xo tắt dần, nghiệm giải tích. Có durationInFrames thì co giãn thời gian cho lò xo lắng đúng số khung đó.
function loXo(t: number, damping: number, stiffness: number, mass: number) {
  if (t <= 0) return 0;
  const w0 = Math.sqrt(stiffness / mass);
  const z = damping / (2 * Math.sqrt(stiffness * mass));
  if (z < 1) {
    const wd = w0 * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + ((z * w0) / wd) * Math.sin(wd * t));
  }
  if (z === 1) return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
  const s = w0 * Math.sqrt(z * z - 1);
  const r1 = -z * w0 + s, r2 = -z * w0 - s;
  return 1 - (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r2 - r1);
}

const _lang = new Map<string, number>();
function khungLang(fps: number, d: number, k: number, m: number) {
  const khoa = `${fps}|${d}|${k}|${m}`;
  if (!_lang.has(khoa)) {
    let cuoi = 0;
    for (let i = 0; i < 2000; i++) if (Math.abs(loXo(i / fps, d, k, m) - 1) > 0.005) cuoi = i + 1;
    _lang.set(khoa, Math.max(1, cuoi));
  }
  return _lang.get(khoa) as number;
}

export function spring({frame, fps, config = {}, durationInFrames, from = 0, to = 1}: {frame: number; fps: number; config?: {damping?: number; stiffness?: number; mass?: number}; durationInFrames?: number; from?: number; to?: number}) {
  const {damping = 10, stiffness = 100, mass = 1} = config;
  let fr = frame;
  if (durationInFrames) fr = (frame * khungLang(fps, damping, stiffness, mass)) / durationInFrames;
  return from + (to - from) * loXo(fr / fps, damping, stiffness, mass);
}

export const registerRoot = () => undefined;
