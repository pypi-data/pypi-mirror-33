import imutils
import cv2
import matplotlib.pyplot as plt

def read(img_file_path, mode=('rgb', 'gray', 'bin'), threshold_val=None):
    ''' read image
    '''
    if mode not in ('rgb', 'gray', 'bin'):
        assert False, "<im_utils> Invalid Mode: {}".format(mode)
    if mode == 'rgb':
        img = cv2.imread(img_file_path, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if mode == 'gray':
        img = cv2.imread(img_file_path, 0)
    if mode == 'bin':
        if threshold_val is None:
            assert False, "<im_utils> NO threshold value"
        img = cv2.imread(img_file_path, 0)
        _,img = cv2.threshold(img,threshold_val,255,cv2.THRESH_BINARY)
    
    return img

def write(img_file_path, img):
    _,_,c = img.shape
    if c == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(img_file_path, img)

def rotate(img, angle):
    img = imutils.rotate(img, angle=angle)

    return img

def rotate_bound(img, angle):
    '''rotate without cut off image
       fill with black pixel
    '''
    img = imutils.rotate_bound(img, angle=angle)

    return img

def rotate_bound_white(img, angle):
    '''rotate without cut off image
       fill with white pixel
    '''
    # convert white 2 black
    img = ~img
    # fill with black
    img = imutils.rotate_bound(img, angle=angle)
    # recover 2 white
    img = ~img

    return img

def resize_with_aspect(img, width=None, height=None):
    img = imutils.resize(img, width=width, height=height)

    return img

def bgr2rgb(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img

def show_img(img, title=None):
    if title is not None:
        plt.figure(title)
    plt.imshow(img)
    plt.show()

def show_gray_img(img, title=None, vmin=0, vmax=255):
    if title is not None:
        plt.figure(title)
    plt.imshow(img, cmap='gray', vmin=vmin, vmax=vmax)
    plt.show()

