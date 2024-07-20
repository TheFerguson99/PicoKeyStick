import os 
from cll.csv import CSVHandler
import storage

from cll.NVMStorage import NVMStorage # type: ignore


settings = NVMStorage(size=20)
first_run = settings.get_key("init")
#Check if first run
if first_run == False:
    settings.write_key("DEBUG",True)
    settings.write_key("show_usb",True)
    settings.write_key("init",True)
DEBUG = settings.get_key("DEBUG")
show_usb = settings.get_key("show_usb")
boot_test = settings.get_key("boot_test")
#TODO: Remove REPL. done bye restart when accesing. Find better way???

if boot_test == True:
    pass

storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = os.getenv("drive_name")
storage.remount("/", readonly=DEBUG)
if show_usb == False:
    storage.disable_usb_drive()

