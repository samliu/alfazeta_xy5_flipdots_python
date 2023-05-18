# XY5 Driver in Python

This repo provides code to display stuff on your AlfaZeta XY5 flip dot display
using a serial connection on linux (e.g Raspbian, Ubuntu, etc).

![my xy5 clock](https://github.com/samliu/alfazeta_xy5_flipdots_python/assets/135933/ab0eb861-0228-4e71-8c48-0d1e6da36b74)


Specially this is written for the 14x28 displays that are controlled by two
separate 7x28 controllers.

* `xy5_driver.py` - library provides a class you can use to write a numpy
  array to. For example, if you write some code to convert an image to a 7x28 or
  14x28 numpy array, you can use this class to easily have it draw the image to
  the board.
* `show_text.py` - library provides a class to write scrolling text along either
  the top or bottom halves of the board. You can also have two simultaneous
  scrolling texts, but they will always only be as tall as the board
  horizontally divided (7 dots tall).
* `game_of_life.py` - Conway's game of life implemented for the 14x28 board.
* `clock.py` - a clock implemented for the 14x28 board.

Please read `xy5_driver.py` comments for more details on how to configure
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

For Game of Life Demo

* scipy (for convolve2D)


## Installation

If you're missing the python dependencies, you can install them using:

```python
pip install -r requirements.txt
```
