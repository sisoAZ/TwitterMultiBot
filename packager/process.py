from PIL import Image
import os

items_path = os.path.join(os.path.dirname(__file__), "items/")

def mergeImage(file, cero = "a"):
    image = Image.open(file)
    frame = Image.open(os.path.join(items_path, "package_frame.png"))
    logo = Image.open(os.path.join(items_path, "logo.png"))
    if is_vaild_cero(cero) == False:
        cero = "a"
    cero_image = Image.open(items_path + f"cero_{cero}" + ".png").convert("RGBA")

    image_x, image_y = image.size
    frame_right_margin = int(image_x / 22)
    frame_left_margin = int(image_x / 120)
    frame_height_margin = int(image_y / 38.4)
    base = Image.new('RGBA', (image_x + frame_left_margin + frame_right_margin, image_y + frame_height_margin * 2), (255, 255, 255, 0))
    resize_frame = frame.resize(base.size)
    base.paste(resize_frame)
    base.paste(image, (frame_left_margin, frame_height_margin))
    resize_logo = scale_to_width(logo, int(image_x / 4))
    base.paste(resize_logo, (frame_left_margin, frame_height_margin))
    resize_cero_image = scale_to_width(cero_image, int(image_x / 12))
    base.paste(resize_cero_image, (frame_left_margin * 4, image_y - resize_cero_image.size[1]), mask=resize_cero_image)
    #base.show()
    filename = os.path.splitext(file)[0]
    base.save(filename + "_package.png")
    return filename + "_package.png"

#アスペクト比を保つ関数
def scale_to_width(img, width):
    height = round(img.height * width / img.width)
    return img.resize((width, height))

def is_vaild_cero(cero):
    return cero in ["a", "b", "c", "d", "z"]

#mergeImage("test7.jpg", "a")