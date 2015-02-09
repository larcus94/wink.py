import cv2
import os

class EyeTracker:

    def __init__(self, faceCascadePath, eyeCascadePath):
        self.faceCascadePath = cv2.CascadeClassifier(faceCascadePath)
        self.eyeCascadePath = cv2.CascadeClassifier(eyeCascadePath)

    def track(self, image):
        faceRects = self.faceCascadePath.detectMultiScale(image,
            scaleFactor = 1.1, minNeighbors = 5, minSize = (30, 30),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE)
        rects = []

        for (fx, fy, fw, fh) in faceRects:
            faceImage = image[fy:fy+fh, fx:fx+fw]

            face = (fx, fy, fx+fw, fy+fh)

            eyeRects = self.eyeCascadePath.detectMultiScale(faceImage,
                scaleFactor = 1.1, minNeighbors = 10, minSize = (20, 20),
                flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

            eyes = []
            for (ex, ey, ew, eh) in eyeRects:
                eyes.append((fx+ex, fy+ey, fx+ex+ew, fy+ey+eh))

            rects.append((face, eyes))

        return rects

fc = "/usr/local/Cellar/opencv/2.4.10.1/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"
ec = "/usr/local/Cellar/opencv/2.4.10.1/share/OpenCV/haarcascades/haarcascade_eye.xml"

tracker = EyeTracker(fc, ec)
camera = cv2.VideoCapture(0)

path = os.path.expanduser("~/Desktop/selfie")
count = 0
suffix = ""
ns = lambda c: "-{0}".format(count)

winked = 0
ready = False

while True:
    (success, frame) = camera.read()

    if not success:
        break

    resizedFrame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)
    grayFrame = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2GRAY)

    rects = tracker.track(grayFrame)

    draw = lambda r: cv2.rectangle(resizedFrame, (r[0], r[1]), (r[2], r[3]), (0, 255, 0), 2)
    for face, eyes in rects:
        draw(face)

        for eye in eyes:
            draw(eye)

        if len(eyes) == 1:
            winked += 1
            if winked > 10:
                ready = True
        elif len(eyes) == 2:
            if ready:
                p = path+suffix+".png"
                cv2.imwrite(p, frame)
                suffix = ns(count)

            winked = 0
            ready = 0

    cv2.imshow("wink.py", resizedFrame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
