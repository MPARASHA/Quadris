# QUADRIS.PY
"""
/*Names: MANU PARASHAR, Harshit Venket Subramanian (FULL COLLABORATION)
ID #: 1547259, 1549859
CMPUT 274 Fa18

Project: Making Quadris (a game like Tetris)

Included Files:
    * quadris.py
    * uagame.py => provided by the instructors
    * Automation.mp3 from soundimage.org link => https://soundimage.org/looping-music/
    * gameover.mp3 from freesound.org link => https://freesound.org/people/Robinhood76/sounds/171200/
    * README
    
DESCRIPTION:
# There are 5 types of blocks and there are various orientations(rotational) of these 5 blocks.
# Only one block is falling on the screen at a time.
# Automation.mp3 is played on the loop untill the game stops running.
# The blocks can move left and right and rotate(anticlockwise) provided they don't overlap any existing block and don't cross over left, right and bottom edge of the
  window in doing so.
# The screen is black originally, A grid of 40 X 10 is printed of the left side of the window and the Score and the next block appear on the right side of the window.
# The blocks keep falling untill they hit either another block or the bottom edge.
# When a block is settled it can't go left or right or rotate.
# The score is just the time since the start of the game is seconds.
# when this happens the block is now fixed and the block previously shown as next starts falling from the top of the grid, and a new next block is printed on the right hand side.
# The block colour and block shape are random is nature, although the blocks always start falling from the center of the grid at the top of the window.
# The score string is white on black and so is the next string and the actual score.
# When a block settles on the screen and it's top left corner touches the top of the window, the game is considered to be over the score stops increasing.
# When the game gets over Automation.mp3 stops playing and the gameover.mp3 is played once and The game over string is displayed on the center of the grid, It's red on blue.
# The player aims to complete rows to avoid reaching the top.
# When a row is completed all the squares in that row are deleted.
## AFTER THIS POINT THE QUADRIS IS DIFFERENT FROM TETRIS ##
# If no square is deleted of a block then the block's "integrity" is intact which means it will fall down untill *any one* of the blocks's square either stacks upon another square or
  reaches the bottom the window
# If one or more squares of a block is deleted then the block's integrity is destroyed and all the remaining squares fall independently of each other untill all of them either stack
  or reach the bottom of the window
# The rows are deleted even if the block is still in motion as it still completes a line  


ADVANTAGES OVER TETRIS:
* This allows the player to delete multiple lines at once creating something like a chain reaction
* Players have a good chance of recovery even if they are almost at the top (something we personally like the most)
* Moreover, the chain reaction gives it a cool candy crush like feeling. :P


"""
# import statements
import pygame,time,math,random
from uagame import Window
import pygame
from pygame.locals import *


def main():
    # Main Algorithm
    # returns nothing
    
    # create the window
    title = 'QUADRIS'
    width = 420
    height = 640
    window = Window(title,width,height) # creating a Window object
    # initializing ingame music
    pygame.mixer.pre_init(44110,16,2,4096)
    pygame.mixer.music.load("Automation.mp3")
    pygame.mixer.music.set_volume(0.5) # 0.5
    pygame.mixer.music.play(-1)
    window.set_auto_update(False)
    # create the Game object
    game = Game(window)
    # play the game
    game.play()
    # close the window
    window.close()
	
# USER DEFINED CLASSES
class Game:
    # An object in this class represents a complete game.

    def __init__(self, window):
        # Initialize a Game.
        # - self is the Game to initialize
        # - window is the uagame window object
        
        # instance attributes
        self.window = window
        
        # Variable to check the event type QUIT
        self.close_clicked = False
        
        # Variable to check the game over condition/ condition to continue the game
        self.continue_game = True
        
        # The time by which the game sleep before refreshing
        self.pause_time = 0.01 # smaller is faster game
  
        # get the surface on which to draw using pygame
        surface = window.get_surface()
        
        # score/ time played in seconds
        self.score = 0
      
        # creating the grid
        self.create_board()
        
        # List containing all the objects of class block
        self.blocks = []
        
        # A variable to keep track of the number of blocks created
        self.created = 0
        
        # A list containing all the times in which the game progressed(blocks moved forward)
        # It is used to control the speed of blocks falling
        self.time_list12 = []
        
        # A list containing all the [x, y] coordinates of the window where a square is present
        self.present_list = []
        
        # A variable which controls when to play the gameoversound it is turned True when the sound is played
        self.gameoversound = False
        
        # A dictionary containing the block number and coordinates of the squares in the block as key value pairs
        self.present_dict = {}
        
        
        
    def create_board(self):
        # self is the Game object
        # Function to create the grid by drawing lines
        # returns nothing
        
        surface = self.window.get_surface()
        color = pygame.Color("white")
        height = self.window.get_height()//40
        width = self.window.get_width()//14
        
        # Drawing lines horizantally
        for i in range(0,41):
            pygame.draw.line(surface, color,[0,i*height],[width*10,i*height],1)
        # Drawing lines vertically
        for j in range(0,11):
            pygame.draw.line(surface, color,[j*width,0],[j*width,self.window.get_height()],1)        
            
   
        
    
    def play(self):
        # Play the game until the player presses the close box.
        # - self is the Game that should be continued or not.
        # returns nothing
        
        # Game-design while loop
        while not self.close_clicked: # while the user has not pressed the close button
            # play frame
            self.handle_event() # handling the conditions of a keypressed
            self.draw()
            if self.continue_game: # if game is not over
                self.update()
                self.decide_continue() # should game continue?
            time.sleep(self.pause_time) # set game velocity by pausing
            
    def handle_event(self):
        # Handle one user event by changing the game state
        # appropriately.
        # - self is the Game whose events will be handled.
        # returns nothing
        # Note: pygame.event.poll() gets only one event at a time (The first in the queue)
        
        event = pygame.event.poll()
        # If the user clicks close window
        if event.type == QUIT:
            self.close_clicked = True
        # If the user presses a key on the keyboard  
        if event.type == KEYDOWN:
            # Get a dictionary of keys pressed by the user as 'keys' with True or False as its pressed or not 'values'
            list_of_keys = pygame.key.get_pressed() 
            
            # If the left arrow key is pressed/ Moving the blocks left
            if list_of_keys[K_LEFT] == True:
                for b in self.blocks:
                    if(b.draw == True and b.settled == False and self.side_collision(b,'l')):
                        try:
                            self.present_list.remove([b.x,b.y])
                            self.present_list.remove([b.x2,b.y2])
                            self.present_list.remove([b.x3,b.y3])
                            self.present_list.remove([b.x4,b.y4])
                        except:
                            pass
                        b.move("l") # moving the block
                        self.present_list.append([b.x,b.y])
                        self.present_list.append([b.x2,b.y2])
                        self.present_list.append([b.x3,b.y3])
                        self.present_list.append([b.x4,b.y4])
                        lisa = [[b.x,b.y],[b.x2,b.y2],[b.x3,b.y3],[b.x4,b.y4]]
                        self.present_dict.update({b.block_num:lisa})    
                        
            # Else If the right arrow key is pressed/ Moving the blocks right         
            elif list_of_keys[K_RIGHT] == True:
                for b in self.blocks:
                    if(b.draw == True and b.settled == False and self.side_collision(b,'r')):
                        try:
                            self.present_list.remove([b.x,b.y])
                            self.present_list.remove([b.x2,b.y2])
                            self.present_list.remove([b.x3,b.y3])
                            self.present_list.remove([b.x4,b.y4])
                        except:
                            pass
                             
                        b.move("r") # moving the block
                        self.present_list.append([b.x,b.y])
                        self.present_list.append([b.x2,b.y2])
                        self.present_list.append([b.x3,b.y3])
                        self.present_list.append([b.x4,b.y4])
                        lisa = [[b.x,b.y],[b.x2,b.y2],[b.x3,b.y3],[b.x4,b.y4]]
                        self.present_dict.update({b.block_num:lisa}) 
            # Else if the space bar is pressed/ Rotating the block            
            elif list_of_keys[K_SPACE] == True:
                for b in self.blocks:
                    if(b.draw == True and b.settled == False and self.rotate_collision(b,'l') and self.rotate_collision(b,'r') and self.rotate_collision(b,'d') and self.rotate_collision2(b)):
                        try:
                            self.present_list.remove([b.x,b.y])
                            self.present_list.remove([b.x2,b.y2])
                            self.present_list.remove([b.x3,b.y3])
                            self.present_list.remove([b.x4,b.y4])
                        except:
                            pass                        
                        b.rotate() # Rotating anti-clockwise
                        self.present_list.append([b.x,b.y])
                        self.present_list.append([b.x2,b.y2])
                        self.present_list.append([b.x3,b.y3])
                        self.present_list.append([b.x4,b.y4])
                        lisa = [[b.x,b.y],[b.x2,b.y2],[b.x3,b.y3],[b.x4,b.y4]]
                        self.present_dict.update({b.block_num:lisa})                         
       
    def rotate_collision2(self,b):
        # A function to make sure that rotating a block doesn't overlap any of the squares of another block
        # self is the Game object
        # b is the block object
        # returns either True(in case no overlaps due to rotation) or False(in case any overlap happens)
        
        # creating a temporary block and rotating it to check if there are any overlaps
        c = block(b.x,b.y,self.window,time,self.created)
        c.step1 = b.step1
        c.step2 = b.step2
        c.step3 = b.step3
        c.make_block()
        c.rotate()
        # A list containing the coordinates of the squares of the rotated block c
        list1 = [[b.x,b.y],[b.x2,b.y2],[b.x3,b.y3],[b.x4,b.y4]] 
        
        # checking for overlap
        if(([c.x,c.y] in self.present_list and [c.x,c.y] not in list1 ) or ([c.x2,c.y2] in self.present_list and [c.x2,c.y2] not in list1) or ([c.x3,c.y3] in self.present_list and [c.x3,c.y3] not in list1) or ([c.x4,c.y4] in self.present_list and [c.x4,c.y4] not in list1)):
            return False
        else:
            return True
        
    def rotate_collision(self,b,k):
        # A function to make sure that rotating a block doesn't cross over the left/right/down edges of the grid
        # self is the game object
        # b is the block object
        # k is the edge to check for
        # returns either True(in case no square crosses the edge) or False(in case any square crosses the edge)      
        
        # A list containing the coordinates of the squares of the rotated block c
        c = block(b.x,b.y,self.window,time,self.created)
        c.step1 = b.step1
        c.step2 = b.step2
        c.step3 = b.step3
        c.make_block()
        c.rotate()
        
        # checking if any square crossed any edge
        if(k == 'l'):
            if(c.x > -self.window.get_width()//14 and c.x2 > -self.window.get_width()//14 and c.x3 > -self.window.get_width()//14 and c.x4 > -self.window.get_width()//14):
                return True
            else:
                return False
        if(k == 'd'):
            if(c.y < 40*self.window.get_height()//40 and c.y2 < 40*self.window.get_height()//40 and c.y3 < 40*self.window.get_height()//40 and c.y4 < 40*self.window.get_height()//40):
                return True
            else:
                return False        
        if(k == 'r'):
            if((c.x < 9*self.window.get_width()//14+2) and (c.x2 < 9*self.window.get_width()//14+2) and (c.x3 < 9*self.window.get_width()//14+2) and (c.x4 < 9*self.window.get_width()//14+2)):
                return True
            else:
                return False          
            

        
    def side_collision(self,b,k):
        # self is the object of Game class
        # b is the object of block class
        # k represents whether to check for left or right movement
        # return either true or false
        
        # checking for movement on left side
        if k == 'l':
            if(([b.x - self.window.get_width()//14,b.y]) in self.present_list and ([b.x - self.window.get_width()//14,b.y]) not in self.present_dict[b.block_num]):
                return False
            elif(([b.x2 - self.window.get_width()//14,b.y2]) in self.present_list and ([b.x2 - self.window.get_width()//14,b.y2]) not in self.present_dict[b.block_num]):               
                return False
            elif(([b.x3 - self.window.get_width()//14,b.y3]) in self.present_list and ([b.x3 - self.window.get_width()//14,b.y3]) not in self.present_dict[b.block_num] ):             
                return False  
            elif(([b.x4 - self.window.get_width()//14,b.y4]) in self.present_list and ([b.x4 - self.window.get_width()//14,b.y4]) not in self.present_dict[b.block_num] ):            
                return False            
            else:
                return True
        
        # checking for movement on right side
        if k == 'r':
            if(([b.x + self.window.get_width()//14,b.y]) in self.present_list and ([b.x + self.window.get_width()//14,b.y]) not in self.present_dict[b.block_num]):
                return False
            elif(([b.x2 + self.window.get_width()//14,b.y2]) in self.present_list and ([b.x2 + self.window.get_width()//14,b.y2]) not in self.present_dict[b.block_num]):
                return False
            elif(([b.x3 + self.window.get_width()//14,b.y3]) in self.present_list and ([b.x3 + self.window.get_width()//14,b.y3]) not in self.present_dict[b.block_num]):
                return False  
            elif(([b.x4 + self.window.get_width()//14,b.y4]) in self.present_list and ([b.x4 + self.window.get_width()//14,b.y4]) not in self.present_dict[b.block_num]):
                return False            
            else:
                return True      
            
    def draw(self):
        # Draw all game objects.
        # - self is the Game to draw
        # returns nothing
        
        # clear window
        self.window.clear()
        # create board
        self.create_board()
        # draw the "next:" string on the window
        self.draw_next()
        force_bool = False
        
        
        for b in self.blocks:
            # draw the blocks supposed to be on the grid
            if ((b != None)and(b.draw == True)):
                b.draw_block()
            # draw the blocks which is supposed to fall next   
            elif((b != None)and(b.draw == False)and(force_bool == False)):
                surface = self.window.get_surface()
                height = self.window.get_height()//40
                width = self.window.get_width()//14
                x = b.x + 152
                y = b.y + 510 + height
                x1 = b.x2 + 152
                y1 = b.y2 + 510 + height
                x2 = b.x3 + 152
                y2 = b.y3 + 510 + height 
                x3 = b.x4 + 152
                y3 = b.y4 + 510 +height
                if(b.step1 == 2 and b.step2 == 3 and b.step3 == 1):
                    x = b.x + 185
                    x1 = b.x2 + 185
                    x2 = b.x3 + 185
                    x3 = b.x4 + 185
                    
                
                rect = pygame.Rect(x, y, width, height)
                rect2 = pygame.Rect(x1, y1, width, height)
                rect3 = pygame.Rect(x2, y2, width, height)
                rect4 = pygame.Rect(x3, y3, width, height)
                
                pygame.draw.rect(surface,b.color,rect,0)
                pygame.draw.rect(surface,b.color,rect2,0)
                pygame.draw.rect(surface,block.border_color,rect,1)
                pygame.draw.rect(surface,block.border_color,rect2,1) 
                pygame.draw.rect(surface,b.color,rect3,0)
                pygame.draw.rect(surface,block.border_color,rect3,1)
                pygame.draw.rect(surface,b.color,rect4,0)
                pygame.draw.rect(surface,block.border_color,rect4,1)                
                
                force_bool = True
        # if the game is over draw game over on the screen       
        if(self.continue_game == False):
            self.draw_game_over()  
        
        # draw the score on the window
        self.draw_score()
       
        # update the window
        self.window.update() 
        
    def draw_next(self):
        # Draws the "next:" string on the screen
        # self is the Game object
        # returns nothing
        
        score_string = 'NEXT:'
        font_size = 30
        fg_color = 'white'
        self.window.set_font_size(font_size)
        self.window.set_font_color(fg_color)
        x = self.window.get_width()-self.window.get_string_width("SCORE") -10
        y = self.window.get_height()//2 +130
        self.window.draw_string(score_string,x,y)
          
        
    def draw_score(self):
        # draws the "score:" string on the screen and the actual score below it
        # self is the Game object
        # returns nothing
    
        score_string = 'SCORE:'
        string2 = str(self.score)
        font_size = 30
        fg_color = 'white'
        self.window.set_font_size(font_size)
        self.window.set_font_color(fg_color)
        x = self.window.get_width()-self.window.get_string_width("SCORE:") - 10
        y = self.window.get_height()//2
        self.window.draw_string(score_string,x,y)
        x = x = self.window.get_width()-self.window.get_string_width("SCORE")//1.2
        
        self.window.draw_string(string2,x,y+self.window.get_font_height())
        
    def draw_game_over(self):
        # draws the game over sign on the window when the game is over
        # self is the Game obeject
        # returns nothing
    
        game_over_string = 'Game Over'
        font_size = 69
        fg_color = 'red'
        bg_color = 'blue'
        self.window.set_font_size(font_size)
        self.window.set_font_color(fg_color)
        self.window.set_bg_color(bg_color)
        x = 0
        y = self.window.get_height()//2
        self.window.draw_string(game_over_string,x,y)
        self.window.set_bg_color('black')
        
        # playing the gameoversound just once
        if(self.gameoversound == False):
            pygame.mixer.music.stop()
            pygame.mixer.music.load("gameover.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(0)  
            self.gameoversound = True
            
        
    def update(self):
        # Update all game objects with state changes
        # that are not due to user events
        # - self is the Game to update
        # returns nothing
        time = pygame.time.get_ticks()//100 # time to be appended to the self.time_list12 to contron the speed (The smaller the value divided by the faster the blocks fall)    
        self.score = pygame.time.get_ticks()//1000
        velocity = 1 # the number of squares inn the grid the blocks move down at a time
        count_1 = 0
        for i in range(0,len(self.blocks)):
            if(((len(self.blocks) != 0)) and self.blocks[i].settled == False):
                break
            else:
                count_1+=1  
        # checking of all the squares in a row is occupied and if they are calling line_deletion
        if(count_1 == self.created-2):        
            for i in range(0,40):
                stack = 0
                for j in range(0,10):
                    if(([(j*self.window.get_width()//14), (i*self.window.get_height()//40)]) in self.present_list):
                        stack += 1
                if(stack == 10):
                    self.line_deletion(i)    
         
        # moving the blocks down           
        if(not(time in self.time_list12)):
            self.time_list12.append(time)
            for b in self.blocks:
                if ((len(self.blocks) != 0) and (b.draw == True)and (self.stack_collision(b)) and  (b.check_collision())):
                    try:
                        if(b.settled1 == False and b.b1 == True):
                            self.present_list.remove([b.x,b.y])
        
                    except:
                        pass                
                    
                    try:
                        if(b.settled2 == False and b.b2 == True):
                            self.present_list.remove([b.x2,b.y2])
        
                
                    except:
                        pass 
                        
                    try:
                        if(b.settled3 == False and b.b3 == True):
                            self.present_list.remove([b.x3,b.y3])
        
                
                    except:
                        pass  
                    try:
                        if(b.settled4 == False and b.b4 == True):
                            self.present_list.remove([b.x4,b.y4])
        
                
                    except:
                        pass                 

                    
                    lisa = []
                    if(b.b1 == True and b.settled1 == False):
                        b.y += velocity*(self.window.get_height()//40)
                        self.present_list.append([b.x,b.y])
                        lisa.append([b.x,b.y])
                    if(b.b2 == True and b.settled2 == False):
                        b.y2 += velocity*(self.window.get_height()//40)
                        self.present_list.append([b.x2,b.y2])
                        lisa.append([b.x2,b.y2])
                    if(b.b3 == True and b.settled3 == False):
                        b.y3 += velocity*(self.window.get_height()//40)
                        self.present_list.append([b.x3,b.y3])
                        lisa.append([b.x3,b.y3])
                    if(b.b4 == True and b.settled4 == False):
                        b.y4 += velocity*(self.window.get_height()//40)
                        self.present_list.append([b.x4,b.y4])
                        lisa.append([b.x4,b.y4])
                    self.present_dict.update({b.block_num:lisa})
        # creating the first two blocks        
        if(self.created == 0):
            x = (6*self.window.get_width()//14)
            y = -1*self.window.get_height()//40
            self.created += 1
            blok = block(x,y,self.window,time,self.created)
            self.created += 1
            blok2 = block(x,y,self.window,time,self.created)            
        
            self.blocks.append(blok) 
            self.blocks.append(blok2)
            
        # if all the blocks on the grid are settled creating a new block
        count = 0
        for i in range(0,len(self.blocks)):
            if(((len(self.blocks) != 0)) and self.blocks[i].settled == False):
                break
            else:
                count+=1
        if(count == self.created-1):
            x = (6*self.window.get_width()//14)
            y = -1*self.window.get_height()//40
            self.created += 1
            blok = block(x,y,self.window,time,self.created)
            self.blocks.append(blok)
         
        # if all the blocks on the screen are settled making the b.draw = True of the next block to come   
        for i in range(0,len(self.blocks)-2):
            if(((len(self.blocks) != 0)) and self.blocks[i].settled == True): 
                self.blocks[i+1].draw = True
                
        # making the b.draw = True for the first block        
        if((len(self.blocks) == 2)):
            self.blocks[0].draw = True
          
        
    def line_deletion(self,i):
        # removing the coordinates of the squares of blocks of the deleted line from present_list
        # making the b.b1/b.b2/b.3/b.b4 False for the squares that are deleted
        # self is the Game object
        # i is the index of the row to be deleted
        # returns nothing
        for j in range(0,10):
            self.present_list.remove([(j*self.window.get_width()//14), (i*self.window.get_height()//40)])
            for b in self.blocks:
                if(b.x == j*self.window.get_width()//14 and b.y == i*self.window.get_height()//40):
                    b.b1 = False
                if(b.x2 == j*self.window.get_width()//14 and b.y2 == i*self.window.get_height()//40):
                    b.b2 = False       
                if(b.x3 == j*self.window.get_width()//14 and b.y3 == i*self.window.get_height()//40):
                    b.b3 = False 
                if(b.x4 == j*self.window.get_width()//14 and b.y4 == i*self.window.get_height()//40):
                    b.b4 = False 
                
        
         
    def  stack_collision(self,b):
        # checking if the blocks are settled on top of another block
        # self is the Game object
        # b is the object of the block class
        # returns either True or False
        
        # coordinates of supposedly the squares below the squares of the block b
        x1 = b.x
        x2 = b.x2
        x3 = b.x3
        y1 = b.y + self.window.get_height()//40
        y2 = b.y2 + self.window.get_height()//40
        y3 = b.y3 + self.window.get_height()//40
        x4 = b.x4
        y4 = b.y4 + self.window.get_height()//40
        
        # Case 1 when no square in the block is deleted and the integrity is still intact
        if(b.b1 == True and b.b2 == True and b.b3 == True and b.b4 == True):
            if (([x1,y1] in self.present_list) and ([x1,y1] not in self.present_dict[b.block_num] and b.b1 == True)):   
                b.settled = True
                b.settled1 = True
                b.settled2 = True
                b.settled3 = True
                b.settled4 = True
                return False
            if(([x2,y2] in self.present_list) and ([x2,y2] not in self.present_dict[b.block_num] and b.b2 == True)):
                b.settled = True
                b.settled1 = True
                b.settled2 = True
                b.settled3 = True
                b.settled4 = True 
                return False
            if(([x3,y3] in self.present_list) and ([x3,y3] not in self.present_dict[b.block_num] and b.b3 == True)):
                b.settled = True
                b.settled1 = True
                b.settled2 = True
                b.settled3 = True
                b.settled4 = True 
                return False
            if(([x4,y4] in self.present_list) and ([x4,y4] not in self.present_dict[b.block_num] and b.b4 == True)):
                b.settled = True
                b.settled1 = True
                b.settled2 = True
                b.settled3 = True
                b.settled4 = True   
                return False
            else:
                b.settled = False
                b.settled1 = False
                b.settled2 = False
                b.settled3 = False
                b.settled4 = False
                return True
            
        # Case 2 when one or more squares in the block has been deleted and the integrity is not present
        else:
            b.settled1 = True
            b.settled2 = True
            b.settled3 = True
            b.settled4 = True 
            b.settled = True
            if (([x1,y1] not in self.present_list) and b.b1 == True and y1<=624):   
                b.settled1 = False  
                
            if(([x2,y2] not in self.present_list) and b.b2 == True and y2<=624):
                b.settled2 = False
                
            if(([x3,y3] not in self.present_list) and b.b3 == True and y3<=624):
                b.settled3 = False
                
            if(([x4,y4] not in self.present_list) and b.b4 == True and y4<=624):
                b.settled4 = False
                
            return True
        

    def decide_continue(self):
        # Determine if the game should continue
        # - self is the Game to update
        # returns nothing
        
        # If any block that has settled has any square with a y coordinate 0 then game is over
        for b in self.blocks:
            if((b.settled ==  True) and (b.y == 0 or b.y2 == 0 or b.y3 == 0 or b.y4 == 0)):
                self.continue_game = False
                    
    
    
class block:
    # class attribute border color for blocks
    border_color = pygame.Color('black')
   
    # An object in this class represents a complete game.
    def __init__(self,x,y,window,block_time,block_num):
        # initialze the block made
        # - self is the Game to initialize
        # - window is the uagame window object  
        # block_time is the time at which it was created
        # block_num is the number of blocks that have been made before this one + 1
        # x and y are the initial coordinates of square1
        # returns nothing
        
        # instance attributes
        self.window = window
        self.x = x
        self.y = y
        self.block_time = block_time
        
        # variable to check if the block is supposed to be drawn on the grid or appear as next
        self.draw = False
        
        self.settled = False
        
        # to see if the squares in the block are settled or not
        self.settled1 = False
        self.settled2 = False
        self.settled3 = False
        self.settled4 = False
        
        self.block_num = block_num
        
        # to check if the block is deleted or not
        self.b1 = True
        self.b2 = True
        self.b3 = True
        self.b4 = True
        
        # list of colors to choose randomly for a block
        color_list = ["red","yellow","blue","green"]
        num = random.randint(0,3)
        self.color = pygame.Color(color_list[num]) 
        
        # choosing randomly which type of block is this gonna be
        step1 = random.randint(1,2)   
        step2 = random.randint(1,3)
        step3 = random.randint(1,4)
        self.step1 = step1
        self.step2 = step2
        self.step3 = step3
        
        # make that type of block
        self.make_block()
        

       
  
    def make_block(self):
        # makes different types of blocks depending on the randomly chosen values of step1, step2 and step3
        # self is the object of block class
        # returns nothing
        
        if (self.step1 == 1):
            self.x2 = self.x + (1)*self.window.get_width()//14
            self.y2 = self.y
        elif(self.step1 == 2):
            self.y2 = self.y - (1)*self.window.get_height()//40
            self.x2 = self.x  
        
        if(self.step2 == 1):
            if(self.step1 == 1):
                self.x3 = self.x - (1)*self.window.get_width()//14
                self.y3 = self.y
                
            if(self.step1 == 2):
                self.y3 = self.y + (1)*self.window.get_height()//40
                self.x3 = self.x
                                          
            
        if(self.step2 == 2):
            if(self.step1 == 1):
                self.x3 = self.x
                self.y3 = self.y - (1)*self.window.get_height()//40
                
            if(self.step1 == 2):
                self.x3 = self.x + (1)*self.window.get_width()//14
                self.y3 = self.y2
                                 
                
            
        if(self.step2 == 3):
            if(self.step1 == 1):
                self.x3 = self.x2
                self.y3 = self.y + (1)*self.window.get_height()//40
                
            if(self.step1 == 2):
                self.x3 = self.x - (1)*self.window.get_width()//14
                self.y3 = self.y
                
             
        if(self.step3 == 1):
            if(self.step2 == 1):
                if(self.step1==1):
                    self.x4 = self.x2 + (1)*self.window.get_width()//14
                    self.y4 = self.y

                if(self.step1 == 2):
                    self.x4 = self.x
                    self.y4 = self.y3 + (1)*self.window.get_height()//40
  
            if(self.step2 == 2):
                if(self.step1==1):
                    self.x4 = self.x
                    self.y4 = self.y3 - (1)*self.window.get_height()//40

                if(self.step1 == 2):
                    self.y4 = self.y3
                    self.x4 = self.x3 + (1)*self.window.get_width()//14

            if(self.step2 == 3):
                if(self.step1==1):
                    self.x4 = self.x-(1)*self.window.get_width()//14
                    self.y4 = self.y

                if(self.step1 == 2):
                    self.x4 = self.x3 - (1)*self.window.get_width()//14
                    self.y4 = self.y
                 
                        
        if(self.step3 == 2):
            if(self.step2 == 1):
                if(self.step1 == 1):
                    self.x4 = self.x3
                    self.y4 = self.y - (1)*self.window.get_height()//40

                if(self.step1 == 2):
                    self.y4 = self.y2
                    self.x4 = self.x - (1)*self.window.get_width()//14     
                    
            if(self.step2 == 2):
                if(self.step1 == 1):
                    self.x4 = self.x2
                    self.y4 = self.y + (1)*self.window.get_height()//40
 
                if(self.step1 == 2):
                    self.x4 = self.x
                    self.y4 = self.y + (1)*self.window.get_height()//40
                
            if(self.step2 == 3):
                if(self.step1 == 1):
                    self.x4 = self.x2 + (1)*self.window.get_width()//14
                    self.y4 = self.y + (1)*self.window.get_height()//40
                    
                if(self.step1 == 2):
                    self.x4 = self.x - (1)*self.window.get_width()//14
                    self.y4 = self.y3 + (1)*self.window.get_height()//40
                                
    
        if(self.step3 == 3):
            if(self.step2 == 1):
                if(self.step1 == 1):  
                    self.x4 = self.x
                    self.y4 = self.y + (1)*self.window.get_height()//40
                    
                if(self.step1 == 2):
                    self.x4 = self.x - (1)*self.window.get_width()//14
                    self.y4 = self.y3

            if(self.step2 == 2):
                if(self.step1 == 1):       
                    self.x4 = self.x - (1)*self.window.get_width()//14
                    self.y4 = self.y
 
                if(self.step1 == 2):
                    self.x4 = self.x
                    self.y4 = self.y2 - (1)*self.window.get_height()//40
                    
            if(self.step2 == 3):
                if(self.step1 == 1): 
                    self.x4 = self.x2
                    self.y4 = self.y2 - (1)*self.window.get_height()//40
                                 
                if(self.step1 == 2):
                    self.x4 = self.x + (1)*self.window.get_width()//14
                    self.y4 = self.y2

        if(self.step3 == 4):
            self.x2 = self.x + (1)*self.window.get_width()//14
            self.x3 = self.x
            self.y2 = self.y
            self.y3 = self.y + (1)*self.window.get_height()//40
            self.y4 = self.y3
            self.x4 = self.x2
          
            
        
    def draw_block(self):
        # draws the block
        # self is the object of block class
        # returns nothing
        
        # drawing the squares in the block and their border squares
        surface = self.window.get_surface()
        height = self.window.get_height()//40
        width = self.window.get_width()//14    
        rect = pygame.Rect(self.x, self.y, width, height)
        rect2 = pygame.Rect(self.x2, self.y2, width, height)
        rect3 = pygame.Rect(self.x3, self.y3, width, height)
        rect4 = pygame.Rect(self.x4, self.y4, width, height)
        if(self.b1 == True):
            pygame.draw.rect(surface,self.color,rect,0)
            pygame.draw.rect(surface,block.border_color,rect,1)
        if(self.b2 == True):
            pygame.draw.rect(surface,self.color,rect2,0)
            pygame.draw.rect(surface,block.border_color,rect2,1)
        if(self.b3 == True):
            pygame.draw.rect(surface,self.color,rect3,0)
            pygame.draw.rect(surface,block.border_color,rect3,1) 
        if(self.b4 == True):
            pygame.draw.rect(surface,self.color,rect4,0)
            pygame.draw.rect(surface,block.border_color,rect4,1)              
    
    def check_collision(self):
        # checks if the block has touched the lower edge of the window
        # self is the object of the block class
        # returns either True or False
        
        # Case 1 when integrity is intact i.e no square of the block has been deleted
        if(self.b1 == True and self.b2 == True and self.b3 == True and self.b4 == True):
            if((self.y == 39*self.window.get_height()//40) or (self.y2 == 39*self.window.get_height()//40) or (self.y3 == 39*self.window.get_height()//40) or (self.y4 == 39*self.window.get_height()//40)):
                self.settled = True
                return False
            else: 
                return True
        
        # Case 2 when there is no integrity i.e one or more squares of the block has been deleted
        else:
            if(self.y == 39*self.window.get_height()//40 and self.b1 ==True):
                self.settled1 = True
            if(self.y2 == 39*self.window.get_height()//40 and self.b2 == True):
                self.settled2 = True
            if(self.y3 == 39*self.window.get_height()//40 and self.b3 == True):
                self.settled3 = True  
            if(self.y4 == 39*self.window.get_height()//40 and self.b4 == True):
                self.settled4 = True 
            return True
            
    def move(self,k):
        # moves the blocks either left or right
        # self is the object of block class
        # k represents the direction to move (either left or right)
        # returns nothing
        
        if(k == 'l'):
            if(self.x > 0 and self.x2 > 0 and self.x3 > 0 and self.x4 > 0):
                self.x -= self.window.get_width()//14
                self.x2 -= self.window.get_width()//14
                self.x3 -= self.window.get_width()//14
                self.x4 -= self.window.get_width()//14
        if(k == 'r'):
            if((self.x < 8*self.window.get_width()//14+2) and (self.x2 < 8*self.window.get_width()//14+2) and (self.x3 < 8*self.window.get_width()//14+2) and (self.x4 < 8*self.window.get_width()//14+2)):
                self.x += self.window.get_width()//14
                self.x2 += self.window.get_width()//14
                self.x3 += self.window.get_width()//14
                self.x4 += self.window.get_width()//14                
            
        
    def  rotate(self):
        # rotates the block in the anti-clockwise direction
        # self is the object of block class
        # returns nothing
        
        if(self.step3 == 1):
            if(self.step2 == 1):
                if(self.step1==1):
                    self.step3 = 1
                    self.step2 = 1
                    self.step1 = 2
                    self.make_block()
                    return
                if(self.step1 == 2):
                    self.step3 = 1
                    self.step2 = 1
                    self.step1 = 1
                    self.make_block()
                    return
            if(self.step2 == 2):
                if(self.step1==1):
                    self.step3 = 1
                    self.step2 = 2
                    self.step1 = 2
                    self.make_block() 
                    return
                if(self.step1 == 2):
                    self.step3 = 2
                    self.step2 = 1
                    self.step1 = 2
                    self.make_block()
                    return
            if(self.step2 == 3):
                if(self.step1==1):
                    self.step3 = 3
                    self.step2 = 1
                    self.step1 = 2
                    self.make_block()
                    return
                if(self.step1 == 2):
                    self.step3 = 1
                    self.step2 = 2
                    self.step1 = 1
                    self.make_block() 
                    return
    
        if(self.step3 == 2):
            if(self.step2 == 1):
                if(self.step1 == 1):
                    self.step3 = 2
                    self.step2 = 2
                    self.step1 = 2
                    self.make_block()
                    return
                if(self.step1 == 2):
                    self.step3 = 1
                    self.step2 = 3
                    self.step1 = 2
                    self.make_block()
                    return
    
            if(self.step2 == 2):
                if(self.step1 == 1):
                    self.step3 = 3
                    self.step2 = 3
                    self.step1 = 2
                    self.make_block()
                    return
                if(self.step1 == 2):
                    self.step3 = 1
                    self.step2 = 3
                    self.step1 = 1
                    self.make_block()
                    return
    
            if(self.step2 == 3):
                if(self.step1 == 1):
                    self.step3 = 2
                    self.step2 = 3
                    self.step1 = 2
                    self.make_block()
                    return
                if(self.step1 == 2):
                    self.step3 = 2
                    self.step2 = 3
                    self.step1 = 1
                    self.make_block()
                    return
    
        if(self.step3 == 3):
            if(self.step2 == 1):
                if(self.step1 == 1):  
                    self.step3 = 3
                    self.step2 = 3
                    self.step1 = 1
                    self.make_block() 
                    return
                if(self.step1 == 2):
                    self.step3 = 2
                    self.step2 = 1
                    self.step1 = 1
                    self.make_block()  
                    return
    
            if(self.step2 == 2):
                if(self.step1 == 1):       
                    self.step3 = 3
                    self.step2 = 2
                    self.step1 = 2
                    self.make_block()  
                    return
                if(self.step1 == 2):
                    self.step3 = 3
                    self.step2 = 1
                    self.step1 = 1
                    self.make_block()
                    return
    
            if(self.step2 == 3):
                if(self.step1 == 1): 
                    self.step3 = 3
                    self.step2 = 2
                    self.step1 = 1
                    self.make_block()    
                    return
                if(self.step1 == 2):
                    self.step3 = 2
                    self.step2 = 2
                    self.step1 = 1
                    self.make_block()  
                    return
 
# main function call   
main()

# The End

