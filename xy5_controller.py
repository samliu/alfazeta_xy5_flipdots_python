"""xy5_controller.py

This script controls an AlfaZeta XY5 Flipdot (flip-disc) display.

<license: MIT>
Copyright 2022 Samuel Chern-Shinn Liu <sam@ambushnetworks.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
</license>

The display is comprised of two 7x28 panels stacked on top of one another, for
total resolution of 14x28.

Your mental model will be clearer if you visualize each of the component 7x28
panels at a time. We give 28 data bytes; each byte has 8 bits, 8x28 is more
than enough for the 7x28 bits in a single panel.

Each 32-bit message sent along the serial port will have this structure:

* Header
  * 0x80 (128)
* One of these bytes to indicate flipping behavior. We typically use 0x83 (send
  bytes and refresh). When you don't refresh, dots can accidentally be in the
  wrong state and not get fixed.
  * 0x82 (130) = refresh (keep painting @ 15hz)
  * 0x83 (131) = 28 bytes of data + refresh
  * 0x84 (132) = 28 bytes of data + no refresh (set once)
* Panel Address
  * 0xFF for all
  * Based on your 6 dip switches. 0 for 000000, 1 for 000001, etc. Careful, the
    bytes are little endian but your dip switches are big endian!
* Data
  * N bytes of data. Generally 28 bytes (though if you specify a special
    flipping behavior byte, you may need to provide more).
  * Examples
    * 0x7F = 01111111, so this sets a 7x1 column of pixels, all on.
    * 0x1 = 00000001, so this sets a 7x1 column of pixels with the first one
      from the top ON.
    * 0x2 = 00000010, so this sets a 7x1 column of pixels with the second one
      from the top ON.
    * 0x8 = 00000100, so this sets a 7x1 column of pixels with the third one
      from the top ON.
* End
  * 0x8F (143) = end
"""

import serial
import time
import numpy as np


class XY5Driver(object):
    """Driver for AlfaZeta XY5 Panel."""

    def __init__(
            self,
            baud=57600,
            serial_port="/dev/ttyUSB0",
            dest_panel_addr_top=0,
            dest_panel_addr_bottom=1):
        # Make sure the first 3 dip switches are set to:
        #   1 - OFF
        #   2 - ON
        #   3 - ON
        self.baud = baud

        # Assumes you're using a USB-to-serial converter, and only have one
        # connected to your linux computer / raspberry pi. To check what serial
        # devices you have connected, run `dmesg | grep tty`. To see what's
        # available you can also run `ls /dev | grep tty` (tty is serial).
        self.serial_port = serial_port
        self.serial_connection = serial.Serial(self.serial_port, self.baud)

        # There are 8 dip switches for setting a panel address, in case you
        # have a lot of these.  If you just want to control 1 board, set the
        # top address to all 0, and set the bottom address to 1-ON, rest-OFF
        # (which is binary address 1 -- the dip switches are big-endian).
        self.dest_panel_addr_top = dest_panel_addr_top
        self.dest_panel_addr_bottom = dest_panel_addr_bottom

        # Clear the panel to start.
        self.paint_14x28(
            np.zeros([14, 28], dtype=np.int8),
            dest_panel_addr_top=self.dest_panel_addr_top,
            dest_panel_addr_bottom=self.dest_panel_addr_bottom)

    def __del__(self):
        self.serial_connection.close()

    def __numpy_matrix_to_bytes(self, arr):
        """Takes a 7x28 binary np.array and returns bytes for the XY5.

        Arguments:
          arr: np.array 7x28 numpy matrix with dtype np.int8.
        Returns:
          bytearray with 28 bytes.
        """
        assert (arr.shape == (7, 28))
        data_bytes = bytearray([])
        for col in arr.T:
          bytes_as_list_of_strs = [str(x) for x in col.flatten().tolist()]
          bytes_as_list_of_strs.reverse()
          hex_byte = int("".join(['0'] + bytes_as_list_of_strs), 2)
          data_bytes.append(hex_byte)
        return data_bytes

    def send_custom_transmission(self, transmission):
        self.serial_connection.write(transmission)

    def paint_7x28(self, numpy_arr, dest_panel_addr=0):
        """Draw a 7x28 matrix to the display (half display)."""
        assert (numpy_arr.shape == (7, 28))
        assert (numpy_arr.dtype == np.int8)
        # Every transmission should have these headers.
        transmission = bytearray([
            0x80,  # Header byte.
            0x83,  # 28 bytes of data, refresh.
            dest_panel_addr,  # Address
        ])
        data_bytes = self.__numpy_matrix_to_bytes(numpy_arr[:7])
        transmission.extend(data_bytes)
        transmission.append(0x8F)  # End of Transmission byte.
        self.serial_connection.write(transmission)

    def paint_14x28(
            self,
            numpy_arr,
            dest_panel_addr_top=0,
            dest_panel_addr_bottom=1):
        """Draw a 14x28 matrix to the display (whole display)."""
        assert (numpy_arr.shape == (14, 28))
        assert (numpy_arr.dtype == np.int8)

        transmission = bytearray([
            0x80,  # Header byte.
            0x83,  # 28 bytes of data, refresh.
            dest_panel_addr_top,  # Address
        ])
        np_slice = numpy_arr[:7]
        data_bytes = self.__numpy_matrix_to_bytes(np_slice)
        transmission.extend(data_bytes)
        transmission.append(0x8F)  # End of Transmission byte.
        self.serial_connection.write(transmission)

        transmission = bytearray([
            0x80,  # Header byte.
            0x83,  # 28 bytes of data, refresh.
            dest_panel_addr_bottom,  # Address
        ])
        np_slice = numpy_arr[7:]
        data_bytes = self.__numpy_matrix_to_bytes(np_slice)
        transmission.extend(data_bytes)
        transmission.append(0x8F)  # End of Transmission byte.
        self.serial_connection.write(transmission)


if __name__ == "__main__":
    # You can run this problem but it's a dumb example. It will flip two dots
    # for 1 second, then unflip them.
    driver = XY5Driver()

    # Generate an image to display. arr[y][x] since matrix notation is
    # "rows x columns" -- sorry if you expected (x, y), heh.
    arr = np.zeros([14, 28], dtype=np.int8)
    arr[0][0] = 1  # Pixel at the top left corner.
    arr[10][21] = 1  # Pixel 9 down, 20 over.
    driver.paint_14x28(arr, 0)

    # Reset after 1 second.
    time.sleep(1)

    # This paints everything black.
    arr = np.zeros([14, 28], dtype=np.int8)
    driver.paint_14x28(arr, 0)
