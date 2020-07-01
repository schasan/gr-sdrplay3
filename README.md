# gr-sdrplay3
GNU Radio Block for SDRPlay for APIv3

First try to let a GNU Radio block cooperate with the SDRPlay version 3 API.
Already plays FM radio on a constant frequency, so still needs work to get all the parameter passing going:
Frequency, Gain, ...

# CW analog to digital decoder block

Implemented a CW to digital decder block in C++.
Is a rectifier using abs(), followed by mean of last n values (Resistor Capacitor).

* Analog output to watch the result
* Schmitt-Trigger output for digital post processing
* Message output issuing a time message in sample count every time a signal rise or fall is detected. Least significant bit indicate rise or fall.

# CW code decoder block 

Picks up messages indcating signal state changes and their timing.
Timings are collectes on a circular lerning buffer, one buffer for "on"-lenghts, the other one for "off"-lengths.
At regular intervals the kMeans cluster algorithm calculates the dot and the dash clusters for the on-vector as well as the signal-gap, letter-gap and word-gap for the off-vector.
The calculated timings are used for decode timing.

ToDo: Handle long pauses in transmissions as well as long carrier signals.
