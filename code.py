import microcontroller
import board
import time
import getpass
import usb_hid
import supervisor
import digitalio
from adafruit_hid.keyboard import Keyboard
import keyboard_layout_win_gr # type: ignore
from keycode_win_gr import Keycode # type: ignore .Change to layout fiting 
import adafruit_ducky


from cll.pioasm_neopixel_bg import NeoPixelBackground # type: ignore

from cll.nvmstorage import NVMStorage # type: ignore

from cll.csv import CSVHandler # type: ignore

from cll.color import InColor

supervisor.runtime.autoreload = False

#region board Config
if board.board_id == "vcc_gnd_yd_rp2040":
    #Onboard Button
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
settings = NVMStorage(size=20)
DEBUG = settings.get_key("DEBUG")
show_usb = settings.get_key("show_usb")
boot_test = settings.get_key("boot_test")
ducky_mode = settings.get_key("ducky_mode")
auto_payload = settings.get_key("auto_payload")
NEOPIXEL = settings.get_key("NEOPIXEL")
wrong_index = 0
Handler = CSVHandler()
app = CSVHandler(file_path="/data/app.csv")

main_loop = True

#Check if it is posible to use neopixel_pin
if NEOPIXEL:
    try:
        pixels = NeoPixelBackground(neopixel_pin, 1)
        pixels.fill((0,0,0))
    except:
        settings.write_key("NEOPIXEL",False)
        NEOPIXEL = False

time.sleep(0.5)
keyboard = Keyboard(usb_hid.devices)
layout = keyboard_layout_win_gr.KeyboardLayout(keyboard)
time.sleep(0.5)

master_key = app.get_value_by_name("materpasword")

def Ducky():
    pass

def Options():
    global settings
    options_items = settings.indexes
    print("Enter setting to change.\n")
    for xkey in options_items.keys():
        yvalue = settings.get_key(xkey)
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
                settings.write_key(option_key,True)
                print("Wrote :" + option_key + "=" + str(True) + ".\n")
                options_loop = True
                print("Value Edited.\n")
            elif opt_nw.lower()  in ['false', '0', 'no', 'n']:
                settings.write_key(option_key,False)
                print("Wrote :" + option_key + "=" + str(False) + ".\n")
                options_loop = True
                print("Value Edited.\n")

def Print():
    global Handler
    try:
        for x in Handler.read_from_csv().keys():
            print("Key:[" + x + "]")
    except:
        print("Failed to print Keys")

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

def Add():
    global app
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
            Delay = int(app.get_value_by_name("delay"))
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

def Masterkey():
    global app
    print("Please enter current Masterkey to confirm")
    master_key_reply = getpass.getpass(InColor("console:","BOLD","GREEN"))
    if master_key_reply == master_key:
        print("Please enter new Masterkey.")
        master_key_new = getpass.getpass(InColor("console:","BOLD","GREEN"))
        print(f'Is {master_key_new} corect? y/n?')
        master_key_finale = input(InColor("console:","BOLD","GREEN"))
        if master_key_finale.lower() in ['true', '1', 'yes', 'y']:
            app.update_value("materpasword",master_key_new)

def Restart():
    microcontroller.reset()

def Inner_loop():
    global main_loop
    global Handler
    secound_loop = True
    while secound_loop:
        print("Commands are [options][print][add][update][remove][key][masterkey][return][restart]:\n")
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
        elif name.lower() == "options":
            Options()
        elif name.lower() == "print":
            Print()
        elif name.lower() == "masterkey":
            Masterkey()
        elif name.lower() == "restart":
            Restart()
        elif name in Handler.read_from_csv().keys():
            Key(name)
        else:
            print(f'Dont know {name}')

def Main():
    global main_loop
    global wrong_index
    global pixels
    global NEOPIXEL
    global DEBUG
    global settings

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
                print("\nBoard:" + InColor(board.board_id,"YELLOW")+"\n")
                for option_key in settings.indexes.keys():
                    if settings.get_key(option_key):
                        print(InColor(option_key,"BLUE") + ":" + InColor(str(settings.get_key(option_key)),"GREEN"))
                    else:
                        print(InColor(option_key,"BLUE") + ":" + InColor(str(settings.get_key(option_key)),"RED"))
            else:
                if NEOPIXEL == True:
                    pixels.fill((0,0,40))

            Inner_loop()
        wrong_index = wrong_index + 1
Main()
