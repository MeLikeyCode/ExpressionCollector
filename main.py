#Imports
import kivy.metrics #allows use of kivy.metrics.cm(1), which converts physical sizes to pixels
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from kivy.properties import NumericProperty
from kivy.properties import StringProperty

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.graphics import Color, Rectangle

from kivy.vector import Vector

from random import random
from random import randint
from random import choice

import math


class MyApp(App):
    def build(self):
        global root
        root = RootWidget()
        return root

class LosingLabel(Label):
    """Represents a random messege that is shown when the player loses.
    When the player loses, the whole screen is cleared and then an instance of this class is displayed. 
    When the user touches the screen, he is taken back to the original start screen."""
    def __init__(self,**kwargs):
        """Sets the initial position, size and messege of the losing label."""
        super().__init__(**kwargs)
        self.font_size = 25
        self.center_x = Window.width/2
        self.center_y = Window.height/2
        self.possible_messeges = ['Don\'t consume negative numbers, they will decrease you!','Game over if you become 0 or less.','You can only consume expressions that are equal or less than you.']
        self.text = choice(self.possible_messeges)

    def on_touch_down(self,touch):
        """Takes the user back to the start screen."""
        root.remove_widget(self)
        root.start_screen()
        return True

class HowToPlay(Label):
    def __init__(self,**kwargs):
        super().__init__(*kwargs)
        self.text_size = [Window.width,Window.height]
        self.text = """Rules:
-Bumping into an expresssion that is less than or equal to you will add that expression's value to you.
-Bumping into an expression that is greater than you will result in game over.
-Becoming less than or equal to 0 will result in game over.
-HINT: try to bump into expressions that are as great as possible but not greater than you.
                            
Movement:
-Swipe in a direction to move.
-Small swipe length -> move one space.
-Medium swipe length -> move two spaces (jumps over the middle space).
-Long swipe length -> slide in that direction until screen is tapped."""

    def on_touch_down(self,touch):
        """Takes the user back to the start screen."""
        root.remove_widget(self)
        root.start_screen()
        return True

class Grid(Widget):
    """Represents a grid. The grid has properties that determine the number of columns, rows, and the width/height of each cell.
    The playerexpr uses the grid to calculate its movement step.
    Properties: num_cols,num_rows, cell_height, cell_width
    Method: adjust_grid() -> Adjusts the grid properties based on the current screen size. Then draws the grid."""
    num_cols = NumericProperty()
    num_rows = NumericProperty()
    cell_width = NumericProperty()
    cell_height = NumericProperty()

    def adjust_grid(self,*args):
        """Adjusts the grid properties based on the current screen size. Then draws the grid."""
        self.canvas.clear()
        cell_size_min = kivy.metrics.cm(1) #TODO: store as global constant

        #Based on the screen size, calculate values for the grid attributes (num_rows, num_cols, cell_width, cell_height).
        num_cols = round(Window.width / cell_size_min)
        num_rows = round(Window.height / cell_size_min)

        cell_width = Window.width / num_cols
        cell_height = Window.height / num_rows

        #Set the grid attributes to these calculated values
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.cell_width = cell_width
        self.cell_height = cell_height

        #draw the grid
        #horizontal lines
        for i in range(self.num_rows):
            with self.canvas:
                Color(1,1,1,0.15)
                Rectangle(pos=[0,i*self.cell_height],size=[Window.width,1])
        #vertical lines
        for i in range(self.num_cols):
            with self.canvas:
                Color(1,1,1,0.15)
                Rectangle(pos=[i*self.cell_width,0],size=[1,Window.height])


class RootWidget(Widget):
    """Represents the world that all other objects live in (grid,playerexpr,Exprs,logo,playbtn,LosingLabel).
    The root widget handles interactions between its various children. Notibaly, it switches between the
    start and play screen. It correctly repositions Exprs and the playerexpr when the Window is resized. It also
    makes the game progressively harder.
    Attributes: grid, playerexpr, children"""

    def __init__(self,**kwargs):
        """Start at the start screen."""
        super().__init__(**kwargs)
        self.start_screen()

    def start_screen(self):
        """Displays the start screen with the title and play button. Also sets the initial difficulty variables."""
        self.clear_widgets()
        #create the logo
        self.logo = Label(text='Expression Collector',font_size=0.1*Window.height)
        self.logo.center_x = Window.width/2
        self.logo.center_y = Window.height/2
        self.add_widget(self.logo)
        #create the playbtn
        self.playbtn = Button(text='play',font_size=0.05*Window.height,background_color=[0,0,0,0])
        self.playbtn.center_x = Window.width/2
        self.playbtn.center_y = Window.height/2 - 0.1*Window.height
        self.playbtn.bind(on_release=self.play)
        self.add_widget(self.playbtn)
        #create the howtoplaybtn 100 px under the playbtn
        self.howtoplaybtn = Button(text='how to play',font_size=0.05*Window.height,background_color=[0,0,0,0])
        self.howtoplaybtn.center_x = Window.width/2
        self.howtoplaybtn.center_y = self.playbtn.center_y - 100
        self.howtoplaybtn.bind(on_release=self.howtoplay)
        self.add_widget(self.howtoplaybtn)
        #make bindings to make start screen fluid
        Window.bind(size=self.adjust_start_widgets)
        #create initial difficulty variables
        self.MINUTE = 0 #it has been 0 minutes so far
        self.MAX_NUMBER = 2 # the biggest number that can be part of an expression
        self.MAX_LENGTH = 2 #the maximum number of numbers in an expression
        self.AVAILABLE_OPERATORS = ['+','-'] #at first just + and - operators are available
        self.sound = SoundLoader.load('startscreen.wav')
        self.sound.loop = True
        self.sound.play()

    def howtoplay(self,*args):
        self.clear_widgets()
        self.sound.stop()
        p = HowToPlay()
        p.width = Window.width
        p.height = Window.height
        self.add_widget(p)

    def adjust_start_widgets(self,*args):
        """Centers the starting logo, play buttin, and instructions."""
        #adjust play button
        self.playbtn.center_x = Window.width/2
        self.playbtn.center_y = Window.height/2 - 0.1 * Window.height
        self.playbtn.font_size = 0.05 * Window.height
        #adjust logo
        self.logo.center_x = Window.width/2
        self.logo.center_y = Window.height/2
        self.logo.font_size = 0.1 * Window.height
        #adjust how to play btn
        self.howtoplaybtn.center_x = Window.width/2
        self.howtoplaybtn.center_y = self.playbtn.center_y - 100
        self.howtoplaybtn.font_size = self.playbtn.font_size

    def play(self,*args):
        """Goes from the start screen to the game screen. Creates the playerexpr, grid, and random Exprs."""
        #Delete the logo and button
        self.remove_widget(self.logo)
        self.remove_widget(self.playbtn)
        self.remove_widget(self.howtoplaybtn)
        #Delete start screen music, load game music
        self.sound.stop()
        self.sound = SoundLoader.load('game.wav')
        self.sound.loop = True
        self.sound.play()

        #create the grid
        global grid
        grid = Grid()
        grid.adjust_grid() #Adjust/draw the grid to the initial window size
        Window.bind(size=grid.adjust_grid) #bind Window.size -> grid.adjust_grid
        self.add_widget(grid)

        #create the playerexpr
        global playerexpr
        playerexpr = PlayerExpr(value=1,text='1',color=[1,1,1,1],font_size=grid.cell_height)
        self.add_widget(playerexpr)

        Clock.schedule_interval(playerexpr.check_collisions,1/30.0) #Check for collisions with PlayerExpr
        Clock.schedule_interval(self.create_expr,2) #create Expr objects for the game
        Clock.schedule_interval(self.make_harder,60) #make the game harder every 60 seconds

        #play bindings
        Window.bind(size=self.reposition_children) #bind window resizing to repositioning all of its children

    def lose_screen(self):
        """Clears the screen and just displays a losing label."""
        Clock.unschedule(self.create_expr)
        Clock.unschedule(self.make_harder)
        Clock.unschedule(playerexpr.check_collisions)
        self.sound.stop() #stop the game music
        self.clear_widgets()
        self.add_widget(LosingLabel())

    def make_harder(self,dt):
        """Alters a bunch of variables to make the game progressively harder. This function is called every minute."""
        self.MINUTE += 1
        self.MAX_NUMBER += playerexpr.value #TODO maybe == instead of +=
        if self.MINUTE % 2 == 0 and self.MAX_LENGTH < 6: #if this is an even minute, increase expression length
            self.MAX_LENGTH += 1
        if self.MINUTE == 2:
            self.AVAILABLE_OPERATORS += ['/']
        if self.MINUTE == 3:
            self.AVAILABLE_OPERATORS += ['*']

    def reposition_children(self,*args):
        """When the winow is resized, reposition all children. If the PlayerExpr child is offscreen, move him back in."""
        for c in self.children:
            c.center_y = round(c.center_y/grid.cell_height) * grid.cell_height - grid.cell_height/2
            #if the PlayerExpr is off screen, put him in the center
            if isinstance(c,PlayerExpr) and (self.center_x < 0 or self.center_x > Window.width):
                c.set_default_pos() #move player to the center

    def create_expr(self,dt):
        """Creates a random expression at a random lane on the left or right edget of the screen."""
        #come up with a random expression
        num_of_nums = randint(2,self.MAX_LENGTH)
        num_of_ops = num_of_nums - 1 # the number of operators is just one less than the number of numbers
        expression = ''
        for i in range(num_of_nums + num_of_ops):
            #this is a number spot
            if i % 2 == 0:
                rand_int = randint(-1*self.MAX_NUMBER,self.MAX_NUMBER)
                #if we get a negative random number
                if rand_int < 0:
                    expression += "(" + str(rand_int) + ")"
                else:
                    expression += str(randint(1,self.MAX_NUMBER))
            #this is an operator spot
            else:
                expression += choice(self.AVAILABLE_OPERATORS)

        #instantiate an Expr with this expression as a value
        expr = Expr(value=expression)
        #set initial position
        expr.center_x = choice([-200,Window.width + 200]) #200 pixels on each side of the window
        expr.center_y = choice(range(grid.num_rows)) * grid.cell_height + 0.5 * grid.cell_height #in one of the lanes
        #set initial velocity
        if expr.center_x < 0:
            expr.velocity = 1 * randint(1,4)
        else:
            expr.velocity = -1 * randint(1,4)
        self.add_widget(expr)


class PlayerExpr(Label):
    """Class that represents a player controlled expression. The player changes positions based on swipe gesters.
    A small swipe in a direction causes the player to move 1 space to that direction. A medium swipe causes 
    the player to move 2 spaces to that direction. A large swipe will cause the player to slide in that direction
    until he collides with an Expr or an edge.
    Properties: value
    Method: set_default_pos() -> Moves to the center of the screen."""
    value = NumericProperty(0)

    def __init__(self,**kwargs):
        self.register_event_type('on_swipe') #allows responding to a swipe event
        super().__init__(**kwargs)

        self.width = self.texture_size[0]
        self.height = grid.cell_height - 2 #1 px for top, 1 px for bottom
        self.sliding = False #not sliding initially
        self.value_to_add = 0
        
        #set initial position as the default position (center of the screen)
        self.set_default_pos()

        #bindings
        self.bind(value=self.change_text) #change the text whenever the num changes
        grid.bind(cell_height=self.setter('font_size')) #change the font size to whatever the cell_height is
        self.bind(texture_size=self.change_size)

        #sounds
        self.sound_move = SoundLoader.load('move.wav')
        self.sound_collect = SoundLoader.load('collect.wav')

    def set_default_pos(self):
        """Move the PlayerExpr to the center of the screen."""
        #calculate center_x position
        num_cols = grid.num_cols
        col_to_live_in = round(num_cols / 2)
        self.center_x =  col_to_live_in * grid.cell_width - grid.cell_width / 2

        #calculate center_y position
        num_rows = grid.num_rows
        row_to_live_in = round(num_rows / 2)
        self.center_y = row_to_live_in * grid.cell_height - grid.cell_height / 2

    def change_size(self,*args):
        """Changes the size of the object to that of the texture_size minus some from the top/bottom."""
        self.width = self.texture_size[0]
        self.height = grid.cell_height - 2

    def change_text(self,*args):
        """Update the text to value of num."""
        self.text = str(self.value)

    def check_collisions(self,dt):
        """Handle any Exprs that are colliding with this object. This function is scheduled to run repeatedly."""
        for child in root.children:
            #if the Expr collides with the PlayerExpr
            if isinstance(child,Expr) and child.collide_widget(self):
                self.sliding = False #stop sliding
                #if the Expr is bigger -> kill player
                if eval(child.value) > self.value:
                    root.lose_screen()
                    return
                #otherwise -> eat the expr
                else:
                    #if the eaten expression is negative -> roll down
                    if eval(child.value) < 0:
                        self.value_to_add = abs(eval(child.value))
                        Clock.schedule_interval(self.roll_down,1/60)
                    #if the eaten expression is positive -> roll up
                    else:
                        self.value_to_add += round(eval(child.value))
                        Clock.schedule_interval(self.roll_up,1/60)
                    self.sound_collect.play()
                    root.remove_widget(child) #remove the Expr

    def on_touch_down(self,touch):
        touch.ud['pt1'] = Vector(touch.x,touch.y)
        if self.sliding == True:
            self.sliding = False
        return super().on_touch_down(touch)

    def on_touch_up(self,touch):
        """Checks if the user has swiped in a movement direction (right,left,up,down,upright,downright,upleft,downleft).
        If so, dispatches a on_swipe event (to which the playerexpr responds by moving)."""
        pt1 = touch.ud['pt1']
        pt2 = Vector(touch.x,touch.y)
        vect = pt2-pt1
        angle = vect.normalize().angle((1,0))
        length = vect.length()

        #If the swipe length is short -> this isn't a swipe, just let parent class's handle this event
        if length < 5:
            return super().on_touch_up(touch)
        #If the swipe length is long enough -> let this class handle it (don't propogate it any more - return True).
        else:
            if (angle >= -45 and angle <= 45):
                self.dispatch('on_swipe','right',length)
            elif angle >= 135 or angle <= -135:
                self.dispatch('on_swipe','left',length)
            elif angle >= 45 and angle <= 135:
                self.dispatch('on_swipe','up',length)
            elif angle <= -45 and angle >= -135:
                self.dispatch('on_swipe','down',length)
            #make sure to let the super classs know that this event has been handled 
            #(so you don't waste CPU time calling all its parents on_touch_up methods)
            return True

    def on_swipe(self,swipe_dir,swipe_len):
        """Move the PlayerExpr to the specified direction. Or slide him if the swipe is big enough."""
        if swipe_len > 200: #if this swipe is long enough to be a slide, call the slide method passing the direction
            self.slide(swipe_dir)
        elif swipe_dir == 'right' and self.center_x + grid.cell_width <= Window.width:
            self.x += grid.cell_width
            #If it was a long swipe, move him again
            if swipe_len > 100:
                self.x += grid.cell_width
            #regardless if it was a single or double move, make the same sound effect
            self.sound_move.play()
        elif swipe_dir == 'left' and self.center_x - grid.cell_width >= 0:
            self.x -= grid.cell_width
            if swipe_len > 100:
                self.x -= grid.cell_width
            self.sound_move.play()
        elif swipe_dir == 'up' and self.center_y + grid.cell_height <= Window.height:
            self.y += grid.cell_height
            if swipe_len > 100:
                self.y += grid.cell_height
            self.sound_move.play()
        elif swipe_dir == 'down' and self.center_y - grid.cell_height >= 0:
            self.y -= grid.cell_height
            if swipe_len > 100:
                self.y -= grid.cell_height
            self.sound_move.play()
        return True #this swipe has been handled!
    def slide(self,dir):
        """If the player is not already sliding, will call one of the slide_direction methods which do the actual moving."""
        #if I'm already sliding, dont try to slide again
        if self.sliding == True:
            return
        #otherwise, slide me
        self.sliding = True
        if dir == 'right':
            Clock.schedule_interval(self.slide_right,1/30)
        elif dir == 'left':
            Clock.schedule_interval(self.slide_left,1/30)
        elif dir == 'up':
            Clock.schedule_interval(self.slide_up,1/30)
        elif dir == 'down':
            Clock.schedule_interval(self.slide_down,1/30)

    def slide_right(self,dt):
        """Causes the player to slide to the right if he is not already sliding."""
        # if i'm done sliding return False so i can be unscheduled
        if self.sliding == False:
            return False
        #if i'm out of bounds return False so i can be unscheduled
        if self.center_x >= grid.num_cols * grid.cell_width - grid.cell_width/2:
            self.sliding = False
            return False
        #if im not done sliding and not out of bounds, continue sliding!
        self.center_x += grid.cell_width
    
    def slide_left(self,dt):
        """Causes the player to slide left if he is not already sliding."""
        # if i'm done sliding return False so i can be unscheduled
        if self.sliding == False:
            return False
        #if i'm out of bounds return False so i can be unscheduled
        if self.center_x <= grid.cell_width:
            self.sliding = False
            return False
        #if im not done sliding and not out of bounds, continue sliding!
        self.center_x -= grid.cell_width

    def slide_up(self,dt):
        """Causes the player to slide up if he is not already sliding."""
        # if i'm done sliding return False so i can be unscheduled
        if self.sliding == False:
            return False
        #if i'm out of bounds return False so i can be unscheduled
        if self.center_y >= grid.cell_height * grid.num_rows - grid.cell_height/2:
            self.sliding = False
            return False
        #if im not done sliding and not out of bounds, continue sliding!
        self.center_y += grid.cell_height

    def slide_down(self,dt):
        """Causes the player to slide down if he is not already sliding."""
        # if i'm done sliding return False so i can be unscheduled
        if self.sliding == False:
            return False
        #if i'm out of bounds return False so i can be unscheduled
        if self.center_y <= grid.cell_height/2:
            self.sliding = False
            return False
        #if im not done sliding and not out of bounds, continue sliding!
        self.center_y -= grid.cell_height

    def roll_up(self,dt):
        """Causes the player's value to be rolled up digit by digit. This method is scheduled when the player collides
        with a positive number smaller than him."""
        if self.value_to_add <= 0:
            return False #unschedule if there is no value to add
        add_step = math.ceil(self.value_to_add/100)
        self.value_to_add -= add_step #subtract from the value to add
        self.value += add_step #add to the value

    def roll_down(self,dt):
        """Causes the player's value to be rolled down digit by digit. This method is scheduled when the player collides
        with a negative number smaller than him."""
        if self.value_to_add <= 0:
            return False #unschedule if there is no value to add
        add_step = math.ceil(self.value_to_add/100)
        self.value_to_add -= add_step #subtract from the value to add
        self.value -= add_step #subtractt from the value
        #if the player becomes 0 or negative, lose.
        if self.value <= 0:
            root.lose_screen()



class Expr(Label):
    """Class that represents a computer controlled random Expr.
    Properties: value, velocity"""
    value = StringProperty() #IMPORTANT: the value property of the Expr is a STRING not a NUMBER!
    velocity = NumericProperty(0)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        #initial properties
        self.text = str(self.value)
        self.color = [random(),random(),random(),1]
        self.font_size = grid.cell_height
        self.width = self.texture_size[0] 
        self.height = grid.cell_height - 2 
        
        #set bindings
        grid.bind(cell_height=self.setter('font_size')) #cell_height -> font_size
        self.bind(texture_size=self.change_size) #texture_size -> self.change_size()

        Clock.schedule_interval(self.move,1/60) #start moving

    def move(self,dt):
        """Move the Expr. Destroy it if it goes off the screen."""
        self.x += self.velocity
        if self.parent != None and (self.center_x > Window.width + 205 or self.center_x < -205):
            root.remove_widget(self)
            return False #unschedule this method after we destroy the Expr

    def change_size(self,obj,texture_size):
        """Changes the size of the object to that of the texture_size minus some from the top/bottom."""
        self.width = texture_size[0]
        self.height = grid.cell_height - 2

if __name__ == '__main__':
    MyApp().run()
