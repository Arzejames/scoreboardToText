import cv2
import os

cameras = []

for i in range(10):
    testCam = cv2.VideoCapture(i)
    if testCam.isOpened():
        cameras.append(i)
        testCam.release()
    else:
        pass

cameraValue = input(f"What camera # would you like to use? Open Cameras: {cameras}: ")

cam = cv2.VideoCapture(int(cameraValue))

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

spotLocation = []

spotValue = [""] * 7

conversionTable = [
    ["1111110"],
    ["0110000"],
    ["1101101"],
    ["1111001"],
    ["0110011"],
    ["1011011"],
    ["1011111"],
    ["1110000"],
    ["1111111"],
    ["1110011"]
]

intensity = 150

circleSize = 5

lastMessage = ""

filesMade = []

colorOn = True

while True:
    ret, frame = cam.read()
    colorFrame = frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.threshold(frame, intensity, 255, cv2.THRESH_BINARY)[1]

    for i in spotLocation:
        indexThing = spotLocation.index(i)
        if indexThing > 6:
            spotValue += [""] * 7
        if frame[i[1],i[0]] >= intensity:
            spotValue[indexThing] = "1"
        elif frame[i[1],i[0]] < intensity:
            spotValue[indexThing] = "0"
        else:
            spotValue[indexThing] = ""

    if colorOn:
        frame = colorFrame
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    for d in spotLocation:
        indexThing = spotLocation.index(d)
        if spotValue[indexThing] == "1":
            cv2.circle(frame,(d[0],d[1]),circleSize,(0,0,255),-1)
        else:
            cv2.circle(frame,(d[0],d[1]),circleSize,(255,0,0),-1)

    totalCount = (spotValue.count("0") + spotValue.count("1"))
    output = ""    

    if totalCount % 7 == 0 and not totalCount == 0:
        for a in range(int(totalCount/7)):
            start = a*7
            end = start + 7
            joined_value = ''.join(spotValue[start:end])
            if [joined_value] == ["0000000"]:
                output += "0"
            if [joined_value] in conversionTable:
                output += str(conversionTable.index([joined_value]))

    cv2.putText(frame,output.replace(" ", "_"), (25,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    cv2.putText(frame,lastMessage, (25,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    filesToMake = list(output)
    for f in range(len(filesToMake)):
        with open((f"text{f}.txt"), "w") as file_object:
            file_object.write(filesToMake[f])
            if (f"text{f}.txt") not in filesMade:
                filesMade.append((f"text{f}.txt"))

    def on_click(event, x, y, p1, p2):
        if event == cv2.EVENT_LBUTTONDOWN:
            spotLocation.append([x,y])

    cv2.imshow('Camera', frame)
    cv2.setMouseCallback('Camera', on_click)

    key = cv2.waitKey(1)
    
    if key == ord('c'):
        colorOn = not colorOn
    if key == ord('u'):
        spotLocation.pop()
    if key == ord('i'):
        intensity+=1
        lastMessage = "intensity: " + str(intensity)
    if key == ord('o'):
        intensity-=1
        lastMessage = "intensity: " + str(intensity)
    if key == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

for r in range(10):
    if os.path.exists((f"text{r}.txt")):
        os.remove((f"text{r}.txt"))