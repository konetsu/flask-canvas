from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Pixel, User
from . import db
from datetime import datetime, timedelta
import os
import time
from PIL import Image
views = Blueprint('views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))

@views.route('/')
@login_required
def home():
    return render_template("canvas.html")

def color_to_rgb(color):
    if color==101:
        rgb=(109, 0, 26)
    elif color==102:
        rgb=(190, 0, 57)
    elif color==103:
        rgb=(255, 69, 0)
    elif color==104:
        rgb=(255, 168, 0)
    elif color==105:
        rgb=(255, 214, 53)
    elif color==106:
        rgb=(255, 248, 184)
    elif color==107:
        rgb=(0, 163, 104)
    elif color==108:
        rgb=(0, 204, 120)
    elif color==109:
        rgb=(126, 237, 86)
    elif color==110:
        rgb=(0, 117, 111)
    elif color==111:
        rgb=(0, 158, 170)
    elif color==112:
        rgb=(0, 204, 192)
    elif color==113:
        rgb=(36, 80, 164)
    elif color==114:
        rgb=(54, 144, 234)
    elif color==115:
        rgb=(81, 233, 244)
    elif color==116:
        rgb=(73, 58, 193)
    elif color==117:
        rgb=(106, 92, 255)
    elif color==118:
        rgb=(148, 179, 255)
    elif color==119:
        rgb=(129, 30, 159)
    elif color==120:
        rgb=(180, 74, 192)
    elif color==121:
        rgb=(228, 171, 255)
    elif color==122:
        rgb=(222, 16, 127)
    elif color==123:
        rgb=(255, 56, 129)
    elif color==124:
        rgb=(255, 153, 170)
    elif color==125:
        rgb=(109, 72, 47)
    elif color==126:
        rgb=(156, 105, 38)
    elif color==127:
        rgb=(255, 180, 112)
    elif color==128:
        rgb=(0, 0, 0)
    elif color==129:
        rgb=(81, 82, 82)
    elif color==130:
        rgb=(137, 141, 144)
    elif color==131:
        rgb=(212, 215, 217)
    elif color==132:
        rgb=(255, 255, 255)
    return(rgb)

@views.route('/demo', methods=['GET', 'POST'])
def demo():
    demopixels=len(Pixel.query.filter(Pixel.placement_ip==request.remote_addr).all())
    if request.method=="GET":
        return render_template("demo.html", pixelcounter=str(demopixels))
    if request.method=="POST":
        if demopixels > 49:
            return("50 pixels for demo")
        x=request.form.get('xcoord')
        y=request.form.get('ycoord')
        color=int(request.form.get('color'))
        if color<137 and color>100:
            img = Image.open(os.path.join(basedir, "static\\konetsu\\", "canvas.webp"))
            img.putpixel((int(x),int(y)), color_to_rgb(color))
            img.save(os.path.join(basedir, "static\\konetsu\\", "canvas.webp"), lossless=True, quality=100)
            img.close()
            new_pixel = Pixel(
                                  placement_ip=request.remote_addr,
                                  placement_date=datetime.now(),
                                  location_x=x,
                                  location_y=y,
                                  color=color)

            db.session.add(new_pixel)
            db.session.commit()
            return ("Pixels: "+str(demopixels+1))

@views.route('/placer', methods=['POST'])
def placer():
    if not current_user.is_authenticated:
        return("you need to login")
    if current_user.lastpixel_date==None:
        current_user.lastpixel_date=datetime.now()-timedelta(seconds=2)
        db.session.commit()
    if current_user.lastpixel_date+timedelta(seconds=1)>=datetime.now():
        return("cooldown not over")
    x=request.form.get('xcoord')
    y=request.form.get('ycoord')
    color=int(request.form.get('color'))
    if color<137 and color>100:
        img = Image.open(os.path.join(basedir, "static\\konetsu\\", "canvas.webp"))
        img.putpixel((int(x),int(y)), color_to_rgb(color))
        img.save(os.path.join(basedir, "static\\konetsu\\", "canvas.webp"), lossless=True, quality=100)
        img.close()
        new_pixel = Pixel(
                              placement_date=datetime.now(),
                              user_id=current_user.id,
                              location_x=x,
                              location_y=y,
                              color=color)

        db.session.add(new_pixel)
        db.session.commit()
        current_user.lastpixel_date=datetime.now()
        current_user.number_of_pixels+=1
        db.session.commit()
        return ("Pixels: "+str(current_user.number_of_pixels))

#just enter this url "once" after a server restart. it'll generate the canvas update script
@views.route('/start')
def start():
    print("started")
    while True:
        newpixels=Pixel.query.filter(Pixel.placement_date>datetime.now()-timedelta(seconds=30)).all()
        pixelupdate=""
        for pixel in newpixels:
            pixelupdate+='u('+pixel.location_x+','+pixel.location_y+','+str(pixel.color)+');'
        updatescript = open(os.path.join(basedir, "static\\konetsu\\", "update.js"), "w")
        updatescript.write(pixelupdate)
        updatescript.close()
        time.sleep(1)
