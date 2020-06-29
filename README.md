# gr-sdrplay3
GNU Radio Block for SDRPlay for APIv3

First try to let a GNU Radio block cooperate with the SDRPlay version 3 API.
Already plays FM radio on a constant frequency, so still needs work to get all the parameter passing going:
Frequency, Gain, ...

# CW Decoder Block

Implemented a CW to digital decder block.
Is a rectifier using abs(), followed by mean of last n values (Resistor Capacitor).
Analog output to watch the result, Schmitt-Trigger output for digital post processing.
