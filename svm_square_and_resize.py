import cv2
from PIL import Image

path = "D:/ProcessedImages/"

def make_square(path, fill_color=(0, 0, 0)):
    im = Image.open(path)
    x, y = im.size
    size = max(x, y)
    new_im = Image.new('RGBA', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    new_im.save(path)
    new_im.close()

def resize_image(path,max_size=512):

    image = cv2.imread(path,0)
    dimension = (max_size,max_size)
    resized = cv2.resize(image, dimension, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path,resized)

def square_and_resize_images(path,length):
    for i in range(0,length):
        imagePath = path+'/'+str(i)+'.png'
        make_square(imagePath)
        resize_image(imagePath)


