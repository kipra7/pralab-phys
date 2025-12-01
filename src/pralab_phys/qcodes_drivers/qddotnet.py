import clr
from qcodes.parameters import Parameter
from qcodes.instrument.base import Instrument
clr.AddReference("System")
from System import Double, UInt16, Int32


# add .net reference and import so python can see .net

DEFAULT_PORT = 11000

class QDdotNET(Instrument):
    """
    A driver class for Quantum Design instruments, providing control over temperature, magnetic field, and position.

    Parameters
    ----------
    name : str
        The name of the instrument instance.
    ip_address : str
        The IP address of the Quantum Design instrument.
    instruent_type : str, optional
        The type of the instrument (default is "DynaCool").
    remote : bool, optional
        Whether to use remote control (default is False).
    QDInstrumentdir : str, optional
        Directory path to the Quantum Design instrument DLL (default is "").
    QDInstrumentname : str, optional
        Name of the Quantum Design instrument DLL (default is "QDInstrument").
    port : int, optional
        The port number for communication (default is 11000).
    **kwargs : dict
        Additional keyword arguments passed to the base class.

    Attributes
    ----------
    temperature : QDTemperature
        Parameter for controlling and reading the temperature.
    temperaturestatus : QDTemperatureStatus
        Parameter for reading the temperature status.
    field : QDField
        Parameter for controlling and reading the magnetic field.
    fieldstatus : QDFieldStatus
        Parameter for reading the magnetic field status.
    position : QDPosition
        Parameter for controlling and reading the position.
    positionstatus : QDPositionStatus
        Parameter for reading the position status.
    fieldrate : Parameter
        Parameter for setting and getting the magnetic field rate.
    temperaturerate : Parameter
        Parameter for setting and getting the temperature rate.
    positionrate : Parameter
        Parameter for setting and getting the position rate.

    Methods
    -------
    get_field()
        Retrieves the current magnetic field value.
    set_field(field)
        Sets the magnetic field to the specified value.
    get_position()
        Retrieves the current position of the motor.
    set_position(position)
        Sets the motor position to the specified value.
    set_temperature(temp)
        Sets the temperature to the specified value.
    get_temperature()
        Retrieves the current temperature value.
    get_idn()
        Returns the instrument identification information.
    """

    def __init__(
        self,
        name: str,
        ip_address: str,
        instruent_type = "DynaCool",
        remote: bool = False,
        QDInstrumentdir: str = "",
        QDInstrumentname: str = "QDInstrument",
        port = DEFAULT_PORT,
        **kwargs,
    ) -> None:
        super().__init__(name=name, **kwargs)

        clr.AddReference(QDInstrumentdir+QDInstrumentname)
        
        from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

        INST_MAP = {"PPMS": QDInstrumentBase.QDInstrumentType.PPMS, "DynaCool":  QDInstrumentBase.QDInstrumentType.DynaCool}

        self.QDIBase = QDInstrumentBase
        self.QDIFactory = QDInstrumentFactory
        try:
            self.device = QDInstrumentFactory.GetQDInstrument(INST_MAP[instruent_type], remote, ip_address, UInt16(port))
        except Exception:
            raise RuntimeError("Unsupported instrument_type")
        
        self.Brate = 100
        self.Trate = 10
        self.prate = 10
        self.minimim_temperature = 1.8

        self.temperature: Parameter = self.add_parameter(
            name = "temperature",
            parameter_class=QDTemperature,
            label = "temperature",
            unit = "K"
        )

        self.temperaturestatus: Parameter = self.add_parameter(
            name = "temperaturestatus",
            parameter_class=QDTemperatureStatus,
            label = "temperaturestatus",
        )

        self.field: Parameter = self.add_parameter(
            name = "field",
            parameter_class = QDField,
            label = "field",
            unit = "T"
        )

        self.fieldstatus: Parameter = self.add_parameter(
            name = "fieldstatus",
            parameter_class = QDFieldStatus,
            label = "fieldstatus",
        )

        self.position: Parameter = self.add_parameter(
            name = "position",
            parameter_class = QDPosition,
            label = "position",
            unit = "deg"
        )

        self.positionstatus: Parameter = self.add_parameter(
            name = "positionstatus",
            parameter_class = QDPositionStatus,
            label = "positionstatus",
        )

        self.fieldrate: Parameter = self.add_parameter(
            name = "fieldrate",
            label = "fieldrate",
            unit = "Oe/s",
            get_cmd = lambda: self.Brate,
            set_cmd = self._set_b_rate,
        )

        self.temperaturerate: Parameter = self.add_parameter(
            name = "temperaturerate",
            label = "temperaturerate",
            unit = "K/s",
            get_cmd = lambda: self.Trate,
            set_cmd = self._set_t_rate,
        )

        self.positionrate: Parameter = self.add_parameter(
            name = "positionrate",
            label = "positionrate",
            unit = "deg/s",
            get_cmd = lambda: self.prate,
            set_cmd = self._set_p_rate,
        )


    def get_field(self):
        return self.device.GetField(Double(0), self.QDIBase.FieldStatus(Int32(0)))
    
    def set_field(self, field):
        if -90000 <= field <= 90000:
            return self.device.SetField(field, self.Brate, self.QDIBase.FieldApproach(Int32(0)), self.QDIBase.FieldMode(0))
        else:
            raise RuntimeError("Field is out of bounds. Should be between -90000 and 90000 Oe")

    def get_position(self):
        error, position, status = self.device.GetPosition("Horizontal Rotator", Double(0), self.QDIBase.PositionStatus(Int32(0)))
        return (error, position, status)

    def set_position(self, position):
        return self.device.SetPosition("Horizontal Rotator", Double(position), self.prate, self.QDIBase.PositionMode(Int32(0)))

    def set_temperature(self, temp):
        if self.minimim_temperature <= temp <= 350:
            return self.device.SetTemperature(temp, self.Trate, self.QDIBase.TemperatureApproach(Int32(0)))
        else:
            raise RuntimeError("Temperature is out of bounds. Should be between " + str(self.minimim_temperature) + " and 350 K")

    def get_temperature(self) -> float:
        error, temperature, status = self.device.GetTemperature(Double(0), self.QDIBase.TemperatureStatus(Int32(0)))
        return (error, temperature, status)

    def _set_t_rate(self, rate: float):
        self.Trate = rate
    
    def _set_b_rate(self, rate: float):
        self.Brate = rate

    def _set_p_rate(self, rate: float):
        self.prate = rate

    def get_idn(self):
        return {
            "vendor": "Qauntum Design",
            "model": "PPMS3",
            "serial": self.serial,
            "firmware": None,
        }
    

class QDPosition(Parameter):
    """
    Parameter class for controlling and reading the motor position.

    Parameters
    ----------
    name : str
        The name of the parameter.
    instrument : QDdotNET
        The instrument instance this parameter belongs to.
    **kwargs : dict
        Additional keyword arguments.

    Methods
    -------
    set_raw(position: float)
        Sets the motor position to the specified value.
    get_raw() -> float
        Retrieves the current motor position.
    """
    """
    Parameter class for the motor position
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, position: float) -> None:
        """Sets the motor position"""
        self.instrument.set_position(position)

    def get_raw(self) -> float:
        """Returns the motor position"""
        return self.instrument.get_position()[1]
    

class QDPositionStatus(Parameter):
    """
    Parameter class for reading the motor position status.

    Parameters
    ----------
    name : str
        The name of the parameter.
    instrument : QDdotNET
        The instrument instance this parameter belongs to.
    **kwargs : dict
        Additional keyword arguments.

    Methods
    -------
    get_raw() -> int
        Retrieves the current motor position status.
    """
    """
    Parameter class for the motor position status
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the motor position status"""
        return int(self.instrument.get_position()[2])


class QDTemperature(Parameter):
    """
    Parameter class for controlling and reading the temperature.

    Parameters
    ----------
    name : str
        The name of the parameter.
    instrument : QDdotNET
        The instrument instance this parameter belongs to.
    **kwargs : dict
        Additional keyword arguments.

    Methods
    -------
    set_raw(temperature: float)
        Sets the temperature to the specified value.
    get_raw() -> float
        Retrieves the current temperature value.
    """
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, temperature: float) -> None:
        """Sets the temperature"""
        self.instrument.set_temperature(temperature)

    def get_raw(self) -> float:
        """Returns the temperature"""
        return self.instrument.get_temperature()[1]


class QDTemperatureStatus(Parameter):
    """
    Parameter class for reading the temperature status.

    Parameters
    ----------
    name : str
        The name of the parameter.
    instrument : QDdotNET
        The instrument instance this parameter belongs to.
    **kwargs : dict
        Additional keyword arguments.

    Methods
    -------
    get_raw() -> int
        Retrieves the current temperature status.
    """
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the temperature"""
        return int(self.instrument.get_temperature()[2])


class QDField(Parameter):
    """
    Parameter class for controlling and reading the magnetic field.

    Parameters
    ----------
    name : str
        The name of the parameter.
    instrument : QDdotNET
        The instrument instance this parameter belongs to.
    **kwargs : dict
        Additional keyword arguments.

    Methods
    -------
    set_raw(mag: float)
        Sets the magnetic field to the specified value.
    get_raw() -> float
        Retrieves the current magnetic field value.
    """
    """
    Parameter class for the field
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, mag: float) -> None:
        """Sets the magnetic field"""
        self.instrument.set_field(mag)

    def get_raw(self) -> float:
        """Returns the magnetic field"""
        return self.instrument.get_field()[1]


class QDFieldStatus(Parameter):
    """
    Parameter class for the field status
    """
    def __init__(
        self,
        name: str,
        instrument: QDdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the magnetic field"""
        return int(self.instrument.get_field()[2])
