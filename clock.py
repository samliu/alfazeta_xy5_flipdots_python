from xy5_driver import XY5Driver
from datetime import datetime
import numpy as np
import time

# These are 7-segment display numbers and letters. The numbers and colon are all
# 5x3 matrices, and we simply choose what 5x3 slice of the master 14x28 array to
# replace, to write the number.
#
# The AM/PM are slightly different. A and P are 4x3, and M is 4x5.
clock_numbers = {
    "0": np.array([[1, 1, 1], [1, 0, 1], [1, 0, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int8),
    "1": np.array([[1, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [1, 1, 1]], dtype=np.int8),

    "2": np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [1, 0, 0], [1, 1, 1]], dtype=np.int8),
    "3": np.array([[1, 1, 1], [0, 0, 1], [1, 1, 1], [0, 0, 1], [1, 1, 1]], dtype=np.int8),
    "4": np.array([[1, 0, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]], dtype=np.int8),
    "5": np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1], [0, 0, 1], [1, 1, 1]], dtype=np.int8),
    "6": np.array([[1, 0, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int8),
    "7": np.array([[1, 1, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype=np.int8),
    "8": np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int8),
    "9": np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [0, 0, 1], [0, 0, 1]], dtype=np.int8),
    ":": np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.int8),
    "A": np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 1]], dtype=np.int8),
    "M": np.array([[1, 0, 0, 0, 1], [1, 1, 0, 1, 1], [1, 0, 1, 0, 1], [1, 0, 0, 0, 1]], dtype=np.int8),
    "P": np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1], [1, 0, 0]], dtype=np.int8),
}

# Set to True if you want the clock numbers to be black and the rest to be
# white.
INVERT = False
SHOW_SECONDS = False

if __name__ == "__main__":
    driver = XY5Driver()

    while True:
        arr = np.zeros([14, 28], dtype=np.int8)

        date_str = datetime.now().strftime("%I:%M%p")
        if SHOW_SECONDS:
          # With seconds.
          date_str = datetime.now().strftime("%I:%M%S%p")

        if date_str.startswith('00'):
            date_str = list(date_str)
            date_str[0] = '1'
            date_str[1] = '2'
        date_str = list(date_str)


        if not SHOW_SECONDS:
            # No seconds; hour and minute only.
            #
            # Remember, matrices are row x column, so the X,Y is flipped. That
            # said, I found it easier to decide the 0-indexed coordinates ahead of
            # time, so they are in the comments.
            #
            # (1,3), 5x3 digit.
            arr[2:7, 1:4] = clock_numbers[date_str[0]]
            # (5,3), 5x3 digit.
            arr[2:7, 5:8] = clock_numbers[date_str[1]]
            # (9,3), 5x3 dots.
            arr[2:7, 9:12] = clock_numbers[date_str[2]]
            # (13,3), 5x3 digit.
            arr[2:7, 13:16] = clock_numbers[date_str[3]]
            # (17,3), 5x3 digit.
            arr[2:7, 17:20] = clock_numbers[date_str[4]]

            # (18, 9), 4x3 letter {A, P}.
            arr[8:12, 18:21] = clock_numbers[date_str[5]]
            # (22, 9), 4x5 letter M.
            arr[8:12, 22:27] = clock_numbers[date_str[6]]
        else:
            # (1,3), 5x3 digit.
            arr[2:7, 1:4] = clock_numbers[date_str[0]]
            # (5,3), 5x3 digit.
            arr[2:7, 5:8] = clock_numbers[date_str[1]]
            # (9,3), 5x3 dots.
            arr[2:7, 8:11] = clock_numbers[date_str[2]]
            # (13,3), 5x3 digit.
            arr[2:7, 11:14] = clock_numbers[date_str[3]]
            # (17,3), 5x3 digit.
            arr[2:7, 15:18] = clock_numbers[date_str[4]]

            # Seconds, 5x3 digits.
            arr[2:7, 20:23] = clock_numbers[date_str[5]]
            arr[2:7, 24:27] = clock_numbers[date_str[6]]

            # (18, 9), 4x3 letter {A, P}.
            arr[8:12, 18:21] = clock_numbers[date_str[7]]
            # (22, 9), 4x5 letter M.
            arr[8:12, 22:27] = clock_numbers[date_str[8]]



        if INVERT:
          arr = abs(arr-1)

        driver.paint_14x28(arr)

        # Update every 1 second.
        time.sleep(1)
