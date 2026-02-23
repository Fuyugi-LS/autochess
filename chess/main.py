'''
    Add or remove bots :
    
    SET_WHITE_AS_BOT = False
    SET_BLACK_AS_BOT = True
'''

# Responsible for handling user input and displaying the current Gamestate object

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import random
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as p
import tkinter as tk
from tkinter import filedialog
from engine import GameState, Move
from chessAi import findRandomMoves, findBestMove, initialize_engines, quit_stockfish, set_elo, get_current_engine_stats, get_skill_level, findOptimalMove
from threading import Thread
from queue import Queue

# Initialize the mixer
p.mixer.init()
# Load sound files
move_sound = p.mixer.Sound("sounds/move-sound.mp3")
capture_sound = p.mixer.Sound("sounds/capture.mp3")
promote_sound = p.mixer.Sound("sounds/promote.mp3")

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''

     ADD BOTS         
    IF IN GameState() , 
    
    playerWantsToPlayAsBlack = True
    SET_BLACK_AS_BOT SHOULD BE = FALSE

'''

SET_WHITE_AS_BOT = True
SET_BLACK_AS_BOT = True

# Define colors

# 1 Green

LIGHT_SQUARE_COLOR = (237, 238, 209)
DARK_SQUARE_COLOR = (119, 153, 82)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)

# 2 Brown

'''
LIGHT_SQUARE_COLOR = (240, 217, 181)
DARK_SQUARE_COLOR = (181, 136, 99)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (255, 255, 51)
'''

# 3 Gray

'''
LIGHT_SQUARE_COLOR = (220,220,220)
DARK_SQUARE_COLOR = (170,170,170)
MOVE_HIGHLIGHT_COLOR = (84, 115, 161)
POSSIBLE_MOVE_COLOR = (164,184,196)
'''


def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK',
              'bp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wp']
    for piece in pieces:
        image_path = "images1/" + piece + ".png"
        original_image = p.image.load(image_path)
        # p.transform.smoothscale is bit slower than p.transform.scale, using this to reduce pixelation and better visual quality for scaling images to larger sizes
        IMAGES[piece] = p.transform.smoothscale(
            original_image, (SQ_SIZE, SQ_SIZE))


def pawnPromotionPopup(screen, gs):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    text = font.render("Choose promotion:", True, p.Color("black"))

    # Create buttons for promotion choices with images
    button_width, button_height = 100, 100
    buttons = [
        p.Rect(100, 200, button_width, button_height),
        p.Rect(200, 200, button_width, button_height),
        p.Rect(300, 200, button_width, button_height),
        p.Rect(400, 200, button_width, button_height)
    ]

    if gs.whiteToMove:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/bQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/bB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/bN.png"), (100, 100))
        ]
    else:
        button_images = [
            p.transform.smoothscale(p.image.load(
                "images1/wQ.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wR.png"), (100, 100)),
            p.transform.smoothscale(p.image.load(
                "images1/wB.png"), (100, 100)),
            p.transform.smoothscale(p.image.load("images1/wN.png"), (100, 100))
        ]

    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if e.button != 1:
                    continue
                mouse_pos = e.pos
                for i, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos):
                        if i == 0:
                            return "Q"  # Return the index of the selected piece
                        elif i == 1:
                            return "R"
                        elif i == 2:
                            return "B"
                        else:
                            return "N"

        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        screen.blit(text, (110, 150))

        for i, button in enumerate(buttons):
            p.draw.rect(screen, p.Color("white"), button)
            screen.blit(button_images[i], button.topleft)

        p.display.flip()


'''
moveLocationWhite = ()
movedPieceWhite = ""
moveLocationBlack = ()
movedPieceBlack = ""

moveWhiteLog = []
moveBlackLog = []
'''


def show_homepage(screen, clock):
    font = p.font.SysFont("Times New Roman", 30, False, False)
    title_font = p.font.SysFont("Times New Roman", 50, True, False)
    
    title_text = title_font.render("AutoChess", True, p.Color("black"))
    text_white = font.render("Play as White", True, p.Color("black"))
    text_black = font.render("Play as Black", True, p.Color("black"))
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    button_white = p.Rect(screen_width // 2 - 125, screen_height // 2 - 40, 250, 50)
    button_black = p.Rect(screen_width // 2 - 125, screen_height // 2 + 40, 250, 50)
    
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if e.button != 1:
                    continue
                if button_white.collidepoint(e.pos):
                    return False, True, False
                elif button_black.collidepoint(e.pos):
                    return True, False, True
                    
        screen.fill(p.Color(LIGHT_SQUARE_COLOR))
        
        # Draw title
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 4 - 30))
        
        # Draw buttons
        p.draw.rect(screen, p.Color("white"), button_white)
        p.draw.rect(screen, p.Color("black"), button_white, 2) # Outline
        p.draw.rect(screen, p.Color("white"), button_black)
        p.draw.rect(screen, p.Color("black"), button_black, 2) # Outline
        
        # Draw text on buttons
        screen.blit(text_white, (button_white.centerx - text_white.get_width() // 2, button_white.centery - text_white.get_height() // 2))
        screen.blit(text_black, (button_black.centerx - text_black.get_width() // 2, button_black.centery - text_black.get_height() // 2))
        
        p.display.flip()
        clock.tick(MAX_FPS)


def main():
    # initialize py game
    p.init()
    initialize_engines()
    
    screen = p.display.set_mode(
        (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    
    set_white_as_bot, set_black_as_bot, play_as_black = show_homepage(screen, clock)
    
    # Randomize ELO if playing against bot
    if set_white_as_bot or set_black_as_bot:
        stats = get_current_engine_stats()
        if stats["name"] == "Stockfish":
            set_elo(random.randint(1320, 3190))
        elif stats["name"] == "Beginner Bot":
            set_elo(random.choice([200, 300, 400, 500, 600, 700, 800, 900]))
    
    screen.fill(p.Color(LIGHT_SQUARE_COLOR))
    moveLogFont = p.font.SysFont("Times New Roman", 12, False, False)
    moveLogFont = p.font.SysFont("Times New Roman", 12, False, False)
    # Creating gamestate object calling our constructor
    gs = GameState()
    # if a user makes a move we can ckeck if its in the list of valid moves
    validMoves = gs.getValidMoves()
    moveMade = False  # if user makes a valid moves and the gamestate changes then we should generate new set of valid move
    animate = False  # flag var for when we should animate a move
    loadImages()
    running = True
    squareSelected = ()  # keep tracks of last click
    # clicking to own piece and location where to move[(6,6),(4,4)]
    playerClicks = []
    gameOver = False  # gameover if checkmate or stalemate
    playerWhiteHuman = not set_white_as_bot
    playerBlackHuman = not set_black_as_bot
    AIThinking = False  # True if ai is thinking
    moveFinderProcess = None
    moveUndone = False
    pieceCaptured = False
    positionHistory = ""
    previousPos = ""
    countMovesForDraw = 0
    COUNT_DRAW = 0
    
    HumanGuessing = False
    StockfishOptimalMove = None
    OptimalMoveProcess = None
    
    invalid_move_text_timer = 0
    
    while running:
        humanTurn = (gs.whiteToMove and playerWhiteHuman) or (
            not gs.whiteToMove and playerBlackHuman)
            
        # Start calculating optimal move if it's the player's turn and we haven't started yet
        if not gameOver and humanTurn and not moveUndone and StockfishOptimalMove is None:
            if not HumanGuessing:
                HumanGuessing = True
                returnQueue = Queue()
                OptimalMoveProcess = Thread(target=findOptimalMove, args=(gs, validMoves, returnQueue))
                OptimalMoveProcess.start()
            if not OptimalMoveProcess.is_alive():
                StockfishOptimalMove = returnQueue.get()
                HumanGuessing = False
        for e in p.event.get():
            if e.type == p.QUIT:
                quit_stockfish()
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if e.button != 1 or invalid_move_text_timer > 0:
                    continue
                if not gameOver:  # allow mouse handling only if its not game over
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if play_as_black:
                        row = 7 - row
                        col = 7 - col
                    # if user clicked on same square twice or user click outside board
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        squareSelected = (row, col)
                        # append player both clicks (place and destination)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        if HumanGuessing:
                            # Still calculating optimal move, ignore clicks or wait
                            squareSelected = ()
                            playerClicks = []
                            continue
                            
                        # user generated a move
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            # check if the move is in the validMoves
                            if move == validMoves[i]:
                                if StockfishOptimalMove and move.getUCINotation() == StockfishOptimalMove.getUCINotation():
                                    # Correct guess!
                                    if gs.board[validMoves[i].endRow][validMoves[i].endCol] != '--':
                                        pieceCaptured = True
                                    gs.makeMove(validMoves[i])
                                    if (move.isPawnPromotion):
                                        # Show pawn promotion popup and get the selected piece
                                        promotion_choice = pawnPromotionPopup(
                                            screen, gs)
                                        # Set the promoted piece on the board
                                        gs.board[move.endRow][move.endCol] = move.pieceMoved[0] + \
                                            promotion_choice
                                        promote_sound.play()
                                        pieceCaptured = False
                                    # add sound for human move
                                    if (pieceCaptured or move.isEnpassantMove):
                                        # Play capture sound
                                        capture_sound.play()
                                        # print("capture sound")
                                    elif not move.isPawnPromotion:
                                        # Play move sound
                                        move_sound.play()
                                        # print("move sound")
                                    pieceCaptured = False
                                    moveMade = True
                                    animate = True
                                    squareSelected = ()
                                    playerClicks = []
                                    StockfishOptimalMove = None # reset for next turn
                                else:
                                    # Wrong guess
                                    invalid_move_text_timer = 6 # Show for 6 frames (~0.1 sec)
                                    squareSelected = ()
                                    playerClicks = []
                                    break
                                    
                        if not moveMade and invalid_move_text_timer == 0:
                            playerClicks = [squareSelected]

            # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    # when user undo move valid move change, here we could use [ validMoves = gs.getValidMoves() ] which would update the current validMoves after undo
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        from chessAi import _send_command
                        _send_command('stop')
                        AIThinking = False
                    if HumanGuessing:
                        from chessAi import _send_hint_command
                        _send_hint_command('stop')
                        HumanGuessing = False
                    StockfishOptimalMove = None
                    moveUndone = True
                if e.key == p.K_r:  # reset board when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        from chessAi import _send_command
                        _send_command('stop')
                        AIThinking = False
                    if HumanGuessing:
                        from chessAi import _send_hint_command
                        _send_hint_command('stop')
                        HumanGuessing = False
                    StockfishOptimalMove = None
                    moveUndone = True

        # AI move finder
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # keep track of data, to pass data between threads
                moveFinderProcess = Thread(target=findBestMove, args=(
                    gs, validMoves, returnQueue))  # when processing start we call these process
                # call findBestMove(gs, validMoves, returnQueue) #rest of the code could still work even if the ai is thinking
                moveFinderProcess.start()
                # AIMove = findBestMove(gs, validMoves)
                # gs.makeMove(AIMove)
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()  # return from returnQueue
                if AIMove is None:
                    AIMove = findRandomMoves(validMoves)

                if gs.board[AIMove.endRow][AIMove.endCol] != '--':
                    pieceCaptured = True

                gs.makeMove(AIMove)

                if AIMove.isPawnPromotion:
                    # Show pawn promotion popup and get the selected piece
                    promotion_choice = pawnPromotionPopup(screen, gs)
                    # Set the promoted piece on the board
                    gs.board[AIMove.endRow][AIMove.endCol] = AIMove.pieceMoved[0] + \
                        promotion_choice
                    promote_sound.play()
                    pieceCaptured = False

                # add sound for human move
                if (pieceCaptured or AIMove.isEnpassantMove):
                    # Play capture sound
                    capture_sound.play()
                    # print("capture sound")
                elif not AIMove.isPawnPromotion:
                    # Play move sound
                    move_sound.play()
                    # print("move sound")
                pieceCaptured = False
                AIThinking = False
                moveMade = True
                animate = True
                squareSelected = ()
                playerClicks = []

        if moveMade:
            if countMovesForDraw == 0 or countMovesForDraw == 1 or countMovesForDraw == 2 or countMovesForDraw == 3:
                countMovesForDraw += 1
            if countMovesForDraw == 4:
                positionHistory += gs.getBoardString()
                if previousPos == positionHistory:
                    COUNT_DRAW += 1
                    positionHistory = ""
                    countMovesForDraw = 0
                else:
                    previousPos = positionHistory
                    positionHistory = ""
                    countMovesForDraw = 0
                    COUNT_DRAW = 0
            # Call animateMove to animate the move
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, play_as_black)
            # genetare new set of valid move if valid move is made
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, play_as_black)
        
        if invalid_move_text_timer > 0:
            # Draw invalid move overlay
            s = p.Surface((BOARD_WIDTH, BOARD_HEIGHT), p.SRCALPHA)
            s.fill((0, 0, 0, 128)) # Darken screen slightly
            screen.blit(s, (0, 0))
            
            invalid_font = p.font.SysFont("Times New Roman", 40, True, False)
            invalid_text = invalid_font.render("[invalid move]", True, p.Color("red"))
            screen.blit(invalid_text, (BOARD_WIDTH // 2 - invalid_text.get_width() // 2, BOARD_HEIGHT // 2 - invalid_text.get_height() // 2))
            
            invalid_move_text_timer -= 1

        if COUNT_DRAW == 1:
            gameOver = True
            text = 'Draw due to repetition'
            drawEndGameText(screen, text)
        if gs.stalemate:
            gameOver = True
            text = 'Stalemate'
            drawEndGameText(screen, text)
        elif gs.checkmate:
            gameOver = True
            text = 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont, play_as_black):
    drawSquare(screen)  # draw square on board
    highlightSquares(screen, gs, validMoves, squareSelected, play_as_black)
    drawPieces(screen, gs.board, play_as_black)
    drawMoveLog(screen, gs, moveLogFont)


def drawSquare(screen):
    global colors
    colors = [p.Color(LIGHT_SQUARE_COLOR), p.Color(DARK_SQUARE_COLOR)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(
                col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, squareSelected, play_as_black):
    if squareSelected != ():  # make sure there is a square to select
        row, col = squareSelected
        # make sure they click there own piece
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected piece square
            # Surface in pygame used to add images or transperency feature
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            # set_alpha --> transperancy value (0 transparent)
            s.set_alpha(100)
            s.fill(p.Color(MOVE_HIGHLIGHT_COLOR))
            
            draw_r = 7 - row if play_as_black else row
            draw_c = 7 - col if play_as_black else col
            screen.blit(s, (draw_c*SQ_SIZE, draw_r*SQ_SIZE))
            
            # highlighting valid square
            s.fill(p.Color(POSSIBLE_MOVE_COLOR))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    draw_end_r = 7 - move.endRow if play_as_black else move.endRow
                    draw_end_c = 7 - move.endCol if play_as_black else move.endCol
                    screen.blit(s, (draw_end_c*SQ_SIZE, draw_end_r*SQ_SIZE))


def drawPieces(screen, board, play_as_black):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                draw_r = 7 - row if play_as_black else row
                draw_c = 7 - col if play_as_black else col
                screen.blit(IMAGES[piece], p.Rect(
                    draw_c * SQ_SIZE, draw_r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    # rectangle
    moveLogRect = p.Rect(
        BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color(LIGHT_SQUARE_COLOR), moveLogRect)
    
    # Draw Engine Info
    engine_stats = get_current_engine_stats()
    elo_font = p.font.SysFont("Times New Roman", 18, True, False)
    
    y_offset = 10
    
    if engine_stats["name"] == "Stockfish":
        engine_text = elo_font.render("Engine: Stockfish", True, p.Color('black'))
        level_text = elo_font.render(f"Stockfish Level: {engine_stats['stockfish_level']}", True, p.Color('black'))
        elo_text = elo_font.render(f"Approximate Elo: {engine_stats['stockfish_elo']}", True, p.Color('black'))
        
        screen.blit(engine_text, moveLogRect.move(10, y_offset))
        y_offset += engine_text.get_height() + 5
        screen.blit(level_text, moveLogRect.move(10, y_offset))
        y_offset += level_text.get_height() + 5
        screen.blit(elo_text, moveLogRect.move(10, y_offset))
        y_offset += elo_text.get_height() + 10
    elif engine_stats["name"] == "Beginner Bot":
        engine_text = elo_font.render("Engine: Beginner Bot", True, p.Color('black'))
        elo_text = elo_font.render(f"ELO: {engine_stats['stockfish_elo']}", True, p.Color('black'))
        chance_val = int(engine_stats.get('beginner_random_chance', 0) * 100)
        random_text = elo_font.render(f"Randomness: {chance_val}%", True, p.Color('black'))
        
        screen.blit(engine_text, moveLogRect.move(10, y_offset))
        y_offset += engine_text.get_height() + 5
        screen.blit(elo_text, moveLogRect.move(10, y_offset))
        y_offset += elo_text.get_height() + 5
        screen.blit(random_text, moveLogRect.move(10, y_offset))
        y_offset += random_text.get_height() + 10
    else:
        engine_text = elo_font.render("Engine: Maia", True, p.Color('black'))
        level_text = elo_font.render(f"Targeted Ranking: {engine_stats['maia_elo']}", True, p.Color('black'))
        elo_text = elo_font.render(f"Lichess Name: {engine_stats['maia_name']}", True, p.Color('black'))
        
        screen.blit(engine_text, moveLogRect.move(10, y_offset))
        y_offset += engine_text.get_height() + 5
        screen.blit(level_text, moveLogRect.move(10, y_offset))
        y_offset += level_text.get_height() + 5
        screen.blit(elo_text, moveLogRect.move(10, y_offset))
        y_offset += elo_text.get_height() + 10
    
    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = " " + str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 10  # Increase padding for better readability
    lineSpacing = 5  # Increase line spacing for better separation
    
    # Start drawing moves below the elo text
    textY = y_offset

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]

        textObject = font.render(text, True, p.Color('black'))

        # Adjust text location based on padding and line spacing
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)

        # Update Y coordinate for the next line with increased line spacing
        textY += textObject.get_height() + lineSpacing


# animating a move
def animateMove(move, screen, board, clock, play_as_black):
    global colors
    # change in row, col
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSquare = 5  # frames move one square
    # how many frame the animation will take
    frameCount = (abs(deltaRow) + abs(deltaCol)) * framesPerSquare
    # generate all the coordinates
    for frame in range(frameCount + 1):
        # how much does the row and col move by
        row, col = ((move.startRow + deltaRow*frame/frameCount, move.startCol +
                    deltaCol*frame/frameCount))  # how far through the animation
        # for each frame draw the moved piece
        drawSquare(screen)
        drawPieces(screen, board, play_as_black)

        draw_r = 7 - row if play_as_black else row
        draw_c = 7 - col if play_as_black else col
        draw_end_r = 7 - move.endRow if play_as_black else move.endRow
        draw_end_c = 7 - move.endCol if play_as_black else move.endCol

        # erase the piece moved from its ending squares
        color = colors[(move.endRow + move.endCol) %
                       2]  # get color of the square
        endSquare = p.Rect(draw_end_c*SQ_SIZE, draw_end_r *
                           SQ_SIZE, SQ_SIZE, SQ_SIZE)  # pygame rectangle
        p.draw.rect(screen, color, endSquare)

        # draw the captured piece back
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                en_r = 7 - enPassantRow if play_as_black else enPassantRow
                endSquare = p.Rect(draw_end_c*SQ_SIZE, en_r *
                                   SQ_SIZE, SQ_SIZE, SQ_SIZE)  # pygame rectangle
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            draw_c*SQ_SIZE, draw_r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(240)


def drawEndGameText(screen, text):
    # create font object with type and size of font you want
    font = p.font.SysFont("Times New Roman", 30, False, False)
    # use the above font and render text (0 ? antialias)
    textObject = font.render(text, True, p.Color('black'))

    # Get the width and height of the textObject
    text_width = textObject.get_width()
    text_height = textObject.get_height()

    # Calculate the position to center the text on the screen
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH/2 - text_width/2, BOARD_HEIGHT/2 - text_height/2)

    # Blit the textObject onto the screen at the calculated position
    screen.blit(textObject, textLocation)

    # Create a second rendering of the text with a slight offset for a shadow effect
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(1, 1))


# if we import main then main function wont run it will run only while running this file
if __name__ == "__main__":
    main()
