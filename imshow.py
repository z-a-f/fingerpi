#!/usr/bin/env python

import pickle
import matplotlib.pyplot as plt
import numpy as np

with open('raw_img.pickle', 'r') as f:
    raw_image = pickle.load(f)

dim = raw_image[1]['Data'][1]
img = bytearray(raw_image[1]['Data'][0])
print "Min, Max: ", (min(img), max(img))
print "Length:", len(img)

img = np.reshape(img, dim)
print "Dimensions: ", img.shape
plt.imshow(img, cmap = 'gray')

plt.show()
