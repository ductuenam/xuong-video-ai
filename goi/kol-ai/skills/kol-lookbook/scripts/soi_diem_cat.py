import subprocess,sys,io
from PIL import Image, ImageDraw
# args: out.jpg clip:tu:den ...
out=sys.argv[1]; rows=[]
for spec in sys.argv[2:]:
    clip,tu,den=spec.rsplit(':',2); tu=float(tu); den=float(den)
    ts=[tu,tu+1/24,tu+2/24,tu+3/24,den-2/24,den-1/24]
    row=[]
    for t in ts:
        b=subprocess.run(['ffmpeg','-v','error','-ss',f'{t:.3f}','-i',clip,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True, timeout=60).stdout
        im=Image.open(io.BytesIO(b)).convert('RGB'); w,h=im.size
        # vung mat: tim theo ty le thoi gian trong clip tien (mat nho dan to)
        frac=min(t/10,1); top=0.04; bot=0.20+0.35*frac
        im=im.crop((int(w*0.15),int(h*top),int(w*0.85),int(h*bot))).resize((220,int(220*(h*(bot-top))/(w*0.7))))
        ImageDraw.Draw(im).text((4,4),f'{t:.2f}',fill='yellow'); row.append(im)
    H=max(i.height for i in row); r=Image.new('RGB',(220*6,H)); 
    for k,i in enumerate(row): r.paste(i,(220*k,0))
    d=ImageDraw.Draw(r); d.text((4,H-14),spec,fill='red'); rows.append(r)
c=Image.new('RGB',(220*6,sum(r.height for r in rows))); y=0
for r in rows: c.paste(r,(0,y)); y+=r.height
c.save(out)
