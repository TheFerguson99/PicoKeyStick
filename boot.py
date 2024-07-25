import os 
from cll.csv import CSVHandler
import storage

from cll.NVMStorage import NVMStorage # type: ignore

settings = CSVHandler(file_path="/data/settings.csv")
config = NVMStorage(size=20)
first_run = config.get_key("init")
#Check if first run
if first_run == False:
    config.write_key("DEBUG",True)
    config.write_key("show_usb",True)
    config.write_key("init",True)
DEBUG = config.get_key("DEBUG")
show_usb = config.get_key("show_usb")
boot_test = config.get_key("boot_test")
#TODO: Remove REPL. done bye restart when accesing. Find better way???

if boot_test == True:
    pass

storage.remount("/", readonly=False)
try:
    files = os.listdir("/temp/")
    for file in files:
        try:
            os.remove("/temp/" + file)
        except:
            if DEBUG:
                print("Failed to delete file :" + file)
except OSError as e:
    print("Error:", e)
m = storage.getmount("/")
m.label = settings.get_value_by_name("drivename")
storage.remount("/", readonly=DEBUG)
if show_usb == False:
    storage.disable_usb_drive()

