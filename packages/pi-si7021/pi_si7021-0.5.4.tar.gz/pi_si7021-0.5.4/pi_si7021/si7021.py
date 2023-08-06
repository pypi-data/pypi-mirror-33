#!/usr/bin/env python3

from time import sleep
import pigpio
import struct
import sys

class Si7021(object):
	__addr = 0x40
	__cmds = {
		"meas_rh_hold": [0xE5],
		"meas_rh_nohold": [0xF5],
		"meas_temp_hold": [0xE3],
		"meas_temp_nohold": [0xF3],
		"read_temp": [0xE0],
		"reset": [0xFE],
		"write_reg1": [0xE6],
		"read_reg1": [0xE7],
		"read_id1": [0xFA, 0x0F],
		"read_id2": [0xFC, 0xC9],
		"read_fw_ver": [0x84, 0xB8],
	}

	def __init__(self):
		self.pi = pigpio.pi()
		self.i2c = self.pi.i2c_open(1,self.__addr)

	def __str__(self):
		return(
			"Temperature: " + str(round(self.temperature, 2)) + u" \u00B0C\n"
			"Relative humidity: " + str(round(self.relative_humidity, 2)) + " %"
		)

	@property
	def temperature(self):
		self.pi.i2c_write_device(self.i2c, self.__cmds["meas_temp_nohold"])
		sleep(0.05)
		_, data = self.pi.i2c_read_device(self.i2c, 2)
		temp_code = struct.unpack(">H",data)
		return (175.72 * temp_code[0] / 65536 - 46.85)

	@property
	def relative_humidity(self):
		self.pi.i2c_write_device(self.i2c, self.__cmds["meas_rh_nohold"])
		sleep(0.05)
		_, data = self.pi.i2c_read_device(self.i2c, 2)
		rh_code = struct.unpack(">H",data)
		return (125*rh_code[0] / 65536 - 6)

	@property
	def heater(self):
		self.pi.i2c_write_device(self.i2c, self.__cmds["read_reg1"])
		_, data = self.pi.i2c_read_device(self.i2c, 1)
		reg = struct.unpack(">B",data)
		return bool(reg[0] & (1<<2))

	@heater.setter
	def heater(self, value):
		self.pi.i2c_write_device(self.i2c, self.__cmds["read_reg1"])
		_, data = self.pi.i2c_read_device(self.i2c, 1)
		reg = struct.unpack(">B",data)
		new_reg = reg[0] | 0x04 if value else reg[0] & 0xFB
		self.pi.i2c_write_device(self.i2c, self.__cmds["write_reg1"] + [new_reg])

	def reset(self):
		self.pi.i2c_write_device(self.i2c, self.__cmds["reset"])

	def close(self):
		self.pi.i2c_close(self.i2c)

if __name__ == "__main__":
	RHTEMP = Si7021()

	if len(sys.argv) > 1 and sys.argv[1] == "--reset":
		RHTEMP.reset()
		RHTEMP.close()
		sys.exit(0)
	if len(sys.argv) > 1 and sys.argv[1] == "--heater":
		heat = "ON" if RHTEMP.heater else "OFF"
		print("Heater: " + heat)

	print("Temperature: " + str(round(RHTEMP.temperature, 2)) + u" \u00B0C")
	print("Relative humidity: " + str(round(RHTEMP.relative_humidity, 2)) + " %")

	RHTEMP.close()
