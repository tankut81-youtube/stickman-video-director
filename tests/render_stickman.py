#!/usr/bin/env python3
"""15-second original stick-figure continuity/motion test. Pillow + FFmpeg."""
import math, subprocess, os
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,DURATION=960,540,24,15
OUT="out/stickman-15s-test.mp4"
os.makedirs("out",exist_ok=True)
ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-crf","21","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
def clamp(x,a=0,b=1):return max(a,min(b,x))
def smooth(x):
    x=clamp(x)
    return x*x*(3-2*x)
def line(d,points,color="#25364b",width=9):
    d.line(points,fill=color,width=width,joint="curve")
    r=width//2
    for x,y in (points[0],points[-1]):d.ellipse((x-r,y-r,x+r,y+r),fill=color)
def stick(d,x,y,t,phase,held):
    c="#25364b"; wob=math.sin(t*12)*3 if phase=="walk" else 0
    head=(x,y-154+wob)
    d.ellipse((head[0]-36,head[1]-36,head[0]+36,head[1]+36),fill="#fff8ed",outline=c,width=7)
    # consistent eyes, eyebrows and smile
    d.ellipse((x-16,head[1]-6,x-11,head[1]+1),fill=c)
    d.ellipse((x+11,head[1]-6,x+16,head[1]+1),fill=c)
    d.arc((x-13,head[1],x+14,head[1]+19),0,180,fill=c,width=3)
    neck=(x,y-115+wob);hip=(x,y-10)
    line(d,[neck,hip],c,9)
    stride=math.sin(t*12)*23 if phase=="walk" else 0
    line(d,[hip,(x-18+stride,y+45),(x-28+stride,y+91)],c,9)
    line(d,[hip,(x+18-stride,y+45),(x+28-stride,y+91)],c,9)
    shoulder=(x,y-100+wob)
    if held:
        line(d,[shoulder,(x+32,y-75),(x+62,y-112)],c,8)
        line(d,[shoulder,(x-36,y-55),(x-45,y-35)],c,8)
    else:
        swing=math.sin(t*12)*16 if phase=="walk" else 0
        line(d,[shoulder,(x-35,y-68+swing),(x-35,y-29+swing)],c,8)
        line(d,[shoulder,(x+35,y-68-swing),(x+35,y-29-swing)],c,8)
def frame(t):
    im=Image.new("RGB",(W,H),"#e7f1f4");d=ImageDraw.Draw(im)
    # background and props are fixed across all frames
    d.rectangle((0,405,W,H),fill="#d2d9d0")
    d.line((0,405,W,405),fill="#90a6b2",width=5)
    d.rectangle((65,82,265,270),fill="#c9e8f3",outline="#566e86",width=9)
    d.line((165,82,165,270),fill="#566e86",width=8)
    d.line((65,176,265,176),fill="#566e86",width=8)
    d.ellipse((675,60,763,148),fill="#f7d782")
    # table remains steady
    d.rounded_rectangle((590,289,817,312),radius=8,fill="#916a55")
    d.rectangle((610,310,625,405),fill="#745446")
    d.rectangle((788,310,803,405),fill="#745446")
    pickup=smooth((t-5.0)/1.0)
    drinking=smooth((t-7.5)/1.2)
    x=195+390*smooth(t/5)
    y=314
    walking=t<4.9
    held=t>=6
    stick(d,x,y,t,"walk" if walking else "idle",held)
    # blue mug transitions from tabletop to hand, keeps identical appearance
    mugx=682*(1-pickup)+(x+62)*pickup
    mugy=275*(1-pickup)+(y-112-35*drinking)*pickup
    d.rounded_rectangle((mugx-18,mugy-22,mugx+18,mugy+12),radius=6,fill="#2e8da3",outline="#22546c",width=3)
    d.arc((mugx+10,mugy-12,mugx+35,mugy+12),270,90,fill="#22546c",width=5)
    # character stays in same frame; no auto-subtitles
    return im
try:
    for i in range(FPS*DURATION):
        im=frame(i/FPS)
        ff.stdin.write(im.tobytes())
finally:
    ff.stdin.close()
    rc=ff.wait()
    if rc:raise SystemExit(f"ffmpeg failed: {rc}")
print(OUT,os.path.getsize(OUT),"bytes")
