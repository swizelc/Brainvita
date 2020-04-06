#-------------------------------------------------------------------------------
# Name:        Brianvita
# Purpose:     CS coursework
#
# Author:      Acer
#
# Created:     26/11/2019
# Copyright:   (c) Swizel Acer 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#------------ imports------------
import pygame
import time
import sqlite3

#initiate pygame
pygame.init()

#-------------global variables-------------------

#make a screen using and pygame function
SCREEN = pygame.display.set_mode((640, 480))

#--------colours-----------
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
YELLOW = (215,246,250)
BLACK = (0,0,0)
WHITE = (255,255,255)

#----------font sizes--------
FONT = pygame.font.Font(None, 32)
LFONT = pygame.font.Font(None, 55)
SFONT = pygame.font.Font(None, 20)
MblFONT = pygame.font.SysFont('comicsansms',200)

CLOCK = pygame.time.Clock()
#width of one box on the tray
BOX = 50
#position of the tray on the screen
BOARDPOS = (150,50)

pausetime = 0
pause = False


#-----------------classes------------------------


class Database:
    def __init__(self, username,password):
        self.username = username
        self.password = password
        #self.activeuser = activeuser
        
    #creates a table in the database with columns:
    #USERNAME  PRIMARY KEY   
    #PASSWORD           
    #POINTS
    def create_table():
        user = sqlite3.connect('user.db')
        user.execute(''' CREATE TABLE USER
        (
        USERNAME  PRIMARY KEY   NOT NULL,
        PASSWORD        TEXT   NOT NULL,
        POINTS          INT);
        ''')
        print("Created!")
        user.close()

    #adds another coloumn called Highscore
    def alter_table():
        user = sqlite3.connect('user.db')
        user.execute('''ALTER TABLE USER
        ADD COLUMN HIGHSCORE INT;
        ''')
        user.close()

    # checks if username entered already exist in the database
    # if not then it creates a record by inserting the new username and password into the table
    # the active user is set as the newly created one and is directed to the menu
    def sign_up(username,password):
        user = sqlite3.connect('user.db')
        cursor=user.cursor() #the cursor is essentially an iterator,which automatically invokes fetchall, or fetchone
        cursor.execute('SELECT * from USER WHERE username="%s"' %(username))
        if cursor.fetchone() is not None: #if the iterator does actually return something (details are found...then...)
            print("this username already exists plase try different")
            surface = txt_surface("this username already exists please try different","small", BLACK)
            SCREEN.blit(surface, (200,300))
            pygame.display.update()
            time.sleep(4)
            start()
        else:
            user.execute("INSERT INTO USER(USERNAME, PASSWORD,POINTS)\
                VALUES (?,?,0)",( username,password))
            user.commit()
            print('Records Created!')
            global activeuser
            activeuser =username
            menu()
            user.close()
            
    #checks if the username entered exists in the database, then if the password entered matches that in field
    # that user is then logined in and is set as the active user and directed to menu
    #if not login is failed
    #user can try again
    def login(username,password):
        user = sqlite3.connect("user.db") #establish a connection to the database
        cursor=user.cursor() #the cursor is essentially an iterator,which automatically invokes fetchall, or fetchone
        cursor.execute('SELECT * from USER WHERE username="%s" AND password="%s"' %(username,password))
        if cursor.fetchone() is not None: #if the iterator does actually return something (details are found...then...)
            print("Welcome you are logged in")
            global activeuser
            activeuser =username
            print("user: ", username)
            menu()
        else:
            print("Login failed")
            surface = txt_surface("Error Try Again","large",BLACK)
            SCREEN.blit(surface, (200,300))
            pygame.display.update()
            time.sleep(3)
            start()

    #sorts the fields in the table in desencing order of points
    def sorting():
        user = sqlite3.connect('user.db')
        the_rows = user.execute('SELECT * FROM USER ORDER BY POINTS DESC;') #ASC

        for row in the_rows:
            print(row)
        user.close()
        
    #finds the user with the maximum points
    def find_max():
        user = sqlite3.connect('user.db')
        the_rows = user.execute('SELECT max(POINTS) from USER;')
        for row in the_rows:
            print(row)

    #fetches the table - used to take a look at all the information in the dadtabase
    def fetch_display():
        user = sqlite3.connect('user.db')
        cursor = user.execute("SELECT * from USER")
        for row in cursor:
            print("USERNAME = ", row[0])
            print("PASSWORD = ", row[1])
            print("POINTS = ", row[2])
            print("HIGH SCORE =", row[3], "\n")
        user.close()

    
    #adds points to a global variable points that belong to the active user
    def calculate_gamepoints(game_points):
        global points
        points += game_points


    #update the points of the active user in the table in the database
    # return the total points the user has gathered 
    def add_points_total():
        global points
        user = sqlite3.connect('user.db')
        cursor=user.cursor() #the cursor is essentially an iterator,which automatically invokes fetchall, or fetchone
        cursor.execute('SELECT POINTS from USER WHERE username="%s"'%activeuser)
        current_points = cursor.fetchone() #tuple so [0] = total gathering [1] can be the round of the game!
        #print(current_points)
        total_points = int(current_points[0]) + points
        user.execute('UPDATE USER set POINTS = "%s" where USERNAME = "%s"'%(total_points,activeuser))
        #user.execute('UPDATE USER set POINTS[1] = "%s" where USERNAME = "%s"'%(game_points,activeuser))
        user.commit()
        return total_points
        #Database.fetch_display()
    

    #if the points the user has collected in this game is more than that is stored in the database
    #these points are set as the users new highscore
    #returns the points of this game
    def calculate_highscore():
        global points
        print(points)
        user = sqlite3.connect('user.db')
        cursor=user.cursor() #the cursor is essentially an iterator,which automatically invokes fetchall, or fetchone
        cursor.execute('SELECT HIGHSCORE from USER WHERE username="%s"'%activeuser)
        current_highscore = cursor.fetchone()
        if current_highscore[0]== None:
            current_highscore = 0,0
        if points > current_highscore[0]:
            user.execute('UPDATE USER set HIGHSCORE = "%s" where USERNAME = "%s"'%(points,activeuser))
        user.commit()
        return points

    #builds a list (scores) of all the highscores of all the users in the database
    #builds another list (players) of all the users in the database
    #then sorts the scores in descensing order and apply the same sort to the players 
    #then take the top 10 in the list for the leaderboard
    #append the username and highscore in a table format
    def leaderboard():
        scores = []
        players = []
        user = sqlite3.connect('user.db')
        cursor = user.execute("SELECT * from USER")
        for row in cursor:
            score = row[3]
            players.append(row[0])
            if score== None:
                score = 0
            scores.append(score)
        scores, players = (list(t) for t in zip(*sorted(zip(scores, players),reverse=True)))
        user.close()
        #print(scores)
        y = 100
        SCREEN.fill(YELLOW)
        title = txt_surface("LEADER BOARD", "large",BLACK)
        line = txt_surface("stopwatch setting only","small",BLACK)
        SCREEN.blit(title,(180,50))
        SCREEN.blit(line,(1,1))
        for i in range(10):
            player = txt_surface((str(players[i])),"medium",BLACK)
            point = txt_surface((str(scores[i])),"medium",BLACK)
            SCREEN.blit(player, (200,y))
            SCREEN.blit(point, (400,y))
            y = y+30
        pygame.display.update()
        wait()


class InputBox:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            if self.active:
                self.color = COLOR_ACTIVE
            else:
                self.color = COLOR_INACTIVE

        #If user is typing
        if event.type == pygame.KEYDOWN:
            # and if active
            if self.active:
                #if key pressed is backspace
                if event.key == pygame.K_BACKSPACE:
                    #eliminate one charachter of the text
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    print(self.text)
                else:
                    #any other charcter just add it to the text in the box
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, SCREEN):
        # Blit the text.
        SCREEN.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(SCREEN, self.color, self.rect, 2)

class Button:
    # the button is a rectangle with specified dimentions with text in the middle to describe it
    def __init__(self,msg,x,y,w,h,action=None,extra1=None,extra2=None,extra3=None):
        # describing name
        self.msg =msg
        #---dimentions---
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        #---name of the subroutine to call if pressed---
        self.action = action
        self.txt_surface = FONT.render(self.msg, True, BLACK)

        #----any parameters of the subroutine if called----
        self.extra1 = extra1
        self.extra2= extra2
        self.extra3 = extra3

    def handle_event(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed() #u get (left, centre, right)
        
        #if the mouse is in the area of the rectangle that makes the button
        if self.x+self.w> mouse[0] > self.x and self.y +self.h >mouse[1]>self.y:
            #update it by changing its colour to the active colour
            pygame.draw.rect(SCREEN,COLOR_ACTIVE,(self.x,self.y,self.w,self.h))
            #if the user clicks on it 
            #call the subroutine that passed along with any applicable parameters
            if click[0]== 1 and self.action!= None and self.extra1 == None and self.extra2 == None and self.extra3==None:
                self.action()
            if click[0]== 1 and self.action!= None and self.extra1 != None and self.extra2 != None and self.extra3==None :
                self.action(self.extra1,self.extra2)
            if click[0]== 1 and self.action!= None and self.extra1 != None and self.extra2 == None and self.extra3==None:
                self.action(self.extra1)
            if click[0]== 1 and self.action!= None and self.extra1 == None and self.extra2 == None and self.extra3!=None:
                self.action(self.extra1,self.extra2, self.extra3)
                
    #else leave it as it is
        else:
            pygame.draw.rect(SCREEN,COLOR_INACTIVE,(self.x,self.y,self.w,self.h))

        SCREEN.blit(self.txt_surface,(self.x +5,self.y+10))

class Tray:
    def __init__(self, BOX):
        self.BOX = BOX

    # create a surface and make a board over it by drawing rectangles of a discrete size
    # these then resemble the english tray layout
    # return the surface with the board on it
    def create_board_surf(self):
            self.board_surf = pygame.Surface((self.BOX*7, self.BOX*7))
            for y in range(7):
                for x in range(7):
                    #no boxes required as not a part of the tray
                    if (x==0 or x ==1 or x==6 or x==5) and (y ==0 or y==1 or y==5 or y==6):
                        pass
                    else:
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)
            return self.board_surf


    def create_board(self):
        self.board = []
        #the board is made as a 2D array
        for y in range(7):
            self.board.append([])
            for x in range(7):
                self.board[y].append(None)
        # the marbles are stored in as a "." character in the applicable positions on the board
        for y in range(7):
            for x in range(7):
                if not(((x==0 or x ==1 or x==6 or x==5 ) and (y ==0 or y==1 or y==5 or y==6)) or (x==3 and y==3)):
                    self.board[y][x] = ('black', ".")#chr(9899)
        #the board is returned
        return self.board

    #draws a marble (".") on the board where it should be
    def draw_pieces(self,SCREEN, board, font):
        for y in range(7):
            for x in range(7):
                self.piece = self.board[y][x]
                #if a marble exists 
                if self.piece:
                    #append it to the screen in the right position
                    color, type = self.piece
                    self.s1 = font.render(type[0], True, pygame.Color(color))
                    self.pos = pygame.Rect(BOARDPOS[0] + x * BOX+1, BOARDPOS[1] + y * BOX -78 + 1, BOX, BOX)
                    SCREEN.blit(self.s1, self.s1.get_rect(center=self.pos.center))

    def draw_selector(self,SCREEN, piece, x, y):
        #if a marble exists
        if self.piece != None:
            #draw the square around the box in red
            self.rect = ((BOARDPOS[0] + x) * BOX, (BOARDPOS[1] + y) * BOX, BOX, BOX)
            pygame.draw.rect(SCREEN, (255, 0, 0, 50), self.rect, 2)

    def square_under_mouse(self, board):
        #get mouse position as vector so it can be used for calculations
        # take away the board position to get mouse position relative to the board
        self.mouse = pygame.Vector2(pygame.mouse.get_pos()) - BOARDPOS
        #divide the position by width of the box to get the row and column of the specific box
        x, y = [int(v // self.BOX) for v in self.mouse]
        try:
            #if its a box applicable for the english tray
            if not ((x==0 or x ==1 or x==6 or x==5) and (y ==0 or y==1 or y==5 or y==6)):
                if x >= 0 and y >= 0:
                    #return what's in that box (marble/None) and x,y
                    return (self.board[y][x], x, y)
            #else return None for all
        except IndexError: pass
        return None, None, None

    def draw_drag(self, SCREEN, board, selected_piece, font):
        #if selected peice is not None
        if selected_piece:
            #locate the box on the board where the peice is being moved
            self.piece, x, y = self.square_under_mouse(board)
            if x != None:
                #draw a green square around the new box position 
                self.rect = (BOARDPOS[0] + x * BOX, BOARDPOS[1] + y * BOX, BOX, BOX)
                pygame.draw.rect(SCREEN, (0, 255, 0, 50), self.rect, 2)
            #place the marble in that new box
            color, type = selected_piece[0]
            # since it is a "." it can just be rendered then blitted to the screen in the new position
            self.s1 = font.render(type[0], True, pygame.Color(color))
            self.pos = pygame.Vector2(pygame.mouse.get_pos())
            self.pos[1] = self.pos[1]-78
            SCREEN.blit(self.s1, self.s1.get_rect(center=self.pos))
            #return the position of the box in terms of x and y
            return (x, y)

    def count_marbles(board):
        marbles= 0
        for y in range(7):
            for x in range(7):
                if board[y][x] != None:
##                    try:
##                        if (board[y][x+1] and board[y][x-1] and board[y+1][x] and board[y-1][x]) == None:
                            marbles += 1
##                    except IndexError:
##                        pass
        return marbles

    def check_game_end(board):
        global ticks
        for y in range(7):
            for x in range(7):
                #if there is a marble
                if board[y][x] != None:
                    try:
                        #and there is a marble around it (a move is possible)
                        if (board[y][x+1] or board[y][x-1] or board[y+1][x] or board[y-1][x]) != None:
                            #cant end game so return false
                            return False
                    except IndexError:
                        pass
                    
        #comes out the loop means game has ended

        # count the remaining marbles
        marbles = Tray.count_marbles(board)
        #get time bonus of applicable
        try:
            timebonus = Tray.timebonus(ticks)
        except:
            pass
        SCREEN.fill(YELLOW)

        #------ end screen display - blit it all to the screen -------------------------
        message = txt_surface("GAME OVER ","large", BLACK)
        SCREEN.blit(message, (180,50))
        #print("game over")
        message = txt_surface("Marbles Remaning = "+str(marbles),"medium", BLACK)
        SCREEN.blit(message, (160,150))
        total_points = txt_surface("Total points collected = "+ str(Database.add_points_total()),"medium",BLACK)
        points = txt_surface("Game points collected = "+ str(Database.calculate_highscore()),"medium",BLACK)
        try:
            extra_points = txt_surface("Bonus from you time = " +str(timebonus), "medium", BLACK)
            SCREEN.blit(extra_points,(160,350))
        except:
            pass
        SCREEN.blit(points, (160,250))
        SCREEN.blit(total_points, (150,450))
        pygame.display.update()
        wait()
        # return true game ended
        return True


    def game_points(board):
        #calculate points depending on how many marbles are remaining
        marbles = Tray.count_marbles(board)
        if marbles >= 20:
            score = 25
        elif marbles >= 10 and marbles < 20:
            score = 30
        elif marbles >= 5 and marbles < 10:
            score = 35
        elif marbles <5 :
            score = 50
        Database.calculate_gamepoints(score)


    def timebonus(ticks):
        # apply the formula like discussed to convert the time into a score
        #and return it
        now = pygame.time.get_ticks()
        time =  (now - ticks)/(1000*60*3)
        bonus = int((1/time)*100) #my random formula
        Database.calculate_gamepoints(bonus)
        return bonus
    
    #checks of the moves are legal moves by checking the 2D array of the board and allows or denys moves accordingly
    def movement_of_marbles(self,board, new_x,old_x,new_y,old_y,piece):
        if ((new_x == old_x +2 and board[old_y][old_x+1]!=None) or (new_x==old_x -2 and board[old_y][old_x-1]!=None)) and old_y==new_y and board[new_y][new_x] == None:
            board[old_y][old_x] = None
            #print(board[old_y][old_x])
            board[new_y][new_x] = piece
            if new_x == old_x +2:
                board[old_y][old_x+1] = None
                Tray.game_points(board)
            else:
                board[old_y][old_x-1] = None
                Tray.game_points(board)
        elif ((new_y == old_y +2 and board[old_y+1][old_x]!=None) or (new_y==old_y-2 and board[old_y-1][old_x]!=None)) and old_x==new_x and board[new_y][new_x] == None:
            board[old_y][old_x] = None
            #print(board[old_y][old_x])
            board[new_y][new_x] = piece
            if new_y == old_y +2:
                board[old_y+1][old_x] = None
                Tray.game_points(board)
            else:
                board[old_y-1][old_x] = None
                Tray.game_points(board)
        else:
            print("Cant make that move!")

class Diamond(Tray):
    #subclass so inherits all methos from above Tray class
    def __init__(self,BOX):
        super().__init__(BOX)

     #creating surface is over-written   
    def create_board_surf(self):
            #different dimention
            self.board_surf = pygame.Surface((self.BOX*9, self.BOX*9))
            #dark = False
            for y in range(9):
                for x in range(9):
                    #different layout of the board for where boxes need to be
                    if (x==0 or x ==8)and (y == 4):
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)
                    elif (x ==1 or x==7) and  (3<= y <= 5) :
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)
                    elif (x == 2 or x==6) and (2<= y <= 6):
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)
                    elif (x == 3 or x==5) and (1<= y <= 7):
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)
                    elif x == 4:
                        self.rect = pygame.Rect(x*self.BOX, y*self.BOX, self.BOX, self.BOX)
                        pygame.draw.rect(self.board_surf, WHITE, self.rect)

            return self.board_surf

    def create_board(self):
        #still a 2D array but different number of elements
        self.board = []
        for y in range(9):
            self.board.append([])
            for x in range(9):
                self.board[y].append(None)

        for y in range(9):
            for x in range(9):
                if (x!=4)and (y == 4):
                    self.board[y][x] = ('black', ".")#chr(9899)
                if (x==4) and (y!= 4):
                    self.board[y][x] = ('black', ".")#chr(9899)
                if (x ==1 or x==7) and (3<= y <= 5) :
                    self.board[y][x] = ('black', ".")#chr(9899)
                if (x == 2 or x==6) and (2<= y <= 6):
                    self.board[y][x] = ('black', ".")#chr(9899)
                if (x == 3 or x==5) and (1<= y <= 7):
                    self.board[y][x] = ('black', ".")#chr(9899)
        return self.board
    
    def draw_pieces(self,SCREEN, board, font):
        #same function just changed the number of loops as the Diamond tray layout differs
        for y in range(9):
            for x in range(9):
                self.piece = self.board[y][x]
                if self.piece:
                    color, type = self.piece
                    self.s1 = font.render(type[0], True, pygame.Color(color))
                    self.pos = pygame.Rect(BOARDPOS[0] + x * BOX+1, BOARDPOS[1] + y * BOX -78 + 1, BOX, BOX)
                    SCREEN.blit(self.s1, self.s1.get_rect(center=self.pos.center))
                    

#displays the end screen by using 'blit' to append to screen
def screen_end(board):
    marbles = Tray.count_marbles(board)
    SCREEN.fill(YELLOW)
    message = txt_surface("GAME OVER ","large", BLACK)
    SCREEN.blit(message, (180,50))
    #print("game over")
    message = txt_surface("Marbles Remaning = "+str(marbles),"medium", BLACK)
    SCREEN.blit(message, (160,150))
    total_points = txt_surface("Total points collected = "+ str(Database.add_points_total()),"medium",BLACK)
    points = txt_surface("Game points collected = "+ str(Database.calculate_highscore()),"medium",BLACK)
    try:
        extra_points = txt_surface("Bonus from you time = " +str(timebonus), "medium", BLACK)
        SCREEN.blit(extra_points,(160,350))
    except:
        pass
    SCREEN.blit(points, (160,250))
    SCREEN.blit(total_points, (150,450))
    pygame.display.update()
    wait()

#Display on the screen the: players username, score, and marbles remaining
def screen_points(board):
    global points
    user = txt_surface("Player: "+activeuser,"medium", WHITE)
    SCREEN.blit(user, (50,50))
    score = txt_surface("Score: "+str(points),"medium", WHITE)
    SCREEN.blit(score, (50,80))
    marbles = txt_surface("Marbles Left: "+str(Tray.count_marbles(board)),"medium", WHITE) #call count_marble from Tray class
    SCREEN.blit(marbles, (50,110))
    #pygame.display.flip()

#return if the password passed  has more than 6 characters
#at least one number, one uppercase letter and one lowercase letter.
def validate(passwd):
    return_val=True
    if len(passwd) < 6:
        print('the length of password should be at least 6 char long')
    if not any(char.isdigit() for char in passwd):
        print('the password should have at least one numeral')
        return_val=False
    if not any(char.isupper() for char in passwd):
        print('the password should have at least one uppercase letter')
        return_val=False
    if not any(char.islower() for char in passwd):
        print('the password should have at least one lowercase letter')
        return_val=False
    if return_val:
        print('Ok')
    return return_val


#Returns surface of the desired text, size and colour using render
def txt_surface(text,size,colour):
    if size == "large":
        txt_surface =LFONT.render(text, True, colour)
    elif size =="medium":
        txt_surface =FONT.render(text, True, colour)

    elif size =="small":
        txt_surface =SFONT.render(text, True, colour)
    return txt_surface


def start():
    #first screen 
    SCREEN.fill(YELLOW)
    username=''
    password=''

    # 2 Input boxes for username and password
    box1 = InputBox(300, 100, 140, 32,username)
    box2 = InputBox(300, 200, 140, 32,password)
    boxes = [box1, box2]

    done = False
    while not done:
        #if user presses the red cross exist
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                done = True

            for box in boxes:
                box.handle_event(event)
                
        #update the boxes
        for box in boxes:
            box.update()

        SCREEN.fill(YELLOW)
        for box in boxes:
            box.draw(SCREEN)
        #SCREEN.fill(YELLOW)

        #---------append text to screen-------------
        surface = txt_surface("Username","medium", BLACK)
        SCREEN.blit(surface, (160,100))
        surface = txt_surface("Password","medium",BLACK)
        SCREEN.blit(surface, (160,200))
        username = str(box1.text)
        password = str(box2.text)
        #pygame.display.flip()
        surface = txt_surface("BRAINVITA","large",BLACK)
        SCREEN.blit(surface, (200,50))
        
        #--- make login and signup buttons --------
        button1 = Button("LOGIN!",100,400,100,50,login,username,password)
        button2 = Button("SIGNUP!",300,400,100,50,sign_up,username,password)
        buttons = [button1,button2]

        for button in buttons :
            button.handle_event()

        pygame.display.flip()
        CLOCK.tick(30)

def countdown(secs):
    #time passed since pygame initiated
    now=pygame.time.get_ticks()
    #time since game is being actively played 
    time = now - ticks - pausetime
    #time in seconds
    seconds=int(time/1000 % 60)
    out='{seconds:02d}'.format(seconds=seconds)
    #time left from countdowntime
    out = secs - int(out)
    #print(out)
    #output = txt_surface(out,"Medium",WHITE)
    output =FONT.render("Time left : "+str(out), True, WHITE)
    SCREEN.blit(output,(480,80))
    #pygame.display.flip()
    CLOCK.tick(60)
    #return time left
    return out

def stopwatch(ticks):
    global  pausetime
    #time since pygame is initiated
    now=pygame.time.get_ticks()
    #time since game is being actively played
    time = now - ticks - pausetime
    #seconds in the time
    seconds=int(time/1000 % 60)
    #minutes in the time
    minutes=int(time/60000)
    #time in min:sec format to output
    out='{minutes:02d}:{seconds:02d}'.format(minutes=minutes, seconds=seconds)
    out =FONT.render(out, True, WHITE)
    SCREEN.blit(out,(480,80))
    CLOCK.tick(60)

def menu():
    CLOCK.tick(30)
    clicked = False
    while not clicked:
        #if red cross is pressed exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                clicked = True
        SCREEN.fill(YELLOW)
        #text to screen
        surface = txt_surface("Hello!","large",BLACK)
        SCREEN.blit(surface,(200,20))
        #---- all buttons in menu -----
        instruction = Button("Instructions", 150,100,300,50, instructions)
        play = Button("Play!", 150, 150,300,50,play_game)
        tray = Button("Select Tray Type",150,200,300,50,choose_tray)
        marble = Button("Select Marble Colour",150,250,300,50)
        timeset = Button("Select your Timer Setting",150,300,300,50,choose_timer)
        buttons = [instruction,play,tray,marble,timeset]
        for button in buttons:
            button.handle_event()

        pygame.display.update()

def sign_up(username,password):
    CLOCK.tick(2)
    valid = validate(password)
    #if the password is valid
    if valid and username!='':
        #sign up in the database
        Database.sign_up(username,password)
    else:
        #password invalid 
        surface = txt_surface("Check Password has Uppercase, Lowercase, Numbers and is 6 characters long","small", BLACK)
        SCREEN.blit(surface, (20,300))
        pygame.display.update()
        time.sleep(4)
        #go back to start
        start()

def login(username,password):
    CLOCK.tick(2)
    #if username and password entered
    if username !='' and password !='':
        #try login with the database
        Database.login(username,password)
    else:
        #if not go back to start
        start()

def choose_tray():
    #attach a picture of the different trays
    trays = pygame.image.load('trays.png')
    chosen = False
    while not chosen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                clicked = True
        SCREEN.fill(WHITE)
        #---- buttons for the trays -----------
        SCREEN.blit(trays,(100,150))
        french = Button("^", 100,300,50,50)
        german = Button("^", 200,300,50,50)
        asymmetric = Button("^",300,300,50,50)
        english = Button("^",400,300,50,50)
        diamond = Button("^",500,300,50,50,play_game,None, None,"Diamond")
        buttons = [french,german,asymmetric,english,diamond]
        for button in buttons:
            button.handle_event()
        back()

        pygame.display.update()

def play_game(timer = None, time = None, tray = None ):
    #ticks is the time gap since pygame is initiated and the game has started
    global ticks
    ticks=pygame.time.get_ticks()
    #depending the tray chosen
    if tray == "Diamond":
        tray1 = Diamond(BOX)
        #print("Hey")
    else:
        tray1 = Tray(BOX)

    #get the board and board surface
    board = tray1.create_board()
    board_surf = tray1.create_board_surf()
    #-- set initial variables ------
    playing = True
    selected_piece = None
    drop_pos = None
    global points
    points = 0
    while playing:
        #--- if quit then exit---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                playing = False
            # if button down identify the peice selected
            if event.type == pygame.MOUSEBUTTONDOWN:
                if piece != None:
                    selected_piece = piece, x, y
            #if button up drop the selected peice in the new position if the move is legal
            if event.type == pygame.MOUSEBUTTONUP:
                if drop_pos:
                    piece, old_x, old_y = selected_piece
                    new_x, new_y = drop_pos
                    tray1.movement_of_marbles(board, new_x,old_x, new_y, old_y, piece)
                #initialise these again
                selected_piece = None
                drop_pos = None
                
            #if p is pressed  to pause
            if event.type ==  pygame.KEYDOWN and timer != "timer":
                if event.key== pygame.K_p:
                    #begining of pause
                    now = pygame.time.get_ticks())
                    global pause
                    pause = True
                    paused()
                    #end of pause
                    end= pygame.time.get_ticks()
                    global pausetime
                    #add up all the time spent in pause (later deducted from the stopwatch)
                    pausetime = pausetime + (end - now)
                    stopwatch(ticks)


        SCREEN.fill(BLACK)
        #back()
        SCREEN.blit(board_surf, BOARDPOS)
        screen_points(board)
        if timer == "timer":
            left = countdown(time)
            #if no time left
            if left == 0:
                #end game
                screen_end(board)
                playing = False
        else:
            stopwatch(ticks)
        #pygame.display.update()
        piece, x, y = tray1.square_under_mouse(board)
        # highlight the boxes red as the mouse move over them - applicable ones only
        if x != None:
            if not ((x==0 or x ==1 or x==6 or x==5) and (y ==0 or y==1 or y==5 or y==6)):

                rect = (BOARDPOS[0] + x * BOX, BOARDPOS[1] + y * BOX, BOX, BOX)
                pygame.draw.rect(SCREEN, (255, 0, 0, 50), rect, 2)
                
        #---- draw everything on to the screen--------
        tray1.draw_pieces(SCREEN, board, MblFONT)
        tray1.draw_selector(SCREEN, piece, x, y)
        back()
        drop_pos = tray1.draw_drag(SCREEN, board, selected_piece, MblFONT)
        screen_points(board)
        end = Tray.check_game_end(board)
        #if game has ended
        if end:
        # call leader board
            Database.leaderboard()
            #exit loop
            playing = False
        #update the sceen
        pygame.display.update()

def wait():
    #delay for 5 seconds
    time.sleep(5)

def unpause():
    global pause
    #set pause as false
    pause = False
    now = pygame.time.get_ticks()
    return now

def paused():
    global pause
    while pause:
        #now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        SCREEN.fill(YELLOW)
        surface = txt_surface("Paused","large", BLACK)
        SCREEN.blit(surface, (250,100))

        #light up the button
        resume = Button("Continue",150,300,100,50,unpause)
        start_menu = Button("Menu",350,300,100,50,menu)
        resume.handle_event()
        start_menu.handle_event()
        pygame.display.update()
        CLOCK.tick(15)


def back():
    #back takes you back to menu
    back = Button("Back", 550,0,65,50,menu)
    back.handle_event()
    pygame.display.update()


def instructions():
     while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        SCREEN.fill(WHITE)
        #get instruction image 
        instruction = pygame.image.load('instructions.png') #have it as png and import the image
        #append to screen
        SCREEN.blit(instruction,(15,0))
        #have the back button
        back()
        pygame.display.update()


def choose_timer():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        SCREEN.fill(YELLOW)
        #--- buttons of the different countdown timers ------------
        stopwatch = Button("Stopwatch", 1,100,160,50, play_game)
        timer1 = Button("Timer 45s", 1,200,160,50, play_game, "timer", 45)
        timer2 = Button("Timer 1min", 1,300,160,50, play_game, "timer", 60)
        timer3 = Button("Timer 1min 15s", 1,400,160,50, play_game, "timer", 75)
        buttons = [stopwatch,timer1,timer2,timer3]
        for button in buttons:
            button.handle_event()
        back()
        pygame.display.update()


#start the game
start()
