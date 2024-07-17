from cll.NVMStorage import NVMStorage # type: ignore
import microcontroller
settings = NVMStorage(size=20)
DEBUG = settings.get_key("DEBUG")
if not DEBUG:
    microcontroller.reset()
