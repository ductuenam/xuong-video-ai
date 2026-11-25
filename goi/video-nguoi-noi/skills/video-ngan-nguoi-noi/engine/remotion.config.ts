import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
// Máy có GPU NVIDIA: dùng ANGLE để render nhanh hơn
Config.setChromiumOpenGlRenderer('angle');
Config.setConcurrency(6);
