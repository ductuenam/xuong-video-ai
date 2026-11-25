import {AbsoluteFill, Img, staticFile} from 'remotion';
import {fontTieuDe} from './theme';
import KENH from './kenh.json';

// Ảnh bìa video dọc: lớp hình do AI tạo (không có chữ), lớp chữ ghép bằng code để luôn đúng dấu tiếng Việt.
export type AnhBiaProps = {
  anh: string;
  dong1: string;
  dong2: string;
  nhan?: string;
  coChu?: number;
  muiTen?: {tuX: number; tuY: number; denX: number; denY: number; congX: number; congY: number};
  thuongHieu?: string;
  chuThich?: string;
  dayNen?: number; // đẩy hình nền xuống bao nhiêu pixel khi biểu tượng sát chữ
};

const CAM = KENH.mauBia;

export const AnhBia: React.FC<AnhBiaProps> = ({anh, dong1, dong2, nhan, coChu = 108, muiTen, thuongHieu = KENH.ten, chuThich = KENH.nhanAnhAI, dayNen = 0}) => {
  const chu = {fontFamily: fontTieuDe, fontWeight: 900, lineHeight: 1.3, letterSpacing: -1, textTransform: 'uppercase'} as const;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Img src={staticFile(anh)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `translateY(${dayNen}px)`}} />
      {dayNen ? <div style={{position: 'absolute', left: 0, right: 0, top: dayNen - 2, height: 160, background: 'linear-gradient(180deg,#000,rgba(0,0,0,0))'}} /> : null}
      <AbsoluteFill style={{background: 'linear-gradient(180deg,rgba(0,0,0,0.72) 0%,rgba(0,0,0,0.35) 24%,rgba(0,0,0,0) 36%)'}} />
      <div style={{position: 'absolute', left: 40, right: 40, top: 140, textAlign: 'center'}}>
        <div style={{...chu, fontSize: coChu, color: '#fff', textShadow: '0 6px 26px rgba(0,0,0,0.85)'}}>{dong1}</div>
        <div style={{...chu, fontSize: coChu * 0.86, color: CAM, marginTop: 10, textShadow: '0 0 34px rgba(255,110,20,0.55), 0 6px 22px rgba(0,0,0,0.8)'}}>{dong2}</div>
        {nhan ? (
          <div style={{display: 'inline-block', marginTop: 30, padding: '14px 40px', transform: 'rotate(-2deg) skewX(-5deg)', background: 'linear-gradient(95deg,#FFB21A,#FF6A13)', border: '4px solid #1A0F06', outline: '3px solid #FFB21A', ...chu, fontSize: coChu * 0.54, letterSpacing: 0, color: '#140A04', boxShadow: '0 16px 44px rgba(255,110,20,0.45)'}}>{nhan}</div>
        ) : null}
      </div>
      {muiTen ? (
        <svg width="1080" height="1920" style={{position: 'absolute', left: 0, top: 0, filter: 'drop-shadow(0 6px 14px rgba(0,0,0,0.7))'}}>
          <defs><marker id="dau" markerWidth="4" markerHeight="4" refX="2.2" refY="2" orient="auto"><path d="M0 0 L4 2 L0 4 Z" fill="#fff" /></marker></defs>
          <path d={`M${muiTen.tuX} ${muiTen.tuY} Q ${muiTen.congX} ${muiTen.congY} ${muiTen.denX} ${muiTen.denY}`} fill="none" stroke="#fff" strokeWidth={15} strokeLinecap="round" markerEnd="url(#dau)" />
        </svg>
      ) : null}
      <div style={{position: 'absolute', right: 24, top: 1726, width: 300, height: 112, boxSizing: 'border-box', paddingTop: chuThich ? 16 : 34, textAlign: 'center', background: 'rgba(14,9,6,0.96)', borderRadius: 22, border: `3px solid ${CAM}`, fontFamily: fontTieuDe}}>
        <div style={{fontWeight: 900, fontSize: 36, color: '#fff', lineHeight: 1.25}}>{thuongHieu}</div>
        {chuThich ? <div style={{fontWeight: 700, fontSize: 24, color: '#FFD9C2', marginTop: 4}}>{chuThich}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
