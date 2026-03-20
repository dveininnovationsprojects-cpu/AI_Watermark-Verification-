from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import cv2
import numpy as np

def add_vis(img, text, x=0, y=0, Font=None,grid=False, opacity=100, size=30):
    img.seek(0)
    if Font is None:
        Font = 'ARIALBD.TTF'
    img = Image.open(BytesIO(img.read())).convert("RGBA")
    font = ImageFont.truetype(Font, size)
    txt_layer = Image.new("RGBA", img.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)
    img_w,img_h=img.size
    if grid==True:
        x,y=0,0
        while y<=img_h:
            draw.text(
            (int(x), int(y)),
            text,
            fill=(255,255,255,int(opacity)),
            font=font
            )
            x=int(x+font.size*8)
            print(x)
            print('img_w:',img_w)
            if x>=img_w:
                x=0
                y=int(y+font.size*4)
                print(y)
        watermarked = Image.alpha_composite(img, txt_layer)
    else:       
        
        draw.text(
            (int(x+1), int(y+1)),
            text,
            fill=(255,255,255,int(opacity)),
            font=font
        )

        watermarked = Image.alpha_composite(img, txt_layer)
    watermarked = watermarked.convert("RGBA")

    img = cv2.cvtColor(np.array(watermarked), cv2.COLOR_RGBA2BGR)
    cv2.resize(img,(img_w,img_h))
    return img

def add_vis_img(img, logo, x=0, y=0,opacity=100,grid=False):
    img.seek(0)
    logo.seek(0)

    img = Image.open(BytesIO(img.read())).convert("RGBA")
    logo = Image.open(BytesIO(logo.read())).convert("RGBA")

    # resize logo
    img_w, img_h = img.size
    logo_w, logo_h = logo.size
    new_w = img_w // 8
    aspect_ratio = logo_h / logo_w
    new_h = int(new_w * aspect_ratio)

    logo = logo.resize((new_w, new_h), Image.LANCZOS)
    # change opacity
    alpha = logo.split()[3]
    alpha = alpha.point(lambda p: p * (opacity / 255))
    logo.putalpha(alpha)
    count=0
    if grid==True:
        while y<img_h:
            count+=1
            img.paste(logo,(x,y),logo)
            x=x+int(new_w*2)
            if x+int(new_w)>=img_w:
                x=0
                y=y+int(new_h*2)
   
    # paste at dragged position
    else:
        img.paste(logo, (int(x), int(y)), logo)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)

    return img#,count
#x=add_vis_img(open(r'dunder(ignore)\africa-animal-big-carnivore-87410.jpeg','rb'),open(r'dunder(ignore)\africa-animal-big-carnivore-87410.jpeg','rb'),0,0,grid=True)
#cv2.imshow('img',x)
#import matplotlib.pyplot as plt 
#plt.show()
#cv2.waitKey(0)
