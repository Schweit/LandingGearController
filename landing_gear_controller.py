import board
import time
import random
from digitalio import DigitalInOut, Direction, Pull

class LandingGearSwitch:
    def __init__(self, gearUp, gearDown):
        self.GEAR_UP = gearUp
        self.GEAR_DOWN = gearDown
        self.LAST_LANDING_GEAR_POSITION = self.getLandingGearSwitchPosition()

    def getLandingGearSwitchPosition(self):
        if self.GEAR_UP.value:
            return 0
        if self.GEAR_DOWN.value:
            return 1

    def checkLandingGearChange(self):
        currentLandingGearPosition = self.getLandingGearSwitchPosition()
        if self.LAST_LANDING_GEAR_POSITION != currentLandingGearPosition:
            time.sleep(0.4)
            currentLandingGearPosition = self.getLandingGearSwitchPosition()
            self.LAST_LANDING_GEAR_POSITION = currentLandingGearPosition
            return True


class ModeSwitch:
    def __init__(self, mode):
        self.MODE_SWITCH = mode
        self.MODE = 0
        self.MODE_TRANSITIONING = False

    def checkModeSwitchPressed(self):
        return self.MODE_SWITCH.value

    def switchModes(self, ledPanel, lastLandingGearPosition):
        if not self.MODE_TRANSITIONING:
            self.MODE_TRANSITIONING = True
            self.MODE = 1 if self.MODE == 0 else 0
            ledPanel.modeTransition(self.MODE, lastLandingGearPosition)
            self.MODE_TRANSITIONING = False
            
    def getCurrentMode(self):
        return self.MODE

    
class Led:
    def __init__(self, redLed, greenLed):
        self.RED = redLed
        self.GREEN = greenLed
        self.green()

    def off(self):
        self.GREEN.value = True
        self.RED.value = True

    def green(self):
        self.GREEN.value = True
        self.RED.value = False

    def red(self):
        self.GREEN.value = False
        self.RED.value = True


class LedPanel:
    def __init__(self, ledArray):
        self.LED_PANEL = ledArray
        self.TRANSITIONING = False

    def isTransitioning(self):
        return self.TRANSITIONING

    def _transitionLandingGear(self):
        self.TRANSITIONING = True

    def getTransitioning(self):
        return self.TRANSITIONING

    def _allGreen(self):
        for led in self.LED_PANEL:
            led.green()

    def _allRed(self):
        for led in self.LED_PANEL:
            led.red()

    def _allOff(self):
        for led in self.LED_PANEL:
            led.off()

    def _funTranstion(self):
        for led in self.LED_PANEL:
            time.sleep(random.random())
            led.red()
        time.sleep(random.randint(2, 4))
        for led in self.LED_PANEL:
            time.sleep(random.random())
            led.green()
        self.TRANSITIONING = False

    def _upTransition(self):
        time.sleep(0.4)
        self._allRed()
        self.TRANSITIONING = False

    def _downTransition(self):
        time.sleep(random.randint(2, 4))
        self._allGreen()
        self.TRANSITIONING = False

    def transition(self, mode, lastLandingGearPosition):
        self._transitionLandingGear()
        if mode == 0:
            if lastLandingGearPosition == 0:
                print("Up Transition")
                self._upTransition()
            if lastLandingGearPosition == 1:
                print("Down Transition")
                self._downTransition()
        if mode == 1:
            print("Fun Transition")
            self._funTranstion()

    def startUpSequence(self, mode, lastLandingGearPosition):
        counter = 0
        self._allOff()
        while counter < 5:
            for led in self.LED_PANEL:
                led.green()
                time.sleep(0.05)
            for led in self.LED_PANEL:
                led.red()
                time.sleep(0.05)
            counter += 1
        if lastLandingGearPosition == 0:
            self._allRed()
        if mode == 1 or lastLandingGearPosition == 1:
            self._allGreen()

    def modeTransition(self, mode, landingGearSwitchPosition):
        counter = 0
        self._allOff()
        while counter < 5:
            self._allOff()
            time.sleep(0.20)
            self._allGreen()
            time.sleep(0.20)
            counter += 1
        if mode == 0 and landingGearSwitchPosition == 0:
            self._allRed()
        if mode == 1 or (mode == 0 and landingGearSwitchPosition == 1):
            self._allGreen()

def setupCommonPin(commonPin):
    COMMON = DigitalInOut(getattr(board, "D" + str(commonPin)))
    COMMON.direction = Direction.OUTPUT
    COMMON.value = True

def setupDigitalPins(pinNum, isOutput = True, pull = Pull.UP):
    pin = DigitalInOut(getattr(board, "D" + str(pinNum)))
    if isOutput:
        pin.direction = Direction.OUTPUT
    else:
        pin.direction = Direction.INPUT
        pin.pull = pull
    return pin


setupCommonPin(6)
landingGearSwitch = LandingGearSwitch(setupDigitalPins(9, False), setupDigitalPins(10, False))
modeSwitch = ModeSwitch(setupDigitalPins(7, False, Pull.DOWN))
ledZero = Led(setupDigitalPins(0), setupDigitalPins(1))
ledOne = Led(setupDigitalPins(2), setupDigitalPins(3))
ledTwo = Led(setupDigitalPins(4), setupDigitalPins(5))
ledPanel = LedPanel([ledZero, ledOne, ledTwo])

print("STARTING")
ledPanel.startUpSequence(modeSwitch.MODE, landingGearSwitch.LAST_LANDING_GEAR_POSITION)

while True:
    if modeSwitch.checkModeSwitchPressed():
        modeSwitch.switchModes(ledPanel, landingGearSwitch.LAST_LANDING_GEAR_POSITION)
    if landingGearSwitch.checkLandingGearChange():
        print("Landing Gear Change")
        if not ledPanel.isTransitioning():
            ledPanel.transition(modeSwitch.MODE, landingGearSwitch.LAST_LANDING_GEAR_POSITION)
    time.sleep(0.1)

