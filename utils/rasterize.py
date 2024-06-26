import numpy as np
from bresenham import bresenham
import scipy.ndimage
from PIL import Image


def get_stroke_num(vector_image):
    return len(np.split(vector_image[:, :2], np.where(vector_image[:, 2])[0] + 1, axis=0)[:-1])


def mydrawPNG_fromlist(vector_image, stroke_idx, Side=256):
    vector_image = np.split(vector_image[:, :2], np.where(vector_image[:, 2])[0] + 1, axis=0)[:-1]
    vector_image = [vector_image[x] for x in stroke_idx]

    raster_image = np.zeros((int(Side), int(Side)), dtype=np.float32)

    for stroke in vector_image:
        initX, initY = int(stroke[0, 0]), int(stroke[0, 1])

        for i_pos in range(1, len(stroke)):
            cordList = list(bresenham(initX, initY, int(stroke[i_pos, 0]), int(stroke[i_pos, 1])))
            #print(cordList)
            for cord in cordList:
                if (cord[0] >= 0 and cord[1] >= 0) and (cord[0] <= Side and cord[1] <= Side):
                    raster_image[cord[1], cord[0]] = 255.0
                else:
                    print('error')
            initX, initY = int(stroke[i_pos, 0]), int(stroke[i_pos, 1])

    raster_image = ~(scipy.ndimage.binary_dilation(raster_image)) * 255.0
    
    return Image.fromarray(raster_image).convert('RGB')


def mydrawPNG(vector_image, Side=256):
    raster_image = np.zeros((int(Side), int(Side)), dtype=np.float32)
    initX, initY = int(vector_image[0, 0]), int(vector_image[0, 1])
    pixel_length = 0

    for i in range(0, len(vector_image)):
        if i > 0:
            if vector_image[i - 1, 2] == 1:
                initX, initY = int(vector_image[i, 0]), int(vector_image[i, 1])

        cordList = list(bresenham(initX, initY, int(vector_image[i, 0]), int(vector_image[i, 1])))
        pixel_length += len(cordList)

        for cord in cordList:
            if (cord[0] > 0 and cord[1] > 0) and (cord[0] < Side and cord[1] < Side):
                raster_image[cord[1], cord[0]] = 255.0
        initX, initY = int(vector_image[i, 0]), int(vector_image[i, 1])

    raster_image = scipy.ndimage.binary_dilation(raster_image) * 255.0
    # return raster_image
    return Image.fromarray(raster_image).convert('RGB').save('utils/test_output/1.png',"png")


def preprocess(sketch_points, side=256.0):

    sketch_points = sketch_points.astype(np.float)
    sketch_points[:, :2] = sketch_points[:, :2] / np.array([256, 256])
    sketch_points[:, :2] = sketch_points[:, :2] * side
    sketch_points[:, :2] = sketch_points[:, :2] * (side - 1)
    sketch_points = np.round(sketch_points)
    
    
    return sketch_points


def rasterize_Sketch(sketch_points):
    strokeNum = get_stroke_num(sketch_points)
    stroke_idx = list(range(strokeNum))
    sketch_points = preprocess(sketch_points)
    raster_images = mydrawPNG_fromlist(sketch_points, stroke_idx)
    return raster_images