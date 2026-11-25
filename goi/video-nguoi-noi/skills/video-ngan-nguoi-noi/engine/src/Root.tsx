import {Composition, type CalculateMetadataFunction} from 'remotion';
import {VideoMoHinh, type MoHinhProps} from './MoHinh';
import {AnhBia, type AnhBiaProps} from './AnhBia';

const FPS = 30;
const thoiLuong: CalculateMetadataFunction<MoHinhProps> = ({props}) => ({durationInFrames: Math.max(1, Math.round(props.thoiLuongGiay * FPS))});

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="MoHinh" component={VideoMoHinh} width={1080} height={1920} fps={FPS} durationInFrames={FPS * 6} defaultProps={{thoiLuongGiay: 6, phuDe: [], canh: []}} calculateMetadata={thoiLuong} />
    <Composition id="AnhBia" component={AnhBia as React.FC<AnhBiaProps>} width={1080} height={1920} fps={FPS} durationInFrames={1} defaultProps={{anh: 'bia.png', dong1: 'Tiêu đề', dong2: 'Dòng hai'}} />
  </>
);
