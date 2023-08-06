Info
====
`vcvf 2018-07-04`

`Author: Zhao Mingming <471106585@qq.com>`

`Copyright: This module has been placed in the public domain.`

`version:2.0.0.1`

Classes:
- `face_detector`: detect the hand in the image 

Functions:

- `test()`: test function  
- `face_detector()`:  a class
- `face_detector.detect_face(image)`: return the face_number,face position,and the confidense

How To Use This Module
======================
.. image:: funny.gif
   :height: 100px
   :width: 100px
   :alt: funny cat picture
   :align: center

1. example code:

.. code:: python
from vcvf import face_detector as fd
import cv2

fd1=fd.face_detector()

fd1.test()
imf=os.path.join(self.site_package,'test.jpg')
print imf
image=cv2.imread(imf)
print(fd1.detect_face(image))


Refresh
========

