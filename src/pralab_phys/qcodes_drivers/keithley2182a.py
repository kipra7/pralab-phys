# most of the drivers only need a couple of these... moved all up here for clarity below
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import (
        Unpack,  # can be imported from typing if python >= 3.12
    )

from qcodes import validators as vals
from qcodes.instrument import (
    VisaInstrument,
    VisaInstrumentKWArgs,
)
from qcodes.parameters import Parameter
from qcodes.validators import Enum, Numbers




class Keithley2182A1ch(VisaInstrument):
    """
    Instrument Driver for Keithley2182A (1 channel, Voltage only)

    Attributes:
        nplc (Parameter): Set or get the number of power line cycles (min=0.01, max=50)
        auto_range (Parameter): Set or get the measurement range automatically (1: ON, 0: OFF)
        rel (Parameter): Enables or disables the application of
                         a relative offset value to the measurement. (1: ON, 0: OFF)
        active (Parameter): Set or get the active function. (VOLT or TEMP)
        filter (Parameter): Enables or disables the digital filter for measurements.
        amplitude (Parameter): Get the voltage (unit: V)

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

    
        self.activate: Parameter = self.add_parameter(
            "active",
            get_cmd=":SENS:FUNC?",
            set_cmd="SENS:FUNC {}",
            vals=Enum("VOLT", "TEMP")
        )

        self.channnel: Parameter = self.add_parameter(
            "channel",
            get_cmd=":SENS:CHAN?",
            set_cmd="SENS:CHAN {}",
            vals=Enum(1, 2)
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


class Keithley2182AChannel(InstrumentChannel):
    """
    Class to hold the two Keithley channels, i.e.
    CH1 and CH2.
    """

    def __init__(
        self,
        parent: Instrument,
        name: str,
        channel: str,
        **kwargs: "Unpack[InstrumentBaseKWArgs]",
    ) -> None:
        """
        Args:
            parent: The Instrument instance to which the channel is
                to be attached.
            name: The 'colloquial' name of the channel
            channel: The name used by the Keithley, i.e. either
                'ch1' or 'ch2'
            **kwargs: Forwarded to base class.

        """

        if channel not in ["ch1", "ch2"]:
            raise ValueError('channel must be either "ch1" or "ch2"')

        dchannel = {
            "ch1": "CHAN1",
            "ch2": "CHAN2"
        }

        super().__init__(parent, name, **kwargs)
        self.model = self._parent.model

        self.auto_range: Parameter = self.add_parameter(
            "auto_range",
            get_cmd=f"SENS:VOLT:{dchannel[channel]}:RANG:AUTO?",
            set_cmd=f"SENS:VOLT:{dchannel[channel]}:RANG:AUTO {{}}"
        )

        self.vrel: Parameter = self.add_parameter(
            "vrel",
            get_cmd=f"SENS:VOLT:{dchannel[channel]}:REFerence:STATe?",
            set_cmd=f"SENS:VOLT:{dchannel[channel]}:REFerence:STATe {{}}"
        )

        self.amplitude: Parameter = self.add_parameter(
            "amplitude",
            get_cmd="SENS:DATA:FRES?",
            get_parser=float,
            unit="V"
        )

        



class Keithley2600(VisaInstrument):
    """
    This is the qcodes driver for the Keithley2600 Source-Meter series,
    tested with Keithley2614B
    """

    default_terminator = "\n"

    def __init__(
        self, name: str, address: str, **kwargs: "Unpack[VisaInstrumentKWArgs]"
    ) -> None:
        """
        Args:
            name: Name to use internally in QCoDeS
            address: VISA ressource address
            **kwargs: kwargs are forwarded to the base class.

        """
        super().__init__(name, address, **kwargs)

        model = self.ask("localnode.model")

        knownmodels = [
            "2601B",
            "2602B",
            "2604B",
            "2611B",
            "2612B",
            "2614B",
            "2635B",
            "2636B",
        ]
        if model not in knownmodels:
            kmstring = ("{}, " * (len(knownmodels) - 1)).format(*knownmodels[:-1])
            kmstring += f"and {knownmodels[-1]}."
            raise ValueError("Unknown model. Known model are: " + kmstring)

        # Add the channel to the instrument
        self.smua = self.add_submodule("smua", KeithleyChannel(self, "smua", "smua"))
        "smua channel of the instrument"
        self.smub = self.add_submodule("smub", KeithleyChannel(self, "smub", "smub"))
        "smub channel of the instrument"

        # display parameter
        # Parameters NOT specific to a channel still belong on the Instrument object
        # In this case, the Parameter controls the text on the display
        self.display_settext = Parameter(
            "display_settext",
            set_cmd=self._display_settext,
            vals=vals.Strings(),
            instrument=self,
        )

        self.connect_message()