import time

import numpy as np
import PySimpleGUI as sg
from PIL import ImageGrab as ig
from PIL import ImageChops as ic
from PIL import Image as img
from PIL import ImageTk as it


def build_layout():
    sg.theme('Material1')

    layout = [[sg.Text('Click button to take screenshot!')],
              [sg.Button('Take Screenshot')],
              [sg.Image(key='screenshot_diff')]]

    return layout


def main():
    window = sg.Window('Detailist', build_layout())

    while True:
        event, _ = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == 'Take Screenshot':
            screenshot1 = ig.grab()
            time.sleep(5)
            screenshot2 = ig.grab()

            screenshot_diff = ic.difference(screenshot1, screenshot2)

            screenshot_data = np.array(screenshot_diff.convert('RGB'))
            red, green, blue = screenshot_data.T
            non_black_areas = (red != 0) | (blue != 0) | (green != 0)
            screenshot_data[non_black_areas.T] = (255, 0, 0)
            screenshot_diff = img.fromarray(screenshot_data)

            tk_image = it.PhotoImage(image=screenshot_diff)
            window['screenshot_diff'].update(data=tk_image)

    window.close()


if __name__ == '__main__':
    main()
