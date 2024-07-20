import microcontroller

class NVMStorage:
    def __init__(self, size: int):
        if size > len(microcontroller.nvm):
            raise ValueError("Specified size exceeds NVM storage size.")
        self.size = size
        self.nvm = microcontroller.nvm

    def _bool_to_byte(self, value: bool) -> bytes:
        return b'\x01' if value else b'\x00'

    def _byte_to_bool(self, byte: bytes) -> bool:
        return byte == b'\x01'

    def write(self, index: int, value: bool):
        if index >= self.size:
            raise IndexError("Index out of range.")
        # Read all current values from NVM
        current_data = bytearray(self.nvm[:self.size])
        # Update the specific value
        current_data[index] = self._bool_to_byte(value)[0]
        # Write all bytes back to NVM
        self.nvm[:self.size] = current_data

    def read(self, index: int) -> bool:
        if index >= self.size:
            raise IndexError("Index out of range.")
        return self._byte_to_bool(bytes([self.nvm[index]]))

    def read_all(self) -> list:
        return [self._byte_to_bool(bytes([self.nvm[i]])) for i in range(self.size)]
    
    indexes = {"DEBUG":0,"show_usb":1,"cdc_usb":2,"boot_test":3,"ducky_mode":4,"auto_payload":5,"PICOW":6,"NEOPIXEL":7,"DHCP":8,"AP_MODE":9,"boot_cdc_lastrun":10}

    def get_key(self, key : str):
        if key not in self.indexes.keys():
            raise Exception("Option key not valid.")
        else:
            index = self.indexes[key]
            return self.read(index)

    def write_key(self, key : str, value : bool):
        if key not in self.indexes.keys():
            raise Exception("Option key not valid.")
        else:
            index = self.indexes[key]
            self.write(index,value)

# Example usage
#storage = NVMStorage(size=10)

# Writing boolean values to NVM


# Reading boolean values from NVM
#print("Value at index 0:", storage.read(0))  # Output: True
#print("Value at index 0:", str(storage.get_key("DEBUG")))  # Output: True
#print("Value at index 1:", str(storage.get_key("show_usb")))  # Output: False
#print("Value at index 1:", storage.read(1))  # Output: False
#print("Value at index 2:", storage.read(2))  # Output: True
#print("Value at index 2:", str(storage.get_key("cdc_usb")))  # Output: True
#
## Reading all boolean values from NVM
#print("All values in NVM:", storage.read_all())
