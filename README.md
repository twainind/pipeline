# ===pipeline

A small, lightweight in-browser application for the Aquaponic inspired gardiner.

## Getting Started

Simply spin up a fresh copy of Raspbian on a RPi 3 or Zero W, Connect it to the internet and drop the project folder in the $pi home directory.

Then run the launch.sh utility from a terminal or ssh session and select "Install".

```
pi@raspberrypi:~$ sudo pipeline/launch.sh
```

### Prerequisites

The launch.sh utility will install all dependencies required to run the application.

Hardware you will also need:

* Raspberry Pi Zero w / 3a / 3b
* SD card with Raspbian installed (lite works too)
* 4 CH 5v relay module
* Temperature probes (ds18b20) (2 can be used via 1-wire)
* DHT-22 probe
* Jumper Cables
* Some techno-savy

### Setup

Setup is not in-depth and only meant to be used as a rough guide for those savy with the Raspberry Pi layout. If in doubt, visit the raspberrypi foundation website and forums for guidance.

Using jumper cables, Connect RPi to a 4 CH 5v Relay module using pins 5v, GPIO 17,18,23 & 24 and Ground.

Using jumper cables, Connect temperature probes to 3V3, GPIO 4 and Ground. Ensure to use 4.7k Ohm resister in circuit (between 3V3 and GPIO 4, connecting the two).

### Installing

Run the launch.sh utility from a terminal or ssh session and select "Install".

```
pi@raspberrypi:~$ sudo pipeline/launch.sh
```

If you would like to run the python scripts separatly, you can do this also.

```
pi@raspberrypi:~$ sudo python pipeline/app.py
```

## Running the application

Run the launch.sh utility from a terminal or ssh session and select "Start pipeline".

```
:pi@raspberrypi:~$ sudo pipeline/launch.sh
```

Make sure to run this utility from the home directory. ie:

```
pi@raspberrypi:~$ sudo pipeline/launch.sh
```

not

```
pi@raspberrypi:~/pipeline $ sudo launch.sh
```
This will create issues.

## Deployment

Copy/Pasta - Nice and easy

## Built With

* [Flask] - The web framework used
* [python2.7] - Programming Language used
* [sqlite3] - Database Management

## Contributing

If you would like to contribute, see "about" section on web app.

Please credit this original project if you intend to publish an altered/changed version of this project.

## Versioning

V 0.0.5a

## Authors

* **Mark Pryor** 2018


## License

OPEN-SOURCE

## Acknowledgments

* Google
* Inspiration
