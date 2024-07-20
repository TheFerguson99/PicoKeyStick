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

supervisor.runtime.autoreload = False

from cll.pioasm_neopixel_bg import NeoPixelBackground # type: ignore

from cll.nvmstorage import NVMStorage # type: ignore

from cll.csv import CSVHandler # type: ignore

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

settings = NVMStorage(size=20)

#region settings decleration
DEBUG = settings.get_key("DEBUG")
show_usb = settings.get_key("show_usb")
boot_test = settings.get_key("boot_test")
ducky_mode = settings.get_key("ducky_mode")
auto_payload = settings.get_key("auto_payload")
NEOPIXEL = settings.get_key("NEOPIXEL")

#how many times the password has been entered incorect.
wrong_index = 0

main_loop = False

Handler = CSVHandler()
app = CSVHandler(file_path="/data/app.csv")

if NEOPIXEL:#Check if it is posible to use neopixel_pin
    try:
        pixels = NeoPixelBackground(neopixel_pin, 1)
        pixels.fill((0,0,0))
    except:
        settings.write_key("NEOPIXEL",False)
        NEOPIXEL = False

#region HID Init
time.sleep(0.5)
keyboard = Keyboard(usb_hid.devices)
layout = keyboard_layout_win_gr.KeyboardLayout(keyboard)
time.sleep(2)

#region Ducky
try:
    if ducky_mode and auto_payload:
        duck = adafruit_ducky.Ducky("/payload/duckyscript.txt", keyboard, layout)
        result = True
        while result is not False:
            result = duck.loop()
            main_loop = True
        settings.write_key("auto_payload",False)
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
except:
    settings.write_key("ducky_mode",False)
    settings.write_key("auto_payload",False)
    print("Failed to execute Ducky script.")
#endregion
#region Main Loop
master_key = app.get_value_by_name("materpasword")
while not main_loop:
    time.sleep(2 * wrong_index)
    pwd = getpass.getpass("console:")
    time.sleep(2 * wrong_index)
    if pwd == "exit":
        main_loop = True
        #region Second Loop
    if pwd == master_key:
        if DEBUG:
            if NEOPIXEL == True:
                pixels.fill((0,40,0))
            print("\nBoard:" + board.board_id+"\n")
            for option_key in settings.indexes.keys():
                print(option_key + ":", str(settings.get_key(option_key)))
        else:
            if NEOPIXEL == True:
                pixels.fill((0,0,40))
        #boot_test is for stuff to run once before the second loop
        if settings.get_key("boot_test"):
            settings.write_key("boot_test",False)
        print("\n\n[Main]\n")
        secound_loop = False
        while not secound_loop:
            print("Commands are [options][print][add][update][remove][key][return][restart]:\n")
            name = input("console:")
            #We exit the Programm.
            if name == "return" or name == "Return":
                secound_loop = True
            #region Add key
            elif name.lower() == "add":
                print("Enter name of key.")
                key_name = input("console:")
                print(f"Name of key is {key_name}")
                print("Confirm y/n")
                add_confirm = input("console:")
                if add_confirm.lower() == "y" or add_confirm.lower() == "yes":
                    print("Enter key")
                    key_input = input("console:")
                    print(f"Is < {key_input} > corect?")
                    print("Confirm y/n")
                    key_finale = input("console:")
                    if key_finale.lower() == "y" or key_finale.lower() == "yes":
                        Handler.write_to_csv({key_name:key_input})
                    elif key_finale.lower() == "n" or key_finale.lower() == "no":
                        pass
                elif add_confirm.lower() == "n" or add_confirm.lower() == "no":
                    pass
            elif name.lower() == "remove":
                print("Enter name of key to be removed.")
                key_name = input("console:")
                print(f"Name of key is {key_name}")
                print("Confirm y/n")
                add_confirm = input("console:")
                if add_confirm.lower() == "y" or add_confirm.lower() == "yes":
                    result = Handler.get_value_by_name(key_name)
                    if result == None:
                        print("No key named " + key_name)
                    else:
                        Handler.remove_entry(key_name)
                else:
                    pass
            elif name.lower() == "update":
                print("Enter name of key.")
                key_name = input("console:")
                print(f"Name of key is {key_name}")
                print("Confirm y/n")
                add_confirm = input("console:")
                if add_confirm.lower() == "y" or add_confirm.lower() == "yes":
                    result = Handler.get_value_by_name(key_name)
                    if result == None:
                        print("No key named " + key_name)
                    else:
                        print("Enter new value")
                        key_input = input("console:")
                        print(f"Is < {key_input} > corect?")
                        print("Confirm y/n")
                        key_finale = input("console:")
                        if key_finale.lower() == "y" or key_finale.lower() == "yes":
                            Handler.update_value(key_name,key_input)
                        elif key_finale.lower() == "n" or key_finale.lower() == "no":
                            pass
            #Print setting 
            elif name == "print" or name == "Print":
                try:
                    for x in Handler.read_from_csv().keys():
                        print("Key:[" + x + "]")
                except:
                    print("Failed to print Keys")
            #region Options edit
            elif name == "options" or name == "Options":
                options_items = settings.indexes
                print("Enter setting to change.\n")
                for xkey in options_items.keys():
                    yvalue = settings.get_key(xkey)
                    print("Name:"+str(xkey)+"; Value:"+str(yvalue)+";\n")
                option_key = input("console:")
                #the key we entered is present in the dictonary/ we only use boolen value types
                if option_key in options_items:
                    options_loop = False
                    while not options_loop:
                        print("Enter new value")
                        opt_nw = input("console:")
                        #We have a valid option key replay from user input and set value acordingly
                        if opt_nw == "true" or opt_nw == "True":
                            settings.write_key(option_key,True)
                            print("Wrote :" + option_key + "=" + str(True) + ".\n")
                            options_loop = True
                            print("Value Edited.\n")
                        elif opt_nw == "False"or opt_nw == "false":
                            settings.write_key(option_key,False)
                            print("Wrote :" + option_key + "=" + str(False) + ".\n")
                            options_loop = True
                            print("Value Edited.\n")
                    pass
                pass
            #endregion
            elif name == "restart" or name == "Restart":
                microcontroller.reset()
            #region Keys and non valid Input.
            else:
                result = Handler.get_value_by_name(name)
                if result == None:
                    print("Wrong Command.")
                else: #Here we have a valid key selected
                    print("Result:" + result)
                    end_loop = False
                    while not end_loop:
                        confirm = input("Use? y/n?:")
                        if confirm == "y" or confirm == "Y" or confirm == "n" or confirm == "N":
                            #We have valid input entered
                            if confirm == "N" or confirm == "n":
                                end_loop = True
                            else:
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
                                #region HID Output 
                                for char in result:
                                    layout.write(char)
                                    time.sleep(0.1)
                                time.sleep(1)
                                #endregion
                                #Exit all loops
                                main_loop = True
                                secound_loop = True
                                end_loop = True
            #endregion
            #endregion
    wrong_index= wrong_index + 1
#endregion
#We say Bye
print("GoodBye!")
 # type: ignore
