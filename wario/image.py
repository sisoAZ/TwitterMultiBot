import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import re


#980, 655
#100, 65
items_path = os.path.join(os.path.dirname(__file__), "items/")

def mergeImage(file, text: None):
    image = Image.open(file)
    overlayImage = Image.open(items_path + "bg.png")
    frame_width = int(abs(image.size[0] / 9))
    frame_height = int(abs(image.size[1] / 9.3))

    if big_height(image) == True:
        base = Image.new('RGBA', (overlayImage.size[0], image.size[1] + frame_height * 2), (255, 255, 255, 0))
    else:
        base = Image.new('RGBA', (image.size[0] + frame_width * 2, image.size[1] + frame_height * 2), (255, 255, 255, 0))

    if big_height(image) == True:
        resize_overlayImage = overlayImage.resize(size=(overlayImage.size[0], image.size[1] + frame_height * 2))
        width = int(resize_overlayImage.size[0] / 2) - int(image.size[0] / 2)
        base.paste(image, (width, frame_height))
    else:
        resize_overlayImage = overlayImage.resize(size=(image.size[0] + frame_width * 2, image.size[1] + frame_height * 2))
        base.paste(image, (frame_width, frame_height))
    base.paste(resize_overlayImage, (0, 0), resize_overlayImage)

    #Draw Text
    if text != None:
        draw = ImageDraw.Draw(base)
        font_size = resize_overlayImage.size[0] / 15
        if check_in_kanji(text) == False:
            font = ImageFont.truetype(items_path + "analog.ttf", int(font_size))
        else:
            font = ImageFont.truetype(items_path + "kyoukasyo.ttc", int(font_size))
        
        #box = draw.textbbox((base.width / 2, base.height / 2), text, font=font, stroke_width=10, anchor="mm")
        #print(box)
        text_size = draw.textsize(text, font=font)
        if text_size[0] >= overlayImage.size[0] - frame_width:
            text_list = split_text(text, font, base, overlayImage.size[0] - frame_width)
            text_count = len(text_list) - 1
            text_height = draw.textsize(text, font=font)[1]
            for splited_text in text_list:
                height_position = (base.height / 2) - (math.floor(text_height * 1.2 * text_count))
                draw.text((base.width / 2, height_position), splited_text, (255,255,255), font=font, stroke_width=10, stroke_fill="black", anchor="mm")
                text_count -= 1
        else:
            draw.text((base.width / 2, base.height / 2), text ,(255,255,255), font=font, stroke_width=10, stroke_fill="black", anchor="mm")
        #draw.text((690, 775), text ,(255,255,255), font=font, stroke_width=10, stroke_fill="black", anchor="mm")


    filename = os.path.splitext(file)[0]
    base.save(filename + "_wario.png")
    return filename + "_wario.png"

def big_height(image):
    if image.size[1] >= 590:
        if image.size[0] <= 880:
            return True
    return False

def check_in_kanji(text):
    pattern = re.compile('[一-鿐]+')
    if pattern.search(text) == None:
        return False
    return True

def split_text(text, font, base, frame_width):
    draw = ImageDraw.Draw(base)
    text_size = draw.textsize(text, font=font)
    text_count = 0
    removed_text_size = text_size[0]
    while_split = True
    split_text = []
    while while_split:
        if text_count >= 100:
            break
        text_size_one = draw.textsize(text[len(text) - (text_count + 1)], font=font)[0]
        text_count += 1
        removed_text_size -= text_size_one
        if frame_width >= removed_text_size:
            split_text.append(text[0:len(text) - text_count])
            if len(text[-text_count:]) >= 1:
                text = text[-text_count:]
                text_size = draw.textsize(text, font=font)
                if text_size[0] >= frame_width:
                    text_count = 0
                    removed_text_size = text_size[0]
                else:
                    split_text.append(text)
                    while_split = False
                    break
    return split_text

#import glob

#mergeImage("./debug_items/ken2.png", "いいあああああああああああああああああああああああああぶり")
#import random
#files = glob.glob("./debug_items/*.png")
#files.extend(glob.glob("./debug_items/*jpg"))
#for file in files:
#    if os.path.splitext(file)[1] == ".jpg" or os.path.splitext(file)[1] == ".png":
#        randomint = random.randint(0, 100)
#        kuso = "ああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああああ"
#        mergeImage(file, kuso[0:randomint])
#loop = asyncio.get_event_loop()
#loop.run_until_complete(mergeImage("./debug_items/tate3.png", "AVC019"))