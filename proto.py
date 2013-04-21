'''
Created on Mar 4, 2013

@author: Joshua
'''
import os, pygame, json
from pygame.locals import *
from utils import *
from modes import ModeManager, GameMode, SimpleMode

kDataDir = 'data'
kGlobals = 'globals.json'

def load_sound( name ):
    '''
    Given a filename 'name' in the data directory,
    loads the sound and returns a pygame.mixer.Sound().
    If sound functionality is not available, returns a dummy sound object
    whose play() method is a no-op.
    '''
    
    class NoneSound:
        def play( self ): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    
    fullname = os.path.join( 'data', name )
    try:
        sound = pygame.mixer.Sound( fullname )
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    
    return sound

class SplashScreen( GameMode ):
    def __init__( self, image, duration_in_milliseconds, next_mode_name ):
        '''
        Given a duration to show the splash screen 'duration_in_milliseconds',
        and the name of the next mode,
        displays 'image' until either a mouse click or 'duration_in_milliseconds'
        milliseconds have elapsed.
        '''
        ## Initialize the superclass.
        GameMode.__init__( self )
        
        self.image = image
        self.duration = duration_in_milliseconds
        self.next_mode_name = next_mode_name
    
    def enter( self ):
        '''
        Reset the elapsed time and hide the mouse.
        '''
        self.so_far = 0
        pygame.mouse.set_visible( 0 )
    
    def exit( self ):
        '''
        Show the mouse.
        '''
        pygame.mouse.set_visible( 1 )
    
    def draw( self, screen ):
        '''
        Draw the splash screen.
        '''
        screen.blit( self.image, ( 0,0 ) )
        pygame.display.flip()
    
    def update( self, clock ):
        '''
        Update the elapsed time.
        '''
        
        self.so_far += clock.get_time()
        
        ## Have we shown the image long enough?
        if self.so_far > self.duration:
            self.switch_to_mode( self.next_mode_name )
    
    def mouse_button_down( self, event ):
        '''
        Switch on mouse click.
        '''
        self.switch_to_mode( self.next_mode_name )


class SelectScreen( GameMode ):
    def __init__( self ):
        ## Initialize the superclass.
        GameMode.__init__( self )
        
        self.image, _ = load_image( 'pause.png' )
        self.quit_rect = pygame.Rect( 255, 340, 337, 250 )
        self.start_rect = pygame.Rect( 271, 100, 302, 250 )
        
        self.mouse_down_pos = (-1,-1)
    
    def mouse_button_down( self, event ):
        self.mouse_down_pos = event.pos
    
    def mouse_button_up( self, event ):
        
        def collides_down_and_up( r ):
            return r.collidepoint( self.mouse_down_pos ) and r.collidepoint( event.pos )
        
        if collides_down_and_up( self.quit_rect ):
            print 'quitting'
            self.quit()
        
        if collides_down_and_up( self.start_rect ):
            print 'play!'
            self.switch_to_mode( 'playing' )
    
    def draw( self, screen ):
        ## Draw the HUD.
        screen.blit( self.image, ( 0,0 ) )
        pygame.display.flip()


class Playing( GameMode ):
    def __init__( self, levels ):
        ## Initialize the superclass.
        GameMode.__init__( self )
        
        self.levels = [ Level( name ) for name in levels ]
        self.current_level_index = 0
    
    def enter( self ):
        ## Reload the level CSV files:
        self.levels = [ Level( level.name ) for level in self.levels ]
    
    def draw( self, screen ):
        ## A variable holding the current level for convenience.
        level = self.levels[ self.current_level_index ]
        
        ## Draw the background and the sprites.
        screen.blit( level.background, ( 0,0 ) )
        level.sprites.draw( screen )
        
        pygame.display.flip()
    
    def update( self, clock ):
        ## A variable holding the current level for convenience.
        level = self.levels[ self.current_level_index ]
        
        ## Update the sprites.  Pass them the clock and a mask.
        level.sprites.update( clock )
    
    def key_down( self, event ):
        ## Go to the pause screen when escape is pressed.
        if event.key == K_ESCAPE:
            self.switch_to_mode( 'select' )

class Avatar( pygame.sprite.Sprite ):
    def __init__( self, level ):
        pygame.sprite.Sprite.__init__( self ) #call Sprite intializer
        self.image, self.rect = load_image( 'R2.png', -1 )
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 370, 250
        self.walk = 0
        self.move = 0
        self.level = level
        self.newpos = self.rect.move(0,0)
    
    
    def update( self, clock ):
        pressed = pygame.key.get_pressed()
        if pressed[ K_RIGHT ]:
            self._walkRight()
        if pressed[ K_LEFT ]:
            self._walkLeft()
        if pressed[ K_DOWN ]:
            self._walkDown()
        if pressed[ K_UP ]:
            self._walkUp()
            
    def _walkRight( self ):
        if self.level.mask_function( self.rect.move( ( 1, self.move)) ):
            self.newpos = self.newpos
        else:
            self.newpos = self.rect.move( ( 1, self.move))    
        if self.walk < 25:
            self.image, self.rect = load_image( 'R1.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 50:
            self.image, self.rect = load_image( 'R2.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 75:
            self.image, self.rect = load_image( 'R3.png', -1 )
            self.walk = self.walk + 1
        else:
            self.walk = 0;
        self.rect = self.newpos
        
    def _walkLeft( self ):
        if self.level.mask_function( self.rect.move( ( -1, self.move)) ):
            self.newpos = self.newpos
        else:
            self.newpos = self.rect.move( ( -1, self.move)) 
        if self.walk < 25:
            self.image, self.rect = load_image( 'L1.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 50:
            self.image, self.rect = load_image( 'L2.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 75:
            self.image, self.rect = load_image( 'L3.png', -1 )
            self.walk = self.walk + 1
        else:
            self.walk = 0;
        self.rect = self.newpos
        
    def _walkUp( self ):
        if self.level.mask_function( self.rect.move( (self.move, -1)) ):
            self.newpos = self.newpos
        else:
            self.newpos = self.rect.move( (self.move, -1)) 
       
        if self.walk < 25:
            self.image, self.rect = load_image( 'Up1.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 50:
            self.image, self.rect = load_image( 'Up2.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 75:
            self.image, self.rect = load_image( 'Up3.png', -1 )
            self.walk = self.walk + 1
        else:
            self.walk = 0;
        self.rect = self.newpos
        
    def _walkDown( self ):
        if self.level.mask_function( self.rect.move( (-self.move,1 )) ):
            self.newpos = self.newpos
        else:
            self.newpos = self.rect.move( (-self.move,1)) 
       
        if self.walk < 25:
            self.image, self.rect = load_image( 'D1.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 50:
            self.image, self.rect = load_image( 'D2.png', -1 )
            self.walk = self.walk + 1
        elif self.walk < 75:
            self.image, self.rect = load_image( 'D3.png', -1 )
            self.walk = self.walk + 1
        else:
            self.walk = 0;
        self.rect = self.newpos
        
class Level( object ):
    def __init__( self, level_name ):
        self.name = level_name
        
        ## Load files for level_name:
        self.background, _ = load_image( level_name + 'background.png' )
        self.mask, _ = load_image( level_name + 'back_mask.png' )
        self.mask_function = create_mask_overlaps_function_from_surface( self.mask )
        font = pygame.font.Font( None, 36 )
        text = font.render( "DELIA", 1, ( 0, 0, 0 ) )
        textpos = (10,10)
        self.background.blit( text, textpos )
        self.sprites = pygame.sprite.Group()
        self.sprites.add( Avatar(self))


def main():
    ### Load global variables.
    globals = json.load( open( os.path.join( kDataDir, kGlobals ) ) )
    
    
    ### Initialize pygame.
    pygame.init()
    screen = pygame.display.set_mode( globals['screen_size'] )
    pygame.display.set_caption( globals['window_title'] )
    clock = pygame.time.Clock()
    
    
    ### Set up the modes.
    modes = ModeManager()

    ## The splash screen.
    splash_image, _ = load_image( globals['splash_screen'] )
    modes.register_mode( 'splash_screen', SplashScreen( splash_image, 5000, 'select' ) )

    ## A dummy "select" mode.
    modes.register_mode( 'select', SelectScreen() )
    modes.register_mode( 'playing', Playing( globals['levels'] ) )
    
    ## Start with the splash screen.
    modes.switch_to_mode( 'splash_screen' )
    
    
    ### The main loop.
    fps = globals['fps']
    while not modes.quitting():
        clock.tick( fps )
        song = load_sound('song.wav')
        if(pygame.mixer.music.get_busy() == 0):
            song.play()
        ## Handle Input Events
        for event in pygame.event.get():
            
            if event.type == QUIT:
                break
            
            elif event.type == KEYDOWN:
                modes.current_mode.key_down( event )
            
            elif event.type == KEYUP:
                modes.current_mode.key_up( event )
            
            elif event.type == MOUSEMOTION:
                modes.current_mode.mouse_motion( event )
            
            elif event.type == MOUSEBUTTONUP:
                modes.current_mode.mouse_button_up( event )
            
            elif event.type == MOUSEBUTTONDOWN:
                modes.current_mode.mouse_button_down( event )
        
        modes.current_mode.update( clock )
        modes.current_mode.draw( screen )
    
    
    ### Game over.
    
    ## TODO: Save game state.


## this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
