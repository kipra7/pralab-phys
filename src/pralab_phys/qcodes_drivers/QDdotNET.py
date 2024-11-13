import time
import clr
from decimal import Decimal
from qcodes.instrument.parameter import Parameter
from qcodes.instrument.base import Instrument

# add .net reference and import so python can see .net
clr.AddReference(r"dlls\QDInstrument")

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

QDINSTRUMENT_TYPE = {'DynaCool': QDInstrumentBase.QDInstrumentType.DynaCool,
                     'PPMS': QDInstrumentBase.QDInstrumentType.PPMS,
                     'SVSM': QDInstrumentBase.QDInstrumentType.SVSM,
                     'VersaLab': QDInstrumentBase.QDInstrumentType.VersaLab,
                     'MPMS': 4121982}
DEFAULT_PORT = 11000

class QDInstrument:

    def __init__(self, instrument_type, ip_address, remote=True):
        self.qdi_instrument = QDInstrumentFactory.GetQDInstrument(
            QDINSTRUMENT_TYPE[instrument_type], remote, ip_address, DEFAULT_PORT)
    


class PPMSdotNET(Instrument):
    """
    QD PPMS Multivu (dotNET)
    """
    def __init__(
        self,
        name: str,
        serial: str,
        min_velocity: float = 0.0,
        max_velocity: float = 0.5,
        acceleration: float = 0.2,
        **kwargs,
    ) -> None:
        super().__init__(name=name, **kwargs)

        # Create Position parameter
        self.add_parameter(
            name="position",
            parameter_class=Position,
            label="Motor position",
            unit="deg",
        )

        self.add_parameter(
            name="temperature",
            parameter_class=Temperature,
            label="Temperature",
            unit="K",
        )

        self.add_parameter(
            name="magfield",
            parameter_class=MagField,
            label="Magnetic Mield",
            unit="Oe",
        )

    def get_position(self):
        return float(str(self.device.Position))

    def get_idn(self):
        return {
            "vendor": "Qauntum Design",
            "model": "PPMS3",
            "serial": self.serial,
            "firmware": None,
        }



class Position(Parameter):
    """
    Parameter class for the motor position
    """
    def __init__(
        self,
        name: str,
        instrument: PPMSdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, position: float) -> None:
        """Sets the motor position"""
        self.instrument.move_position(position)

    def get_raw(self) -> float:
        """Returns the motor position"""
        return self.instrument.get_position()


class Temperature(Parameter):
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: PPMSdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, temperature: float) -> None:
        """Sets the temperature"""
        self.instrument.set_temperature(temperature)

    def get_raw(self) -> float:
        """Returns the temperature"""
        return self.instrument.get_temperature()


class MagField(Parameter):
    """
    Parameter class for the temperature
    """
    def __init__(
        self,
        name: str,
        instrument: PPMSdotNET,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def set_raw(self, mag: float) -> None:
        """Sets the magnetic field"""
        self.instrument.set_mag(mag)

    def get_raw(self) -> float:
        """Returns the magnetic field"""
        return self.instrument.get_mag()