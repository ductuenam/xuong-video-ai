import subprocess,sys
import numpy as np
from PIL import Image, ImageDraw
f,tu,den,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
w,h=150,267
raw=subprocess.run(['ffmpeg','-v','error','-ss',str(tu),'-t',str(den-tu),'-i',f,'-vf',f'fps=12,scale={w}:{h}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,timeout=300).stdout
n=len(raw)//(w*h*3); ks=np.frombuffer(raw[:n*w*h*3],np.uint8).reshape(n,h,w,3)
cot=12; hang=(n+cot-1)//cot
o=Image.new('RGB',(w*cot,h*hang))
d=ImageDraw.Draw(o)
for i,k in enumerate(ks):
  x,y=(i%cot)*w,(i//cot)*h; o.paste(Image.fromarray(k),(x,y)); d.text((x+2,y+2),f'{tu+i/12:.2f}',fill='yellow')
o.save(out,quality=85)
