from xy5_controller import XY5Driver

import time

# Think of each byte here as controlling one 7-dot column. Your text length may
# be longer than the total 28 available columns; other code will handle
# windowing & showing only the 28 relevant columns (via the scrolling effect).
#
# Note: each of these characters are 5 dots tall, with 1 dot above and 1 dot
# below set to black for spacing. So these characters are good for scrolling
# messages on either the top or bottom half of your board.
#
# This code was taken from github.com/philetus's work in
# https://github.com/vwyf/vwyf_door_sensor. Thanks for making my life that much
# easier :)
CHARACTER_CONVERTER = {
    ' ': bytearray([0]),
    '+': bytearray([24,  126, 126,  24,  0]),
    '-': bytearray([24,   24,  24,  24,  0]),
    '0': bytearray([62,   65,  65,  62,  0]),
    '1': bytearray([0,   66,  127, 64,  0]),
    '2': bytearray([98,   81,  73,  70,  0]),
    '3': bytearray([34,   65,  73,  54,  0]),
    '4': bytearray([56,   36,  34, 127, 32]),
    '5': bytearray([79,   73,  73,  49,  0]),
    '6': bytearray([62,   73,  73,  50,  0]),
    '7': bytearray([3,    1,   1, 127,  0]),
    '8': bytearray([54,   73,  73,  54,  0]),
    '9': bytearray([38,   73,  73,  62,  0]),
    'A': bytearray([0x3C, 0x0A, 0x0A, 0x3C]),
    'B': bytearray([0x3E, 0x2A, 0x2A, 0x14]),
    'C': bytearray([0x1C, 0x22, 0x22, 0x14]),
    'D': bytearray([0x3E, 0x22, 0x22, 0x1C]),
    'E': bytearray([0x3E, 0x2A, 0x2A]),
    'F': bytearray([0x3E, 0x0A, 0x0A]),
    'G': bytearray([0x1C, 0x22, 0x2A, 0x2A]),
    'H': bytearray([0x3E, 0x08, 0x08, 0x3E]),
    'I': bytearray([0x3E]),
    'J': bytearray([0x10, 0x20, 0x20, 0x1E]),
    'K': bytearray([0x3E, 0x08, 0x14, 0x22]),
    'L': bytearray([0x3E, 0x20, 0x20]),
    'M': bytearray([0x3E, 0x04, 0x08, 0x04, 0x3E]),
    'N': bytearray([0x3E, 0x04, 0x08, 0x3E]),
    'O': bytearray([0x1C, 0x22, 0x22, 0x1C]),
    'P': bytearray([0x3E, 0x0A, 0x0A, 0x1C, 0x04]),
    'Q': bytearray([0x1C, 0x22, 0x12, 0x2C]),
    'R': bytearray([0x3E, 0x0A, 0x1A, 0x24]),
    'S': bytearray([0x24, 0x2A, 0x2A, 0x12]),
    'T': bytearray([0x02, 0x02, 0x3E, 0x02, 0x02]),
    'U': bytearray([0x1E, 0x20, 0x20, 0x1E]),
    'V': bytearray([0x06, 0x18, 0x20, 0x18, 0x6]),
    'W': bytearray([0x1E, 0x20, 0x1E, 0x20, 0x1E]),
    'X': bytearray([0x36, 0x08, 0x08, 0x36]),
    'Y': bytearray([0x2E, 0x28, 0x28, 0x1E]),
    'Z': bytearray([0x32, 0x2A, 0x2A, 0x26])
}


class XY5TextScroller(object):
    def __init__(
            self,
            panel_addr_top=0,
            panel_addr_bottom=1,
            refresh_duration=0.1):
        self.panel_width = 28  # XY5Driver doesn't support different values.
        self.panel_addr_top = panel_addr_top
        self.panel_addr_bottom = panel_addr_bottom
        self.refresh_duration = refresh_duration
        self.driver = XY5Driver()

    def __text_to_bytes(self, text):
        # Loop over question string and add columns to text.
        text = text.upper()
        text_bytes = bytearray()
        for c in text:
            if c in CHARACTER_CONVERTER:
                text_bytes.extend(CHARACTER_CONVERTER[c])
                # Space between letters.
                text_bytes.append(0)

        # If question is fewer than 28 columns, pad it out with spaces.
        while len(text_bytes) < 28:
            text_bytes.extend(CHARACTER_CONVERTER[' '])
        return text_bytes

    def scroll_text(self, text_top, text_bottom):
      t = 0
      while True:
          # Every transmission should have these headers.
          transmission = bytearray([
              0x80,  # header
              0x83,  # 28 bytes, refresh
              self.panel_addr_top,  # address
          ])
          text_bytes = self.__text_to_bytes(text_top)
          for i in range(t, t + self.panel_width):
              transmission.append(text_bytes[i % len(text_bytes)])
          transmission.append(0x8F)  # End of Transmission byte.
          self.driver.send_custom_transmission(transmission)
          time.sleep(self.refresh_duration)

          # Every transmission should have these headers.
          transmission = bytearray([
              0x80,  # header
              0x83,  # 28 bytes, refresh
              self.panel_addr_bottom,  # address
          ])
          text_bytes = self.__text_to_bytes(text_bottom)
          for i in range(t, t + self.panel_width):
              transmission.append(text_bytes[i % len(text_bytes)])
          transmission.append(0x8F)  # End of Transmission byte.
          self.driver.send_custom_transmission(transmission)
          time.sleep(self.refresh_duration)

          t += 1


if __name__ == "__main__":
    scroller = XY5TextScroller()
    scroller.scroll_text(
        text_top="Hello              ",
        text_bottom="                 World")
