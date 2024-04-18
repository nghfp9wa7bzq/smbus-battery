#!/usr/bin/python

"""
    Read out SMBus connected smart battery data.
    Copyright (C) 2024  nghfp9wa7bzq@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from smbus2 import SMBus

# Based on the Smart Battery Data Specification:
# http://sbs-forum.org/specs/sbdat110.pdf
# Need to connect GND, SDA, SCL, SP (System present), V+ pins of the battery.
# V+ is needed if the battery is fully discharged, to power the battery controller.

I2C_BUS = 1
BATT_ADDR = 0x0b


# These functions format the return data into strings.
def make_temp(temp):
    return "{:.2f}".format(temp / 10 - 273)


def div_1000(num):
    return str(num / 1000)


def bit_list_to_int(bit_list):
    ret = 0
    for bit in bit_list:
        ret = ret * 2 + bit
    return ret


def make_date(date_int):
    bits = [1 if digit == '1' else 0 for digit in bin(date_int)[2:]]
    ret = str(1980 + bit_list_to_int(bits[:-9])) + '.'  # year
    ret += str(bit_list_to_int(bits[-9:-5])) + '.'  # month
    ret += str(bit_list_to_int(bits[-5:])) + '.'  # day
    return ret


# Limit the number of characters for string data readout.
def check_number(num):
    if isinstance(num, int) and 0 < num < 32:
        return True
    return False


# Turn an array of ints into a string.
# The first int is the length of the string, so it is ignored.
def make_str(int_array):
    ret = ""
    for c in int_array[1:]:
        ret += chr(c)
    return ret


# print_callback is a function that converts the return value to a string.
# See above.
def call_bus_fn(fn_name, *args, print_callback=None):
    with SMBus(I2C_BUS) as bus:
        if not hasattr(bus, fn_name):
            print("No such bus function!")
            return

        try:
            fn = getattr(bus, fn_name)
            ret = fn(BATT_ADDR, *args)
            if print_callback is not None:
                ret = print_callback(ret)
                # This check prevents printing 'None' when using the make_read_block_cb function.
                if ret is not None:
                    print(ret)
            else:
                print(ret)
        except OSError:
            print("ERROR")


# This is a decorator / wrapper function, which allows reading the length byte for string data
# and then using it to get that data.
def make_read_block_cb(block_addr):
    def inner(bytes_to_read):
        call_bus_fn("read_i2c_block_data",
                    block_addr,
                    bytes_to_read + 1,
                    print_callback=make_str)

    return inner


# Using the original library function:
# with SMBus(I2C_BUS) as bus:
#    b = bus.read_word_data(BATT_ADDR, 0x00)
#    print(b)
# Using my encapsulation:
print("manufacturer access word: ", end="")
call_bus_fn("read_word_data", 0x00)

# Init charging on a Dell U4873 battery.
# This is normally not needed for other manufacturers.
# Using the original library function:
# with SMBus(I2C_BUS) as bus:
#    b = bus.write_word_data(BATT_ADDR, 0x00, 0x000a)
#    print(b)
# Using my encapsulation:
# print("Init charging: ", end="")
# call_bus_fn("write_word_data", 0x00, 0x000a)

print("battery temperature: ", end="")
call_bus_fn("read_word_data", 0x08, print_callback=make_temp)
print("voltage (V): ", end="")
call_bus_fn("read_word_data", 0x09, print_callback=div_1000)
print("design voltage (V): ", end="")
call_bus_fn("read_word_data", 0x19, print_callback=div_1000)
print("current flow (mA): ", end="")
call_bus_fn("read_word_data", 0x0a)
print("remaining capacity: ", end="")
call_bus_fn("read_word_data", 0x0f)
print("full charge capacity: ", end="")
call_bus_fn("read_word_data", 0x10)
print("design capacity: ", end="")
call_bus_fn("read_word_data", 0x18)
print("relative charge: ", end="")
call_bus_fn("read_word_data", 0x0d)
print("absolute charge: ", end="")
call_bus_fn("read_word_data", 0x0e)
print("battery status: ", end="")
call_bus_fn("read_word_data", 0x16, print_callback=hex)

print()
print("charging current: ", end="")
call_bus_fn("read_word_data", 0x14)
print("charging voltage: ", end="")
call_bus_fn("read_word_data", 0x15)

print()
print("cycle count: ", end="")
call_bus_fn("read_word_data", 0x17)
print("manufacture date: ", end="")
call_bus_fn("read_word_data", 0x1b, print_callback=make_date)
print("manufacturer name: ", end="")
call_bus_fn("read_byte_data", 0x20, print_callback=make_read_block_cb(0x20))
print("device name: ", end="")
call_bus_fn("read_byte_data", 0x21, print_callback=make_read_block_cb(0x21))
print("device chemistry: ", end="")
call_bus_fn("read_byte_data", 0x22, print_callback=make_read_block_cb(0x22))
