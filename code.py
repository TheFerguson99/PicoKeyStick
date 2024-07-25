import microcontroller
import board
import os
import time
import getpass
import usb_hid
import supervisor
import digitalio
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
import keyboard_layout_win_gr # type: ignore
from keycode_win_gr import Keycode # type: ignore .Change to layout fiting 
import adafruit_ducky
#import circuitpython_base64 as base64#type: ignore
from cll.pioasm_neopixel_bg import NeoPixelBackground # type: ignore

from cll.nvmstorage import NVMStorage # type: ignore

from cll.csv import CSVHandler# type: ignore

from cll.color import InColor

from cll.settings import settings as Setting_type_name # type:ignore

supervisor.runtime.autoreload = False

#region board Config
if board.board_id == "vcc_gnd_yd_rp2040":
    #Onboard Button ore any other switch mechanism to unlock from auto_payload and jiggle
    button  = digitalio.DigitalInOut(board.BUTTON)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    button_pressed = not button.value
    #onboard LED
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    led.value = True
    #Neopixel pin
    neopixel_pin = board.NEOPIXEL
else:
    #Here we can implement the same for other Boards
    pass

#region settings decleration
config = NVMStorage(size=20)
DEBUG = config.get_key("DEBUG")
show_usb = config.get_key("show_usb")
boot_test = config.get_key("boot_test")
single_mode = config.get_key("single_mode")
auto_payload = config.get_key("auto_payload") #press the defined button while plugging in so auto_payload gets deacktivated
NEOPIXEL = config.get_key("NEOPIXEL")

Handler = CSVHandler()
settings = CSVHandler(file_path="/data/settings.csv")

main_loop = True
wrong_index = 0

# Define the area boundaries
AREA_WIDTH = 100
AREA_HEIGHT = 100

# Define movement step and delay
STEP = 1
DELAY = 0.1

#Check if it is posible to use neopixel_pin
if NEOPIXEL:
    try:
        pixels = NeoPixelBackground(neopixel_pin, 1)
        pixels.fill((0,0,0))
    except:
        config.write_key("NEOPIXEL",False)
        NEOPIXEL = False

time.sleep(0.5)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
layout = keyboard_layout_win_gr.KeyboardLayout(keyboard)
time.sleep(0.5)

master_key = settings.get_value_by_name("materpasword")
#region auto_payload
if single_mode or auto_payload:
    try:
        filename = settings.get_value_by_name("auto_payload_filename")
        if single_mode:
            duck = adafruit_ducky.Ducky("/payload/" + filename, keyboard, layout)
            result = True
            while result is not False:
                result = duck.loop()
                main_loop = True
            config.write_key("auto_payload",False)
            time.sleep(0.5)
            if NEOPIXEL == True:
                pixels.fill((200,200,200))
            time.sleep(0.5)
            if NEOPIXEL == True:
                pixels.fill((0,0,0))
            time.sleep(0.5)
            if NEOPIXEL == True:
                pixels.fill((200,200,200))
            time.sleep(1)
            config.write_key("single_mode",False)
        elif auto_payload:
            if button_pressed:
                config.write_key("auto_payload",False)
            else:
                duck = adafruit_ducky.Ducky("/payload/" + filename, keyboard, layout)
                result = True
                while result is not False:
                    result = duck.loop()
                while True:
                    time.sleep(1)
    except:
        config.write_key("single_mode",False)
        config.write_key("auto_payload",False)
        print("Failed to execute Ducky script.")

def list_files(directory):
    try:
        files = os.listdir(directory)
        for file in files:
            print(file)
    except OSError as e:
        print("Error:", e)
#region ducky
def Ducky():
    global NEOPIXEL
    global pixels
    global keyboard
    global layout
    print(InColor("[DUCKY]","BOLD","RED"))
    while True:
        print("Commands are [load][exit]")

        ducky_input = input(InColor("console:","BOLD","GREEN"))

        if ducky_input.lower() == "load":
            try:
                files = os.listdir("/payload/")
                for file in files:
                    print(InColor("[File]","BOLD","GREEN") + file)
            except OSError as e:
                print("Error:", e)
            print("Enter Filename.")
            filename = input(InColor("console:","BOLD","GREEN"))
            try:
                os.stat("/payload/"+filename)#we have a valid filename if this dosnt raise exception
                print("Confirm loading file y/n " + filename)
                ducky_confirm = input(InColor("console:","BOLD","GREEN"))
                if ducky_confirm.lower() in ['true', '1', 'yes', 'y']:
                    duck = adafruit_ducky.Ducky(("/payload/"+filename), keyboard, layout)
                    result = True
                    while result is not False:
                        result = duck.loop()
                    config.write_key("auto_payload",False)
                    time.sleep(0.5)
                    if NEOPIXEL == True:
                        pixels.fill((100,100,100))
                    time.sleep(0.5)
                    if NEOPIXEL == True:
                        pixels.fill((0,0,0))
                    time.sleep(0.5)
                    if NEOPIXEL == True:
                        pixels.fill((100,100,100))
                    time.sleep(1)
                    if DEBUG:
                        if NEOPIXEL == True:
                            pixels.fill((0,40,0))
                    else:
                        if NEOPIXEL == True:
                            pixels.fill((0,0,40))
                    return
                elif ducky_confirm.lower() in ['false', '0', 'no', 'n']:
                    pass
            except OSError:
                print("File not found.")
        elif ducky_input.lower() == "exit":
            return
#region Config
def Config():
    global config
    options_items = config.indexes
    print("Enter setting to change.\n")
    for xkey in options_items.keys():
        yvalue = config.get_key(xkey)
        if yvalue:
            print("Name:" + InColor(str(xkey),"BLUE") + ": Value:" + InColor(str(yvalue),"GREEN") + ";\n")
        else:
            print("Name:" + InColor(str(xkey),"BLUE") + ": Value:" + InColor(str(yvalue),"RED") + ";\n")
    option_key = input(InColor("console:","BOLD","GREEN"))
    #the key we entered is present in the dictonary/ we only use boolen value types
    if option_key in options_items:
        options_loop = False
        while not options_loop:
            print("Enter new value")
            opt_nw = input(InColor("console:","BOLD","GREEN"))
            if opt_nw.lower() in ['true', '1', 'yes', 'y']:
                config.write_key(option_key,True)
                print("Wrote :" + option_key + "=" + str(True) + ".\n")
                options_loop = True
                print("Value Edited.\n")
            elif opt_nw.lower()  in ['false', '0', 'no', 'n']:
                config.write_key(option_key,False)
                print("Wrote :" + option_key + "=" + str(False) + ".\n")
                options_loop = True
                print("Value Edited.\n")
#region Print
def Print():
    global Handler
    try:
        for x in Handler.read_from_csv().keys():
            print("Key:[" + x + "]")
    except:
        print("Failed to print Keys")
#region Remove
def Remove():
    global Handler
    print("Enter name of key to be removed.")
    key_name = input(InColor("console:","BOLD","GREEN"))
    print(f"Name of key is {key_name}")
    print("Confirm y/n")
    add_confirm = input(InColor("console:","BOLD","GREEN"))
    if add_confirm.lower()  in ['true', '1', 'yes', 'y']:
        result = Handler.get_value_by_name(key_name)
        if result == None:
            print("No key named " + key_name)
        else:
            Handler.remove_entry(key_name)
    else:
        pass
#region Update
def Update():
    global Handler
    print("Enter name of key.")
    key_name = input(InColor("console:","BOLD","GREEN"))
    print(f"Name of key is {key_name}")
    print("Confirm y/n")
    add_confirm = input(InColor("console:","BOLD","GREEN"))
    if add_confirm.lower()  in ['true', '1', 'yes', 'y']:
        result = Handler.get_value_by_name(key_name)
        if result == None:
            print("No key named " + key_name)
        else:
            print("Enter new value")
            key_input = input(InColor("console:","BOLD","GREEN"))
            print(f"Is < {key_input} > corect?")
            print("Confirm y/n")
            key_finale = input(InColor("console:","BOLD","GREEN"))
            if key_finale.lower()  in ['true', '1', 'yes', 'y']:
                Handler.update_value(key_name,key_input)
            elif key_finale.lower() in ['false', '0', 'no', 'n']:
                pass
#region Add
def Add():
    global settings
    global Handler
    print("Enter name of new key.")
    key_name = input(InColor("console:","BOLD","GREEN"))
    print(f"Name of key is {key_name}")
    print("Confirm y/n")
    add_confirm = input(InColor("console:","BOLD","GREEN"))
    if add_confirm.lower()  in ['true', '1', 'yes', 'y']:
        print("Enter key")
        key_input = input(InColor("console:","BOLD","GREEN"))
        print(f"Is < {key_input} > corect?")
        print("Confirm y/n")
        key_finale = input(InColor("console:","BOLD","GREEN"))
        if key_finale.lower() in ['true', '1', 'yes', 'y']:
            Handler.write_to_csv({key_name:key_input})
        elif key_finale.lower() in ['false', '0', 'no', 'n']:
            pass
    elif add_confirm.lower() in ['false', '0', 'no', 'n']:
        pass
#region Key
def Key(name):
    global Handler
    global pixels
    key_keys = Handler.get_value_by_name(name)
    keyloop = True
    print("Result:" + key_keys)
    while keyloop:
        print("Use? y/n?")
        confirm = input(InColor("console:","BOLD","GREEN"))
        if confirm.lower() in ['true', '1', 'yes', 'y']:
            Delay = int(settings.get_value_by_name("delay"))
            while Delay != 0:
                time.sleep(0.5)
                if NEOPIXEL == True:
                    pixels.fill((50,0,50))
                time.sleep(0.5)
                if NEOPIXEL == True:
                    pixels.fill((0,0,0))
                print(str(Delay) + " seconds left.")
                Delay = Delay-1
            time.sleep(0.2)
            for char in key_keys:
                layout.write(char)
                time.sleep(0.1)    
            time.sleep(1)
            keyloop = False
        elif confirm.lower() in ['false', '0', 'no', 'n']:
            keyloop = False
#region Masterkey
def Masterkey():
    global settings
    print("Please enter current Masterkey to confirm")
    master_key_reply = getpass.getpass(InColor("console:","BOLD","GREEN"))
    if master_key_reply == master_key:
        print("Please enter new Masterkey.")
        master_key_new = getpass.getpass(InColor("console:","BOLD","GREEN"))
        print(f'Is {master_key_new} corect? y/n?')
        master_key_finale = input(InColor("console:","BOLD","GREEN"))
        if master_key_finale.lower() in ['true', '1', 'yes', 'y']:
            settings.update_value("materpasword",master_key_new)

def Settings():
    global settings
    for key, value in settings.read_from_csv().items():
        print("Name:" + InColor(key,"BLUE","BOLD") + "; Value:" + InColor(value,"GREEN","BOLD"))
    print("Enter name to edit.")
    setting_name = input(InColor("console:","BOLD","GREEN"))
    if setting_name in settings.read_from_csv().keys():
        setting_type = Setting_type_name[setting_name]
        print("Enter new Value")
        newvalue = input(InColor("console:","BOLD","GREEN"))
        if setting_type == 'int':
            newvalue_str = str(int(newvalue))
        elif setting_type == 'float':
            newvalue_str = str(float(newvalue))
        elif setting_type == 'str':
            newvalue_str = str(newvalue)
        elif setting_type == 'bool':
            if newvalue.lower() in ['true', '1', 'yes', 'y']:
                newvalue_str = str(True)
            elif newvalue.lower() in ['false', '0', 'no', 'n']:
                newvalue_str = str(False)
            else:
                raise ValueError("Invalid boolean value")
        else:
            raise ValueError(f"Unsupported data type: {setting_type}")
        settings.update_value(setting_name,newvalue_str)
    else:
        print(f"Didnt find [{setting_name}]")
def Restart():
    microcontroller.reset()
#region Jiggler
def Jiggler():
    print("Press defined button to release jiggler")
    global button
    global button_pressed
    x, y = 0, 0
    dx, dy = STEP, STEP
    while True:
        try:
            if NEOPIXEL:
                pixels.fill((0,x,y))
            mouse.move(x=dx, y=dy)
            # Update the cursor position
            x += dx
            y += dy

            # Change direction if boundaries are hit
            if x >= AREA_WIDTH or x <= 0:
                dx = -dx
            if y >= AREA_HEIGHT or y <= 0:
                dy = -dy
            time.sleep(DELAY)
            button_pressed = not button.value
            if button_pressed:
                if NEOPIXEL:
                    pixels.fill((0,0,0))
                return
        except:
            print("Failed Jiggler")
            return
#region Inner_loop
def Inner_loop():
    global main_loop
    global Handler
    secound_loop = True
    while secound_loop:
        print("\nCommands are [print][key][add][update][remove][masterkey][ducky][jiggler][config][settings][return][restart]:\n")
        name = input(InColor("console:","BOLD","GREEN"))
        #We exit the Programm.
        if name.lower() == "return":
            secound_loop = False
        elif name.lower() == "add":
            Add()
        elif name.lower() == "update":
            Update()
        elif name.lower() == "remove":
            Remove()
        elif name.lower() == "config":
            Config()
        elif name.lower() == "print":
            Print()
        elif name.lower() == "masterkey":
            Masterkey()
        elif name.lower() == "restart":
            Restart()
        elif name.lower() == "ducky":
            Ducky()
        elif name.lower() == "jiggler":
            Jiggler()
        elif name.lower() == "settings":
            Settings()
        elif name in Handler.read_from_csv().keys():
            Key(name)
        else:
            print(f'Dont know {name}')
#region Main
def Main():
    global main_loop
    global wrong_index
    global pixels
    global NEOPIXEL
    global DEBUG
    global config

    while main_loop:
        time.sleep(2 * wrong_index)
        pwd = getpass.getpass(InColor("console:","BOLD","GREEN"))
        time.sleep(2 * wrong_index)
        if pwd == "exit":
            main_loop = False
        if pwd == master_key:
            if DEBUG:
                if NEOPIXEL == True:
                    pixels.fill((0,40,0))
                print("\nBoard:" + InColor(board.board_id,"YELLOW"))
                print(InColor("Board config","UNDERLINE","MAGENTA","BOLD"))
                for option_key in config.indexes.keys():
                    if config.get_key(option_key):
                        print(InColor(option_key,"BLUE") + ":" + InColor(str(config.get_key(option_key)),"GREEN"))
                    else:
                        print(InColor(option_key,"BLUE") + ":" + InColor(str(config.get_key(option_key)),"RED"))
                print(InColor("Board settings","UNDERLINE","MAGENTA","BOLD"))
                for key, value in settings.read_from_csv().items():
                    print("Name:" + InColor(key,"BLUE","BOLD") + "; Value:" + InColor(value,"GREEN","BOLD"))
            else:
                if NEOPIXEL == True:
                    pixels.fill((0,0,40))

            Inner_loop()
        wrong_index = wrong_index + 1

Main()
