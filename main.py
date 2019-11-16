# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from pidev.stepper import stepper

# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
STAIRCASEDONE = False  # staircase
OFF = True  # staircase
RAMPONTOP = True
GATEOPEN = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 5
RAMP_LENGTH = 725

ramp = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
               steps_per_unit=200, speed=8)
cyprus.initialize()


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()


#  ramp = stepper(port=0, speed=INIT_RAMP_SPEED)


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    staircaseSpeedText = '0'
    rampSpeed = INIT_RAMP_SPEED
    staircaseSpeed = 40

    cyprus.initialize()  # stop staircase
    cyprus.setup_servo(2)  # setup gate servo
    cyprus.set_servo_position(2, 0)  # close gate

    # ramp.set_speed(1)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def toggleGate(self):
        global GATEOPEN  # GATEOPEN is initially declared as True
        global STAIRCASEDONE
        if STAIRCASEDONE:
            sleep(2)
            cyprus.set_servo_position(2, .7)  # open gate
            sleep(2)
            GATEOPEN = True

        if GATEOPEN:
            cyprus.set_servo_position(2, 0.25)  # close gate
            GATEOPEN = False

    def toggleStaircase(self):
        global STAIRCASEDONE
        # if OFF:
        cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        sleep(7.5)

        cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)

        # OFF = False
        print("Staircase running")
        STAIRCASEDONE = True
        # if RAMPONTOP:
        # ramp.goHome()
        # else:
        # OFF = True

    def toggleRamp(self):
        global RAMPONTOP
        print("Ramp Prepared")
        while True:
            if not (cyprus.read_gpio()) & 0b0010:
                sleep(DEBOUNCE)
                if not (cyprus.read_gpio()) & 0b0010:
                    ramp.start_relative_move(28.2)
                    sleep(11)
                    RAMPONTOP = True

            if RAMPONTOP:
                ramp.go_until_press(0, 50000)
                print("going home")
                return
                # RAMPONTOP = False

            # if (cyprus.read_gpio()) & 0b0001:
            # sleep(DEBOUNCE)
            # if not ((cyprus.read_gpio()) & 0b0001):
            # ramp.goHome()

        # ramp length is 28.2 (slightly less than 28.5)

    def auto(self):
        print("Run through one cycle of the perpetual motion machine")
        x = 1
        # while x < 5:
        # self.toggleRamp()
        # self.toggleStaircase()
         # self.toggleGate()
        # x = x+1
        while True:
            self.toggleRamp()
            self.toggleStaircase()
            self.toggleGate()

    def setRampSpeed(self, speed):
        print("Set the ramp speed and update slider text")

        ramp.set_speed(1)

    def setStaircaseSpeed(self, speed):

        print("Set the staircase speed and update slider text")

    def initialize(self):
        global RAMPONTOP
        cyprus.initialize()  # stop staircase
        cyprus.setup_servo(2)  # setup gate servo
        cyprus.setup_servo(1)  # setup staircase servo
        cyprus.set_servo_position(2, 0)  # close gate
        ramp.set_speed(3)
        ramp.free_all()

        ramp.go_until_press(0, 50000)
        ramp.set_as_home()
        RAMPONTOP = False
        # ramp.go_to_position(0)
        # ramp.set_as_home()

        print("Close gate, stop staircase and home ramp here")

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        print("Exit")
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()
