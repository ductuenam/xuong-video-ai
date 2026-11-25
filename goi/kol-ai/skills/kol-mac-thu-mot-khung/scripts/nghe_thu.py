"""Cho Whisper nghe thử các phương án cắt trước khi dựng: ghép các đoạn, nghe, in chữ kèm giây.

Dùng: python nghe_thu.py canh.mp4 "7.4-9.04,9.45-10.4" "17.3-18.34,19.40-21.0" ...
Mỗi tham số là một phương án: các đoạn "từ-đến" (giây) nối bằng dấu phẩy.
Ghép đoạn nghe thử dài từ 2 giây trở lên: đoạn ngắn hơn Whisper hay bịa câu
("cảm ơn các bạn đã theo dõi"). Chạy bằng python hệ thống (cần faster-whisper, GPU nếu có).
"""
import sys, subprocess, numpy as np, wave, tempfile, os
from faster_whisper import WhisperModel
v=sys.argv[1]; SR=16000
raw=subprocess.run(["ffmpeg","-v","error","-i",v,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,np.int16)
try:
    import ctranslate2
    gpu = ctranslate2.get_cuda_device_count() > 0
except Exception:
    gpu = False
m=WhisperModel("large-v3" if gpu else "medium",device="cuda" if gpu else "cpu",compute_type="float16" if gpu else "int8")
for spec in sys.argv[2:]:
    parts=[tuple(map(float,p.split("-"))) for p in spec.split(",")]
    y=np.concatenate([x[int(a*SR):int(b*SR)] for a,b in parts])
    f=tempfile.mktemp(suffix=".wav")
    with wave.open(f,"wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
    segs,_=m.transcribe(f,language="vi",word_timestamps=True,condition_on_previous_text=False)
    print(spec,"=>"," ".join(f"{wd.word.strip()}[{wd.start:.2f}]" for s in segs for wd in s.words)); os.remove(f)
