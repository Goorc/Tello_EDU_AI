from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()
print("Battery Level:", me.get_battery(),"%")
me.takeoff()
me.move_back(20)
me.land()