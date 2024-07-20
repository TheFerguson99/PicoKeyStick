from cll.NVMStorage import NVMStorage # type: ignore
import microcontroller
settings = NVMStorage(size=20)
repl_remove = settings.get_key("repl_remove")
DEBUG = settings.get_key("DEBUG")
if repl_remove and DEBUG == False:
    print("I dont think so.")
    microcontroller.reset()
