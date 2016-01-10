import sys
import os.path
import xbmc

class AmlogicDoze:
    def __init__(self):
        self.__isInDozeState = False

        self.__powerLedPath   = "/sys/class/leds/wetek:blue:powerled/brightness"
        self.__powerStatePath = "/sys/power/state"
        self.__wakeLock       = "locked_by_Amlogic_doze"
	self.__wakeLockPath   = "/sys/power/wake_lock"
	self.__wakeUnLockPath = "/sys/power/wake_unlock"

    def __writeToWakeLock(self, data):
        doze = open(self.__wakeLockPath, "w")
        doze.write(data)
        doze.close()

    def __writeToWakeUnlock(self, data):
        doze = open(self.__wakeUnlockPath, "w")    
        doze.write(data)                        
        doze.close()                            

    def isInDozeState(self):
        return self.__isInDozeState

    def powerLedOn(self):
        powerLed = open(self.__powerLedPath, "w")
        powerLed.write("1")
        powerLed.close()

    def powerLedOff(self):
        powerLed = open(self.__powerLedPath, "w")
        powerLed.write("0")
        powerLed.close()

    def hasDoze(self):
        return os.path.isfile(self.__wakeLockPath)

    def setWakeLock(self):
        xbmc.log('AmlogicDoze: setting wake lock') 
        self.__writeToWakeLock(self.__wakeLock);

    def releaseWakeLock(self):
        xbmc.log('AmlogicDoze: release wake lock')
        self.__writeToWakeUnlock(self.__wakeLock);  

    def enterDoze(self):
        xbmc.log('AmlogicDoze: enterDoze') 
        self.powerLedOff()
        self.__isInDozeState = True

    def wakeFromDoze(self):
        xbmc.log('AmlogicDoze: wakeFromDoze') 
        self.powerLedOn()
        powerState = open(self.__powerStatePath, "w")                             
        powerState.write("on")                                                   
        powerState.close()             
        self.__isInDozeState = False

class XBMCMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.__doze = kwargs['doze'];

    def onNotification(self, sender, method, data):
        xbmc.log('AmlogicDoze: got notification %s' % method) 

        if (method == 'Player.OnPlay'):
            if self.__doze.isInDozeState():
                self.__doze.wakeFromDoze()

        elif (method == 'System.OnWake'):
            if self.__doze.isInDozeState():
                self.__doze.wakeFromDoze()
            else:
                self.__doze.enterDoze()

if __name__ == '__main__':
    xbmc.log('AmlogicDoze: started') 
    AmlogicDoze = AmlogicDoze()
    if AmlogicDoze.hasDoze():
        AmlogicDoze.setWakeLock()
        monitor = XBMCMonitor(doze=AmlogicDoze)

        while not xbmc.abortRequested:
            xbmc.sleep(500)

        AmlogicDoze.releaseWakeLock()
    else:
	xbmc.log('AmlogicDoze: doze not found') 
