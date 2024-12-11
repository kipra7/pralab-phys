from collections.abc import Collection
from numbers import Real


def critical_current(current: Collection[Real], voltage: Collection[Real], threshold: Real | None = None) -> float:
    """
    Calculate the critical current from a current-voltage curve.

    Args:
        current: The current values.
        voltage: The voltage values.
        threshold: The threshold voltage. If None, the threshold is calculated as the maximum voltage divided by 2.

    Returns:
        The critical current.
    """
    if len(current) != len(voltage):
        raise ValueError("The current and voltage arrays must have the same length.")

    if threshold is None:
        threshold = max(voltage) / 2

    for i, v in enumerate(voltage):
        if v > threshold:
            return current[i]

    return 0


def critical_temperature(temperature: Collection[Real], resistance: Collection[Real], threshold: Real | None = None) -> float:
    """
    Calculate the critical temperature from a temperature-resistance curve.

    Args:
        temperature: The temperature values.
        resistance: The resistance values.
        threshold: The threshold resistance. If None, the threshold is calculated as the maximum resistance divided by 2.

    Returns:
        The critical temperature.
    """
    if len(temperature) != len(resistance):
        raise ValueError("The temperature and resistance arrays must have the same length.")

    temperature, resistance = zip(*sorted(zip(temperature, resistance)))

    if threshold is None:
        threshold = max(resistance) / 2

    for i, r in enumerate(resistance):
        if r > threshold:
            return temperature[i]

    return 0


def ic_to_jc(ic: Real, width: Real, height: Real) -> float:
    """
    Calculate the critical current density from the critical current.

    Args:
        ic: The critical current. (mA)
        width: The width of the wire. (nm)
        height: The height of the wire. (nm)

    Returns:
        The critical current density. (kA/cm^2)
    """

    # kA/cm^2 = (10^-3 A)/(10^2 m)^2 = (10^-6 mA)/(10^-7 cm)^2

    return ic / (width * height) * 10**(-6 + 7 * 2) # kA/cm^2