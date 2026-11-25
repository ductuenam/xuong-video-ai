// Điểm vào trang HyperFrames: vẽ VideoMoHinh của engine Remotion theo giây HyperFrames gửi qua hf-seek.
import React from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {KhungCtx, FPS} from 'remotion';
import {VideoMoHinh} from '../src/MoHinh';

declare global { interface Window { __PROPS__: any } }
const props = window.__PROPS__;
const goc = createRoot(document.getElementById('app') as HTMLElement);
const ve = (giay: number) => flushSync(() => goc.render(<KhungCtx.Provider value={Math.round(giay * FPS)}><VideoMoHinh {...props} /></KhungCtx.Provider>));
ve(0);
window.addEventListener('hf-seek', (e: any) => ve(e.detail.time));
