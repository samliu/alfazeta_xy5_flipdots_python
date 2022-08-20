# XY5 Driver in Python

This repo provides code to display stuff on your AlfaZeta XY5 flip dot display
using a serial connection on linux (e.g Raspbian, Ubuntu, etc).

Specially this is written for the 14x28 displays that are controlled by two
separate 7x28 controllers.

* `xy5_controller.py` - library provides a class you can use to write a numpy
  array to. For example, if you write some code to convert an image to a 7x28 or
  14x28 numpy array, you can use this class to easily have it draw the image to
  the board.
* `show_text.py` - library provides a class to write scrolling text along either
  the top or bottom halves of the board. You can also have two simultaneous
  scrolling texts, but they will always only be as tall as the board
  horizontally divided (7 dots tall).

Please read `xy5_controller.py` comments for more details on how to configure
the hardware or find your serial port.

The library makes it easy to instantiate multiple XY5Driver classes to control
more than one display at a time, but for now I only control a single display.

## Example usage

```bash
python3 show_text.py
```

## Requirements

* Your XY5 display is connected via a serial port (e.g. to `/dev/ttyUSB0`)

System packages:

* python3
* python3-pip

Python packages:

* numpy
* pyserial

## Installation

If you're missing the python dependencies, you can install them using:

```python
pip install -r requirements.txt
```
