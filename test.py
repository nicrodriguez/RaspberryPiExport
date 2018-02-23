import cv2
import time
import numpy as np

video_capture = cv2.VideoCapture(0)  # This line captures the video stream

cap_frame = np.array(0)
past_image = []
# past_image = np.array(0)
# counter = 0
while True:

    # if counter > 0 and past_image.all() != cap_frame.all():
    #     past_image = cap_frame.all()
    #     counter = 1
    if past_image == cap_frame.all():
        past_image = cap_frame
        cv2.imshow('Previous Frame', past_image)
        print("g")

    _, cap_frame = video_capture.read()

    # if past_image is not None:
    cv2.imshow('Video', cap_frame)
    # counter += 1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
