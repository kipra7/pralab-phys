# most of the drivers only need a couple of these... moved all up here for clarity below
import ctypes  # only for DLL-based instrument
import sys
import time
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

class Keithley2182A(VisaInstrument):
    """
    QCoDes driver for the Keithley 2182A Nanovoltmeter.
    """

    def __init__(
        self,
        name: str,
        address: str,
        reset: bool = False,
        **kwargs: "Unpack[VisaInstrumentKWArgs]",
    ):
        super().__init__(name, address, **kwargs)

        self._trigger_sent = False

        self.nplc: Parameter = self.add_parameter(
            "nplc",
            get_cmd="SENS:VOLT:NPLC?",
            set_cmd="SENS:VOLT:NPLC {}",
            vals=Numbers(min_value=0.01, max_value=50),
            get_parser=float
        )

        # 将来的にチャンネルを変更できるようにする
        self.auto_range: Parameter = self.add_parameter(
            "auto_range",
            get_cmd="SENS:VOLT:CHAN1:RANG:AUTO?",
            set_cmd="SENS:VOLT:CHAN1:RANG:AUTO {}"
        )

        # 将来的に「チャンネルの変更」「Bool値の入力方法」「温度かボルテージか」など変更できるようにしたい
        self.rel: Parameter = self.add_parameter(
            "rel",
            get_cmd="SENS:VOLT:REFerence:STATe?",
            set_cmd="SENS:VOLT:REFerence:STATe {}"
        )

        self.active: Parameter = self.add_parameter(
            "active",
            get_cmd=":SENS:FUNC?",
            set_cmd="SENS:FUNC {}",
            vals=Enum("VOLT", "TEMP")
        )

        self.filter: Parameter = self.add_parameter(
            "filter",
            get_cmd=":SENS:VOLT:DFILter:STAT?",
            set_cmd=":SENS:VOLT:DFILter:STAT {}"
        )

        self.amplitude: Parameter = self.add_parameter(
            "amplitude",
            get_cmd="SENS:DATA:FRES?",
            get_parser=float,
            unit="V"
        )

        self.get = self.amplitude

        


