# most of the drivers only need a couple of these... moved all up here for clarity below
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing_extensions import (
        Unpack,  # can be imported from typing if python >= 3.12
    )

from qcodes import validators as vals
from qcodes.instrument import (
    Instrument,
    VisaInstrument,
    VisaInstrumentKWArgs,
)
from qcodes.parameters import Parameter
from qcodes.validators import Enum, Ints, MultiType, Numbers

import math

class nfLI5640(VisaInstrument):
    """Instrument Driver for Keithley6221"""

    default_terminator = "\r\n"

    def __init__(
        self,
        name: str,
        address: str,
        reset: bool = False,
        **kwargs: "Unpack[VisaInstrumentKWArgs]",
    ):

        """initial
        """
        super().__init__(name, address, **kwargs)

        self.get_data: Parameter = self.add_parameter(
            "get_data",
            get_cmd="DOUT?",
            set_cmd=None,
            unit="V",
        )

        self.getdata: Parameter = self.add_parameter(
            name = "getdata",
            parameter_class=nfLI5640GetData,
            label = "getdata",
        )

        self.getdatax: Parameter = self.add_parameter(
            name = "getdatax",
            parameter_class=nfLI5640GetDataX,
            label = "getdatax",
        )

        self.getdatay: Parameter = self.add_parameter(
            name = "getdatay",
            parameter_class=nfLI5640GetDataY,
            label = "getdatay",
        )

    def get_data(self):
        x, y = map(float, self.write("DOUT?").split(","))
        return (x, y)


class nfLI5640GetData(Instrument):

    def __init__(
        self,
        name: str,
        instrument: nfLI5640,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the temperature"""
        x, y = self.instrument.get_data()
        return math.sqrt(x**2 + y**2)


class nfLI5640GetDataX(Instrument):

    def __init__(
        self,
        name: str,
        instrument: nfLI5640,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the temperature"""
        x, y = self.instrument.get_data()
        return x
    

class nfLI5640GetDataY(Instrument):

    def __init__(
        self,
        name: str,
        instrument: nfLI5640,
        **kwargs,
    ) -> None:
        super().__init__(name, instrument=instrument, **kwargs)

    def get_raw(self) -> float:
        """Returns the temperature"""
        x, y = self.instrument.get_data()
        return y