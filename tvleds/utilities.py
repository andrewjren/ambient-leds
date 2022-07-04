import numpy as np

def hsi2rgb(H,S,I):

    # convert HSI to RGB
    if H == 0:
        r = I + 2*I*S
        g = I - I*S
        b = I - I*S

    elif H < 120:
        r = I + I*S*np.cos(H*np.pi/180)/np.cos((60-H)*np.pi/180)
        g = I + I*S*(1-np.cos(H*np.pi/180)/np.cos((60-H)*np.pi/180))
        b = I - I*S

    elif H == 120:
        r = I - I*S
        g = I + 2*I*S
        b = I - I*S 

    elif H < 240:
        r = I - I*S 
        g = I + I*S*np.cos((H-120)*np.pi/180)/np.cos((180-H)*np.pi/180)
        b = I + I*S*(1 - np.cos((H-120)*np.pi/180)/np.cos((180-H)*np.pi/180))

    elif H == 240:
        r = I - I*S 
        g = I - I*S 
        b = I + 2*I*S 

    else:
        r = I + I*S*(1 - np.cos((H-240)*np.pi/180)/np.cos((300-H)*np.pi/180))
        g = I - I*S 
        b = I + I*S*np.cos((H-240)*np.pi/180)/np.cos((300-H)*np.pi/180) 

    max_rgb = np.max([r,g,b])
    r = 255 * r/max_rgb
    g = 255 * g/max_rgb
    b = 255 * b/max_rgb

    return int(r), int(g), int(b)

# hex rgb string has format: #000000
def hex2rgb(hex_string):
    r = int(hex_string[1:2], 16)
    g = int(hex_string[3:4], 16)
    b = int(hex_string[5:6], 16)

    return r,g,b



def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)
