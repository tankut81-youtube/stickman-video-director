#!/usr/bin/env python3
"""15s cinematic stickman story: ancient cave, fire, discovery and escape.
Rendered entirely in GitHub Actions; no external video model required.
"""
import math,random,os,subprocess
from PIL import Image,ImageDraw,ImageFilter
W,H,FPS,SEC=960,540,24,15
random.seed(7); os.makedirs("out",exist_ok=True)
OUT="out/stickman-cinematic-v2.mp4"
def mix(a,b,t):return a+(b-a)*t
def clamp(x):return max(0.,min(1.,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def p(x,y):return int(x),int(y)
def line(d,a,b,col,width=5):d.line([p(*a),p(*b)],fill=col,width=width,joint="curve")
def glow(im,x,y,r,col):
    lay=Image.new("RGBA",(W,H));d=ImageDraw.Draw(lay)
    d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    return Image.alpha_composite(im,lay.filter(ImageFilter.GaussianBlur(r*.42)))
# fixed cave textures, silhouettes, dust
rocks=[(random.randint(0,W),random.randint(30,500),random.randint(10,55)) for _ in range(75)]
stars=[(random.randint(0,W),random.randint(0,220),random.randint(1,3)) for _ in range(30)]
def backdrop(t):
    im=Image.new("RGB",(W,H))
    pix=im.load()
    for y in range(H):
        f=y/H
        c=(int(15+22*f),int(27+17*f),int(47+11*f))
        ImageDraw.Draw(im).line((0,y,W,y),fill=c)
    d=ImageDraw.Draw(im)
    # moon outside cave mouth, in distance
    d.ellipse((707,65,794,152),fill="#d9e8d5")
    d.polygon([(500,365),(630,180),(760,350),(850,230),(960,370)],fill="#24384e")
    d.polygon([(540,370),(650,230),(800,370),(920,255),(960,365)],fill="#33485b")
    d.rectangle((0,380,W,H),fill="#413b3d")
    for x,y,r in rocks:
        d.ellipse((x-r,y-r/3,x+r,y+r/3),fill="#574947" if y>320 else "#242f3e")
    # cave silhouette frame, avoid blocking active stage
    d.polygon([(0,0),(960,0),(960,75),(880,40),(795,62),(680,31),(550,65),(420,24),(315,67),(200,30),(70,90),(0,155)],fill="#101c2c")
    d.polygon([(0,0),(126,0),(76,115),(110,250),(55,390),(0,480)],fill="#111c29")
    d.polygon([(960,0),(865,0),(908,140),(871,248),(925,360),(960,440)],fill="#111c29")
    for i in range(12):
        sx=50+i*81
        d.line((sx,419,sx+18,413),fill="#685550",width=2)
    return im.convert("RGBA")
def hero(d,x,y,t,arm=0,scared=0,alpha=1):
    # Proportional stick figure, stable expressive face and braided hair tuft
    c="#1b2535"
    bob=3*math.sin(t*13) if t<5 or t>10 else math.sin(t*3)
    hx=x;hy=y-141+bob
    d.ellipse((hx-32,hy-34,hx+32,hy+30),fill="#f8ead1",outline=c,width=6)
    d.arc((hx-30,hy-31,hx+28,hy-4),175,340,fill="#2b2630",width=8)
    d.line((hx+1,hy-36,hx+15,hy-49),fill="#2b2630",width=5)
    # features
    for ex in [-12,12]:d.ellipse((hx+ex-2,hy-5,hx+ex+2,hy+2),fill=c)
    if scared:d.ellipse((hx-4,hy+8,hx+4,hy+18),outline=c,width=2)
    else:d.arc((hx-12,hy+6,hx+12,hy+17),0,180,fill=c,width=3)
    shoulder=(x,y-102+bob);hip=(x,y-21)
    line(d,shoulder,hip,"#e0a857",11)
    # thin limbs but bold readable
    stride=18*math.sin(t*13) if t<5 or t>10 else 0
    line(d,hip,(x-20+stride,y+52),c,8)
    line(d,hip,(x+20-stride,y+52),c,8)
    d.ellipse((x-30+stride,y+49,x-10+stride,y+57),fill="#1b2535")
    d.ellipse((x+10-stride,y+49,x+30-stride,y+57),fill="#1b2535")
    # left arm
    line(d,shoulder,(x-32,y-68),(c),7)
    line(d,(x-32,y-68),(x-45,y-40),c,7)
    # torch arm raised and moving
    fx=x+48; fy=y-165-30*arm
    line(d,shoulder,(x+28,y-93),(c),7)
    line(d,(x+28,y-93),(fx,fy+37),c,7)
    line(d,(fx,fy+37),(fx,fy-4),"#7f5131",10)
    return fx,fy
def mammoth(d,off):
    # giant silhouette seen outside cave, theatrical depth
    x=770+off
    c="#141e2a"
    d.ellipse((x-125,220,x+110,365),fill=c)
    d.ellipse((x+72,209,x+161,305),fill=c)
    d.polygon([(x+140,269),(x+172,295),(x+161,373),(x+142,384),(x+149,319)],fill=c)
    for dx in (-90,-20,65):
        d.polygon([(x+dx,335),(x+dx+29,335),(x+dx+19,436),(x+dx-4,436)],fill=c)
    d.ellipse((x+111,245,x+116,250),fill="#edb96e")
    d.arc((x+132,263,x+200,349),65,160,fill="#e9d4a0",width=7)
    d.arc((x+132,256,x+195,330),60,160,fill="#e9d4a0",width=5)
def frame(t):
    im=backdrop(t)
    x=(125+220*ease(t/4.5)) if t<6 else (345 if t<10 else 345-460*ease((t-10)/5))
    if t>=10:x=345-460*ease((t-10)/5)
    # shadow of large mammoth appears at 6s
    d=ImageDraw.Draw(im)
    if t>5.6:mammoth(d,110-110*ease((t-5.6)/2.8))
    # torch light glow and halo
    torchx=x+48;torchy=325-165-30*ease((t-3)/2)
    im=glow(im,int(torchx),int(torchy),115,(255,142,55,90))
    im=glow(im,int(torchx),int(torchy),55,(255,211,92,115))
    d=ImageDraw.Draw(im)
    fx,fy=hero(d,x,325,t,ease((t-2.5)/1.8),t>6.5)
    flutter=math.sin(t*15)*8
    d.polygon([(fx-11,fy),(fx-7,fy-30+flutter),(fx,fy-56+flutter),(fx+7,fy-29-flutter),(fx+13,fy),(fx,fy+8)],fill="#f9b13f")
    d.polygon([(fx-6,fy),(fx,fy-35+flutter/2),(fx+6,fy),(fx,fy+4)],fill="#ffe897")
    # footsteps dust
    if t<5 or t>10:
        for i in range(4):
            xx=x-36-i*10; yy=385+6*math.sin(t*11+i)
            d.ellipse((xx,yy,xx+5+i,yy+3+i),fill="#a38b71")
    # title card in scene, not model subtitles
    if t<3.2:
        d.rounded_rectangle((480,380,910,468),radius=15,fill="#11273b",outline="#9b7f53",width=2)
        d.text((509,401),"THE CAVE AT NIGHT",fill="#f6e4bc")
        d.text((509,431),"A stickman survival story",fill="#b3d6d8")
    if 6.5<t<9.5:
        d.rounded_rectangle((75,52,330,106),radius=12,fill="#132638")
        d.text((100,68),"SOMETHING MOVES...",fill="#fce2b5")
    return im.convert("RGB")
cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","20","-movflags","+faststart",OUT]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
    for idx in range(FPS*SEC):
        proc.stdin.write(frame(idx/FPS).tobytes())
finally:
    proc.stdin.close()
    rc=proc.wait()
    if rc:raise RuntimeError(f"ffmpeg exit {rc}")
print(OUT,os.path.getsize(OUT))
