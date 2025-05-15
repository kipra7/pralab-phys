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