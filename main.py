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
    ["1111011"]
]

spaceLocation = []
colonLocation = []

intensity = 150

circleSize = 5

lastAction = 0

lastMessage = ""

filesMade = []

while True:
    ret, frame = cam.read()

    #frame = frame[0:400, 0:600]

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    frame = cv2.threshold(frame, intensity, 255, cv2.THRESH_BINARY)[1]

    for i in spotLocation:
        indexThing = spotLocation.index(i)

        if indexThing > 6:
            spotValue += [""] * 7

        if frame[i[1],i[0]] >= intensity:
            #cv2.circle(frame,(i[0],i[1]),1,(0,0,255),-1)
            spotValue[indexThing] = "1"
        elif frame[i[1],i[0]] < intensity:
            #cv2.circle(frame,(i[0],i[1]),1,(255,0,0),-1)
            spotValue[indexThing] = "0"
        else:
            spotValue[indexThing] = ""

        
        #cv2.putText(frame,str(indexThing), (i[0],i[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1,)

    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    for d in spotLocation:
        indexThing = spotLocation.index(d)
        if spotValue[indexThing] == "1":
            cv2.circle(frame,(d[0],d[1]),circleSize,(0,0,255),-1)
        else:
            cv2.circle(frame,(d[0],d[1]),circleSize,(255,0,0),-1)

        #cv2.putText(frame,str(indexThing), (d[0],d[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    #print((spotValue.count("0") + spotValue.count("1")) % 8)

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
        if spaceLocation:
            for b in spaceLocation:
                output = output[:b] + " " + output[b:]
            #print("place" + str(spaceLocation))
        if colonLocation:
            for b in colonLocation:
                output = output[:b] + ":" + output[b:]

        # print(f"loc:{spotLocation} vals:{spotValue}")
        #print(spotLocation)
        #print(output)

    #print(f"loc:{spotLocation} vals:{spotValue}")

    cv2.putText(frame,output.replace(" ", "_"), (25,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    cv2.putText(frame,lastMessage, (25,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    #print(output)

    filesToMake = output.split()
    for f in range(len(filesToMake)):
        with open((f"text{f}.txt"), "w") as file_object:
            file_object.write(filesToMake[f])
            if (f"text{f}.txt") not in filesMade:
                filesMade.append((f"text{f}.txt"))

    def on_click(event, x, y, p1, p2):
        if event == cv2.EVENT_LBUTTONDOWN:
            spotLocation.append([x,y])
            lastAction = 0


    cv2.imshow('Camera', frame)
    cv2.setMouseCallback('Camera', on_click)

    key = cv2.waitKey(1)
    
    if key == ord('r'):
        spotLocation = []
        spotValue = [""] * 7
        spaceLocation = []
        colonLocation = []
    
    if key == ord('s'):
        if totalCount % 7 == 0:
            spaceLocation.append(len(output))
            lastAction = 2
            #print("added")
            lastMessage = "added space"
    
    if key == ord('c'):
        if totalCount % 7 == 0:
            colonLocation.append(len(output))
            lastAction = 1
            #print("added")
            lastMessage = "added colon"
    
    if key == ord('i'):
        intensity+=1
        lastMessage = "intensity: " + str(intensity)
    if key == ord('o'):
        intensity-=1
        lastMessage = "intensity: " + str(intensity)

    if key == ord('u'):
        if lastAction == 2:
            spaceLocation.pop()
        elif lastAction == 1:
            colonLocation.pop()
        else:
            spotLocation.pop()
            spotValue.pop()
        lastAction = 0
        spotValue = [""] * 7

    if key == ord('q'):
        break


cam.release()
cv2.destroyAllWindows()

for r in range(10):
    if os.path.exists((f"text{r}.txt")):
        os.remove((f"text{r}.txt"))