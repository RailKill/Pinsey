import cv2
import numpy as np
import os
import urllib.request
from pathlib import Path


class FaceDetector:
    """
    Pump in a list of image URLs and this will automatically fetch them for you. It will then run through
    OpenCV face detection algorithms and tell you how many faces it detects (using Haar Cascade by default).
    """
    def __init__(self, url_list):
        # Create the Haar cascade.
        #casc_path = str(Path(os.path.dirname(__file__)).parent.joinpath('resources')
        #               .joinpath('haarcascade_frontalface_default.xml'))
        casc_path = '../resources/ haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(casc_path)
        self.url_list = url_list

    def run(self):
        for url in self.url_list:
            img = self.fetch_image(url)
            self.detect_faces(img)

    def detect_faces(self, image):
        """
        Returns number of faces detected (integer) based on a given image.
        This uses the Haar cascade in OpenCV to detect frontal faces.
        """
        # Read the image in grayscale.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image.
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        print("Found {0} faces!".format(len(faces)))

        # Draw a rectangle around the faces.
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Faces found", image)
        #cv2.moveWindow("Faces found", 0, 0)
        cv2.waitKey(0)

    @staticmethod
    def fetch_image(img_url):
        """Returns a CV2 image object from the given image URL."""
        req = urllib.request.urlopen(img_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        return cv2.imdecode(arr, -1)  # 'load it as it is'



