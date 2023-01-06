# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
from utime import sleep_ms
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 30
LED_PIN_NUM = 22
BRIGHTNESS = 0.2
BUTTON = Pin(17, Pin.IN, Pin.PULL_UP)   #Internal pull-up
BUTTON_STATE=0

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(LED_PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * BRIGHTNESS)
        g = int(((c >> 16) & 0xFF) * BRIGHTNESS)
        b = int((c & 0xFF) * BRIGHTNESS)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)

while True:
    if BUTTON.value() == 0:       #key press
      if BUTTON_STATE==0:
        pixels_fill(BLACK)
        pixels_show()
        sleep_ms=100
        while BUTTON.value() == 0:
          BUTTON_STATE="RED"
      elif BUTTON_STATE=="RED":
        pixels_fill(RED)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="YELLOW"
      elif BUTTON_STATE=="YELLOW":
        pixels_fill(YELLOW)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="GREEN"
      elif BUTTON_STATE=="GREEN":
        pixels_fill(GREEN)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="CYAN"
      elif BUTTON_STATE=="CYAN":
        pixels_fill(CYAN)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="BLUE"
      elif BUTTON_STATE=="BLUE":
        pixels_fill(BLUE)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="PURPLE"
      elif BUTTON_STATE=="PURPLE":
        pixels_fill(PURPLE)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="WHITE"
      elif BUTTON_STATE=="WHITE":
        pixels_fill(WHITE)
        pixels_show()
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="CHASES"
      elif BUTTON_STATE=="CHASES":
        for color in COLORS:       
          color_chase(color, 0.01)
          sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE="RAINBOW"
      elif BUTTON_STATE=="RAINBOW":
        rainbow_cycle(0)
        sleep_ms=100
        while BUTTON.value()== 0:
          BUTTON_STATE=0