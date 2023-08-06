from . import os_utils
from . import im_utils
import cv2
import os
import numpy as np

def read_img_file(img_file_path, input_shape, threshold_val=None):
    '''read image and convert to input_shape
    '''
    w, h, c = input_shape
    if c == 3:
        mode = 'rgb'
    if c == 1:
        mode = 'gray'
        if threshold_val is not None:
            mode = 'bin'
    img = im_utils.read(img_file_path, mode=mode, threshold_val=threshold_val)
    # resize
    img = cv2.resize(img, (w, h))
    # expand shape
    img = np.expand_dims(img, axis=0)

    return img

def read_img_dir(img_dir_path, ext, input_shape, threshold_val):
    '''read image directory and convert to input_shape
    '''
    img_list = []
    img_file_path_list = os_utils.get_all_files_pathList(img_dir_path, ext)
    for img_file_path in img_file_path_list:
        img = read_img_file(img_file_path, input_shape, threshold_val=threshold_val)
        img_list.append(img)
    # reshape
    img_ds = np.array(img_list).reshape(-1, input_shape[0], input_shape[1], input_shape[2])

    return img_ds, img_file_path_list

def image_dataset_from(img_file_path_list, input_shape, threshold_val=None):
    '''read image set and convert to input_shape
    '''
    img_list = []
    for img_file_path in img_file_path_list:
        img = read_img_file(img_file_path, input_shape, threshold_val=threshold_val)
        img_list.append(img)
    # reshape
    img_ds = np.array(img_list).reshape(-1, input_shape[0], input_shape[1], input_shape[2])

    return img_ds

def read_img_label_dir(img_label_dir_path, ext, input_shape, threshold_val):
    ''' read image-label directory
    '''
    X, img_file_path_list = read_img_dir(img_label_dir_path, ext, input_shape, threshold_val)
    y = []
    for img_file_path in img_file_path_list:
        label = os_utils.get_dir_name(img_file_path)
        try:
            label = int(label)
        except ValueError:
            assert False, "<ds_utils: read_img_label_dir> Invalid Label Name: {}".format(label)
        y.append(label)
    
    return X, y, img_file_path_list

def image_dir_2array(img_dir_path, ext, img_format='gray', th_value=None):
    '''create image array
    '''
    img_list = []
    name_list = []
    # read image
    for img_path in os_utils.get_all_files_pathList(img_dir_path, ext):
        img_name = os_utils.get_fileName_ext(img_path)
        name_list.append(img_name)
        # read image data
        if img_format == 'gray':
            img = cv2.imread(img_path, 0)
            if th_value is not None:
                _,img = cv2.threshold(img,th_value,255,cv2.THRESH_BINARY)
        elif img_format == 'rgb':
            img = cv2.imread(img_path, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            assert False, "Invalid Image Format! {}".format(img_format)
        # create record
        img_list.append(img)

    return name_list, img_list

def image_array_from_dir(img_dir_path, input_shape, ext, th_value=None):
    '''create image array
    '''
    img_W, img_H, img_C = input_shape
    x_list = []
    # read image
    for img_path in os_utils.get_all_files_pathList(img_dir_path, ext):
        print(img_path)
        # read image data
        if img_C == 1:
            img = cv2.imread(img_path, 0)
            if th_value is not None:
                _,img = cv2.threshold(img,th_value,255,cv2.THRESH_BINARY)
        elif img_C == 3:
            img = cv2.imread(img_path, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            assert False, "<create_dataset> Invalid img_C value! {}".format(img_C)
        img = cv2.resize(img, (img_W, img_H))
        # create record
        x_list.append(img)
    # dataset
    X = np.array(x_list).reshape(-1,img_W, img_H, img_C)

    return X

def image_dataset_from_dir(img_dir_path, input_shape, ext, th_value = None):
    '''create image dataset with label from directory
    '''
    img_W, img_H, img_C = input_shape
    y_list = []
    x_list = []
    # read category
    for dir_name in os_utils.get_dir_name_list(img_dir_path):
        dir_path = os.path.join(img_dir_path, dir_name)
        # read image
        for img_path in os_utils.get_file_path_list(dir_path, ext):
            print(img_path)
            # read image data
            if img_C == 1:
                img = cv2.imread(img_path, 0)
                if th_value is not None:
                    _,img = cv2.threshold(img,th_value,255,cv2.THRESH_BINARY)
            elif img_C == 3:
                img = cv2.imread(img_path, 1)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                assert False, "<create_dataset> Invalid img_C value! {}".format(img_C)
            img = cv2.resize(img, (img_W, img_H))
            # create record
            y_list.append(int(dir_name))
            x_list.append(img)
    # dataset
    y = np.array(y_list)
    X = np.array(x_list).reshape(-1,img_W, img_H, img_C)

    return y, X