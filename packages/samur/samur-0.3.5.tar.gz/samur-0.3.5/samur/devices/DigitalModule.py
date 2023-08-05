import smbus2

class DigitalModule:
    expander_type = 'MCP23017'
    CLEAR_ALL = 0x00    # Clear for OUTPUT
    SET_ALL = 0xFF      # Set for INPUT
    REGISTER_A = 0x00   # PORT A
    REGISTER_B = 0x01   # PORT B
    REGISTER_OUT = 0x12 # GPIO A
    REGISTER_IN = 0x13  # GPIO B
    REGISTER_PULLUP_A = 0x0C
    REGISTER_PULLUP_B = 0x0D

    def __init__(self, address):
        self.address = address
        self.bus = smbus2.SMBus(1)

        #Set PORTA as output
        self.bus.write_byte_data(self.address, self.REGISTER_A, self.CLEAR_ALL)

        #Set PORTB as input
        self.bus.write_byte_data(self.address, self.REGISTER_B, self.SET_ALL)
        self.bus.write_byte_data(self.address, self.REGISTER_PULLUP_B, 0xFF)

        self.inputs = [0] * 6

    def output(self, pin_number, value):
        outputs = self.bus.read_byte_data(self.address, self.REGISTER_OUT)
        if value:
            if not (outputs >> pin_number) & 1 :
                outputs += (1 << pin_number)
        else:
            if (outputs >> pin_number) & 1 :
                outputs -= (1 << pin_number)
        self.bus.write_byte_data(self.address, self.REGISTER_OUT, outputs)

    def read(self):
        value = self.bus.read_byte_data(self.address, self.REGISTER_IN)
        return value
