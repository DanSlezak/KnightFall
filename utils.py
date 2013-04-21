## Import Modules
import os, pygame
## put commonly used in global namespace
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


## functions to create our resources
def load_image( name, colorkey = None ):
    '''
    Given a filename 'name' in the data directory and
    a color 'colorkey' whose RGB value (or color map index) will be treated as transparent,
    loads the image and returns a pygame.Surface.
    
    NOTE: The default 'colorkey' parameter, None, causes the image
          to be entirely opaque.
    NOTE: The special 'colorkey' value of -1 causes the top-left pixel color
          in the image to be used as the transparent color.
    '''
    
    ## Find 'name' within the 'data' directory independent of
    ## operating system path character.
    fullname = os.path.join( 'data', name )
    try:
        image = pygame.image.load( fullname )
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at( (0,0) )
        ## accelerate
        image.set_colorkey( colorkey, RLEACCEL )
    return image, image.get_rect()

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

def load_image_alpha( name ):
    '''
    Given a filename 'name' of an image with an alpha channel in the data directory,
    loads the image and returns a pygame.Surface.
    '''
    
    ## Find 'name' within the 'data' directory independent of
    ## operating system path character.
    fullname = os.path.join( 'data', name )
    try:
        image = pygame.image.load( fullname )
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    
    image = image.convert_alpha()
    return image, image.get_rect()

def extract_frames_from_spritesheet( sheet_rect, sprite_width, sprite_height, num_frames = None ):
    '''
    Given a sprite sheet rectangle 'sheet_rect' as a pygame.Rect,
    the integer width of a sprite 'sprite_width',
    the integer height of a sprite 'sprite_height',
    and an optional parameter 'num_frames',
    returns a list of offset pygame.Rect's that tile in sequence to fill 'sheet_rect'.
    
    The 'num_frames' parameter, if specified, limits the number of frames returned.
    This can be used in cases where the 'sheet_rect' isn't completely full of sprites.
    
    NOTE: The 'num_frames' parameter can be negative, in which case '-num_frames' frames
          are subtracted from the end of the returned frames.
    
    NOTE: The 'sheet_rect' parameter need not have a .top or .left of 0.
          This way you can pass offsets into a larger sprite sheet.
    '''
    
    frames = []
    for yoff in range( sheet_rect.top, sheet_rect.bottom-sprite_height, sprite_height ):
        for xoff in range( sheet_rect.left, sheet_rect.right-sprite_width, sprite_width ):
            frame_rect = Rect( ( xoff, yoff ), ( sprite_width, sprite_height ) )
            frames.append( frame_rect )
    
    ## If the sprite sheet isn't "full":
    if num_frames is not None:
        frames = frames[:num_frames]
    
    return frames

def rect_overlaps_mask( rect, mask, unpassable_color = (0,0,0) ):
    '''
    Given a pygame.Rect 'rect',
    a pygame.Surface 'mask',
    and an optional RGB color (three integers between 0 and 255) 'unpassable_color'
    whose default is black,
    returns whether or not 'rect' overlaps any pixels in 'mask' whose value is
    'unpassable_color'.
    
    NOTE: This function is slower than using create_mask_overlaps_function_from_surface().
    '''
    
    clipped_rect = rect.clip( mask.get_rect() )
    ## If 'rect' is completely outside of 'mask', it doesn't overlap an unpassable pixel.
    if clipped_rect.width == 0 or clipped_rect.height == 0: return False
    
    ## Let's make a numpy.array out of the region of the mask we are interested in.
    submask = mask.subsurface( clipped_rect )
    ## UPDATE: pygame.surfarray.array3d() is unusably slow,
    ##         but pygame.surfarray.pixels3d() is fast.
    arr = pygame.surfarray.pixels3d( submask )
    ## Now we can call a numpy function to check if any pixels in the subregion equal
    ## 'unpassable_color'.
    return ( arr == unpassable_color ).all( axis = 2 ).any()

def create_mask_overlaps_function_from_surface( mask, unpassable_color = (0,0,0) ):
    '''
    Given a pygame.Surface 'mask' and
    an optional RGB color (three integers between 0 and 255) 'unpassable_color'
    whose default is black,
    returns a function that takes a pygame.Rect and returns whether or not 'rect'
    overlaps any pixels in 'mask' whose value is 'unpassable_color'.
    
    Example:
        ## Create the overlaps function once just after loading the mask:
        overlaps = create_mask_overlaps_function_from_surface( mask )
        
        ...
        
        ## Call overlaps() repeatedly when updating the game world:
        if overlaps( rect ): print 'rect overlaps unpassable region of mask!'
    '''
    
    ## Let's make a numpy.array out of the region of the mask we are interested in.
    ## UPDATE: pygame.surfarray.pixels3d() is much faster than pygame.surfarray.array3d().
    arr = pygame.surfarray.pixels3d( mask )
    ## Convert the array into a boolean array of pixels that equal the unpassable_color.
    arr = ( arr == unpassable_color ).all( axis = 2 )
    
    ## Return the desired function.
    def rect_overlaps_unpassable( rect ):
        clipped_rect = rect.clip( mask.get_rect() )
        ## If 'rect' is completely outside of 'mask', it doesn't overlap an unpassable pixel.
        if clipped_rect.width == 0 or clipped_rect.height == 0: return False
        
        return arr[ clipped_rect.left : clipped_rect.right, clipped_rect.top : clipped_rect.bottom ].any()
    
    return rect_overlaps_unpassable

def path_rejoin( path ):
    return os.path.join( *path.split('/') )
