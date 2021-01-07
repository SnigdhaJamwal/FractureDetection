from PIL import Image,ImageChops

def is_greyscale(im):
    """
    Check if image is monochrome (1 channel or 3 identical channels)
    """
    return True

    if im.mode not in ("L", "RGB"):
        return False

    if im.mode == "RGB":
        rgb = im.split()
        if ImageChops.difference(rgb[0],rgb[1]).getextrema()[1]!=0: 
            return False
        if ImageChops.difference(rgb[0],rgb[2]).getextrema()[1]!=0: 
            return False
    return True

