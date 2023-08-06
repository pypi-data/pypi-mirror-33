import imutils
import cv2
import matplotlib.pyplot as plt
import os_utils
import ds_utils
import numpy as np

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

def dir_image(image_dir_path, result_dir_path, batch=10, ext='png'):
    one_image = None
    image_path_list = os_utils.get_all_files_pathList(image_dir_path, ext)
    image_path_set = [image_path_list[i:i+batch] for i in range(0, len(image_path_list), batch)]
    input_shape = (64, 64, 3)
    for sub_image_list in image_path_set:
        images_row = np.zeros((input_shape[0], input_shape[1]*batch, input_shape[2]), dtype=np.uint8)
        sub_image_data = ds_utils.image_dataset_from(sub_image_list, input_shape)
        sub_image_data = np.concatenate((sub_image_data), axis=1)
        images_row[0:sub_image_data.shape[0], 0:sub_image_data.shape[1], 0:sub_image_data.shape[2]] = sub_image_data
        if one_image is not None:
            one_image = np.concatenate((one_image, images_row), axis=0)
        else:
            one_image = images_row
    one_image = cv2.cvtColor(one_image, cv2.COLOR_RGB2BGR)
    image_file_path = result_dir_path + "/" + "one_image-" + os_utils.get_dir_name(image_dir_path) + "_" + str(len(image_path_list)) + ".png"
    cv2.imwrite(image_file_path, one_image)

    return (image_file_path)

def multi_dir_image(image_dir_path, result_dir_path, batch=10, ext='png'):
    sub_image_dir_path_list = os_utils.get_dir_path_list(image_dir_path)
    for sub_image_dir_path in sub_image_dir_path_list:
        yield dir_image(sub_image_dir_path, result_dir_path, batch=batch, ext=ext)