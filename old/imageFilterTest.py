import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.ndimage as ndimage
import scipy.misc as misc


#load image from file
image = Image.open('testImages\TestImage.jpg')

#convert image to numpy array
imageArray = np.asarray(image)

#convert image to grayscale
imageArrayGray = np.asarray(image.convert('L'))

#convert image to black and white
#imageBW = np.asarray(image.convert('1'))
imageBW = imageArrayGray / 250
imageBW = np.power(imageBW,2)
imageBW = imageBW > 1
imageBW = imageBW * 255




print(imageBW.min())
print(imageBW.max())

im = Image.fromarray(imageBW)
im = im.convert(mode="1")
im.save("test.jpeg")


# #plot image as in black and white
# plt.imshow(imageBW,cmap='Greys')
# plt.show()