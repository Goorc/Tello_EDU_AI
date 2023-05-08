import cv2
import numpy as np

# Bild laden und in Graustufen konvertieren
img = cv2.imread('testImages\TestImage2.jpg')
#scale down image
img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

threshold = 220
#set all pixels below threshold to 0 and all above to 255
gray[gray < threshold] = 0
gray[gray >= threshold] = 255

# Rauschen reduzieren
gray = cv2.medianBlur(gray,5)
# Kreiserkennung mit der Hough-Transformation
circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,200,
                            param1=60,param2=40,minRadius=10,maxRadius=50)

# Kreise zeichnen
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # Kreismittelpunkt
        cv2.circle(gray,(i[0],i[1]),2,(0,0,255),3)
        # Kreisumfang
        cv2.circle(gray,(i[0],i[1]),i[2],(0,255,0),2)

# Ergebnis anzeigen
cv2.imshow('Kreiserkennung',gray)
cv2.waitKey(0)
cv2.destroyAllWindows()
