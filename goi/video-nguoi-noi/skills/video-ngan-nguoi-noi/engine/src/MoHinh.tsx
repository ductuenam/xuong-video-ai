import {createContext, useContext} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';
import {loadFont as loadBeVietnam} from '@remotion/google-fonts/BeVietnamPro';
import {fontTieuDe} from './theme';
import KENH from './kenh.json';

// Bộ mô hình minh họa dùng cho mọi video. Không ghi chữ riêng của video hay của kênh ở đây:
// chữ của video nằm trong canh.json của dự án, chữ và màu của kênh nằm trong kenh.json.
const FONT = loadBeVietnam('normal', {weights: ['400', '500', '600', '700', '800', '900'], subsets: ['vietnamese', 'latin']}).fontFamily;

export type CumPhuDe = {text: string; start: number; end: number};
export type CanhMoHinh = {loai: string; tu: number; den: number; viTriPhuDe?: number; [k: string]: unknown};
export type MoHinhProps = {thoiLuongGiay: number; phuDe: CumPhuDe[]; canh: CanhMoHinh[]};

const CAM = KENH.mauChinh;
const CAM2 = KENH.mauPhu;
const DAM = '#1D1B1A';
const XAM = '#8B8580';
const VIEN = '#F4E4D8';
const BONG = '0 2px 4px rgba(120,60,20,0.05), 0 18px 50px rgba(150,80,30,0.13)';
const f = (giay: number) => Math.round(giay * 30);
const kep = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const HAT_NEN = Array.from({length: 22}).map((_, i) => ({x: (i * 173) % 1080, y: (i * 389) % 1920, r: 3 + (i * 7) % 6, toc: 0.4 + ((i * 13) % 10) / 12, lech: (i * 37) % 360}));

// Bốn kiểu nền động, đặt bằng trường kieuNen của cảnh: dao (mặc định), luoi, song, toi
const KieuNen = createContext<string>('dao');

const NenDao: React.FC<{children?: React.ReactNode}> = ({children}) => {
  const fr = useCurrentFrame();
  const kieu = useContext(KieuNen);
  const a = Math.sin(fr / 90) * 90;
  const b = Math.cos(fr / 120) * 110;
  const toi = kieu === 'toi';
  const nen = toi
    ? `radial-gradient(800px 700px at ${50 + a / 12}% ${28 + b / 30}%,rgba(255,106,26,0.30) 0%,rgba(255,106,26,0) 70%),radial-gradient(800px 700px at ${25 - a / 14}% ${85 - b / 40}%,rgba(255,150,70,0.16) 0%,rgba(255,150,70,0) 70%),linear-gradient(170deg,#100C0A 0%,#0A0A0C 100%)`
    : kieu === 'luoi'
    ? `radial-gradient(900px 800px at ${80 + a / 30}% ${15 + b / 50}%,#FFE0C7 0%,rgba(255,224,199,0) 70%),linear-gradient(170deg,#FFF8F2 0%,#FFFDFB 100%)`
    : kieu === 'song'
    ? 'linear-gradient(175deg,#FFF1E6 0%,#FFF9F4 58%,#FFE9D9 100%)'
    : `radial-gradient(900px 700px at ${15 + a / 30}% ${80 + b / 40}%,#FFE3CC 0%,rgba(255,227,204,0) 70%),radial-gradient(800px 700px at ${85 - a / 30}% ${18 - b / 50}%,#FFD9BF 0%,rgba(255,217,191,0) 68%),radial-gradient(900px 800px at 90% 95%,#FFFFFF 0%,rgba(255,255,255,0) 65%),linear-gradient(170deg,#FCE9DC 0%,#FFF3EA 45%,#FFF9F4 100%)`;
  return (
    <AbsoluteFill style={{background: nen, fontFamily: FONT}}>
      {kieu === 'luoi' ? <div style={{position: 'absolute', inset: -60, backgroundImage: 'radial-gradient(rgba(232,90,20,0.22) 3px,transparent 3.5px)', backgroundSize: '60px 60px', transform: `translate(${(fr * 0.4) % 60}px,${(fr * 0.25) % 60}px)`}} /> : null}
      {kieu === 'song' ? (
        <svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
          {[0, 1, 2].map((i) => {
            const y = 1260 + i * 170;
            const pha = fr / (34 + i * 10) + i * 1.7;
            const d = Array.from({length: 13}).map((_, k) => `${k === 0 ? 'M' : 'L'}${k * 90} ${y + Math.sin(pha + k * 0.7) * (46 - i * 8)}`).join(' ');
            return <path key={i} d={`${d} L1080 1920 L0 1920 Z`} fill={CAM2} opacity={0.09 + i * 0.03} />;
          })}
        </svg>
      ) : null}
      {kieu === 'luoi' || kieu === 'song' ? null : HAT_NEN.map((h, i) => {
        const y = ((h.y - fr * h.toc) % 1920 + 1920) % 1920;
        return <div key={i} style={{position: 'absolute', left: h.x + Math.sin((fr + h.lech) / 40) * 16, top: y, width: h.r * 2, height: h.r * 2, borderRadius: 99, background: CAM2, opacity: toi ? 0.32 : 0.13}} />;
      })}
      {children}
    </AbsoluteFill>
  );
};

const useLen = (giay: number, tre = 14) => {
  const frame = useCurrentFrame();
  return spring({frame: frame - f(giay), fps: 30, config: {damping: 15, stiffness: 170, mass: 0.7}, durationInFrames: tre});
};

const Len: React.FC<{at?: number; style?: React.CSSProperties; children: React.ReactNode; tu?: number}> = ({at = 0, style, children, tu = 26}) => {
  const v = useLen(at);
  return <div style={{opacity: Math.min(1, v * 1.5), transform: `translateY(${interpolate(v, [0, 1], [tu, 0])}px) scale(${interpolate(v, [0, 1], [0.96, 1])})`, ...style}}>{children}</div>;
};

const The: React.FC<{style?: React.CSSProperties; children: React.ReactNode}> = ({style, children}) => (
  <div style={{background: '#fff', borderRadius: 26, boxShadow: BONG, ...style}}>{children}</div>
);

const Dong: React.FC<{w: string | number; mau?: string; cao?: number; style?: React.CSSProperties}> = ({w, mau = '#D5CFCA', cao = 11, style}) => (
  <div style={{width: w, height: cao, background: mau, borderRadius: 99, ...style}} />
);

const Nhan: React.FC<{chu: string; cam?: boolean; co?: number; cham?: boolean}> = ({chu, cam, co = 32, cham}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, padding: `${co * 0.42}px ${co * 0.85}px`, borderRadius: 99, background: cam ? CAM : '#fff', color: cam ? '#fff' : DAM, fontWeight: 700, fontSize: co, boxShadow: BONG, whiteSpace: 'nowrap'}}>
    {cham ? <span style={{width: 12, height: 12, borderRadius: 99, background: CAM}} /> : null}{chu}
  </div>
);

// ===== Linh vật
const LinhVat: React.FC<{co?: number; mat?: 'thuong' | 'x' | 'vui' | 'dung'; so?: string; style?: React.CSSProperties}> = ({co = 1, mat = 'thuong', so, style}) => {
  const frame = useCurrentFrame();
  const nhun = Math.sin(frame / 9) * 4 * co;
  const chop = frame % 80 < 4;
  const MatT: React.FC<{i: number}> = ({i}) => {
    if (mat === 'x' && i === 1) return <span style={{color: CAM2, fontSize: 40 * co, fontWeight: 900, lineHeight: 1}}>×</span>;
    if (mat === 'vui') return <div style={{width: 26 * co, height: 13 * co, borderTop: `${5 * co}px solid #fff`, borderRadius: '50% 50% 0 0'}} />;
    if (mat === 'dung' && i === 1) return <span style={{color: CAM2, fontSize: 34 * co, fontWeight: 900, lineHeight: 1}}>✓</span>;
    return <div style={{width: 26 * co, height: chop ? 3 * co : 26 * co, background: i === 1 ? CAM2 : '#fff', borderRadius: 99}} />;
  };
  return (
    <div style={{position: 'relative', width: 170 * co, height: 215 * co, transform: `translateY(${nhun}px)`, ...style}}>
      <div style={{position: 'absolute', left: 118 * co, top: 0, width: 16 * co, height: 16 * co, background: CAM, borderRadius: 99}} />
      <div style={{position: 'absolute', left: 124 * co, top: 12 * co, width: 4 * co, height: 18 * co, background: CAM}} />
      <div style={{position: 'absolute', left: 0, top: 26 * co, width: 170 * co, height: 124 * co, borderRadius: 40 * co, background: 'linear-gradient(180deg,#fff,#F6F1ED)', boxShadow: `0 ${14 * co}px ${30 * co}px rgba(120,60,20,0.2)`}}>
        <div style={{position: 'absolute', left: 22 * co, top: 26 * co, width: 126 * co, height: 58 * co, borderRadius: 30 * co, background: '#22201F', display: 'flex', alignItems: 'center', justifyContent: 'space-around', padding: `0 ${10 * co}px`, boxSizing: 'border-box'}}><MatT i={0} /><MatT i={1} /></div>
        <div style={{position: 'absolute', left: 66 * co, top: 98 * co, width: 38 * co, height: 7 * co, background: '#D9D2CC', borderRadius: 9}} />
      </div>
      <div style={{position: 'absolute', left: 42 * co, top: 156 * co, width: 86 * co, height: 58 * co, background: 'linear-gradient(180deg,#fff,#EFE8E2)', clipPath: 'polygon(14% 0,86% 0,100% 100%,0 100%)', fontWeight: 900, fontSize: 22 * co, color: CAM, textAlign: 'center', paddingTop: 14 * co, boxSizing: 'border-box'}}>{KENH.chuLinhVat}</div>
      {so ? <div style={{position: 'absolute', right: -20 * co, top: 92 * co, width: 62 * co, height: 62 * co, borderRadius: 99, background: CAM, color: '#fff', fontWeight: 800, fontSize: 32 * co, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `${4 * co}px solid #fff`}}>{so}</div> : null}
    </div>
  );
};

// ===== Cảnh: đếm token + lưới 20 trang
const Dem: React.FC<{tu: number; den: number; dai: number; a: number}> = ({tu, den, dai, a}) => {
  const frame = useCurrentFrame();
  const v = Math.round(interpolate(frame, [f(a), f(a + dai)], [tu, den], {...kep, easing: (t) => 1 - Math.pow(1 - t, 3)}));
  return <>{v.toLocaleString('de-DE')}</>;
};

// ===== Cảnh: terminal gõ lệnh, nửa dưới là mặt
// Master dọc 1080×1920
const Nguoi: React.FC<{tu: number; co?: number; x?: number; y?: number}> = ({tu, co = 1, x = 540, y = 960}) => (
  <OffthreadVideo src={staticFile('master.mp4')} startFrom={f(tu)} muted style={{position: 'absolute', width: Math.round(1080 * co), height: Math.round(1920 * co), left: Math.round(x - 540 * co), top: Math.round(y - 960 * co), maxWidth: 'none'}} />
);

// ===== Thẻ kho mã nguồn: số liệu lấy thật khi kiểm chứng, không ghi số không có nguồn
const TheRepo: React.FC<{chu: string; ten: string; moTa: string; so: [string, string][]; nhan?: string}> = ({chu, ten, moTa, so, nhan}) => (
  <NenDao>
    <div style={{position: 'absolute', left: 84, right: 84, top: 480}}>
      {nhan ? <Len style={{textAlign: 'center', marginBottom: 32}}><Nhan chu={nhan} cam co={32} /></Len> : null}
      <Len at={0.15}>
        <The style={{padding: '52px 56px 44px', borderRadius: 18, borderBottom: '14px solid #3F7CAC'}}>
          <div style={{fontSize: 62, color: '#33373B', lineHeight: 1.25}}>{chu}/</div>
          <div style={{fontSize: 62, fontWeight: 800, color: '#24282C', lineHeight: 1.25}}>{ten}</div>
          <div style={{fontSize: 30, color: '#6B7178', marginTop: 28, lineHeight: 1.35}}>{moTa}</div>
          <div style={{display: 'flex', gap: 76, marginTop: 44}}>
            {so.map(([a, b]) => <div key={b}><div style={{fontSize: 34, fontWeight: 700, color: '#33373B'}}>{a}</div><div style={{fontSize: 24, color: '#8A9096'}}>{b}</div></div>)}
          </div>
        </The>
      </Len>
    </div>
  </NenDao>
);

const Terminal: React.FC<{dai: number; lenh: string; chuChay?: string}> = ({dai, lenh, chuChay = '→ Đang chạy'}) => {
  const frame = useCurrentFrame();
  const so = Math.round(interpolate(frame, [f(0.15), f(dai * 0.45)], [0, lenh.length], kep));
  const chay = interpolate(frame, [f(dai * 0.5), f(dai * 0.92)], [0, 100], kep);
  return (
    <NenDao>
      <Len style={{position: 'absolute', left: 60, right: 60, top: 420}}>
        <div style={{height: 400, borderRadius: 30, background: '#111827', boxShadow: '0 30px 70px rgba(17,24,39,0.35)', overflow: 'hidden', fontFamily: 'Consolas, monospace'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '22px 28px', background: '#1B2433'}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <div key={c} style={{width: 18, height: 18, borderRadius: 99, background: c}} />)}
            <span style={{color: '#9AA4B2', fontSize: 26, marginLeft: 14, fontFamily: FONT, fontWeight: 600}}>Terminal</span>
          </div>
          <div style={{padding: '34px 30px', fontSize: 37, color: '#E5E9F0'}}>
            <span style={{color: CAM2}}>$ </span>{lenh.slice(0, so)}{so < lenh.length && frame % 16 < 8 ? '▌' : ''}
            {chay > 0 ? (
              <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 34, fontSize: 28, color: '#9AA4B2'}}>
                <span>{chuChay}</span>
                <div style={{flex: 1, height: 14, borderRadius: 99, background: '#2A3445', overflow: 'hidden'}}><div style={{width: `${chay}%`, height: '100%', background: CAM}} /></div>
                <span>{Math.round(chay)}%</span>
              </div>
            ) : null}
          </div>
        </div>
      </Len>
      <div style={{position: 'absolute', left: 455, top: 880}}><LinhVat co={0.95} mat={chay >= 100 ? 'vui' : 'thuong'} /></div>
    </NenDao>
  );
};

// ===== Cảnh mở đầu và chữ lớn trên cảnh Flow
// Nhãn này che logo Flow ở góc clip (nghiem_thu.py kiểm VUNG_NHAN_GOC). Watermark của bước nhan-dien phủ đúng khung này, không bỏ nhãn.
const NhanGoc: React.FC = () => (
  <div style={{position: 'absolute', right: 24, top: 1668, width: 300, height: 112, boxSizing: 'border-box', paddingTop: KENH.nhanCanhAI ? 16 : 34, textAlign: 'center', background: 'rgba(18,12,8,0.96)', borderRadius: 22, border: `3px solid ${CAM}`, fontFamily: FONT}}>
    <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: KENH.ten.length <= 10 ? 36 : Math.max(20, Math.round(360 / KENH.ten.length)), color: '#fff', lineHeight: 1.25, whiteSpace: 'nowrap'}}>{KENH.ten}</div>
    {KENH.nhanCanhAI ? <div style={{fontWeight: 700, fontSize: 24, color: '#FFD9C2', marginTop: 4}}>{KENH.nhanCanhAI}</div> : null}
  </div>
);

const Clip: React.FC<{ten: string; tuGiay?: number}> = ({ten, tuGiay = 0}) => (
  <OffthreadVideo src={staticFile(`canh/${ten}.mp4`)} startFrom={f(tuGiay)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
);

const ChuLon: React.FC<{tren: string; duoi?: string; y?: number; at?: number; nen?: boolean}> = ({tren, duoi, y = 1120, at = 0.15, nen}) => {
  const v = useLen(at);
  const dam = {fontFamily: fontTieuDe, fontWeight: 900, fontStyle: 'italic', fontSize: 104, lineHeight: 1.3, letterSpacing: -1.5, textShadow: '0 10px 34px rgba(0,0,0,0.75)'} as const;
  return (
    <div style={{position: 'absolute', left: 30, right: 30, top: y, textAlign: 'center', opacity: v, transform: `scale(${interpolate(v, [0, 1], [1.25, 1])})`}}>
      <div style={nen ? {display: 'inline-block', padding: '10px 34px 16px', borderRadius: 30, background: 'rgba(16,10,8,0.74)'} : undefined}>
        <div style={{...dam, color: '#fff', ...(nen ? {fontSize: 92} : {})}}>{tren}</div>
        {duoi ? <div style={{...dam, color: nen ? '#FF7A4D' : '#FF3B2F', textShadow: '0 0 40px rgba(255,40,30,0.7), 0 10px 34px rgba(0,0,0,0.7)', ...(nen ? {fontSize: 92, textShadow: 'none'} : {})}}>{duoi}</div> : null}
      </div>
    </div>
  );
};

const FlowChu: React.FC<{ten: string; tren: string; duoi?: string; y?: number; nen?: boolean; tuGiay?: number}> = ({ten, tren, duoi, y, nen, tuGiay}) => (
  <AbsoluteFill style={{background: '#000'}}><Clip ten={ten} tuGiay={tuGiay} /><AbsoluteFill style={{background: 'linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,0.25))'}} /><NhanGoc /><ChuLon tren={tren} duoi={duoi} y={y} nen={nen} /></AbsoluteFill>
);

const NguoiToanMan: React.FC<{nguon: number; children?: React.ReactNode}> = ({nguon, children}) => (
  <AbsoluteFill style={{background: '#111'}}><Nguoi tu={nguon} />{children}</AbsoluteFill>
);

// Tên công cụ: nền mờ cảnh Flow + chữ lớn + con trỏ bấm
const TenCongCu: React.FC<{ten: string; dai: number; nhan: string; nen: string}> = ({ten, dai, nhan, nen}) => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [f(dai * 0.3), f(dai * 0.55)], [860, 620], {...kep, easing: (t) => 1 - Math.pow(1 - t, 3)});
  const bam = frame > f(dai * 0.58);
  return (
    <AbsoluteFill style={{background: '#000', fontFamily: FONT}}>
      <div style={{position: 'absolute', inset: -40, filter: 'blur(20px)'}}><Clip ten={nen} /></div>
      <AbsoluteFill style={{background: 'rgba(30,14,6,0.4)'}} />
      <div style={{position: 'absolute', left: 40, right: 40, top: 620, textAlign: 'center'}}>
        <Len><div style={{fontFamily: fontTieuDe, fontWeight: 900, fontStyle: 'italic', fontSize: 84, color: '#fff', textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>{nhan}</div></Len>
        <div style={{display: 'inline-block', marginTop: 36, padding: '30px 58px', borderRadius: 30, background: bam ? CAM : '#fff', color: bam ? '#fff' : CAM, fontFamily: fontTieuDe, fontWeight: 900, fontSize: 104, transform: `scale(${bam ? 1.04 : 1})`, boxShadow: '0 26px 70px rgba(0,0,0,0.45)'}}>{ten}</div>
      </div>
      <svg width="110" height="140" viewBox="0 0 24 30" style={{position: 'absolute', left: x, top: 860, transform: `scale(${bam ? 0.88 : 1})`, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.5))'}}><path d="M2 1 L2 23 L8 18 L12 28 L16 26 L12 17 L20 17 Z" fill="#fff" stroke="#111" strokeWidth="1.6" strokeLinejoin="round" /></svg>
      <NhanGoc />
    </AbsoluteFill>
  );
};

// Kết: mặt thật, phía trên câu hỏi và khung chỉ về bình luận ghim, giữ khung cuối khi hết tiếng.
// Từ 16/11/2026 bỏ "COMMENT: <từ khóa>" (xin bình luận đổi tài liệu bị Meta coi là kéo tương tác).
// Từ khóa cũ một chữ (CÀI, MẪU...) bị bỏ qua để dựng lại video cũ không phải sửa canh.json.
const Ket: React.FC<{tu: number; hetTieng: number; tuKhoa?: string; nhan: string; tieuDe: string; clip?: string}> = ({tu, hetTieng, tuKhoa, nhan, tieuDe, clip}) => {
  const frame = useCurrentFrame();
  const chuGhim = tuKhoa && tuKhoa.trim().includes(' ') ? tuKhoa : 'XEM BÌNH LUẬN GHIM';
  const conTieng = frame < f(hetTieng - tu);
  return (
    <AbsoluteFill style={{background: '#111', fontFamily: FONT}}>
      {clip ? <><Clip ten={clip} /><NhanGoc /></> : conTieng ? <Nguoi tu={tu} /> : <Img src={staticFile('khung-cuoi.jpg')} style={{width: '100%', height: '100%'}} />}
      <Len at={0.1} style={{position: 'absolute', left: 90, right: 90, top: 110}}>
        <div style={{background: 'linear-gradient(120deg,#FFF9EE,#FFF1D6)', borderRadius: 20, padding: '24px 34px', boxShadow: '0 24px 60px rgba(60,20,0,0.35)', display: 'flex', alignItems: 'center', gap: 24}}>
          <div style={{flex: 1}}><div style={{fontSize: 24, fontWeight: 700, color: CAM, letterSpacing: 2}}>{nhan}</div><div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 50, color: DAM, lineHeight: 1.25}}>{tieuDe}</div></div>
          <div style={{background: DAM, color: '#fff', padding: '10px 18px', borderRadius: 12, fontFamily: fontTieuDe, fontWeight: 900, fontSize: 30, textAlign: 'center', lineHeight: 1.25, maxWidth: 170}}>{KENH.ten}</div>
        </div>
      </Len>
      <Len at={0.4} style={{position: 'absolute', left: 0, right: 0, top: 340, textAlign: 'center'}}>
        <div style={{display: 'inline-block', padding: '16px 44px', borderRadius: 26, background: CAM, fontFamily: fontTieuDe, fontWeight: 900, fontStyle: 'italic', fontSize: chuGhim.length > 14 ? 62 : 76, color: '#fff', boxShadow: '0 20px 50px rgba(0,0,0,0.4)'}}>{chuGhim}</div>
      </Len>
    </AbsoluteFill>
  );
};

// ===== Bộ mô hình dạng "review công cụ" (video 03). Các thẻ hiện dần theo mốc lời, mốc tính bằng giây từ đầu cảnh.
const XANH = '#14915A';
const DO = '#D1341F';
const VANG = '#E39A12';

const TroiNhe: React.FC<{dai: number; children: React.ReactNode}> = ({dai, children}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [0, f(dai)], [1, 1.045], kep);
  return <AbsoluteFill style={{transform: `scale(${v})`, transformOrigin: '50% 40%'}}>{children}</AbsoluteFill>;
};

// Linh vật đứng dưới cụm thẻ, vào sau cảnh một nhịp
const LinhVatDung: React.FC<{y: number; co?: number; mat?: 'thuong' | 'x' | 'vui' | 'dung'}> = ({y, co = 0.85, mat}) => (
  <Len at={0.5} style={{position: 'absolute', left: 540 - 85 * co, top: y}}><LinhVat co={co} mat={mat} /></Len>
);

const TieuDe: React.FC<{tren: string; duoi: string; y?: number; mau?: string}> = ({tren, duoi, y = 170, mau = CAM}) => {
  const toi = useContext(KieuNen) === 'toi';
  return (
    <Len style={{position: 'absolute', left: 40, right: 40, top: y, textAlign: 'center', fontFamily: fontTieuDe, fontWeight: 900, fontSize: 84, lineHeight: 1.24, letterSpacing: -1}}>
      <div style={{color: toi ? '#fff' : DAM}}>{tren}</div>
      <div style={{color: toi ? CAM2 : mau}}>{duoi}</div>
    </Len>
  );
};

const ChuTrenTran: React.FC<{tren: string; duoi?: string; at?: number}> = ({tren, duoi, at = 0}) => <ChuLon tren={tren} duoi={duoi} y={200} at={at} nen />;

// Mặt thật, phía trên là hai thẻ số chạy lên
const TheSo: React.FC<{hinh: string; so: number; ten: string; at: number; dai: number; them?: string}> = ({hinh, so, ten, at, dai, them = ''}) => (
  <Len at={at} style={{flex: 1}}>
    <The style={{padding: '30px 26px', textAlign: 'center', borderRadius: 28}}>
      <div style={{fontSize: 46, color: CAM, lineHeight: 1, fontWeight: 800}}>{hinh}</div>
      <div style={{fontWeight: 800, fontSize: 86, color: DAM, letterSpacing: -2, lineHeight: 1.25, marginTop: 8}}><Dem tu={0} den={so} dai={dai} a={at} />{them}</div>
      <div style={{fontWeight: 600, fontSize: 32, color: '#6F6964'}}>{ten}</div>
    </The>
  </Len>
);

const NguoiSo: React.FC<{nguon: number; moc: number[]; the: {hinh: string; so: number; ten: string; them?: string}[]}> = ({nguon, moc, the}) => (
  <NguoiToanMan nguon={nguon}>
    <div style={{position: 'absolute', left: 70, right: 70, top: 230, display: 'flex', gap: 30, fontFamily: FONT}}>
      {the.map((x, i) => <TheSo key={x.ten} {...x} at={moc[i]} dai={i === 0 ? 1.2 : 1.0} />)}
    </div>
  </NguoiToanMan>
);

const BieuTuong: React.FC<{loai: string; mau: string}> = ({loai, mau}) => {
  const n = {fill: 'none', stroke: mau, strokeWidth: 5, strokeLinecap: 'round', strokeLinejoin: 'round'} as const;
  const hinh: Record<string, React.ReactNode> = {
    'y-tuong': <><path d="M30 44 C18 36 18 14 36 12 C54 14 54 36 42 44 L42 50 L30 50 Z" {...n} /><path d="M31 58 H41" {...n} /></>,
    viet: <><path d="M14 58 L18 44 L48 14 L58 24 L28 54 Z" {...n} /><path d="M42 20 L52 30" {...n} /></>,
    'nhan-vat': <><circle cx="36" cy="24" r="12" {...n} /><path d="M14 60 C16 44 56 44 58 60" {...n} /></>,
    anh: <><rect x="12" y="16" width="48" height="40" rx="6" {...n} /><circle cx="26" cy="30" r="5" {...n} /><path d="M14 52 L30 38 L42 48 L50 42 L58 50" {...n} /></>,
    clip: <><rect x="10" y="18" width="52" height="36" rx="7" {...n} /><path d="M31 28 L45 36 L31 44 Z" {...n} /></>,
    mic: <><rect x="27" y="10" width="18" height="32" rx="9" {...n} /><path d="M18 34 C18 56 54 56 54 34 M36 50 V62" {...n} /></>,
    ghep: <><rect x="10" y="14" width="32" height="28" rx="5" {...n} /><rect x="30" y="30" width="32" height="28" rx="5" {...n} /></>,
    thumb: <><rect x="10" y="16" width="52" height="40" rx="6" {...n} /><path d="M18 28 H42 M18 38 H34" {...n} /></>,
    terminal: <><rect x="8" y="14" width="56" height="44" rx="7" {...n} /><path d="M20 28 L30 36 L20 44 M36 46 H50" {...n} /></>,
    duyet: <><circle cx="36" cy="36" r="26" {...n} /><path d="M24 37 L33 46 L49 27" {...n} /></>,
    doc: <><path d="M18 8 H42 L56 22 V64 H18 Z" {...n} /><path d="M42 8 V22 H56 M27 36 H47 M27 47 H47" {...n} /></>,
    yt: <><rect x="8" y="16" width="56" height="40" rx="12" fill={mau} /><path d="M31 27 L46 36 L31 45 Z" fill="#fff" /></>,
  };
  return <svg width="72" height="72" viewBox="0 0 72 72">{hinh[loai]}</svg>;
};

const DayChuyen: React.FC<{moc: number[]; tren: string; duoi: string; buoc: [string, string][]}> = ({moc, tren, duoi, buoc}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const so = moc.filter((x) => t >= x).length;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 440, display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 26}}>
        {buoc.map(([k, ten], i) => {
          const sang = i < so;
          const yt = k === 'yt';
          const moi = i === so - 1;
          return (
            <The key={k} style={{height: 230, borderRadius: 26, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, opacity: sang ? 1 : 0.42, border: `4px solid ${moi ? (yt ? DO : CAM) : 'transparent'}`, boxSizing: 'border-box', transform: `scale(${moi ? 1.05 : 1})`, boxShadow: moi ? '0 22px 60px rgba(216,76,11,0.28)' : BONG}}>
              <BieuTuong loai={k} mau={sang ? (yt ? DO : CAM) : '#C9C2BC'} />
              <div style={{fontWeight: 700, fontSize: 34, color: sang ? DAM : XAM}}>{ten}</div>
            </The>
          );
        })}
      </div>
      <LinhVatDung y={1186} co={0.74} mat={so >= buoc.length ? 'vui' : 'thuong'} />
    </NenDao>
  );
};

const OKhoNhat: React.FC<{ten: string; nhan: string; at: number; mo?: boolean; mo2: number}> = ({ten, nhan, at, mo, mo2}) => (
  <Len at={at} style={{width: 410}}>
    <The style={{padding: 12, borderRadius: 26}}>
      <div style={{height: 560, borderRadius: 16, overflow: 'hidden', position: 'relative', background: '#222'}}>
        <div style={{width: '100%', height: '100%', transform: 'scale(1.32)', transformOrigin: '35% 12%', filter: mo ? `blur(${mo2 * 16}px) hue-rotate(${mo2 * 40}deg)` : undefined}}><Clip ten={ten} /></div>
        {mo ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: fontTieuDe, fontWeight: 900, fontSize: 170, color: '#fff', opacity: mo2, textShadow: '0 10px 40px rgba(0,0,0,0.6)'}}>?</div> : null}
      </div>
      <div style={{fontWeight: 800, fontSize: 38, textAlign: 'center', padding: '12px 0 4px', color: mo ? DO : DAM}}>{nhan}</div>
    </The>
  </Len>
);

const KhoNhat: React.FC<{moc: number[]; tren: string; duoi: string; o: [{ten: string; nhan: string}, {ten: string; nhan: string}]}> = ({moc, tren, duoi, o}) => {
  const frame = useCurrentFrame();
  const lech = interpolate(frame, [f(moc[1]), f(moc[1] + 0.5)], [0, 1], kep);
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={150} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 450, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <OKhoNhat {...o[0]} at={moc[0]} mo2={0} />
        <OKhoNhat {...o[1]} at={moc[0] + 0.3} mo mo2={lech} />
      </div>
    </NenDao>
  );
};

// Ảnh gốc của 1 nhân vật tỏa ra các cảnh. Phóng clip và cắt phần dưới phải để không lộ logo góc.
const OCanh: React.FC<{ten: string; nhan: string; at: number}> = ({ten, nhan, at}) => (
  <Len at={at} style={{width: 296}}>
    <The style={{padding: 10, borderRadius: 22}}>
      <div style={{height: 430, borderRadius: 14, overflow: 'hidden'}}><div style={{width: '100%', height: '100%', transform: 'scale(1.32)', transformOrigin: '35% 12%'}}><Clip ten={ten} /></div></div>
      <div style={{fontWeight: 700, fontSize: 30, textAlign: 'center', padding: '10px 0 4px', color: DAM}}>{nhan}</div>
    </The>
  </Len>
);

const AnhGoc: React.FC<{moc: number[]; tren: string; duoi: string; anh: string; catAnh?: React.CSSProperties; o: {ten: string; nhan: string}[]}> = ({moc, tren, duoi, anh, catAnh, o}) => {
  const frame = useCurrentFrame();
  const day = interpolate(frame, [f(moc[1]), f(moc[1] + 0.6)], [0, 1], kep);
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={120} />
      <Len at={moc[0]} style={{position: 'absolute', left: 390, top: 340}}>
        <div style={{width: 300, height: 300, borderRadius: 40, border: `8px solid ${CAM}`, overflow: 'hidden', boxShadow: '0 26px 70px rgba(216,76,11,0.3)', background: '#fff'}}><Img src={staticFile(anh)} style={{width: '100%', maxWidth: 'none', ...catAnh}} /></div>
      </Len>
      <svg width="1080" height="150" style={{position: 'absolute', left: 0, top: 640}}>
        {[190, 540, 890].map((x) => <path key={x} d={`M540 0 C540 80 ${x} 50 ${x} 145`} fill="none" stroke={CAM} strokeWidth="6" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - day} />)}
      </svg>
      <div style={{position: 'absolute', left: 36, right: 36, top: 790, display: 'flex', justifyContent: 'space-between'}}>
        {o.map((x, i) => <OCanh key={x.ten} {...x} at={moc[1] + 0.2 + i * 0.2} />)}
      </div>
    </NenDao>
  );
};

const TheLop: React.FC<{mau: string; ten: string; phu: string; kyHieu: string; at: number; style?: React.CSSProperties; sang?: boolean; phai?: React.ReactNode}> = ({mau, ten, phu, kyHieu, at, style, sang, phai}) => (
  <Len at={at} style={style}>
    <The style={{display: 'flex', alignItems: 'center', gap: 26, padding: '28px 32px', borderRadius: 28, border: `4px solid ${sang ? mau : 'transparent'}`, boxSizing: 'border-box', height: 170}}>
      <div style={{width: 104, height: 104, flex: 'none', borderRadius: 24, background: mau, color: '#fff', fontWeight: 800, fontSize: 42, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{kyHieu}</div>
      <div style={{flex: 1, minWidth: 0}}><div style={{fontWeight: 800, fontSize: 44, color: DAM, lineHeight: 1.25}}>{ten}</div><div style={{fontWeight: 500, fontSize: 31, color: '#6F6964', marginTop: 4}}>{phu}</div></div>
      {phai}
    </The>
  </Len>
);

// Sơ đồ 3 lớp nối nhau. moc: [lớp 3 hiện, chữ gạch hiện, lớp 2 hiện, lớp 3 sáng, lớp 1 hiện + chạy dây 1, chạy dây 2]
type Lop = {mau: string; ten: string; phu: string; kyHieu: string; phuSau?: string};
const CauNoi: React.FC<{moc: number[]; tren: string; duoi: string; gach?: string; lop: [Lop, Lop, Lop]}> = ({moc, tren, duoi, gach, lop}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const a = interpolate(frame, [f(moc[4]), f(moc[4] + 0.9)], [0, 1], kep);
  const b = interpolate(frame, [f(moc[5]), f(moc[5] + 0.9)], [0, 1], kep);
  const Day: React.FC<{y: number; v: number; hien: boolean}> = ({y, v, hien}) => (
    <div style={{position: 'absolute', left: 536, top: y, width: 8, height: 92, background: '#F3D8C7', borderRadius: 9, opacity: hien ? 1 : 0}}>
      <div style={{width: '100%', height: `${v * 100}%`, background: CAM, borderRadius: 9}} />
      {v > 0 && v < 1 ? <div style={{position: 'absolute', left: -9, top: `${v * 100}%`, width: 26, height: 26, marginTop: -13, borderRadius: 99, background: CAM2, boxShadow: `0 0 22px ${CAM2}`}} /> : null}
    </div>
  );
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} />
      {gach ? <Len at={moc[1]} style={{position: 'absolute', left: 0, right: 0, top: 400, textAlign: 'center'}}>
        <div style={{display: 'inline-block', padding: '12px 34px', borderRadius: 99, background: '#FDE7E2', color: DO, fontWeight: 700, fontSize: 40, textDecoration: 'line-through'}}>{gach}</div>
      </Len> : null}
      <TheLop at={moc[4]} mau={lop[0].mau} ten={lop[0].ten} phu={lop[0].phu} kyHieu={lop[0].kyHieu} sang={t >= moc[4] && t < moc[5]} style={{position: 'absolute', left: 70, right: 70, top: 500}} />
      <Day y={670} v={a} hien={t >= moc[4]} />
      <TheLop at={moc[2]} mau={lop[1].mau} ten={lop[1].ten} phu={lop[1].phu} kyHieu={lop[1].kyHieu} sang={t >= moc[2] && t < moc[4]} style={{position: 'absolute', left: 70, right: 70, top: 762}} />
      <Day y={932} v={b} hien={t >= moc[2]} />
      <TheLop at={moc[0]} mau={lop[2].mau} ten={lop[2].ten} phu={t >= moc[5] && lop[2].phuSau ? lop[2].phuSau : lop[2].phu} kyHieu={lop[2].kyHieu} sang={t >= moc[3]} style={{position: 'absolute', left: 70, right: 70, top: 1024}} />
      <LinhVatDung y={1205} co={0.8} />
    </NenDao>
  );
};

type TheVui = {nhan: string; ten: string; lenh?: string; ketQua?: string};
type TheBuon = {nhan: string; ten: string; dong?: string; canhBao?: string};
const TinVuiBuon: React.FC<{moc: number[]; vui: TheVui; buon: TheBuon}> = ({moc, vui, buon}) => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  return (
    <NenDao>
      <Len at={moc[0]} style={{position: 'absolute', left: 70, right: 70, top: 150}}>
        <The style={{padding: '34px 38px', borderRadius: 30, borderTop: `14px solid ${XANH}`, opacity: t >= moc[1] ? 0.72 : 1}}>
          <span style={{display: 'inline-block', padding: '8px 26px', borderRadius: 99, background: XANH, color: '#fff', fontWeight: 800, fontSize: 32}}>{vui.nhan}</span>
          <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 92, color: DAM, lineHeight: 1.25, marginTop: 8}}>{vui.ten}</div>
          {vui.lenh ? <div style={{marginTop: 14, padding: '20px 24px', borderRadius: 16, background: '#111827', color: '#E5E9F0', fontFamily: 'Consolas, monospace', fontSize: 33}}><span style={{color: CAM2}}>$ </span>{vui.lenh}<br /><span style={{color: '#5ED39B'}}>{vui.ketQua}</span></div> : null}
        </The>
      </Len>
      <Len at={moc[1]} style={{position: 'absolute', left: 70, right: 70, top: 690}}>
        <The style={{padding: '34px 38px', borderRadius: 30, borderTop: `14px solid ${DO}`, boxShadow: '0 26px 70px rgba(209,52,31,0.22)'}}>
          <span style={{display: 'inline-block', padding: '8px 26px', borderRadius: 99, background: DO, color: '#fff', fontWeight: 800, fontSize: 32}}>{buon.nhan}</span>
          <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 66, color: DAM, lineHeight: 1.25, marginTop: 10}}>{buon.ten}</div>
          {buon.dong ? <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 20, padding: '18px 24px', borderRadius: 16, background: '#F4EFEB'}}>
            <div style={{width: 22, height: 22, borderRadius: 99, background: XANH}} />
            <div style={{fontWeight: 600, fontSize: 34, color: DAM}}>{buon.dong}</div>
            <div style={{marginLeft: 'auto', fontWeight: 800, fontSize: 30, color: DO, opacity: t >= moc[2] ? 1 : 0}}>{buon.canhBao}</div>
          </div> : null}
        </The>
      </Len>
      <LinhVatDung y={1240} co={0.95} mat={t >= moc[1] ? 'x' : 'vui'} />
    </NenDao>
  );
};

const DongCanhBao: React.FC<{mau: string; ten: string; phu: string; hien: boolean; moi: boolean}> = ({mau, ten, phu, hien, moi}) => (
  <The style={{display: 'flex', gap: 24, padding: '26px 30px', borderRadius: 26, borderLeft: `16px solid ${hien ? mau : '#E5DED8'}`, opacity: hien ? 1 : 0.32, transform: `scale(${moi ? 1.025 : 1})`, boxShadow: moi ? `0 24px 60px ${mau}44` : BONG}}>
    <div style={{flex: 1}}><div style={{fontWeight: 800, fontSize: 44, color: DAM, lineHeight: 1.2}}>{ten}</div><div style={{fontWeight: 500, fontSize: 35, color: '#6F6964', marginTop: 8, lineHeight: 1.3}}>{phu}</div></div>
  </The>
);

const MAU_MUC: Record<string, string> = {do: DO, vang: VANG, xanh: XANH};
const CanhBao: React.FC<{moc: number[]; tren: string; duoi: string; dong: [string, string, string][]; linhVat?: boolean}> = ({moc, tren, duoi, dong, linhVat}) => {
  const t = useCurrentFrame() / 30;
  const so = moc.filter((x) => t >= x).length;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={120} mau={DO} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 370, display: 'flex', flexDirection: 'column', gap: 22}}>
        {dong.map(([m, a, b], i) => <DongCanhBao key={a} mau={MAU_MUC[m]} ten={a} phu={b} hien={i < so} moi={i === so - 1} />)}
      </div>
      {linhVat === false ? null : <LinhVatDung y={1250} co={0.95} mat={so >= dong.length ? 'dung' : 'x'} />}
    </NenDao>
  );
};

const HaiPhe: React.FC<{moc: number[]; tren: string; duoi: string; phe: [{nhan: string; ten: string; phu: string}, {nhan: string; ten: string; phu: string}]}> = ({moc, tren, duoi, phe}) => {
  const t = useCurrentFrame() / 30;
  const toi = useContext(KieuNen) === 'toi';
  const The1: React.FC<{mau: string; nhan: string; ten: string; phu: string; at: number; mo: boolean}> = ({mau, nhan, ten, phu, at, mo}) => (
    <Len at={at}>
      <The style={{padding: '36px 40px', borderRadius: 30, borderLeft: `16px solid ${mau}`, opacity: mo ? 0.82 : 1}}>
        <span style={{display: 'inline-block', padding: '8px 26px', borderRadius: 99, background: mau, color: '#fff', fontWeight: 800, fontSize: 32}}>{nhan}</span>
        <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 58, color: DAM, lineHeight: 1.25, marginTop: 12}}>{ten}</div>
        <div style={{fontWeight: 500, fontSize: 34, color: '#6F6964', marginTop: 10, lineHeight: 1.3}}>{phu}</div>
      </The>
    </Len>
  );
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} />
      <div style={{position: 'absolute', left: 70, right: 70, top: 450, display: 'flex', flexDirection: 'column', gap: 34}}>
        <The1 mau={XANH} {...phe[0]} at={moc[0]} mo={t >= moc[1]} />
        <The1 mau={DO} {...phe[1]} at={moc[1]} mo={false} />
      </div>
      <LinhVatDung y={1040} co={1} />
    </NenDao>
  );
};

// Kết chia phe: mặt thật, câu hỏi nằm trên khoảng trần, giữ khung cuối khi hết tiếng
const KetPhe: React.FC<{tu: number; hetTieng: number; cauHoi: string; phe: [string, string]}> = ({tu, hetTieng, cauHoi, phe}) => {
  const frame = useCurrentFrame();
  const conTieng = frame < f(hetTieng - tu);
  return (
    <AbsoluteFill style={{background: '#111', fontFamily: FONT}}>
      {conTieng ? <Nguoi tu={tu} /> : <Img src={staticFile('khung-cuoi.jpg')} style={{width: '100%', height: '100%'}} />}
      <Len at={0.1} style={{position: 'absolute', left: 0, right: 0, top: 190, textAlign: 'center'}}>
        <div style={{display: 'inline-block', padding: '18px 44px', borderRadius: 26, background: CAM, fontFamily: fontTieuDe, fontWeight: 900, fontSize: 72, color: '#fff', boxShadow: '0 20px 50px rgba(0,0,0,0.4)'}}>{cauHoi}</div>
      </Len>
      <Len at={0.5} style={{position: 'absolute', left: 0, right: 0, top: 350, display: 'flex', justifyContent: 'center', gap: 26}}>
        <div style={{padding: '14px 36px', borderRadius: 99, background: XANH, color: '#fff', fontWeight: 800, fontSize: 38}}>{phe[0]}</div>
        <div style={{padding: '14px 36px', borderRadius: 99, background: DO, color: '#fff', fontWeight: 800, fontSize: 38}}>{phe[1]}</div>
        <div style={{padding: '14px 36px', borderRadius: 99, background: DAM, color: '#fff', fontFamily: fontTieuDe, fontWeight: 900, fontSize: 34}}>{KENH.ten}</div>
      </Len>
    </AbsoluteFill>
  );
};

// Ảnh chụp hoặc video quay trang web thật, khung đỏ khoanh chỗ đang nói. x, y, khoanh tính theo pixel trang (rộng 1080).
type Khoanh = {x: number; y: number; w: number; h: number};
const ManWeb: React.FC<{tren?: string; duoi?: string; anh?: string; video?: string; x?: number; y?: number; zoom?: number; cao?: number; khoanh?: Khoanh[]; moc?: number[]; nguon: string}> = ({tren, duoi, anh, video, x = 0, y = 0, zoom = 1, cao = 860, khoanh = [], moc = [], nguon}) => {
  const toi = useContext(KieuNen) === 'toi';
  const s = (980 * zoom) / 1080;
  const noi: React.CSSProperties = {position: 'absolute', left: -x * s, top: -y * s, width: 1080 * s, maxWidth: 'none'};
  return (
    <NenDao>
      {tren ? <TieuDe tren={tren} duoi={duoi ?? ''} y={110} /> : null}
      <Len at={0.1} style={{position: 'absolute', left: 50, right: 50, top: tren ? 340 : 200}}>
        <The style={{height: cao, overflow: 'hidden', position: 'relative', borderRadius: 22}}>
          {video ? <OffthreadVideo src={staticFile(video)} muted style={noi} /> : <Img src={staticFile(anh as string)} style={noi} />}
          {khoanh.map((k, i) => (
            <Len key={i} at={moc[i] ?? 0.5} style={{position: 'absolute', left: (k.x - x) * s - 10, top: (k.y - y) * s - 10, width: k.w * s + 20, height: k.h * s + 20, boxSizing: 'border-box', border: `7px solid ${DO}`, borderRadius: 16, boxShadow: '0 0 34px rgba(209,52,31,0.45)'}}><span /></Len>
          ))}
        </The>
      </Len>
      <div style={{position: 'absolute', left: 0, right: 0, top: (tren ? 340 : 200) + cao + 14, textAlign: 'center', fontFamily: FONT, fontWeight: 600, fontSize: 26, color: toi ? '#D6CFC9' : '#7B756F'}}>{nguon}</div>
    </NenDao>
  );
};

// Cuốn sổ tay: tựa, dòng khi nào, các bước, file mẫu hiện dần theo moc; bước cuối đánh dấu xong
const SoTayCongViec: React.FC<{tren: string; duoi: string; ten: string; khi: string; buoc: string[]; tep?: string; moc: number[]; chu?: string}> = ({tren, duoi, ten, khi, buoc, tep, moc, chu}) => {
  const t = useCurrentFrame() / 30;
  const xong = t >= moc[moc.length - 1];
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <Len at={moc[0]} style={{position: 'absolute', left: 90, right: 90, top: 345}}>
        <div style={{position: 'relative', background: 'linear-gradient(180deg,#FFFBF1,#FFF4DE)', borderRadius: 26, padding: '34px 44px 36px 76px', boxShadow: '0 4px 8px rgba(120,60,20,0.08), 0 30px 70px rgba(150,80,30,0.22)', border: '2px solid #F3E3C6'}}>
          <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 34, borderRadius: '26px 0 0 26px', background: `linear-gradient(180deg,${CAM2},${CAM})`}} />
          {[0.18, 0.5, 0.82].map((y) => <div key={y} style={{position: 'absolute', left: 22, top: `${y * 100}%`, width: 26, height: 26, borderRadius: 99, background: '#fff', border: `4px solid ${DAM}`}} />)}
          <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 52, color: DAM, lineHeight: 1.25}}>{ten}</div>
          <Len at={moc[1] ?? 0.3} style={{marginTop: 14, display: 'inline-block', padding: '8px 22px', borderRadius: 99, background: '#FDE7D6', color: CAM, fontWeight: 700, fontSize: 32}}>{khi}</Len>
          <div style={{marginTop: 22}}>
            {buoc.map((b, i) => (
              <Len key={b} at={(moc[2] ?? 0.5) + i * 0.3} style={{display: 'flex', alignItems: 'center', gap: 18, padding: '14px 0', borderBottom: '2px solid #F1E3CB'}}>
                <div style={{flex: 'none', width: 50, height: 50, borderRadius: 99, background: xong ? XANH : CAM, color: '#fff', fontWeight: 800, fontSize: 28, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{xong ? '✓' : i + 1}</div>
                <div style={{fontWeight: 600, fontSize: 38, color: DAM}}>{b}</div>
              </Len>
            ))}
          </div>
          {tep ? <Len at={moc[3] ?? 1} style={{marginTop: 22, display: 'inline-flex', alignItems: 'center', gap: 12, padding: '10px 22px', borderRadius: 14, background: '#fff', border: `3px solid ${CAM2}`, fontWeight: 700, fontSize: 32, color: DAM}}><BieuTuong loai="doc" mau={CAM} />{tep}</Len> : null}
        </div>
      </Len>
      {chu ? <Len at={moc[moc.length - 1]} style={{position: 'absolute', left: 0, right: 0, top: 1145, textAlign: 'center'}}><Nhan chu={chu} cam co={36} /></Len> : null}
      <LinhVatDung y={1235} co={0.8} mat={xong ? 'vui' : 'thuong'} />
    </NenDao>
  );
};

// ===== So sánh trước và sau: thẻ trên mờ đi khi thẻ dưới hiện. moc: [trước, sau]
const TruocSau: React.FC<{tren: string; duoi: string; truoc: {nhan: string; ten: string; dong: string[]}; sau: {nhan: string; ten: string; dong: string[]}; moc: number[]}> = ({tren, duoi, truoc, sau, moc}) => {
  const t = useCurrentFrame() / 30;
  const toi = useContext(KieuNen) === 'toi';
  const The1: React.FC<{mau: string; x: {nhan: string; ten: string; dong: string[]}; dau: string; mo?: boolean}> = ({mau, x, dau, mo}) => (
    <The style={{height: '100%', boxSizing: 'border-box', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: '30px 44px', borderRadius: 30, borderTop: `14px solid ${mau}`, opacity: mo ? (toi ? 0.85 : 0.62) : 1}}>
      <span style={{display: 'inline-block', padding: '10px 32px', borderRadius: 99, background: mau, color: '#fff', fontWeight: 800, fontSize: 40}}>{x.nhan}</span>
      <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 88, color: DAM, lineHeight: 1.25, marginTop: 18}}>{x.ten}</div>
      {x.dong.map((d) => <div key={d} style={{display: 'flex', gap: 14, alignItems: 'baseline', fontWeight: 600, fontSize: 48, color: '#45403C', lineHeight: 1.25, marginTop: 16}}><span style={{color: mau, fontWeight: 900}}>{dau}</span>{d}</div>)}
    </The>
  );
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <div style={{position: 'absolute', left: 70, right: 70, top: 340, height: 990, display: 'flex', flexDirection: 'column', gap: 30}}>
        <Len at={moc[0]} style={{flex: 1, minHeight: 0}}><The1 mau={DO} x={truoc} dau="✕" mo={t >= moc[1]} /></Len>
        <Len at={moc[1]} style={{flex: 1, minHeight: 0}}><The1 mau={XANH} x={sau} dau="✓" /></Len>
      </div>
    </NenDao>
  );
};

// ===== Biểu đồ cột, thanh mọc theo moc, số chạy lên. Chỉ dùng số có nguồn
const BieuDo: React.FC<{tren: string; duoi: string; cot: {ten: string; so: number; donVi?: string; noiBat?: boolean}[]; nguon?: string; moc: number[]}> = ({tren, duoi, cot, nguon, moc}) => {
  const fr = useCurrentFrame();
  const toi = useContext(KieuNen) === 'toi';
  const lon = Math.max(...cot.map((c) => c.so));
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <Len at={0.1} style={{position: 'absolute', left: 70, right: 70, top: 340}}>
        <The style={{padding: '40px 36px 30px', borderRadius: 26}}>
          <div style={{display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: 780, gap: 22, borderBottom: '3px solid #EFE7E0'}}>
            {cot.map((c, i) => {
              const a = moc[i] ?? 0.3 + i * 0.3;
              const v = interpolate(fr, [f(a), f(a + 0.8)], [0, 1], {...kep, easing: (x) => 1 - Math.pow(1 - x, 3)});
              return (
                <div key={c.ten} style={{flex: 1, textAlign: 'center'}}>
                  <div style={{fontWeight: 800, fontSize: 46, color: c.noiBat ? CAM : DAM, opacity: v > 0.05 ? 1 : 0, marginBottom: 8}}>{Math.round(c.so * v).toLocaleString('de-DE')}{c.donVi ?? ''}</div>
                  <div style={{height: (c.so / lon) * 650 * v, borderRadius: '16px 16px 0 0', background: c.noiBat ? `linear-gradient(180deg,${CAM2},${CAM})` : '#E8DDD4'}} />
                </div>
              );
            })}
          </div>
          <div style={{display: 'flex', justifyContent: 'space-around', gap: 22, marginTop: 14}}>{cot.map((c) => <div key={c.ten} style={{flex: 1, textAlign: 'center', fontWeight: 600, fontSize: 34, color: '#6F6964', lineHeight: 1.2}}>{c.ten}</div>)}</div>
        </The>
      </Len>
      {nguon ? <div style={{position: 'absolute', left: 0, right: 0, top: 1335, textAlign: 'center', fontFamily: FONT, fontWeight: 600, fontSize: 28, color: toi ? '#D6CFC9' : '#7B756F'}}>{nguon}</div> : null}
    </NenDao>
  );
};

// ===== Danh sách bước cài: đánh dấu xong lần lượt theo moc
const DanhSachBuoc: React.FC<{tren: string; duoi: string; buoc: {ten: string; phu?: string}[]; moc: number[]}> = ({tren, duoi, buoc, moc}) => {
  const t = useCurrentFrame() / 30;
  const so = moc.filter((x) => t >= x).length;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <div style={{position: 'absolute', left: 70, right: 70, top: 340, height: 1040, display: 'flex', flexDirection: 'column', gap: 22}}>
        {buoc.map((b, i) => {
          const sang = i < so;
          const moi = i === so - 1;
          return (
            <The key={b.ten} style={{flex: 1, maxHeight: 250, display: 'flex', alignItems: 'center', gap: 28, padding: '22px 34px', borderRadius: 28, opacity: sang ? 1 : 0.4, transform: `scale(${moi ? 1.025 : 1})`, border: `4px solid ${moi ? CAM : 'transparent'}`, boxSizing: 'border-box'}}>
              <div style={{flex: 'none', width: 92, height: 92, borderRadius: 99, background: sang ? (moi ? CAM : XANH) : '#E8DDD4', color: '#fff', fontWeight: 900, fontSize: 46, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{sang && !moi ? '✓' : i + 1}</div>
              <div style={{flex: 1, minWidth: 0}}><div style={{fontWeight: 800, fontSize: 52, color: DAM, lineHeight: 1.25}}>{b.ten}</div>{b.phu ? <div style={{fontWeight: 500, fontSize: 36, color: '#6F6964', marginTop: 4}}>{b.phu}</div> : null}</div>
            </The>
          );
        })}
      </div>
    </NenDao>
  );
};

// ===== Bảng màu: trang web thu nhỏ tô bằng đúng bộ màu, chữ Minh họa để không đóng giả giao diện thật
type TrangMau = {nhan: string; ten: string; mau: string[]; nen?: string; chuTrang?: boolean; serif?: boolean; tranh?: string[]; ghi?: string};
const BangMau: React.FC<{tren: string; duoi: string; trang: TrangMau[]; nguon?: string; moc: number[]}> = ({tren, duoi, trang, nguon, moc}) => {
  const fr = useCurrentFrame();
  const toi = useContext(KieuNen) === 'toi';
  const mot = trang.length === 1;
  const cao = mot ? 660 : 470;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <div style={{position: 'absolute', left: 60, right: 60, top: mot ? 400 : 345, display: 'flex', flexDirection: 'column', gap: 26}}>
        {trang.map((t, i) => {
          const at = moc[i] ?? 0.2 + i * 0.4;
          const chu = t.chuTrang ? '#fff' : t.mau[4];
          const nhat = t.chuTrang ? 'rgba(255,255,255,0.28)' : `${t.mau[4]}22`;
          return (
            <Len key={t.nhan} at={at}>
              <The style={{height: cao, boxSizing: 'border-box', padding: 24, borderRadius: 30, display: 'flex', gap: 28}}>
                <div style={{flex: 'none', width: mot ? 470 : 410, borderRadius: 20, overflow: 'hidden', background: t.nen ?? t.mau[3], padding: 26, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', position: 'relative', border: '2px solid rgba(0,0,0,0.07)'}}>
                  <div style={{display: 'flex', gap: 8, marginBottom: 22}}>{[0, 1, 2].map((k) => <div key={k} style={{width: 14, height: 14, borderRadius: 99, background: nhat}} />)}</div>
                  <div style={{fontFamily: t.serif ? 'Georgia, serif' : FONT, fontWeight: t.serif ? 700 : 900, fontSize: mot ? 58 : 46, lineHeight: 1.2, color: chu}}>{t.ten}</div>
                  <div style={{height: 14, width: '86%', borderRadius: 9, background: nhat, marginTop: 18}} />
                  <div style={{height: 14, width: '62%', borderRadius: 9, background: nhat, marginTop: 10}} />
                  <div style={{alignSelf: 'flex-start', marginTop: 20, padding: '12px 30px', borderRadius: t.serif ? 99 : 14, background: t.chuTrang ? '#fff' : t.mau[0], color: t.chuTrang ? t.mau[0] : (t.mau[5] ?? '#fff'), fontWeight: 800, fontSize: 26}}>Bắt đầu</div>
                  <div style={{flex: 1}} />
                  <div style={{display: 'flex', gap: 12, marginBottom: 26}}>{[0, 1, 2].map((k) => <div key={k} style={{flex: 1, height: mot ? 150 : 74, borderRadius: 12, background: t.chuTrang ? 'rgba(255,255,255,0.2)' : '#fff', borderTop: `6px solid ${t.mau[k === 1 ? 1 : k === 2 ? 2 : 0]}`, boxShadow: '0 4px 14px rgba(0,0,0,0.08)'}} />)}</div>
                  <div style={{position: 'absolute', right: 14, bottom: 8, fontWeight: 600, fontSize: 22, color: chu, opacity: 0.75}}>Minh họa</div>
                </div>
                <div style={{flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                  <div style={{fontFamily: fontTieuDe, fontWeight: 900, fontSize: 50, color: DAM, lineHeight: 1.25}}>{t.nhan}</div>
                  <div style={{display: 'flex', gap: 10, marginTop: 16}}>
                    {t.mau.slice(0, 5).map((m, k) => {
                      const v = interpolate(fr, [f(at + 0.25 + k * 0.1), f(at + 0.5 + k * 0.1)], [0, 1], kep);
                      return <div key={k} style={{width: 66, height: 66, borderRadius: 99, background: m, border: '3px solid #EFE7E0', boxSizing: 'border-box', transform: `scale(${v})`}} />;
                    })}
                  </div>
                  {t.tranh?.length ? <div style={{marginTop: 22, fontWeight: 800, fontSize: 30, color: DO}}>Dặn tránh</div> : null}
                  {t.tranh?.map((x) => <div key={x} style={{fontWeight: 600, fontSize: 32, color: '#4F4A46', lineHeight: 1.3, marginTop: 4}}>✕ {x}</div>)}
                  {t.ghi ? <div style={{marginTop: 22, fontWeight: 600, fontSize: 38, color: '#4F4A46', lineHeight: 1.32}}>{t.ghi}</div> : null}
                </div>
              </The>
            </Len>
          );
        })}
      </div>
      {nguon ? <div style={{position: 'absolute', left: 0, right: 0, top: 1335, textAlign: 'center', fontWeight: 600, fontSize: 28, color: toi ? '#D6CFC9' : '#7B756F'}}>{nguon}</div> : null}
    </NenDao>
  );
};

// ===== Lưới thẻ: nhiều tên chia nhóm màu, sang là các đợt thẻ sáng theo moc, thẻ còn lại mờ đi
const MAU_NHOM = ['#E8540F', '#2563EB', '#14915A', '#7C3AED', '#D97706'];
const LuoiThe: React.FC<{tren: string; duoi: string; nhom: {ten: string; o: string[]}[]; sang?: string[][]; moc: number[]}> = ({tren, duoi, nhom, sang = [], moc}) => {
  const fr = useCurrentFrame();
  const t = fr / 30;
  const toi = useContext(KieuNen) === 'toi';
  const dot = moc.filter((x) => t >= x).length;
  const dang = dot > 0 ? sang[dot - 1] : undefined;
  let stt = 0;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <div style={{position: 'absolute', left: 50, right: 50, top: 345, display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16}}>
        {nhom.flatMap((n, i) => n.o.map((ten) => {
          const k = stt++;
          const v = interpolate(fr, [k * 0.8, k * 0.8 + 7], [0, 1], kep);
          const bat = !dang || dang.includes(ten);
          const vuaBat = dang && bat;
          return (
            <div key={ten} style={{height: 152, boxSizing: 'border-box', padding: '10px 8px', borderRadius: 22, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', background: vuaBat ? MAU_NHOM[i] : (toi ? 'rgba(255,255,255,0.09)' : '#fff'), border: `4px solid ${MAU_NHOM[i]}`, color: vuaBat ? '#fff' : (toi ? '#fff' : DAM), fontWeight: 800, fontSize: ten.length > 11 ? 31 : 37, lineHeight: 1.22, opacity: v * (bat ? 1 : 0.2), transform: `scale(${(0.8 + v * 0.2) * (vuaBat ? 1.03 : 1)})`, boxShadow: vuaBat ? '0 12px 30px rgba(0,0,0,0.22)' : 'none'}}>{ten}</div>
          );
        }))}
      </div>
    </NenDao>
  );
};

// ===== Khối nối dây: các khối hiện theo moc, dây nối chạy xung sáng; loi đánh dấu một khối hỏng rồi được sửa. Có chữ Minh họa
const KhoiNoi: React.FC<{tren: string; duoi: string; khoi: {ten: string; phu?: string}[]; moc: number[]; loi?: {o: number; tu: number; den: number; nhan?: string; xong?: string}}> = ({tren, duoi, khoi, moc, loi}) => {
  const fr = useCurrentFrame();
  const t = fr / 30;
  const toi = useContext(KieuNen) === 'toi';
  const R = 800, C = 180, B = 250, X = [70, 210];
  const vt = (i: number) => ({x: X[i % 2], y: 365 + i * B});
  const chay = moc[khoi.length];
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
        {khoi.slice(1).map((_, i) => {
          const a = vt(i), b = vt(i + 1), at = moc[i + 1] ?? 0;
          const x1 = a.x + R / 2, y1 = a.y + C, x2 = b.x + R / 2, y2 = b.y;
          const v = interpolate(fr, [f(at), f(at + 0.35)], [0, 1], kep);
          const d = `M${x1} ${y1} C${x1} ${y1 + 40},${x2} ${y2 - 40},${x2} ${y2}`;
          const p = chay !== undefined ? ((t - chay - i * 0.25) % 0.75) / 0.75 : -1;
          return (
            <g key={i} opacity={v}>
              <path d={d} fill="none" stroke={CAM} strokeWidth={7} strokeLinecap="round" />
              {chay !== undefined && t >= chay + i * 0.25 ? <circle cx={x1 + (x2 - x1) * p} cy={y1 + (y2 - y1) * p} r={15} fill="#fff" stroke={CAM} strokeWidth={6} /> : null}
            </g>
          );
        })}
      </svg>
      {khoi.map((k, i) => {
        const p = vt(i);
        const dangLoi = loi && loi.o === i && t >= loi.tu && t < loi.den;
        const daSua = loi && loi.o === i && t >= loi.den;
        const vien = dangLoi ? DO : daSua ? XANH : CAM;
        return (
          <Len key={k.ten} at={moc[i] ?? 0} style={{position: 'absolute', left: p.x, top: p.y, width: R}}>
            <The style={{height: C, boxSizing: 'border-box', borderRadius: 26, border: `5px solid ${vien}`, display: 'flex', alignItems: 'center', gap: 26, padding: '0 34px'}}>
              <div style={{flex: 'none', width: 96, height: 96, borderRadius: 22, background: vien, color: '#fff', fontWeight: 900, fontSize: 50, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{dangLoi ? '!' : daSua ? '✓' : i + 1}</div>
              <div style={{flex: 1, minWidth: 0}}><div style={{fontWeight: 800, fontSize: 50, color: DAM, lineHeight: 1.25}}>{k.ten}</div>{k.phu ? <div style={{fontWeight: 500, fontSize: 33, color: dangLoi ? DO : '#6F6964'}}>{dangLoi ? loi?.nhan ?? k.phu : daSua ? loi?.xong ?? k.phu : k.phu}</div> : null}</div>
            </The>
          </Len>
        );
      })}
      <div style={{position: 'absolute', left: 0, right: 0, top: 365 + khoi.length * B - 30, textAlign: 'center', fontWeight: 600, fontSize: 28, color: toi ? '#D6CFC9' : '#7B756F'}}>Minh họa</div>
    </NenDao>
  );
};

// ===== Khung chat minh họa: tin nhắn hiện theo moc, chỉ để giải thích, không đóng giả giao diện thật
const KhungChat: React.FC<{tren: string; duoi: string; ten: string; tin: {ai?: boolean; chu: string}[]; moc: number[]}> = ({tren, duoi, ten, tin, moc}) => {
  const t = useCurrentFrame() / 30;
  const fr = useCurrentFrame();
  const dangGo = moc.some((x, i) => tin[i]?.ai && t >= x - 0.6 && t < x);
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <Len at={0.1} style={{position: 'absolute', left: 70, right: 70, top: 340}}>
        <The style={{overflow: 'hidden', borderRadius: 30}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '20px 28px', background: '#fff', borderBottom: '2px solid #F4E4D8'}}><div style={{width: 18, height: 18, borderRadius: 99, background: XANH}} /><div style={{fontWeight: 800, fontSize: 38, color: DAM}}>{ten}</div><div style={{marginLeft: 'auto', fontSize: 26, fontWeight: 600, color: XAM}}>Minh họa</div></div>
          <div style={{height: 800, background: '#FFF8F3', padding: 30, boxSizing: 'border-box', display: 'flex', flexDirection: 'column', gap: 22, justifyContent: 'flex-end', overflow: 'hidden'}}>
            {tin.map((m, i) => t >= (moc[i] ?? 0) ? (
              <Len key={i} at={moc[i] ?? 0} style={{alignSelf: m.ai ? 'flex-start' : 'flex-end', maxWidth: '84%'}}>
                <div style={{padding: '22px 30px', borderRadius: 26, background: m.ai ? '#fff' : CAM, color: m.ai ? DAM : '#fff', fontWeight: 600, fontSize: tin.length <= 2 ? 52 : 42, lineHeight: 1.28, boxShadow: BONG}}>{m.chu}</div>
              </Len>
            ) : null)}
            {dangGo ? <div style={{alignSelf: 'flex-start', padding: '16px 24px', borderRadius: 22, background: '#fff', display: 'flex', gap: 8}}>{[0, 1, 2].map((k) => <div key={k} style={{width: 14, height: 14, borderRadius: 99, background: CAM2, opacity: 0.4 + 0.6 * Math.abs(Math.sin((fr + k * 6) / 6))}} />)}</div> : null}
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 18, padding: '20px 28px', background: '#fff', borderTop: '2px solid #F4E4D8'}}><div style={{flex: 1, height: 58, borderRadius: 99, background: '#FFF3EA'}} /><div style={{width: 58, height: 58, borderRadius: 99, background: CAM, color: '#fff', fontWeight: 900, fontSize: 32, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>↑</div></div>
        </The>
      </Len>
    </NenDao>
  );
};

// ===== Biểu tượng 3D nền đen lớn giữa khung, chữ trên. anh: đường dẫn trong public/
const BieuTuong3D: React.FC<{anh: string; tren: string; duoi?: string}> = ({anh, tren, duoi}) => {
  const fr = useCurrentFrame();
  const v = spring({frame: fr, fps: 30, config: {damping: 13, stiffness: 120, mass: 0.8}});
  return (
    <AbsoluteFill style={{background: '#000', fontFamily: FONT}}>
      <div style={{position: 'absolute', left: 130, top: 480, width: 820, height: 820, transform: `scale(${interpolate(v, [0, 1], [0.75, 1]) + Math.sin(fr / 26) * 0.012}) translateY(${Math.sin(fr / 20) * 10}px)`, mixBlendMode: 'screen'}}><Img src={staticFile(anh)} style={{width: '100%', height: '100%'}} /></div>
      <ChuLon tren={tren} duoi={duoi} y={160} at={0.05} />
    </AbsoluteFill>
  );
};

// ===== Cây thư mục: các file sáng theo từng đợt. kieu 'cau-truc' (file hiện dần, giải thích cấu trúc)
// hoặc 'chay' (cả cây hiện sẵn, file đang mở viền cam, đã dùng có dấu xanh, file trong tat mờ đi kèm chữ "không mở")
type TepCay = {ten: string; cap?: number; ghi?: string; san?: boolean};
type DotCay = {sang?: string[]; tat?: string[]; nhan?: string};
const BieuTuongTep: React.FC<{ten: string}> = ({ten}) => {
  if (ten.endsWith('/')) {
    return (
      <div style={{position: 'relative', width: 62, height: 50, flex: 'none'}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: 28, height: 12, borderRadius: '6px 6px 0 0', background: CAM}} />
        <div style={{position: 'absolute', left: 0, top: 8, width: 62, height: 42, borderRadius: 8, background: CAM2}} />
      </div>
    );
  }
  const duoi = (ten.split('.').pop() ?? '').toUpperCase().slice(0, 4);
  const mau = duoi === 'MD' ? '#2563EB' : duoi === 'PY' || duoi === 'JS' || duoi === 'SH' ? XANH : '#7C3AED';
  return (
    <div style={{width: 50, height: 62, flex: 'none', borderRadius: 8, background: '#fff', border: `4px solid ${mau}`, boxSizing: 'border-box', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: 6}}>
      <span style={{fontSize: duoi.length > 2 ? 13 : 17, fontWeight: 900, color: mau}}>{duoi}</span>
    </div>
  );
};
const CayThuMuc: React.FC<{tren: string; duoi: string; tep: TepCay[]; dot: DotCay[]; moc: number[]; kieu?: string; minhHoa?: boolean}> = ({tren, duoi, tep, dot, moc, kieu = 'cau-truc', minhHoa}) => {
  const t = useCurrentFrame() / 30;
  const so = moc.filter((x) => t >= x).length;
  const daQua = dot.slice(0, so);
  const hienTai = so ? dot[so - 1] : undefined;
  const chay = kieu === 'chay';
  const caoDong = tep.length > 6 ? 118 : 132;
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <Len at={0.1} style={{position: 'absolute', left: 60, right: 60, top: 340}}>
        <The style={{padding: '18px 26px 22px', borderRadius: 30}}>
          {minhHoa ? <div style={{textAlign: 'right', fontSize: 26, fontWeight: 600, color: XAM, marginBottom: 4}}>Minh họa</div> : null}
          {tep.map((x) => {
            const dangMo = !!hienTai?.sang?.includes(x.ten);
            const daDung = chay && !dangMo && daQua.some((d) => d.sang?.includes(x.ten));
            const tat = daQua.some((d) => d.tat?.includes(x.ten));
            const hien = chay || x.san || daQua.some((d) => d.sang?.includes(x.ten));
            const lucHien = x.san || chay ? 0.1 : moc[dot.findIndex((d) => d.sang?.includes(x.ten))] ?? 0.1;
            const cap = x.cap ?? 0;
            if (!hien) return <div key={x.ten} style={{height: caoDong}} />;
            return (
              <Len key={x.ten} at={lucHien} style={{height: caoDong, display: 'flex', alignItems: 'center'}}>
                <div style={{width: cap * 62, flex: 'none', alignSelf: 'stretch', position: 'relative'}}>
                  {cap ? <div style={{position: 'absolute', right: 14, top: -caoDong / 2 + 8, height: caoDong, width: 30, borderLeft: '4px solid #E6D6C8', borderBottom: '4px solid #E6D6C8', borderBottomLeftRadius: 10}} /> : null}
                </div>
                <div style={{flex: 1, minWidth: 0, display: 'flex', alignItems: 'center', gap: 20, padding: '12px 18px', borderRadius: 20, background: dangMo ? '#FFF1E6' : 'transparent', border: `4px solid ${dangMo ? CAM : 'transparent'}`, boxSizing: 'border-box', opacity: tat ? 0.35 : 1, transform: `scale(${dangMo ? 1.02 : 1})`}}>
                  <BieuTuongTep ten={x.ten} />
                  <div style={{minWidth: 0}}>
                    <div style={{fontFamily: 'Consolas, monospace', fontWeight: 700, fontSize: 40, color: DAM, whiteSpace: 'nowrap', textDecoration: tat ? 'line-through' : 'none'}}>{x.ten}</div>
                    {x.ghi ? <div style={{fontSize: 28, fontWeight: 600, color: '#6F6964'}}>{x.ghi}</div> : null}
                  </div>
                  <div style={{marginLeft: 'auto', flex: 'none'}}>
                    {chay && dangMo ? <span style={{padding: '8px 18px', borderRadius: 99, background: CAM, color: '#fff', fontWeight: 800, fontSize: 26}}>đang mở</span> : null}
                    {daDung ? <span style={{padding: '8px 18px', borderRadius: 99, background: '#E3F4EA', color: XANH, fontWeight: 800, fontSize: 26}}>✓ đã dùng</span> : null}
                    {tat ? <span style={{padding: '8px 18px', borderRadius: 99, background: '#EEE8E3', color: XAM, fontWeight: 800, fontSize: 26}}>không mở</span> : null}
                  </div>
                </div>
              </Len>
            );
          })}
        </The>
      </Len>
      {hienTai?.nhan ? (
        <Len key={so} at={moc[so - 1]} style={{position: 'absolute', left: 60, right: 60, top: 340 + tep.length * caoDong + (minhHoa ? 110 : 80), textAlign: 'center'}}>
          <span style={{display: 'inline-block', padding: '16px 34px', borderRadius: 99, background: DAM, color: '#fff', fontWeight: 800, fontSize: 38}}>{hienTai.nhan}</span>
        </Len>
      ) : null}
    </NenDao>
  );
};

// ===== Khung file mã: soi từng vùng dòng (tu, den đếm từ 1), mỗi vùng một màu và một nhãn, sáng theo moc
const MAU_VUNG = [CAM, '#2563EB', XANH, '#7C3AED'];
const TepMa: React.FC<{tren: string; duoi: string; ten: string; dong: string[]; vung: {tu: number; den: number; nhan: string}[]; moc: number[]}> = ({tren, duoi, ten, dong, vung, moc}) => {
  const t = useCurrentFrame() / 30;
  const so = moc.filter((x) => t >= x).length;
  const mauDong = (s: string) => (s.startsWith('---') ? '#6B7280' : s.startsWith('#') ? CAM2 : '#E5E9F0');
  return (
    <NenDao>
      <TieuDe tren={tren} duoi={duoi} y={110} />
      <Len at={0.1} style={{position: 'absolute', left: 50, right: 50, top: 340}}>
        <div style={{borderRadius: 28, background: '#111827', boxShadow: '0 30px 70px rgba(17,24,39,0.35)', overflow: 'hidden'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '18px 26px', background: '#1B2433'}}>
            {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => <div key={c} style={{width: 16, height: 16, borderRadius: 99, background: c}} />)}
            <span style={{color: '#C9D1DC', fontSize: 28, marginLeft: 14, fontFamily: 'Consolas, monospace', fontWeight: 700}}>{ten}</span>
          </div>
          <div style={{padding: '18px 0 22px', fontFamily: 'Consolas, monospace', fontSize: 33}}>
            {dong.map((s, i) => {
              const k = vung.findIndex((v) => i + 1 >= v.tu && i + 1 <= v.den);
              const bat = k >= 0 && k < so;
              const moi = k === so - 1;
              const mau = k >= 0 ? MAU_VUNG[k % MAU_VUNG.length] : CAM;
              return (
                <div key={i} style={{display: 'flex', alignItems: 'center', minHeight: 52, background: bat ? `${mau}${moi ? '40' : '22'}` : 'transparent', borderLeft: `8px solid ${bat ? mau : 'transparent'}`}}>
                  <span style={{width: 58, flex: 'none', textAlign: 'right', paddingRight: 18, color: '#4B5563', fontSize: 26}}>{i + 1}</span>
                  <span style={{color: s.includes(':') && !s.startsWith(' ') && !s.startsWith('#') ? '#93C5FD' : mauDong(s), whiteSpace: 'pre', opacity: so && !bat ? 0.55 : 1}}>{s}</span>
                </div>
              );
            })}
          </div>
        </div>
      </Len>
      <div style={{position: 'absolute', left: 60, right: 60, top: 340 + 82 + dong.length * 52 + 70, display: 'flex', flexWrap: 'wrap', gap: 16, justifyContent: 'center'}}>
        {vung.slice(0, so).map((v, i) => (
          <Len key={v.nhan} at={moc[i]} style={{padding: '12px 26px', borderRadius: 99, background: MAU_VUNG[i % MAU_VUNG.length], color: '#fff', fontWeight: 800, fontSize: i === so - 1 ? 38 : 32}}><span>{v.nhan}</span></Len>
        ))}
      </div>
    </NenDao>
  );
};

const PhuDe: React.FC<{phuDe: CumPhuDe[]; canh: CanhMoHinh[]}> = ({phuDe, canh}) => {
  const t = useCurrentFrame() / 30;
  const c = phuDe.find((x, i) => t >= x.start && t < (phuDe[i + 1]?.start ?? x.end + 0.4));
  if (!c) return null;
  const hien = canh.find((x) => t >= x.tu && t < x.den);
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top: hien?.viTriPhuDe ?? 1470, textAlign: 'center'}}>
      <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 58, lineHeight: 1.45, color: '#fff', background: 'rgba(70,60,55,0.62)', padding: '6px 20px', borderRadius: 12, WebkitBoxDecorationBreak: 'clone', boxDecorationBreak: 'clone'}}>{c.text}</span>
    </div>
  );
};

const VeCanh: React.FC<{c: CanhMoHinh}> = ({c}) => {
  const dai = c.den - c.tu;
  const nguon = (c.nguon as number) ?? c.tu;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const p = c as any;
  switch (c.loai) {
    case 'nguoi': return <NguoiToanMan nguon={nguon} />;
    case 'nguoi-chu': return <NguoiToanMan nguon={nguon}><ChuTrenTran tren={p.tren} duoi={p.duoi} at={p.at ?? 0} /></NguoiToanMan>;
    case 'nguoi-so': return <NguoiSo nguon={nguon} moc={p.moc} the={p.the} />;
    case 'flow-chu': return <FlowChu ten={p.ten} tren={p.tren} duoi={p.duoi} y={p.y} nen={p.nen} tuGiay={p.tuGiay} />;
    case 'ten-cong-cu': return <TenCongCu ten={p.ten} dai={dai} nhan={p.nhan} nen={p.canhNen} />;
    case 'day-chuyen': return <TroiNhe dai={dai}><DayChuyen moc={p.moc} tren={p.tren} duoi={p.duoi} buoc={p.buoc} /></TroiNhe>;
    case 'hai-o-canh': return <TroiNhe dai={dai}><KhoNhat moc={p.moc} tren={p.tren} duoi={p.duoi} o={p.o} /></TroiNhe>;
    case 'anh-goc': return <TroiNhe dai={dai}><AnhGoc moc={p.moc} tren={p.tren} duoi={p.duoi} anh={p.anh} catAnh={p.catAnh} o={p.o} /></TroiNhe>;
    case 'ba-lop': return <TroiNhe dai={dai}><CauNoi moc={p.moc} tren={p.tren} duoi={p.duoi} gach={p.gach} lop={p.lop} /></TroiNhe>;
    case 'tin-vui-buon': return <TroiNhe dai={dai}><TinVuiBuon moc={p.moc} vui={p.vui} buon={p.buon} /></TroiNhe>;
    case 'canh-bao': return <TroiNhe dai={dai}><CanhBao moc={p.moc} tren={p.tren} duoi={p.duoi} dong={p.dong} linhVat={p.linhVat} /></TroiNhe>;
    case 'hai-phe': return <TroiNhe dai={dai}><HaiPhe moc={p.moc} tren={p.tren} duoi={p.duoi} phe={p.phe} /></TroiNhe>;
    case 'ket-phe': return <KetPhe tu={c.tu} hetTieng={p.hetTieng} cauHoi={p.cauHoi} phe={p.phe} />;
    case 'ket-comment': return <Ket tu={c.tu} hetTieng={p.hetTieng} tuKhoa={p.tuKhoa} nhan={p.nhan} tieuDe={p.tieuDe} clip={p.clip} />;
    case 'man-web': return <TroiNhe dai={dai}><ManWeb tren={p.tren} duoi={p.duoi} anh={p.anh} video={p.video} x={p.x} y={p.y} zoom={p.zoom} cao={p.cao} khoanh={p.khoanh} moc={p.moc} nguon={p.nguon} /></TroiNhe>;
    case 'so-tay': return <TroiNhe dai={dai}><SoTayCongViec tren={p.tren} duoi={p.duoi} ten={p.ten} khi={p.khi} buoc={p.buoc} tep={p.tep} moc={p.moc} chu={p.chu} /></TroiNhe>;
    case 'truoc-sau': return <TroiNhe dai={dai}><TruocSau tren={p.tren} duoi={p.duoi} truoc={p.truoc} sau={p.sau} moc={p.moc} /></TroiNhe>;
    case 'bieu-do': return <TroiNhe dai={dai}><BieuDo tren={p.tren} duoi={p.duoi} cot={p.cot} nguon={p.nguon} moc={p.moc ?? []} /></TroiNhe>;
    case 'danh-sach-buoc': return <TroiNhe dai={dai}><DanhSachBuoc tren={p.tren} duoi={p.duoi} buoc={p.buoc} moc={p.moc} /></TroiNhe>;
    case 'khung-chat': return <TroiNhe dai={dai}><KhungChat tren={p.tren} duoi={p.duoi} ten={p.ten} tin={p.tin} moc={p.moc} /></TroiNhe>;
    case 'bang-mau': return <TroiNhe dai={dai}><BangMau tren={p.tren} duoi={p.duoi} trang={p.trang} nguon={p.nguon} moc={p.moc ?? []} /></TroiNhe>;
    case 'luoi-the': return <TroiNhe dai={dai}><LuoiThe tren={p.tren} duoi={p.duoi} nhom={p.nhom} sang={p.sang} moc={p.moc ?? []} /></TroiNhe>;
    case 'khoi-noi': return <TroiNhe dai={dai}><KhoiNoi tren={p.tren} duoi={p.duoi} khoi={p.khoi} moc={p.moc ?? []} loi={p.loi} /></TroiNhe>;
    case 'bieu-tuong': return <BieuTuong3D anh={p.anh} tren={p.tren} duoi={p.duoi} />;
    case 'repo': return <TheRepo chu={p.chu} ten={p.ten} moTa={p.moTa} so={p.so} nhan={p.nhan} />;
    case 'terminal': return <Terminal dai={dai} lenh={p.lenh} chuChay={p.chuChay} />;
    case 'cay-thu-muc': return <TroiNhe dai={dai}><CayThuMuc tren={p.tren} duoi={p.duoi} tep={p.tep} dot={p.dot ?? []} moc={p.moc ?? []} kieu={p.kieu} minhHoa={p.minhHoa} /></TroiNhe>;
    case 'tep-ma': return <TroiNhe dai={dai}><TepMa tren={p.tren} duoi={p.duoi} ten={p.ten} dong={p.dong} vung={p.vung} moc={p.moc ?? []} /></TroiNhe>;
    default: throw new Error(`Không có mô hình cảnh: ${c.loai}`);
  }
};

export const VideoMoHinh: React.FC<MoHinhProps> = ({phuDe, canh}) => (
  <AbsoluteFill style={{background: '#FFF3EA'}}>
    {canh.map((c, i) => (
      <Sequence key={i} from={f(c.tu)} durationInFrames={f(c.den) - f(c.tu)} layout="none"><AbsoluteFill><KieuNen.Provider value={(c.kieuNen as string) ?? 'dao'}><VeCanh c={c} /></KieuNen.Provider></AbsoluteFill></Sequence>
    ))}
    <PhuDe phuDe={phuDe} canh={canh} />
  </AbsoluteFill>
);
