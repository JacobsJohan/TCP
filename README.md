# TCP
This code has been written as part of my master's thesis titled "Localization of cellular devices in 5G networks". The idea is to localize a transmit antenna using multiple antenna arrays as receivers to compute the angle of arrival (AoA) from different positions. These AoAs are then sent to a host which computes the transmitter position via triangulation.
A linear or extended Kalman filter can additionally be used to improve the tracking of a moving transmitter.

## How does it work
The Host.py should be launched first. This will read out the config.txt file to know the number of receivers, their locations and their IP + port. For each receiver, the Host will open up a socket for a Client to connect to.

Note: when launching the Host it will explicitly ask how many receivers will be connected. This is done to make it possible to test things in the Host.py file without actually requiring a connection with the receivers. When 0 receivers are selected, the Host will run as usual but without receiving new AoA information from the nonexisting clients.

Once the Host has launched, all Clients can connect to it. The Clients will start up their GRC scripts to start computing the AoA using the MUSIC algorithm. They will then continuously send this AoA to the Host which performs triangulation based on this information.
The Host will also launch a GUI to display the location of the transmitter visually. It contains a start button to start the triangulation, a pause button to pause it and a stop button to shut down the Host and all Clients.
