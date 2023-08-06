import numpy as np
from PIL import Image


def image_reader(img_path, array_read=False):
	'''
	Reads the image file into python

	Args::
		img_path (str): Path to the image file
		array_read (bool): Whether to read image as numpy array or PIL object (default False)
	Returns::
		Numpy image matrix / PIL Image object (array_read True/False)

	'''
	im = Image.open(img_path)
	if(array_read):
		im = np.asarray(im)
		return im
	else:
		return im

