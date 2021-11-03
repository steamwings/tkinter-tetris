from graphics import *
import random
from copy import copy
from os import _exit
import threading
from asyncio import Queue


def synchronized(method):
    def new_method(self, *arg, **kws):
        with self.lock:
            return method(self, *arg, **kws)
    return new_method


############################################################
# BLOCK CLASS
############################################################

class Block(Rectangle):
    ''' Block class:
        Implement a block for a tetris piece
        Attributes: x - type: int
                    y - type: int
        specify the position on the tetris board
        in terms of the square grid
    '''

    BLOCK_SIZE = 25 
    SIDE_LENGTH = 2

    lock = threading.Lock()

    def __init__(self, pos, color):
        
        self.x = int(pos.x)
        self.y = int(pos.y) # We take the top to be y=0 for calculation purposes
        self.color = color
        
        pos.y = Tetris.BOARD_HEIGHT- 2*pos.y
        pos.x *= 2 
        p2 = Point(pos.x+ self.SIDE_LENGTH, pos.y - self.SIDE_LENGTH ) 
        Rectangle.__init__(self,pos,p2) # However in the Rectangle object, the lower left is (0,0)
        self.setFill(color)
   
    @synchronized 
    def move(self, dx=0, dy=1):
        ''' Parameters: dx - type: int
                        dy - type: int
                        
            moves the block dx blocks in the x direction
            and dy blocks in the y direction
        '''
         
        self.x += int(dx)
        self.y += int(dy)
        #print("Moving block to x: {}, y: {}".format(self.x, self.y))
        Rectangle.move(self, dx*self.SIDE_LENGTH ,-dy*self.SIDE_LENGTH)

############################################################
# SHAPE CLASS
############################################################

class Shape():
    ''' Shape class:
        Base class for all the tetris shapes
        Attributes: blocks - type: list - the list of blocks making up the shape
                    rotation_dir - type: int - the current rotation direction of the shape
                    shift_rotation_dir - type: Boolean - whether or not the shape rotates
    '''

    def __init__(self, coords=None, color='blue'):
        self.blocks = []
        ### A boolean to indicate if a shape shifts rotation direction or not.
        ### Defaults to false since only 3 shapes shift rotation directions (I, S and Z)
        
        if(coords!=None): 
            for pos in coords:
                self.blocks.append(Block(pos, color))


    def get_blocks(self):
        '''returns the list of blocks
        '''
        return self.blocks

    def draw(self, win):
        ''' Parameter: win - type: CanvasFrame

            Draws the shape 
        ''' 
        for block in self.blocks:
           # print("Drawing block at x: {}, y: {}".format(block.x, block.y))
            block.draw(win)
    def deepcopy(self):
        ''' Returns a deep copy of self with new blocks and such '''
        new = Shape()
        for block in self.get_blocks():
            
            newBlock = Block(Point(block.x,block.y),block.color)
            new.blocks.append(newBlock)
            if(block==self.center_block):
                new.center_block=newBlock
        return new
        
 
    def test_move(self, point):
        '''Returns a shallow copy of self, moved
        '''
        tmp = self.deepcopy()
        tmp.move(point) 
        return tmp

    def move(self, point):

        ''' Parameters: point 
            point.x - dx - type: int
            point.y - dy - type: int

            moves the shape dx squares in the x direction
            and dy squares in the y direction
        '''
        #print("move x: {}, y: {}".format(point.x, point.y))
        for block in self.blocks:
            block.move(point.x, point.y)


    def test_rotate(self, direction):
        ''' Parameters: x, y coordinates of rotation block
            Return value: Shape object, a deep copy of self
            
            This function returns a "test rotation" of the shape, a
            deep copy that was rotated and did not affect the original,
            but that can be tested to see if it will fit on the board.
        '''
        temp_shape = self.deepcopy()
        temp_shape.rotate(direction)
        return temp_shape   

    def rotate(self, direction='Right'):
        ''' Parameters: board - type: Board object

            rotates the shape:
            1. Get the rotation direction using the get_rotation_dir method
            2. Compute the position of each block after rotation
            3. Move the block to the new position
            
        '''    
        sign = 1  if direction=='Right' else -1 # If not Right, then Left
        
        c_x = self.center_block.x
        c_y = self.center_block.y

        for block in self.blocks:
            x_diff, y_diff = c_x-block.x, c_y-block.y  # The block's x,y differences from center_block 

            # To perform the rotation, we (abstractly) transform each block to a grid where
            # the center block is the origin. We then swap x, y differences from origin.
            # The resultant x diff (the original y diff) is negated for right rotation.
            # The results are then transformed back to the original grid.

            block.move( (sign*(y_diff) + c_x - block.x) , (-sign*(x_diff) + c_y - block.y))
        
        

############################################################
# ALL SHAPE CLASSES
############################################################

 
class I_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 2, center.y),
                  Point(center.x - 1, center.y),
                  Point(center.x    , center.y),
                  Point(center.x + 1, center.y)]
        Shape.__init__(self, coords, 'blue')
        self.center_block = self.blocks[2]

class J_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x    , center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x + 1, center.y + 1)]
        Shape.__init__(self, coords, 'orange')        
        self.center_block = self.blocks[1]

class L_shape(Shape):
    '''
    A four-piece L 
    '''
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x    , center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'cyan')        
        self.center_block = self.blocks[0]


class O_shape(Shape):
    '''
    A four-piece square
    '''
    def __init__(self, center):
        coords = [Point(center.x    , center.y),
                  Point(center.x - 1, center.y),
                  Point(center.x   , center.y + 1),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'red')
        self.center_block = self.blocks[0]

    def rotate(self, direction):
        # Override Shape's rotate method since O_Shape does not rotate
        return 

class S_shape(Shape):
 
   def __init__(self, center):
        coords = [Point(center.x    , center.y),
                  Point(center.x    , center.y + 1),
                  Point(center.x + 1, center.y),
                  Point(center.x - 1, center.y + 1)]
        Shape.__init__(self, coords, 'green')
        self.center_block = self.blocks[0]


class T_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x    , center.y),
                  Point(center.x + 1, center.y),
                  Point(center.x    , center.y + 1)]
        Shape.__init__(self, coords, 'yellow')
        self.center_block = self.blocks[1]


class Z_shape(Shape):
    def __init__(self, center):
        coords = [Point(center.x - 1, center.y),
                  Point(center.x    , center.y), 
                  Point(center.x    , center.y + 1),
                  Point(center.x + 1, center.y + 1)]
        Shape.__init__(self, coords, 'magenta')
        self.center_block = self.blocks[1]



############################################################
# BOARD CLASS
############################################################

class Board(GraphWin):
    ''' Board class: it represents the Tetris board
        GraphWin is a sub-class of tk.Canvas, so Board is also a Canvas.

        Attributes: width - type:int - width of the board in squares
                    height - type:int - height of the board in squares
                    canvas - type:CanvasFrame - where the pieces will be drawn
                    grid - type:Dictionary - keeps track of the current state of
                    the board; stores the blocks for a given position
    '''

    lock = threading.Lock()
 
    def __init__(self, title, width=200, height=200):
        super().__init__(title, width, height)
        # create a canvas to draw the tetris shapes on
        super().setBackground('light gray')
        #super().setCoords(0,0,width/Block.BLOCK_SIZE,height/Block.BLOCK_SIZE)
        super().setCoords(0,0,Tetris.BOARD_WIDTH,Tetris.BOARD_HEIGHT)
        # The grid is a two dimensional list which holds a Block at every location a Block can be.
        self.blank_block = Block(Point(0,0), 'blue')
        self.grid = [[self.blank_block for y in range(Tetris.BB_HEIGHT)] for x in range(Tetris.BB_WIDTH)]
        self.game_over = False
        self.cant_move = False

        self.text_score = Text(Point(2,Tetris.BOARD_HEIGHT-1), "Score: 0")
        self.text_score.draw(self)

    def add_score(self, val):
        new_score = val + int(self.text_score.getText()[7:])
        self.text_score.setText("Score: " + str(new_score))


    @synchronized    
    def move_on_board(self,point=Point(0,1)):
        ''' Parameters: x - type:int
                        y - type:int
            Return value: type: bool

            if there is already a block at that postion, can't move there
            return False

            otherwise return True
        '''
        if(point==None): return
        
        moved_shape = self.active_shape.test_move(point)
        
        for block in moved_shape.get_blocks():
            # Check if the translated block is valid, and either open or a part of the original shape
            if not(self.valid_block(block)):
                if(block.y>=Tetris.BB_HEIGHT): self.cant_move = True
                return False    
            if not(self.open_block(block)) and not(self.grid[block.x][block.y] in self.active_shape.get_blocks()):
                self.cant_move = True
                return False
        
        self.remove_shape(self.active_shape)
        #self.active_shape.move(point)
        self._add_shape(moved_shape)
        
        return True
    @synchronized
    def rotate(self, direction):
        '''Parameters: direction string - 'Left' for CCW  or 'Right' for CW
           Determines if the current shape can move in the given direction
        '''
        if self.cant_move == True: return False
        rotated_shape = self.active_shape.test_rotate(direction)

        for block in rotated_shape.get_blocks():
            if(
                not self.valid_block(block) or
                not(self.open_block(block) or 
                   self.grid[block.x][block.y] in self.active_shape.get_blocks())
              ):
                return False
        self.remove_shape(self.active_shape) # Removes from grid
        #self.active_shape.rotate(direction) #Transforms shape's internals
        self._add_shape(rotated_shape) # Adds back transformed shape to the grid
        return True      

    def valid_block(self, block):
        #print("Testing valid: x: {}, y: {} ".format(block.x, block.y)) 
        if(block.x<0 or block.y<0 or block.x>=Tetris.BB_WIDTH or block.y>=Tetris.BB_HEIGHT):
            return False
        return True

    def open_block(self, block):
       
       #print("Testing open:  x: {}, y: {} ".format(block.x, block.y)) 
       if self.grid[block.x][block.y] != self.blank_block:
           return False
       return True

    def add_shape(self, shape):
        ''' Parameter: shape - type:Shape
            
            add a shape to the board grid
        '''
          
        self.clean_rows()

        for block in shape.get_blocks():
           if not(self.valid_block(block)): 
               raise RuntimeError("The block with coordinates x: {}, y: {} was out of bounds.".format(block.x, block.y)) 
           if not self.open_block(block):
               self.game_over = True 
               return False              # A shape could not be added so the game is over
  
           self.grid[block.x][block.y] = block
   
        self.active_shape = shape
        shape.draw(self)
        return True       

    def _add_shape(self, shape):
        '''Does not check for validity'''
        for block in shape.get_blocks():
            self.grid[block.x][block.y] = block
            block.draw(self)
        self.active_shape = shape
        

    def remove_shape(self, shape):
        ''' Removes the shape from the board's grid
        '''
        for block in self.active_shape.get_blocks():
            self.grid[block.x][block.y] = self.blank_block
            block.undraw()

    def clean_rows(self):
        ''' removes all the complete rows and shifts down after deletions
        '''
        delete_ct = 0
        row = Tetris.BB_HEIGHT-1 # Start cleaning from the bottom
        while row>self.find_empty_row():
            if self.row_is_complete(row): 
                self.delete_row(row)
                delete_ct += 1
            else:  row -= 1
        
        if delete_ct>0: self.add_score(10*(delete_ct**3))

    def find_empty_row(self, num=1):
        
        if(num<=0): raise RuntimeError("Cannot find '{}'th empty row!".format(num))
        for row in range(Tetris.BB_HEIGHT-1, -1, -1):
            if self.row_is_empty(row):
                if(num==1): return row
                else: num-=1
        return -1 # No empty rows!

    def delete_row(self, y):
        ''' Parameters: y - type:int

            remove all the blocks in row y
        '''
         
        for i in range(Tetris.BB_WIDTH):
            self.grid[i][y].undraw()
            self.grid[i][y] = self.blank_block
        
        self.move_down_rows(y-1)
 
    def row_is_empty(self, y):
        '''Returns True if the row is empty'''
        for col in range(Tetris.BB_WIDTH):
            block = self.grid[col][y] 
            if block != self.blank_block: 
                return False
        return True 

    def row_is_complete(self, y):        
        ''' Parameter: y - the row index - type: int
            Return value: type: bool
        '''
       
        for i in range(Tetris.BB_WIDTH):
        #   print("x:",i,"y:",y)
            if(self.grid[i][y]==self.blank_block):     
                return False

        return True

    def move_down_rows(self, y_start):
        ''' Parameters: y_start - type:int                        
            Move down rows from y_start to the last non-empty row
        '''
        top = self.find_empty_row(2)
        if y_start<=top: return # No rows to move

        for row in range(y_start, top, -1):
            self.move_down_row(row)
   
    def move_down_row(self, y):
        '''Just moves down a given row''' 
        if y>=Tetris.BB_HEIGHT-1: raise RuntimeError("Cannot move down the bottom row!")
        for col in range(Tetris.BB_WIDTH):
            block = self.grid[col][y]
            self.grid[col][y] = self.blank_block
            block.move(0,1) #down
            self.grid[col][y+1] = block

    def show_game_over(self):
        ''' Call when the game has ended
        '''
        self.board.game_over = True
        
        #Display GAME OVER
        text = Text(Point(Tetris.BOARD_WIDTH/2,Tetris.BOARD_HEIGHT/2), "Game over")
        text.setFill('black')
        text.setSize(36)
        text.draw(self.board)


    
             

############################################################
# TETRIS CLASS
############################################################

class Tetris():
    ''' Tetris class: Controls the game play
        Attributes:
            SHAPES - type: list (list of Shape classes)
            DIRECTION - type: dictionary - converts string direction to (dx, dy)
            BOARD_WIDTH - type:int - the width of the board
            BOARD_HEIGHT - type:int - the height of the board
            board - type:Board - the tetris board
            delay - type:int - the speed in milliseconds for moving the shapes
            current_shape - type: Shape - the current moving shape on the board
    '''
   
 
    SHAPES = [I_shape, J_shape, L_shape, O_shape, S_shape, T_shape, Z_shape]
    DIRECTION = {'Left': Point(-1, 0), 'Right': Point(1, 0), 'Down': Point(0,1)}
    # The true coordinates
    BOARD_WIDTH = 20 
    BOARD_HEIGHT = 40
    # Used for Block calculations
    BB_WIDTH =  BOARD_WIDTH//Block.SIDE_LENGTH 
    BB_HEIGHT = BOARD_HEIGHT//Block.SIDE_LENGTH 
    
    def __init__(self, title, delay=800):
        self.queue = Queue(3000)
        self.board = Board(title, Block.BLOCK_SIZE*self.BOARD_WIDTH, Block.BLOCK_SIZE*self.BOARD_HEIGHT)
        self.delay = delay #ms
        # set the current shape to a random new shape
        if not self.create_new_shape(): raise RuntimeError("The initial shape could not be created.")
        
        # Bind key-presses
        self.board.bind_all('<Key>', self.key_eval)
          

    def animate(self):
       
        #print("auto_move")
        if self.board.cant_move:
            self.board.cant_move = False
            self.create_new_shape()
            
            if(self.board.game_over):
                self.board.show_game_over()
        else:
           #pass
           self.queue.put_nowait('Down')

 
    def create_new_shape(self):
        ''' Return value: type: Shape
            Create a random new shape that is centered
             at y = 0 and x = int(self.BOARD_WIDTH/2)
            set the current_shape with this shape
        '''
        shape = Tetris.SHAPES[random.randrange(0,len(Tetris.SHAPES))]
        center = Point(self.BB_WIDTH//2,0)
        self.current_shape = shape(center) # Creates new instance of whichever shape, passing in the center

        if not self.board.add_shape(self.current_shape): return False
        return True

    def key_eval(self, evnt):
        '''
            if the user presses the space bar 'space', the shape will move
            down until it can no longer move and is added to the board

            if the user presses the ['Ctrl','0'] key ,
                the shape should rotate ['Left','Right'].

        '''
        key = evnt.keysym   # self.board.checkKey()    
      
        if(self.board.game_over or key=='e' or key=='c'): os._exit(0)

        if(key==""): return # If there was no key pressed, do nothing
        elif(key=='Control_R'):
            self.queue.put_nowait('Rotate Left')
        elif key=='KP_0':
            self.queue.put_nowait('Rotate Right')
        elif key=='space':
            self.queue.put_nowait('All Down')
        elif len(key)>1:
            self.queue.put_nowait(key)
             
      #  print(key)

    def update(self):
        ''' Processes updates from self.queue '''
        while not self.queue.empty():
            if self.board.isClosed(): os._exit(0) 
            item = self.queue.get_nowait()
            if item == None: continue
            elif item=='Rotate Right':
                self.board.rotate('Right')
            elif item=='Rotate Left':
                self.board.rotate('Left')
            elif item=='All Down':
                while not self.board.cant_move:
                    self.board.move_on_board()
            else:
                direction = self.DIRECTION.get(item, None)
                if(direction != None): self.board.move_on_board(direction)

    
################################################################
# Start the game
################################################################

game = Tetris("Tetris")

def auto_move():
    ''' Moves the current_shape every self.delay ms
    '''
    if not(game.board.game_over):
        game.animate() 
        game.board.getRoot().after(game.delay, auto_move)

def auto_update():
    if not(game.board.game_over):
       game.update()
       game.board.getRoot().after(100, auto_update)

game.board.getRoot().after(0, auto_move)
game.board.getRoot().after(0, auto_update)
game.board.getRoot().mainloop()
