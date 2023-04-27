import time
import random
import pygame
from pygame import mixer
from gpiozero import Button
from gpiozero import LED
import RPi.GPIO as GPIO
from RPLCD import *
from time import sleep
from RPLCD.i2c import CharLCD

# LED Stuff
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22, GPIO.OUT) # Red
GPIO.setup(23, GPIO.OUT) # Green
GPIO.setup(24, GPIO.OUT) # Blue

# LCD Stuff
lcd = CharLCD("PCF8574", 0x27)
lcd.cursor_pos = (0, 0)

# For LCD scrolling text
framebuffer = [
        '',
        '',
        ]
def write_to_lcd(lcd, framebuffer, num_cols):
        """Write the framebuffer out to the specified LCD."""
        lcd.home()
        for row in framebuffer:
            lcd.write_string(row.ljust(num_cols)[:num_cols])
            lcd.write_string('\r\n')
def long_text(text):
        if len(text)<16:
            lcd.write_string(text)
        for i in range(len(text) - 16 + 1):
            framebuffer[1] = text[i:i+16]
            write_to_lcd(lcd, framebuffer, 16)
            sleep(0.5)

# Buttons and variables
vol_down_button = Button(6)
vol_up_button = Button(5)
pause_button=Button(4)
skip_button = Button(27)
prev_button = Button(17)

mixer.init()

song_list = []
volume = 0.5
song_index = 0
song_playing = True
speaker_on = True

# All songs go into array and shuffled
song_list.append("Breezeblocks-Alt-J")
song_list.append("Washing-Machine-Heart-Mitski")
song_list.append("Alien-Blues-Vundabar")
song_list.append("Glass-Animals-Heat-Waves")
song_list.append("Glass-Animals-Season-2-Episode-3")
random.shuffle(song_list)

while speaker_on:
    mixer.music.load(song_list[song_index] + ".ogg")
    mixer.music.play()
    mixer.music.set_volume(volume)

    # LED lights on
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)

    # LCD text
    text = "Now Playing:"
    framebuffer[0] = text
    write_to_lcd(lcd,framebuffer,16)
    lcd.cursor_pos = (1, 0)
    long_text(song_list[song_index])
    print(song_list[song_index])

    while mixer.music.get_busy():
        # While song is playing...
        if vol_down_button.is_pressed:
            volume = max(0, volume-.01)
            mixer.music.set_volume(volume)
            print("lowing volume")
        if vol_up_button.is_pressed:
            volume = min(1, volume+.01)
            mixer.music.set_volume(volume)
            print("increasing volume")
        if skip_button.is_pressed:
            mixer.music.stop()
            print("skip")
        if prev_button.is_pressed:
            mixer.music.stop()
            print("previous")
            if song_index == 0:
                song_index = -1
            else:
                song_index = song_index - 2
        if pause_button.is_pressed:
            # Lights go out
            GPIO.output(22, GPIO.HIGH)
            GPIO.output(23, GPIO.HIGH)
            GPIO.output(24, GPIO.HIGH)
            print("pause")
            lcd.cursor_pos = (0,0)
            lcd.write_string("Paused:        ")
            mixer.music.pause()
            time.sleep(1) # while pause_button.is_pressed:
            waiting=True
            while(waiting):
                if pause_button.is_pressed:
                    mixer.music.unpause()
                    print("unpause")
                    waiting = False
                    # Lights are on when playing, text displays Now Playing:
                    GPIO.output(22, GPIO.LOW)
                    GPIO.output(23, GPIO.LOW)
                    GPIO.output(24, GPIO.LOW)
                    text = "Now Playing:"
                    framebuffer[0] = text
                    write_to_lcd(lcd,framebuffer,16)
                    lcd.cursor_pos = (1, 0)
                    long_text(song_list[song_index])
                    time.sleep(1)
        time.sleep(0.01)

    # Plays next song once song is over and cleans up GPIO if done
    if song_index != len(song_list) - 1 and not mixer.music.get_busy():
        song_index = song_index + 1
    elif song_index == len(song_list) - 1:
        speaker_on = False
        GPIO.output(22, GPIO.LOW)
        GPIO.output(23, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        vol_down_button.close()
        vol_up_button.close()
        pause_button.close()
        skip_button.close()
        prev_button.close()
        GPIO.cleanup()
        quit()
