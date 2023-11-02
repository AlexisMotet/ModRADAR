# ModRADAR

The aim of this project was to display the speeds of track and field runners in real time.

It uses 3 FMCW embedded radars (https://urad.es/en/) on Raspberry Pi 4 and Arduino Uno boards.
The radars deposit the raw measurements (IQ signal) on a Redis server and a Python server retrieves and processes them to get the speeds and positions of the runners.


https://github.com/AlexisMotet/ModRADAR/assets/84445302/d53f624c-56a4-40a6-b9de-c92200e4b1b3


At the same time, the Python server receives a video stream from a mobile phone filming the track. It detects people moving around using the background subtraction technique. Finally, it associates the radar measurements with the bouding boxes of the detected people using the vectors that the user places on the web interface.

The web interface also displays the Fourier transforms of the raw signals in real time and the technique used to eliminate phantom targets (signal processing).


https://github.com/AlexisMotet/ModRADAR/assets/84445302/e1d54d20-99dd-406a-bff6-8ba74e7ad0fe

