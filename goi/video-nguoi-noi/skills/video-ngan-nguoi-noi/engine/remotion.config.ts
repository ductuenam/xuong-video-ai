import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
// Máy có GPU NVIDIA: dùng ANGLE để render nhanh hơn
Config.setChromiumOpenGlRenderer('angle');
// Không đặt concurrency ở đây: Remotion kiểm số này cả lúc bundle, máy dưới 6 nhân sẽ hỏng (thử 25/11/2026).
// Số luồng do dung.py › so_luong_dung() truyền theo RAM của máy.
