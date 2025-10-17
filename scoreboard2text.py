import cv2
import os
from cv2_enumerate_cameras import enumerate_cameras

#Get connected cameras via enumerate_cameras
def getUVCcameras():
    cameraList = []
    cameras = enumerate_cameras()
    for cameraInfo in cameras:
        cameraList.append([cameraInfo.name, cameraInfo.index])
    return cameraList

#Ask and list what camera to connect to
print("What camera would you like to use?")
connectedCameras = getUVCcameras()
cameraAmountConnected = len(connectedCameras)
for cams in connectedCameras:
    print(f"{cams[0]}:{cams[1]} - ({connectedCameras.index(cams)})")

#Function to have user select camera
def selectCamera():
    cameraToUse = input("Camera to use: ")
    if cameraToUse.isdigit() and int(cameraToUse) >= 0 and int(cameraToUse) <  cameraAmountConnected:
        testCam = cv2.VideoCapture(connectedCameras[int(cameraToUse)][1])
        if testCam.isOpened():
            print("Test connect to camera successful")
            testCam.release()
            return connectedCameras[int(cameraToUse)][1]
        else:
            print("ERROR: Cannot connect to camera")
            selectCamera()
    else:
        print("ERROR: Input was not valid")
        selectCamera()

#Start video capture
videoCapture = cv2.VideoCapture(selectCamera())

if videoCapture.isOpened():
    print("Connected to camera successfully")

conversionTable = [
    ["1111110"], #0
    ["0110000"], #1
    ["1101101"], #2
    ["1111001"], #3
    ["0110011"], #4
    ["1011011"], #5
    ["0011111"], #6
    ["1110000"], #7
    ["1111111"], #8
    ["1110011"] #9
]

#Get Font Choice
def getFont():
    fontToUse = input("Font to use (Check scoreboardFontSelector.png for number) 4 normaly: ")
    if fontToUse.isdigit() and int(fontToUse) >= 0 and int(fontToUse) < 8:
        fontToUse = int(fontToUse)
        if fontToUse in (4,5,6,7):
            conversionTable[6] = "1011111"
        if fontToUse in (2,3,6,7):
            conversionTable[7] = "1110010"
        if fontToUse in (1,3,5,7):
            conversionTable[9] = "1111011"

getFont()

#Set Camera resoltion and window size
videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

frameWidth = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

ret, testFrame = videoCapture.read()
cv2.imshow('Scoreboard2Text', testFrame)

cv2.resizeWindow("Scoreboard2Text", frameWidth, frameHeight)

bwIntensity = 150

numberOfTrackers = 0

circleSize = 5

trackerGroups = []

trackerGroupsValues = []

filesMade = []

colorMode = True

output = ""
lastOutput = ""

updateMessage = ""

#Loop to run window
while True:
    ret, originalFrame = videoCapture.read()
    colorFrame = originalFrame
    bwFrame = cv2.cvtColor(originalFrame, cv2.COLOR_BGR2GRAY)
    bwFrame = cv2.threshold(bwFrame, bwIntensity, 255, cv2.THRESH_BINARY)[1]

    #Set color mode
    if colorMode == True:
        currentFrame = colorFrame
    elif colorMode == False:
        currentFrame = cv2.cvtColor(bwFrame, cv2.COLOR_GRAY2RGB)

    #Set locations for pointers
    def placeTracker(event, x, y, p1, p2):
        global numberOfTrackers
        if event == cv2.EVENT_LBUTTONDOWN:
            if numberOfTrackers % 7 == 0 or numberOfTrackers == 0:
                trackerGroups.append([])
                trackerGroupsValues.append([])
            trackerGroups[numberOfTrackers//7].append([x,y])
            trackerGroupsValues[numberOfTrackers//7].append([])
            numberOfTrackers += 1
    
    cv2.setMouseCallback('Scoreboard2Text', placeTracker)

    #Set values for trackers and set circle color
    for groupsAmount in range(len(trackerGroups)):
        for pointsAmount in range(len(trackerGroups[groupsAmount])):
            cords = trackerGroups[groupsAmount][pointsAmount]
            pointerValue = bwFrame[cords[1],cords[0]]

            if pointerValue >= bwIntensity:
                trackerGroupsValues[groupsAmount][pointsAmount] = "1"
                cv2.circle(currentFrame,(cords[0],cords[1]),circleSize,(0,0,255),-1)
            else:
                trackerGroupsValues[groupsAmount][pointsAmount] = "0"
                cv2.circle(currentFrame,(cords[0],cords[1]),circleSize,(255,0,0),-1)

    #Convert numbers to output
    lastOutput = output
    output = ""

    for groupsOfPoints in trackerGroupsValues:
        joinedBinaryValues = ''.join(groupsOfPoints)
        if [joinedBinaryValues] in conversionTable:
            output += str(conversionTable.index([joinedBinaryValues]))
        # elif joinedBinaryValues == "0000000":
        #     output += "0"
        # elif len(groupsOfPoints) < 7:
        #     output += '@'
        else:
            output += "#"

    #Show output
    cv2.putText(currentFrame,output, (25,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    #Show updated message
    cv2.putText(currentFrame,updateMessage, (25,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,)

    if '#' in output and numberOfTrackers % 7 == 0:
        for replace in range(output.count('#')):
            hashIndex = output.index('#')
            if hashIndex < len(lastOutput):
                replacementChar = lastOutput[hashIndex]
            else:
                replacementChar = '0'
            output = output[:hashIndex] + replacementChar + output[hashIndex + 1:]

    #Save ouput to files
    filesToMake = list(output)
    for f in range(len(filesToMake)):
        with open((f"text{f}.txt"), "w") as file_object:
            file_object.write(filesToMake[f])
            if (f"text{f}.txt") not in filesMade:
                filesMade.append((f"text{f}.txt"))

    # for i in range(len(trackerGroups)):
    #     print(trackerGroups[i])
    #     print(trackerGroupsValues[i])

    #Show current frame
    cv2.imshow('Scoreboard2Text', currentFrame)

    #Do things on keypresses
    key = cv2.waitKey(1)

    #Change color mode
    if key == ord('c'):
        colorMode = not colorMode

    #Turn up and down intensity
    if key == ord('o'):
        bwIntensity+=1
        updateMessage = "intensity: " + str(bwIntensity)
        #colorMode = False

    if key == ord('i'):
        bwIntensity-=1
        updateMessage = "intensity: " + str(bwIntensity)
        #colorMode = False

    def offsetTrackers(x,y):
        for groupsAmount in range(len(trackerGroups)):
            for pointsAmount in range(len(trackerGroups[groupsAmount])):
                trackerGroups[groupsAmount][pointsAmount][0] = trackerGroups[groupsAmount][pointsAmount][0] + x
                trackerGroups[groupsAmount][pointsAmount][1] = trackerGroups[groupsAmount][pointsAmount][1] + y

    #Use WASD to move around trackers
    if key == ord('w'):
        offsetTrackers(0,-1)

    if key == ord('s'):
        offsetTrackers(0,1)

    if key == ord('a'):
        offsetTrackers(-1,0)

    if key == ord('d'):
        offsetTrackers(1,0)

    #Undo Trackers
    if key == ord('u'):
        if numberOfTrackers != 0:
            trackerGroups[-1].pop()
            if trackerGroups[-1] == []:
                del trackerGroups[-1]

            trackerGroupsValues[-1].pop()
            if trackerGroupsValues[-1] == []:
                del trackerGroupsValues[-1]

            numberOfTrackers -= 1
    
    #Quit on q
    if key == ord('q'):
        break


videoCapture.release()
cv2.destroyAllWindows()

for r in range(10):
    if os.path.exists((f"text{r}.txt")):
        os.remove((f"text{r}.txt"))