import {loadFont as loadMontserrat} from '@remotion/google-fonts/Montserrat';

// Font tiêu đề có đủ dấu tiếng Việt
export const fontTieuDe = loadMontserrat('normal', {weights: ['900'], subsets: ['vietnamese', 'latin']}).fontFamily;
