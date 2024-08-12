# for computer vision tasks
import cv2
# for face detection and tracking
import dlib
#  for time-related operations
import time
# for mathematical calculations
import math
import datetime
# Load the car classifier
carCascade = cv2.CascadeClassifier("C:/Users/harsh/OneDrive/Documents/programming/python folder/open-cv folder/vech.xml")

# Open the video file
video = cv2.VideoCapture("C:/Users/harsh/OneDrive/Documents/programming/python folder/open-cv folder/cars.mp4")

# Constants
#Importing Libraries


# Constant Declaration
WIDTH =1280
HEIGHT = 720

#estimate speed function
def estimateSpeed(location1, location2):
    # Euclidean distance formula
    d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
    # pixel per meter = ppm
    ppm = 8.8
    # convert distance from pixels to meters
    d_meters = d_pixels / ppm
    # frames per second
    fps = 18
    # calculate speed in m/s using =distance/time
    speed_mps = d_meters / (1 / fps)
    # convert speed from meters per second to kilometer per hour
    speed = speed_mps * 3.6
    return speed

#tracking multiple objects
def trackMultipleObjects():
    rectangleColor = (0, 255, 0)
    frameCounter = 0
    currentCarID = 0
    fps = 0

    # Dictionaries allow you to associate a unique identifier
    carTracker = {}
    carNumbers = {}
    carLocation1 = {}
    carLocation2 = {}

    # create List of 1000 elements 
    # Initially, all speeds are set to None
    speed = [None] * 1000
    # specify the video format while writing video files
    out = cv2.VideoWriter('C:/Users/harsh/OneDrive/Documents/programming/python folder/Measure-speed.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH, HEIGHT))

    while True:
        start_time = time.time()
        print("\n\nstarting time:" + str(start_time))
        rc, image = video.read()
        if type(image) == type(None):
            break   

        image = cv2.resize(image, (WIDTH, HEIGHT))
        resultImage = image.copy()

        frameCounter = frameCounter + 1
        carIDtoDelete = []

        for carID in carTracker.keys():
            # Each key represents a unique car being tracked.
            # updates the tracking position of the car represented by 'carID' in the current frame 'image'
            trackingQuality = carTracker[carID].update(image)
            # higher value pf trackingQuality indicates a more reliable update
            if trackingQuality < 7:
                # tracking information for these cars is not reliable in the current frame and needs to be removed.
                carIDtoDelete.append(carID)

        
        for carID in carIDtoDelete:
            print("Removing carID " + str(carID) + ' from list of trackers. ')
            print("Removing carID " + str(carID) + ' previous location. ')
            print("Removing carID " + str(carID) + ' current location. ')
            carTracker.pop(carID, None)
            carLocation1.pop(carID, None)
            carLocation2.pop(carID, None)

        
        if not (frameCounter % 10):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # cascades used in the 'detectMultiScale' function, operate on grayscale images
            cars = carCascade.detectMultiScale(gray, 1.1, 13, 18, (24, 24))

            for (_x, _y, _w, _h) in cars:
                x = int(_x)
                y = int(_y)
                w = int(_w)
                h = int(_h)

                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h

                matchCarID = None

                for carID in carTracker.keys():
                    trackedPosition = carTracker[carID].get_position()

                    t_x = int(trackedPosition.left())
                    t_y = int(trackedPosition.top())
                    t_w = int(trackedPosition.width())
                    t_h = int(trackedPosition.height())

                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                        matchCarID = carID

                if matchCarID is None:
                    print(' Creating new tracker' + str(currentCarID))

                    tracker = dlib.correlation_tracker()
                    tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

                    carTracker[currentCarID] = tracker
                    carLocation1[currentCarID] = [x, y, w, h]

                    currentCarID = currentCarID + 1

        for carID in carTracker.keys():
            trackedPosition = carTracker[carID].get_position()

            t_x = int(trackedPosition.left())
            t_y = int(trackedPosition.top())
            t_w = int(trackedPosition.width())
            t_h = int(trackedPosition.height())

            cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)

            carLocation2[carID] = [t_x, t_y, t_w, t_h]

        end_time = time.time()
        print("end time :" + str(end_time))
        if not (end_time == start_time):
            fps = 1.0/(end_time - start_time)

        for i in carLocation1.keys():
            if frameCounter % 1 == 0:
                [x1, y1, w1, h1] = carLocation1[i]
                [x2, y2, w2, h2] = carLocation2[i]

                carLocation1[i] = [x2, y2, w2, h2]

                if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                    if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                        speed[i] = estimateSpeed([x1, y1, w1, h1], [x1, y2, w2, h2])

                    if speed[i] != None and y1 >= 180:
                        cv2.putText(resultImage, str(int(speed[i])) + "km/h", (int(x1 + w1/2), int(y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 100) ,2)
            date=str(datetime.datetime.now())

            font=cv2.FONT_HERSHEY_SIMPLEX
            resultImage=cv2.putText(resultImage,"LIVE :",(100,70),font,1.2,(0,0,0),2,cv2.LINE_AA)
            resultImage=cv2.putText(resultImage,date,(80,100),font,1.2,(150,0,78),2,cv2.LINE_AA)
        

        cv2.imshow('result', resultImage)

        out.write(resultImage)

        if cv2.waitKey(1) & 0xff==ord('q')  :
            break

    
    cv2.destroyAllWindows()
    out.release()
    
    # print(trackingQuality)
    print(carTracker)

if __name__ == '__main__':
    trackMultipleObjects()
