# ModRADAR

The aim of this project was to display the speeds of track and field runners in real time.

We used 3 FMCW radars (https://urad.es/en/) embedded on Raspberry Pi 4 and Arduino Uno.

The radars deposit the raw measurements (IQ signal) on a Redis server and a Python server processes the measurements to recover the speeds and positions of the riders.

At the same time, the Python server retrieves the video from a mobile phone filming the track. It detects people moving around using the background subtraction technique. Finally, it associates the radar measurements with the bouding boxes of the detected people using the vectors that the user places on the web interface.

The web interface also displays the Fourier transforms of the raw signals in real time and the technique used to eliminate phantom targets (signal processing).
