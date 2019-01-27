import pygame
from random import *
from pygame.locals import *



#global variables

red = (255, 0, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
yellow = (247, 255, 0)
black = (0, 0, 0)

mouseX = 0
mouseY = 0

gamePhase = 0

displayX = 1200
displayY = 650

fps = 60

#holds: "piecename": [number availabe for placing, piece object]
pieceData = {"Marshal": [1], "General": [1], "Colonel": [2], "Major": [3], "Captain": [4], "Lieutenant": [4], "Sergeant": [4], "Miner": [5], "Scout": [8], "Spy": [1], "Bomb": [6], "Flag": [1]}

rankData = {"Marshal": 1, "General": 2, "Colonel": 3, "Major": 4, "Captain": 5, "Lieutenant": 6, "Sergeant": 7, "Miner": 8, "Scout": 9, "Spy": 10, "Bomb": 0, "Flag": "F"}

#holds: [["piecename", "piececolor"], ...]
capturedPieces = []

ready = False

selectedPiece = None
selectedPieceCoords = None

targetCoords = None

#counts number of squares between a piece and it's target
dif = 1

battlePt1 = (240, 300)
battlePt2 = (360, 300)

battlePiece1 = None
battlePiece2 = None

#holds: [[piece name, [square row, square col]], ...]
AIKnownPieces = []

#holds: [[[object for each game square, piece occupying square, occupying piece team], ...], ...]
#[row[col[piece list]]]
boardData = [[],[],[],[],[],[],[],[],[],[]]

boardImage = pygame.image.load("board.png")

turn = red

#cheats
bypass = False
alwaysShowEnemy = False
showAIIntel = False


#initialize game, create window, set fps

getInit = pygame.init()
print("successful initializations:", getInit[0])
print("failed initializations:", getInit[1])

gameDisplay = pygame.display.set_mode((displayX, displayY))
pygame.display.set_caption("STRATEGO")
gameDisplay.fill(white)

fpsClock = pygame.time.Clock()



#define functions

def startButton():

    buttonRect = pygame.Rect(displayX/2 - 100, displayY/2 + 110, 200, 80)
    pygame.draw.rect(gameDisplay, red, buttonRect)

    startTextObj = pygame.font.Font("Becker.ttf", 34)
    startTextSurfaceObj = startTextObj.render("START", True, black)
    startTextRectObj = startTextSurfaceObj.get_rect()
    startTextRectObj.center = (displayX/2, displayY/2 + 150)
    gameDisplay.blit(startTextSurfaceObj, startTextRectObj)

    return buttonRect


def loadTitleScreen():

    pygame.mixer.music.load("Title Screen Music.ogg")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)

    titleImage = pygame.image.load("Title Screen.png")
    gameDisplay.blit(titleImage, (0, 0))


def startGame():

    if buttonRect.left < mouseX < buttonRect.right and buttonRect.top < mouseY < buttonRect.bottom and mouseClicked == True:
        gameDisplay.fill(white)
        newPhase()


def writeRules():

    y = 150

    titleTextObj = pygame.font.Font("Becker.ttf", 38)
    titleTextSurfaceObj = titleTextObj.render("RULES:", True, black)
    titleTextRectObj = titleTextSurfaceObj.get_rect()
    titleTextRectObj.center = (displayX/2, y/2)
    gameDisplay.blit(titleTextSurfaceObj, titleTextRectObj)

    ruleTextObj = pygame.font.Font("Becker.ttf", 18)

    file = open("rules.csv", "r")

    for line in file:

        ruleTextSurfaceObj = ruleTextObj.render(line.rstrip(), True, black)
        ruleTextRectObj = ruleTextSurfaceObj.get_rect()
        ruleTextRectObj.center = (displayX/2, y)
        gameDisplay.blit(ruleTextSurfaceObj, ruleTextRectObj)

        y += 25

    file.close()

    newPhase()



def genCoords():

    x = 0
    y = 0

    for item in boardData:

        for num in range(10):

            squareRect = pygame.Rect(x, y, 65, 65)
            item.append([squareRect, None, None])

            x += 65

        x = 0
        y += 65

    #removes square data for obstacle squares
    boardData[4][2][0] = None
    boardData[4][3][0] = None
    boardData[4][6][0] = None
    boardData[4][7][0] = None
    boardData[5][2][0] = None
    boardData[5][3][0] = None
    boardData[5][6][0] = None
    boardData[5][7][0] = None

    return boardData
            



def drawBoardLines():

    y = 65
    x = 0

    for num in range(11):

        if x == 195 or x == 455:

            pygame.draw.line(gameDisplay, black, (x, 0), (x, 260))
            pygame.draw.line(gameDisplay, black, (x, 390), (x, displayY))
            
        else:
            
            pygame.draw.line(gameDisplay, black, (x, 0), (x, displayY))

        x += 65

    for num in range(10):

        if y == 325:

            pygame.draw.line(gameDisplay, black, (0, y), (130, y))
            pygame.draw.line(gameDisplay, black, (260, y), (390, y))
            pygame.draw.line(gameDisplay, black, (520, y), (650, y))

        else:
        
            pygame.draw.line(gameDisplay, black, (0, y), (650, y))
            
        y += 65


def drawBoard():

    alt = altColor()

    gameDisplay.blit(boardImage, (0, 0))
    drawBoardLines()

    for item in boardData:

        for obj in item:

            squareObj = obj[0]
            occupyingPiece = obj[1]
            color = obj[2]

            if occupyingPiece != None:

                genPieceObject(squareObj.left + 7, squareObj.top + 7, occupyingPiece, color, False, False)


    #displays pieces currently in a battle
    if battlePiece1 and battlePiece2 != None:

        pygame.draw.rect(gameDisplay, white, (230, 290, 190, 70))

    if battlePiece1 != None:

        genPieceObject(battlePt1[0], battlePt1[1], battlePiece1, turn, True, False)

    if battlePiece2 != None:

        genPieceObject(battlePt2[0], battlePt2[1], battlePiece2, alt, True, False)


    if showAIIntel == True:
        
        for item in AIKnownPieces:

            itemRect = boardData[item[1][0]][item[1][1]][0]
            pygame.draw.rect(gameDisplay, yellow, (itemRect.centerx - 5, itemRect.centery - 5, 10, 10))

        





def setupPhase():

    global pieceData, ready

    gameDisplay.fill(white)
    
    drawBoard()


    #draws text and pieces beside board
    titleTextObj = pygame.font.Font("Becker.ttf", 38)
    titleTextSurfaceObj = titleTextObj.render("PIECES", True, black)
    titleTextRectObj = titleTextSurfaceObj.get_rect()
    titleTextRectObj.center = (925, 75)
    gameDisplay.blit(titleTextSurfaceObj, titleTextRectObj)

    textObj = pygame.font.Font("Becker.ttf", 18)

    x = 745
    y = 150

    ready = True

    for item in pieceData:

        textSurfaceObj = textObj.render(item, True, black)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (x, y)
        gameDisplay.blit(textSurfaceObj, textRectObj)

        numTextSurfaceObj = textObj.render("x" + str(pieceData[item][0]), True, black)
        numTextRectObj = numTextSurfaceObj.get_rect()
        numTextRectObj.center = (x, y + 100)
        gameDisplay.blit(numTextSurfaceObj, numTextRectObj)

        if pieceData[item][0] != 0:

            ready = False
            pieceRect = genPieceObject(x - 25, y + 25, item, red, False, False)
            pieceData[item] = [pieceData[item][0], pieceRect]


        if x > 1050:

            x = 745
            y += 150

        else:
            x += 120
            

    dragPiece()


    #Draws button, takes input, and moves game to the next phase
    if ready == True and selectedPiece == None or bypass == True:

        buttonRect = pygame.Rect(displayX - 115, displayY - 55, 100, 40)
        pygame.draw.rect(gameDisplay, red, buttonRect)

        endPhaseTextSurfaceObj = textObj.render("DONE", True, black)
        endPhaseTextRectObj = endPhaseTextSurfaceObj.get_rect()
        endPhaseTextRectObj.center = (buttonRect.left + 50, buttonRect.top + 20)
        gameDisplay.blit(endPhaseTextSurfaceObj, endPhaseTextRectObj)

        if buttonRect.left < mouseX < buttonRect.right and buttonRect.top < mouseY < buttonRect.bottom and mouseClicked == True:
            pieceData = {"Marshal": 1, "General": 1, "Colonel": 2, "Major": 3, "Captain": 4, "Lieutenant": 4, "Sergeant": 4, "Miner": 5, "Scout": 8, "Spy": 1, "Bomb": 6, "Flag": 1}
            genAIPieces()
            pygame.mixer.music.load("Battle Phase Music.ogg")
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)
            gameDisplay.fill(white)
            newPhase()







def genPieceObject(x, y, item, color, showEnemy, drawShadow):

    if drawShadow == True:

        shadowImage = pygame.image.load("Piece Shadow.png")
        gameDisplay.blit(shadowImage, (x + 2, y + 2))

    pieceRect = pygame.Rect(x, y, 50, 50)
    pygame.draw.rect(gameDisplay, color, pieceRect)

    if color != blue or showEnemy == True or alwaysShowEnemy == True:
            
        image = pygame.image.load(item + ".png")
        gameDisplay.blit(image, (x, y))
        

    return pieceRect



def dragPiece():

    #Gives the game instruction regarding mouse in setup phase
    #clicks and selected pieces in the setup phase.

    global selectedPiece, pieceData, boardData

    if mouseClicked == True:

        if selectedPiece == None:

            for item in pieceData:

                pieceRect = pieceData[item][1]

                if pieceRect.left < mouseX < pieceRect.right and pieceRect.top < mouseY < pieceRect.bottom and pieceData[item][0] > 0:

                    selectedPiece = item
                    pieceData[item][0] -= 1
                    print("You've found a piece! good job")

                    grabPieceSoundObj = pygame.mixer.Sound("Click Effect High.ogg")
                    grabPieceSoundObj.play()


            for item in boardData:

                for obj in item:

                    pieceRect = obj[0]

                    if pieceRect != None and obj[1] != None and pieceRect.left + 7 < mouseX < pieceRect.right - 8 and pieceRect.top + 7 < mouseY < pieceRect.bottom - 8:

                        selectedPiece = obj[1]
                        obj[1] = None
                        obj[2] = None
                        print("You've found a piece! good job")

                        grabPieceSoundObj = pygame.mixer.Sound("Click Effect High.ogg")
                        grabPieceSoundObj.play()


        else:

            placeSquareFromClick()

    elif selectedPiece != None:

        genPieceObject(mouseX - 25, mouseY - 25, selectedPiece, red, False, True)

        


def placeSquareFromClick():

    global boardData, selectedPiece, pieceData, ready
    validSquare = False

    for item in boardData:

        for obj in item:

            square = obj[0]
            occupyingPiece = obj[1]

            #conditions:
            #there is a valid square. the square is not occupied. the click is within the square. the click is on the player's side of the board.
            if square != None and occupyingPiece == None and square.left < mouseX < square.right and square.top < mouseY < square.bottom and mouseY > 390:

                obj[1] = selectedPiece
                obj[2] = red
                validSquare = True

    if validSquare == False:

        pieceData[selectedPiece][0] += 1
        ready = False

    selectedPiece = None

    dropPieceSoundObj = pygame.mixer.Sound("Click Effect Low.ogg")
    dropPieceSoundObj.play()




def playPhase():

    global turn, selectedPiece

    moveDirection = None
    attackDirection = None

    gameDisplay.fill(white)

    drawBoard()

    deadPiecePoint = drawCapturedPieces()

    cleanAIIntel()

    if turn == red:

        moveDirection, attackDirection = processClick()

        drawSelectedMovePiece(selectedPieceCoords)


    elif turn == blue:

        attackDirection = attackKnownPiece()

        if attackDirection == None:

            moveDirection, attackDirection = randomAction()


    if moveDirection != None:

        executeMove(0, moveDirection)
        
        deselectPiece(True)

        turn = altColor()

    elif attackDirection != None:

        executeMove(-30, attackDirection)
        executeBattle(deadPiecePoint, attackDirection)

        selectedPiece = None

        turn = altColor()






def drawCapturedPieces():

    x = 700
    y = 150

    titleTextObj = pygame.font.Font("Becker.ttf", 38)
    titleTextSurfaceObj = titleTextObj.render("CAPTURED PIECES", True, black)
    titleTextRectObj = titleTextSurfaceObj.get_rect()
    titleTextRectObj.center = (925, 75)
    gameDisplay.blit(titleTextSurfaceObj, titleTextRectObj)

    for item in capturedPieces:

        genPieceObject(x, y, item[0], item[1], True, False)

        x += 25

        if x > 1100:

            y += 100
            x = 700

    return x, y

    

def genAIPieces():

    col = randint(0, 9)

    placeAIPiece(0, col, "Flag")
    placeAIPiece(1, col, "Bomb")

    if col < 9:

        placeAIPiece(0, col + 1, "Bomb")

    if col > 0:

        placeAIPiece(0, col - 1, "Bomb")


    while pieceData["Spy"] > 0:

        col = randint(0, 9)
        row = randint (0, 1)

        placeAIPiece(row, col, "Spy")

    while pieceData["Miner"] > 0:

        col = randint(0, 9)
        row = randint(0, 2)

        placeAIPiece(row, col, "Miner")

    while pieceData["Bomb"] > 0:

        col = randint(0, 9)
        row = randint(1, 2)

        placeAIPiece(row, col, "Bomb")

    while pieceData["Scout"] > 0:

        col = randint(0, 9)
        row = randint(2, 3)

        placeAIPiece(row, col, "Scout")

    while pieceData["Marshal"] > 0:

        row = randint(1, 3)
        col = noFrontLines(row)

        placeAIPiece(row, col, "Marshal")

    while pieceData["General"] > 0:

        row = randint(1, 3)
        col = noFrontLines(row)

        placeAIPiece(row, col, "General")

    remainderPieces = ("Colonel", "Major", "Lieutenant", "Captain", "Sergeant")

    for item in remainderPieces:

        while pieceData[item] > 0:

            row = randint(0, 3)
            col = randint(0, 9)

            placeAIPiece(row, col, item)



def placeAIPiece(row, col, piece):

    global pieceData, boardData

    if boardData[row][col][1] == None:

        boardData[row][col][1] = piece
        boardData[row][col][2] = blue
        pieceData[piece] -= 1


#avoids putting valuble pieces on the front lines
def noFrontLines(row):

    if row == 3:

        num = randint(1, 2)

        if num == 1:

            col = randint(2, 3)

        if num == 2:

            col = randint(6, 7)

    else:

        col = randint(0, 9)

    return col



def processClick():

    global selectedPiece, selectedPieceCoords, boardData

    moveDirection = None
    attackDirection = None

    if mouseClicked == True:

        for item in boardData:

            for obj in item:

                pieceRect = obj[0]
                occupyingPiece = obj[1]
                color = obj[2]

                #conditions:
                #there is a valid square, the square is occupied, and the click falls within the occupying piece
                if pieceRect != None and occupyingPiece != None and pieceRect.left + 7 < mouseX < pieceRect.right - 8 and pieceRect.top + 7 < mouseY < pieceRect.bottom - 8:

                    if color != blue:

                        selectMovePiece(item, obj, occupyingPiece)

                    elif color == blue and selectedPiece != None:

                        attackDirection = getDirection(item, obj)
                        print("attack direction: " + str(attackDirection))

                        if attackDirection == None:

                            deselectPiece(True)

                        else:

                            attackSoundObj = pygame.mixer.Sound("Sword Effect.ogg")
                            attackSoundObj.play()

                    drawBoard()

                    drawSelectedMovePiece(selectedPieceCoords)

                    pygame.display.update()

                    break

                #conditions:
                #there is a valid square, a piece is selected, no piece is in the square, and the click falls within the square
                elif pieceRect != None and selectedPiece != None and occupyingPiece == None and pieceRect.left < mouseX < pieceRect.right and pieceRect.top < mouseY < pieceRect.bottom:

                    moveDirection = getDirection(item, obj)
                    print("move direction: " + str(moveDirection))

                    if moveDirection == None:

                        deselectPiece(True)

                    drawBoard()

                    drawSelectedMovePiece(selectedPieceCoords)

                    pygame.display.update()

                    break

    return moveDirection, attackDirection
                    


def selectMovePiece(item, obj, occupyingPiece):

    global selectedPiece, selectedPieceCoords, boardData

    if selectedPiece != None:

        deselectPiece(False)

    selectedPiece = occupyingPiece
    obj[1] = None
    obj[2] = None
    print("You've found a piece! good job")

    grabPieceSoundObj = pygame.mixer.Sound("Click Effect High.ogg")
    grabPieceSoundObj.play()

    print("coordinates: " + str(boardData.index(item)), str(item.index(obj)))

    selectedPieceCoords = (boardData.index(item), item.index(obj))



def getDirection(item, obj):

    global dif, targetCoords

    pieceRow = boardData.index(item)
    pieceCol = item.index(obj)

    targetCoords = (pieceRow, pieceCol)

    selPieceRow = selectedPieceCoords[0]
    selPieceCol = selectedPieceCoords[1]

    if selectedPiece == "Bomb":

        return None

    if selectedPiece == "Flag":

        return None

    if selectedPiece == "Scout":

        if pieceCol == selPieceCol:

            if pieceRow < selPieceRow:

                dif = selPieceRow - pieceRow

                #searches adjecent squares for blocking pieces
                for num in range(dif):

                    if boardData[selPieceRow - num][selPieceCol][1] != None or boardData[selPieceRow - num][selPieceCol][0] == None:

                        return None

                return "up"


            elif pieceRow > selPieceRow:

                dif = pieceRow - selPieceRow

                for num in range(dif):

                    if boardData[selPieceRow + num][selPieceCol][1] != None or boardData[selPieceRow + num][selPieceCol][0] == None:

                        return None

                return "down"


        elif pieceRow == selPieceRow:

            if pieceCol < selPieceCol:

                dif = selPieceCol - pieceCol

                for num in range(dif):

                    if boardData[selPieceRow][selPieceCol - num][1] != None or boardData[selPieceRow][selPieceCol - num][0] == None:

                        return None

                return "left"


            elif pieceCol > selPieceCol:

                dif = pieceCol - selPieceCol

                for num in range(dif):

                    if boardData[selPieceRow][selPieceCol + num][1] != None or boardData[selPieceRow][selPieceCol + num][0] == None:

                        return None

                return "right"


    else:

        if selPieceCol == pieceCol:

            if selPieceRow - 1 == pieceRow:

                return "up"

            elif selPieceRow + 1 == pieceRow:

                return "down"

        elif selPieceRow == pieceRow:

            if selPieceCol + 1 == pieceCol:

                return "right"

            elif selPieceCol - 1 == pieceCol:

                return "left"



def drawSelectedMovePiece(coords):

    if selectedPiece != None:

        row = coords[0]
        col = coords[1]
    
        selectedSquareRect = boardData[row][col][0]

        genPieceObject(selectedSquareRect.left + 3, selectedSquareRect.top + 3, selectedPiece, turn, False, True)



def deselectPiece(playSound):

    global selectedPiece, selectedPieceCoords

    boardData[selectedPieceCoords[0]][selectedPieceCoords[1]][1] = selectedPiece
    boardData[selectedPieceCoords[0]][selectedPieceCoords[1]][2] = turn

    if playSound != False:

        dropPieceSoundObj = pygame.mixer.Sound("Click Effect Low.ogg")
        dropPieceSoundObj.play()

    selectedPiece = None
    selectedPieceCoords = None



def executeMove(modifier, direction):

    global dif, selectedPieceCoords, turn

    oldPoint = selectedPieceCoords

    x = 0
    y = 0

    moveNum = dif * 65 + modifier

    if direction == "up":

        while y <= moveNum:

            eventHandler()

            gameDisplay.fill(white)
            drawBoard()
            drawCapturedPieces()

            animateMovePiece(x, y)

            y += dif

            pygame.display.update()

            fpsClock.tick(fps)

        selectedPieceCoords = (selectedPieceCoords[0] - dif, selectedPieceCoords[1])


    elif direction == "down":

        while y >= -1 * moveNum:

            eventHandler()

            gameDisplay.fill(white)
            drawBoard()
            drawCapturedPieces()

            animateMovePiece(x, y)

            y -= dif

            pygame.display.update()

            fpsClock.tick(fps)

        selectedPieceCoords = (selectedPieceCoords[0] + dif, selectedPieceCoords[1])


    elif direction == "left":

        while x <= moveNum:

            eventHandler()

            gameDisplay.fill(white)
            drawBoard()
            drawCapturedPieces()

            animateMovePiece(x, y)

            x += dif

            pygame.display.update()

            fpsClock.tick(fps)

        selectedPieceCoords = (selectedPieceCoords[0], selectedPieceCoords[1] - dif)


    elif direction == "right":

        while x >= -1 * moveNum:

            eventHandler()

            gameDisplay.fill(white)
            drawBoard()
            drawCapturedPieces()

            animateMovePiece(x, y)

            x -= dif

            pygame.display.update()

            fpsClock.tick(fps)

        selectedPieceCoords = (selectedPieceCoords[0], selectedPieceCoords[1] + dif)

    updateAIIntel(selectedPieceCoords, oldPoint, selectedPiece)

    dif = 1



def animateMovePiece(x, y):

    row = selectedPieceCoords[0]
    col = selectedPieceCoords[1]
    
    selectedSquareRect = boardData[row][col][0]

    genPieceObject(selectedSquareRect.left + 3 - x, selectedSquareRect.top + 3 - y, selectedPiece, turn, False, True)



def getBattleResult(attacker, defender, attackDirection):

    if defender == attacker:

        return "tie"

    elif defender == "Flag":

        winGame(attackDirection)
        
        return "game over"

    elif attacker == "Miner" and defender == "Bomb":

        return "attacker"

    elif attacker != "Miner" and defender == "Bomb":

        return "defender"

    elif attacker == "Spy" and defender == "Marshal":

        return "attacker"

    elif rankData[attacker] < rankData[defender]:

        return "attacker"

    elif rankData[defender] < rankData[attacker]:

        return "defender"

    
    
def executeBattle(deadPiecePoint, attackDirection):

    global boardData, battlePiece1, battlePiece2, capturedPieces, targetCoords, AIKnownPieces

    defender = boardData[targetCoords[0]][targetCoords[1]][1]
    attacker = selectedPiece

    attackerSquareRect = boardData[targetCoords[0]][targetCoords[1]][0]
    defenderSquareRect = attackerSquareRect

    battleSoundObj = pygame.mixer.Sound("Sword Effect 2.ogg")
    battleSoundObj.play()

    attackerPt = getAttackerPt(attackerSquareRect, attackDirection)

    defColor = altColor()

    defenderPt = (defenderSquareRect.left + 7, defenderSquareRect.top + 7)

    result = getBattleResult(attacker, defender, attackDirection)

    if result != "game over":

        mod1 = getModifier(attackerPt, battlePt1)
        mod2 = getModifier(defenderPt, battlePt2)

        animateMove(attackerPt, battlePt1, mod1, attacker, turn)
        battlePiece1 = attacker

        boardData[targetCoords[0]][targetCoords[1]][1] = None
        boardData[targetCoords[0]][targetCoords[1]][2] = None
        animateMove(defenderPt, battlePt2, mod2, defender, defColor)
        battlePiece2 = defender

        animateBattle(attacker, defender)

        if result == "attacker":

            deathEffect(battlePt2, altColor())
            battlePiece2 = None
            animateMove(battlePt2, deadPiecePoint, 4, defender, altColor())
            capturedPieces.append([defender, altColor()])

            mod = getModifier(battlePt1, defenderPt)
            battlePiece1 = None
            animateMove(battlePt1, defenderPt, mod, attacker, turn)

            boardData[targetCoords[0]][targetCoords[1]][1] = attacker
            boardData[targetCoords[0]][targetCoords[1]][2] = turn

            isKnown = updateAIIntel(targetCoords, targetCoords, attacker)

            if turn == red and isKnown == False:

                AIKnownPieces.append([attacker, targetCoords])

        elif result == "defender":

            deathEffect(battlePt1, turn)
            battlePiece1 = None
            animateMove(battlePt1, deadPiecePoint, 4, attacker, turn)
            capturedPieces.append([attacker, turn])

            mod = getModifier(battlePt2, defenderPt)
            battlePiece2 = None
            animateMove(battlePt2, defenderPt, mod, defender, altColor())

            boardData[targetCoords[0]][targetCoords[1]][1] = defender
            boardData[targetCoords[0]][targetCoords[1]][2] = altColor()

            isKnown = updateAIIntel(targetCoords, targetCoords, defender)

            if turn == blue and isKnown == False:

                AIKnownPieces.append([defender, targetCoords])

        elif result == "tie":

            deathEffect(battlePt1, turn)
            deathEffect(battlePt2, altColor())

            battlePiece1 = None
            animateMove(battlePt1, deadPiecePoint, 4, attacker, turn)
            capturedPieces.append([attacker, turn])

            deadPiecePoint = drawCapturedPieces()
            
            battlePiece2 = None
            animateMove(battlePt2, deadPiecePoint, 4, defender, altColor())
            capturedPieces.append([defender, altColor()])

    targetCoords = None





def getAttackerPt(rect, attackDirection):

    if attackDirection == "up":

        return (rect.left + 3, rect.top + 33)

    elif attackDirection == "right":

        return (rect.left - 27, rect.top + 3)

    elif attackDirection == "down":

        return (rect.left + 3, rect.top - 27)

    elif attackDirection == "left":

        return (rect.left + 33, rect.top + 3)


#can move a piece between any two points on the board
def animateMove(p1, p2, modifier, piece, color):

    squareRect = boardData[selectedPieceCoords[0]][selectedPieceCoords[1]][0]

    difX = p1[0] - p2[0]
    difY = p1[1] - p2[1]

    moveSlope = difY/difX

    if difX > 0:

        xDirection = 1

    else:

        xDirection = -1
        moveSlope = -1 * moveSlope


    blitX = 0
    blitY = 0

    for x in range(abs(int(difX/modifier))):


        eventHandler()

        gameDisplay.fill(white)
        drawBoard()
        drawCapturedPieces()

        genPieceObject(p1[0] - int(blitX), p1[1] - int(blitY), piece, color, True, True)

        blitX += xDirection * modifier
        blitY += moveSlope * modifier

        pygame.display.update()

        fpsClock.tick(fps)



def animateBattle(attacker, defender):

    battleAmbienceObj = pygame.mixer.Sound("Battle Sounds.ogg")
    battleAmbienceObj.play()

    eventHandler()

    gameDisplay.fill(white)
    drawBoard()
    drawCapturedPieces()

    swordsImage = pygame.image.load("Crossed Swords.png")
    gameDisplay.blit(swordsImage, (300, 300))

    pygame.display.update()

    fpsClock.tick(fps)

    pygame.time.delay(2500)



#scales movement modifier based on distance
def getModifier(pt1, pt2):

    if 30 > pt1[0] - pt2[0] > -30:

        return 1

    elif 100 > pt1[0] - pt2[0] > -100:

        return 2

    else:

        return 3



#returns color of player who's turn it isn't
def altColor():

    if turn == red:

        return blue

    else:

        return red



def displayFps():

    framerate = fpsClock.get_fps()

    textObj = pygame.font.Font("Becker.ttf", 10)
    textSurfaceObj = textObj.render(str(framerate), True, black)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (1000, 600)
    gameDisplay.blit(textSurfaceObj, textRectObj)



def deathEffect(point, color):

    pygame.draw.rect(gameDisplay, color, (point[0], point[1], 50, 50))

    deathSoundObj = pygame.mixer.Sound("Death Sound.ogg")
    deathSoundObj.play()

    skullImage = pygame.image.load("Skull.png")
    gameDisplay.blit(skullImage, (point[0], point[1]))

    pygame.display.update()

    fpsClock.tick(fps)

    pygame.time.delay(2500)



def winGame(attackDirection):

    if turn == red:

        winStr = "RED WINS!"
        winSoundObj = pygame.mixer.Sound("Triumph Effect.ogg")
        winSoundObj.play()

        pygame.mixer.music.load("Win Game Music.ogg")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)

    else:

        winStr = "BLUE WINS!"
        loseSoundObj = pygame.mixer.Sound("Death Sound.ogg")
        loseSoundObj.play()

        pygame.mixer.music.load("Lose Game Music.ogg")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)


    #redraws board to show enemy pieces
    for item in boardData:

        for obj in item:

            squareObj = obj[0]
            occupyingPiece = obj[1]
            color = obj[2]

            if occupyingPiece != None and color == blue:

                genPieceObject(squareObj.left + 7, squareObj.top + 7, occupyingPiece, color, True, False)

            if occupyingPiece == "Flag" and color == altColor():

                attackerPt = getAttackerPt(squareObj, attackDirection)

    genPieceObject(attackerPt[0], attackerPt[1], selectedPiece, turn, False, True)


    winTextObj = pygame.font.Font("Becker.ttf", 36)
    winTextSurfaceObj = winTextObj.render(winStr, True, turn)
    winTextRectObj = winTextSurfaceObj.get_rect()
    winTextRectObj.center = (325, 325)
    gameDisplay.blit(winTextSurfaceObj, winTextRectObj)

    print(winStr)

    pygame.display.update()

    pygame.time.delay(4000)

    newPhase()



def playAgain():

    buttonRect = pygame.Rect(225, 400, 200, 80)
    pygame.draw.rect(gameDisplay, red, buttonRect)

    textObj = pygame.font.Font("Becker.ttf", 24)
    textSurfaceObj = textObj.render("PLAY AGAIN", True, black)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (325, 440)
    gameDisplay.blit(textSurfaceObj, textRectObj)

    return buttonRect

        


def newPhase():
    global gamePhase
    gamePhase = gamePhase + 1
    print("game phase:", gamePhase)


    

def eventHandler():
    global mouseX, mouseY, mouseClicked
    mouseClicked = False

    #runs through game events

    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            quit()

        elif event.type == MOUSEMOTION:
            mouseX, mouseY = event.pos

        elif event.type == MOUSEBUTTONUP:
            mouseX, mouseY = event.pos
            print(mouseX, mouseY)
            mouseClicked = True




#AI

def randomAction():

    loopCounter = 0

    moveDirection = None
    attackDirection = None

    global selectedPiece, selectedPieceCoords, dif, targetCoords

    while moveDirection == None and attackDirection == None:

        randomRow = randint(0, 9)
        randomCol = randint(0, 9)

        pieceRect = boardData[randomRow][randomCol][0]
        pieceName = boardData[randomRow][randomCol][1]
        pieceColor = boardData[randomRow][randomCol][2]

        if pieceRect != None and pieceName != None and pieceColor == blue and pieceName != "Flag" and pieceName != "Bomb":

            selectedPiece = pieceName
            boardData[randomRow][randomCol][1] = None
            boardData[randomRow][randomCol][2] = None
            
            selectedPieceCoords = (randomRow, randomCol)

            if selectedPiece == "Scout":

                #looks for move down
                for x in range(-9, 0):

                    if randomRow + abs(x) <= 9:

                        if boardData[randomRow + abs(x)][randomCol][2] == red and not isKnown(boardData[randomRow + abs(x)][randomCol][1], randomRow + abs(x), randomCol):

                            attackDirection = getDirection(boardData[randomRow + abs(x)], boardData[randomRow + abs(x)][randomCol])

                            if attackDirection != None:
                                break

                        elif boardData[randomRow + abs(x)][randomCol][1] == None and boardData[randomRow + abs(x)][randomCol][0] != None and loopCounter > 25:

                            moveDirection = getDirection(boardData[randomRow + abs(x)], boardData[randomRow + abs(x)][randomCol])

                            if moveDirection != None:
                                break


                randDirection = randint(0, 1)

                #looks for move right
                if attackDirection == None and moveDirection == None and randDirection == 0:

                    for x in range(-9, 0):

                        if randomCol + abs(x) <= 9:

                            if boardData[randomRow][randomCol + abs(x)][2] == red and not isKnown(boardData[randomRow][randomCol + abs(x)][1], randomRow, randomCol + abs(x)):

                                attackDirection = getDirection(boardData[randomRow], boardData[randomRow][randomCol + abs(x)])

                                if attackDirection != None:
                                    break

                            elif boardData[randomRow][randomCol + abs(x)][1] == None and boardData[randomRow][randomCol + abs(x)][0] != None and loopCounter > 50:

                                moveDirection = getDirection(boardData[randomRow], boardData[randomRow][randomCol + abs(x)])

                                if moveDirection != None:
                                    break


                #looks for move left
                if attackDirection == None and moveDirection == None and randDirection == 1:

                    for x in range(-9, 0):

                        if randomCol + x >= 0:

                            if boardData[randomRow][randomCol + x][2] == red and not isKnown(boardData[randomRow][randomCol + x][1], randomRow, randomCol + x):

                                attackDirection = getDirection(boardData[randomRow], boardData[randomRow][randomCol + x])

                                if attackDirection != None:
                                    break

                            elif boardData[randomRow][randomCol + x][1] == None and boardData[randomRow][randomCol + x][0] != None and loopCounter > 50:

                                moveDirection = getDirection(boardData[randomRow], boardData[randomRow][randomCol + x])

                                if moveDirection != None:
                                    break


                #looks for move up, as a last resort
                if attackDirection == None and moveDirection == None:
                    
                    for x in range(-9, 0):

                        if randomRow + x >= 0:

                            if boardData[randomRow + x][randomCol][2] == red and not isKnown(boardData[randomRow + x][randomCol][1], randomRown + x, randomCol):

                                attackDirection = getDirection(boardData[randomRow + x], boardData[randomRow + x][randomCol])

                                if attackDirection != None:
                                    break

                            elif boardData[randomRow + x][randomCol][1] == None and boardData[randomRow + x][randomCol][0] != None and loopCounter > 200:

                                moveDirection = getDirection(boardData[randomRow + x], boardData[randomRow + x][randomCol])

                                if moveDirection != None:
                                    break



            else:

                randDirection = randint(0, 1)

                #looks for move down
                if randomRow + 1 <= 9 and boardData[randomRow + 1][randomCol][2] == red:

                    attackDirection = "down"
                    targetCoords = (randomRow + 1, randomCol)

                elif randomRow + 1 <= 9 and boardData[randomRow + 1][randomCol][1] == None and boardData[randomRow + 1][randomCol][0] != None and loopCounter > 25:

                    moveDirection = "down"


                #looks for move right
                elif randomCol + 1 <= 9 and boardData[randomRow][randomCol + 1][2] == red and randDirection == 0:

                    attackDirection = "right"
                    targetCoords = (randomRow, randomCol + 1)

                elif randomCol + 1 <= 9 and boardData[randomRow][randomCol + 1][1] == None and boardData[randomRow][randomCol + 1][0] != None and randDirection == 0 and loopCounter > 50:

                    moveDirection = "right"

                
                #looks for move left
                elif randomCol - 1 >= 0 and boardData[randomRow][randomCol - 1][2] == red and randDirection == 1:

                    attackDirection = "left"
                    targetCoords = (randomRow, randomCol - 1)

                elif randomCol - 1 >= 0 and boardData[randomRow][randomCol - 1][1] == None and boardData[randomRow][randomCol - 1][0] != None and loopCounter > 50:

                    moveDirection = "left"


                #looks for move up, as a last resort
                if randomRow - 1 >= 0 and boardData[randomRow - 1][randomCol][2] == red:

                    attackDirection = "up"
                    targetCoords = (randomRow - 1, randomCol)

                elif randomRow - 1 >= 0 and boardData[randomRow - 1][randomCol][1] == None and boardData[randomRow - 1][randomCol][0] != None and loopCounter > 200:

                    moveDirection = "up"



            if moveDirection == None and attackDirection == None and selectedPiece != None:

                boardData[randomRow][randomCol][1] = selectedPiece
                boardData[randomRow][randomCol][2] = blue
                selectedPiece = None

                dif = 1

        loopCounter += 1

    return moveDirection, attackDirection


def updateAIIntel(newPoint, oldPoint, pieceName):

    global AIKnownPieces

    for item in AIKnownPieces:

        if item[0] == pieceName and item[1] == oldPoint:

            item[1] = newPoint
            return True

    return False


#removes any known pieces that do not correspond with existing pieces
def cleanAIIntel():

    global AIKnownPieces

    for item in AIKnownPieces:

        if boardData[item[1][0]][item[1][1]][1] == None and item[1] != selectedPieceCoords or boardData[item[1][0]][item[1][1]][2] == blue:

            AIKnownPieces.remove(item)


#attacks a known piece with an AI piece of higher rank
def attackKnownPiece():

    global selectedPiece, selectedPieceCoords, targetCoords

    result = None

    for item in AIKnownPieces:

        row = item[1][0]
        col = item[1][1]

        if row > 0 and boardData[row - 1][col][2] == blue and boardData[row - 1][col][1] != "Bomb" and boardData[row - 1][col][1] != "Flag" and getBattleResult(boardData[row - 1][col][1], item[0], None) == "attacker":

            print("comparing: ", boardData[row - 1][col][1], item[0])

            selectedPiece = boardData[row - 1][col][1]
            boardData[row - 1][col][1] = None
            boardData[row - 1][col][2] = None
            
            selectedPieceCoords = (row - 1, col)
            targetCoords = (row, col)

            return "down"
            

        elif col > 0 and boardData[row][col - 1][2] == blue and boardData[row][col - 1][1] != "Bomb" and boardData[row][col - 1][1] != "Flag" and getBattleResult(boardData[row][col - 1][1], item[0], None) == "attacker":

            print("comparing: ", boardData[row][col - 1][1], item[0])

            selectedPiece = boardData[row][col - 1][1]
            boardData[row][col - 1][1] = None
            boardData[row][col - 1][2] = None
            
            selectedPieceCoords = (row, col - 1)
            targetCoords = (row, col)

            return "right"
            

        elif col < 9 and boardData[row][col + 1][2] == blue and boardData[row][col + 1][1] != "Bomb" and boardData[row][col + 1][1] != "Flag" and getBattleResult(boardData[row][col + 1][1], item[0], None) == "attacker":

            print("comparing: ", boardData[row][col + 1][1], item[0])

            selectedPiece = boardData[row][col + 1][1]
            boardData[row][col + 1][1] = None
            boardData[row][col + 1][2] = None
            
            selectedPieceCoords = (row, col + 1)
            targetCoords = (row, col)

            return "left"
            

        elif row < 9 and boardData[row + 1][col][2] == blue and boardData[row + 1][col][1] != "Bomb" and boardData[row + 1][col][1] != "Flag" and getBattleResult(boardData[row + 1][col][1], item[0], None) == "attacker":

            print("comparing: ", boardData[row + 1][col][1], item[0])

            selectedPiece = boardData[row + 1][col][1]
            boardData[row + 1][col][1] = None
            boardData[row + 1][col][2] = None
            
            selectedPieceCoords = (row + 1, col)
            targetCoords = (row, col)

            return "up"


#returns true if a piece with this name and coordinates is known by the AI
def isKnown(name, row, col):

    for item in AIKnownPieces:

        if item[1][0] == row and item[1][1] == col:

            assert item[0] == name
            return True

    return False
                        


#run game

boardData = genCoords()
loadTitleScreen()
buttonRect = startButton()

while True:

    eventHandler()

    if gamePhase == 0:
        startGame()

    elif gamePhase == 1:
        writeRules()

    elif gamePhase == 2:
        if mouseClicked == True:
            gameDisplay.fill(white)
            newPhase()
            pygame.mixer.music.load("Setup Phase Music.ogg")
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)

    elif gamePhase == 3:
        setupPhase()

    elif gamePhase == 4:
        playPhase()

    elif gamePhase == 5:
        returnRect = playAgain()
        newPhase()

    elif gamePhase == 6:
        if returnRect.left < mouseX < returnRect.right and returnRect.top < mouseY < returnRect.bottom and mouseClicked == True:
            gameDisplay.fill(white)

            #resets game global variables
            gamePhase = 0

            pieceData = {"Marshal": [1], "General": [1], "Colonel": [2], "Major": [3], "Captain": [4], "Lieutenant": [4], "Sergeant": [4], "Miner": [5], "Scout": [8], "Spy": [1], "Bomb": [6], "Flag": [1]}
            capturedPieces = []
            ready = False
            selectedPiece = None
            selectedPieceCoords = None
            targetCoords = None
            dif = 1
            AIKnownPieces = []
            boardData = [[],[],[],[],[],[],[],[],[],[]]
            battlePiece1 = None
            battlePiece2 = None
            turn = red

            boardData = genCoords()
            loadTitleScreen()
            buttonRect = startButton()

    
    pygame.display.update()

    fpsClock.tick(fps)


