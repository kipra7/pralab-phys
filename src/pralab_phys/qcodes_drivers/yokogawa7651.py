from functools import partial
from qcodes import (VisaInstrument,
					validators as vals)
from qcodes.parameters import Parameter

import logging

log = logging.getLogger(__name__)


class Yokogawa7651(VisaInstrument):
	""" 
        QCoDeS driver for the Yokogawa 7651 I/V source.  

        Args:  
            VisaInstrument (_type_): _description_  

        Attributes:  
            voltage_range (Parameter):
				Set output voltage range in mV.  

            current_range (Parameter):
				Set output current range in mA.  

            voltage_limit (Parameter):
				Set output voltage limit in mV.  

            current_limit (Parameter):
				Set output current limit in mA.  

            auto_voltage (Parameter):
				Set output voltage in mV.  

            auto_current (Parameter):
				Set output current in mA.  

            output (Parameter):
				Output Status. ("on", "off")
        """  
	def __init__(self, name, address, **kwargs):
		# supplying the terminator means you don't need to remove it from every response
		super().__init__(name, address, terminator='\n', **kwargs)

		# init: crashes the I/O, clear from visa test panel fixes the issue
		# self.write('RC')
        
		''' 
			A Parameter object for the current output of the Yokogawa7651.

			Args:
				current: The current output of the Yokogawa7651. (mA)

			Returns:
				The current output of the Yokogawa7651. (mA)
		'''
		self.current: Parameter = self.add_parameter(
                name="current",
                parameter_class=Y7651AutoCurrent,
                label="current",
                unit="A",
            )
		
		self.current_peak_amplitude: Parameter = self.add_parameter(
                name="current_peak_amplitude",
                parameter_class=Y7651AutoCurrent,
                label="current peak amplitude",
                unit="A",
            )

		self.auto_voltage: Parameter = self.add_parameter(
			name="voltage",
			parameter_class=Y7651AutoVoltage,
			label="voltage",
			unit="V",
		)

		self.mode: Parameter = self.add_parameter(
			name="mode",
			parameter_class=Y7651Mode,
			label="mode",
		)

		self.voltage_range: Parameter = self.add_parameter(
			name = 'voltage_range',  
			label = 'Set the output voltage range in mV',
			vals = vals.Enum(10, 100, 1000, 10000, 30000),
			unit  = 'mV',
			set_cmd = partial(self._set_range, mode = "VOLT"),
			get_cmd = None
			)

		self.current_range: Parameter = self.add_parameter(
			name = 'current_range',  
			label = 'Set output current range in mA',
			vals = vals.Enum(1,10,100),
			unit  = 'A',
			set_cmd = partial(self._set_range, mode = "CURR"),
			get_cmd = None
			)

		self.voltage_limit: Parameter = self.add_parameter(
			name = 'voltage_limit',  
			label = 'Set output voltage limit in mV',
			vals = vals.Numbers(1000,30_000),
			unit  = 'mV',
			set_parser = self._div_1000_int,
			set_cmd = 'LV'+'{}'
			)

		self.current_limit: Parameter = self.add_parameter(
			name = 'current_limit',
			label = 'Set output current limit in mA',
			vals = vals.Numbers(5,120),
			unit  = 'mA',
			set_parser = int,
			set_cmd = 'LA'+'{}')

		self.output = self.add_parameter(
			name = 'output',  
			label = 'Output State',
			set_cmd=lambda x: self.on() if x else self.off(),
            get_cmd=lambda x: self._get_output(),
			val_mapping={"off": 0, "on": 1,},
			)

	
	def on(self):
		self.write('O1E')
	
	def off(self):
		self.write('O0E')

	def output_on(self):
		self.write('O1E')
	
	def output_off(self):
		self.write('O0E')

	def _get_output(self):
		return int(self.ask("OC")[5:].strip()) >> 4 & 1

	def _get_amplitude(self):
		return float(self.ask("OD")[4:].strip())
	
	def _set_range(self, range:int, mode:str) -> None:
		if mode == "CURR":
			range_options = {1:'R4', 10:'R5', 100:'R6' } # 修正箇所
			self.write('F5'+range_options[int(range)]+'E')
		elif mode == "VOLT":
			range_options = {10:'R2', 100:'R3', 1000:'R4', 10000:'R5', 30000:'R6' } # 修正箇所
			self.write('F1'+range_options[int(range)]+'E')

	def _div_1000_int(self,val):
		return int(val/1000)

	def _set_V(self,voltage):
		if voltage>0:
			polarity = '+'
		else:
			polarity = '-'
		self.write('F1SA'+polarity+str(round(abs(voltage),6))+'E')

	def _set_A(self,current):
		if current>0:
			polarity = '+'
		else:
			polarity = '-'
		self.write('F5SA'+polarity+str(round(abs(current),6))+'E')

	def initialize(self):
		self.write('RC')

	def reverse(self):
		self.write('RC')

	# To avoid identity query error
	def get_idn(self):
		return self.ask('OS')


class Y7651AutoCurrent(Parameter):
	def __init__(
            self,
            name: str,
            instrument: Yokogawa7651,
            **kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def get_raw(self):
		# self は Parameter インスタンス。 instrument にアクセスして _get_amplitude を呼び出す。
		return self.instrument._get_amplitude() 

	def set_raw(self, value):
		self.instrument._set_A(value)


class Y7651AutoVoltage(Parameter):
	def __init__(
		self,
		name: str,
		instrument: Yokogawa7651,
		**kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def get_raw(self):
		# self は Parameter インスタンス。 instrument にアクセスして _get_amplitude を呼び出す。
		return self.instrument._get_amplitude()

	def set_raw(self, value):
		self.instrument._set_V(value)


class Y7651Mode(Parameter):
	def __init__(
		self,
		name: str,
		instrument: Yokogawa7651,
		**kwargs,) -> None:
		
		super().__init__(name, instrument=instrument, **kwargs)

	def set_raw(self, value):
		if value == "Voltage":
			self.instrument.write('F1E')
		elif value == "Current":
			self.instrument.write('F5E')

