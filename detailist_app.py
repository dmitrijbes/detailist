import pystray as tray
import keyboard as kb
import numpy as np
import PySimpleGUI as gui
from PIL import Image as img
from PIL import ImageGrab as ig
from PIL import ImageChops as ic
from PIL import ImageTk as it


class DetailistApp():
    def __init__(self):
        self.init_gui()
        self.init_hotkeys()
        self.create_tray_entry()

    def init_gui(self):
        gui.theme('Material1')

    def init_hotkeys(self):
        kb.add_hotkey('print screen', self.create_screenshot)

    def create_tray_entry(self):
        # TODO: Change icon.
        tray_icon = img.open('detailist_icon.png')
        tray_menu = tray.Menu(
            tray.MenuItem('Take a Screenshot',
                          self.create_screenshot, default=True),
            tray.MenuItem('About', self.open_about_window),
            tray.MenuItem('Exit', self.stop))
        self.tray_entry = tray.Icon(
            'detailist', tray_icon, 'Detailist', tray_menu)

    def start(self):
        self.tray_entry.run()

    def stop(self):
        self.tray_entry.stop()

    def open_about_window(self):
        # TODO: Add info about Detailist.
        about_layout = [[gui.Text(text='Some info about Detailist')]]
        about_window = gui.Window('About Detailist', about_layout)

        while True:
            event, _ = about_window.read(timeout=400)
            if event == gui.WIN_CLOSED:
                break

        about_window.close()

    def open_diff_window(self):
        print('open diff')
        pass
        # layout = [
        #     [sg.Image(key='screenshot_diff', source='./bla.png')]]

        # window = sg.Window('Detailist', build_layout(), finalize=True,
        #                    no_titlebar=True, location=(0, 0), keep_on_top=True)
        # window.Maximize()

        # while True:
        #     event, _ = window.read()
        #     if event == sg.WIN_CLOSED:
        #         break

        # window.close()

    def create_screenshot(self):
        print('creating screen')
        return
        # screenshot1 = ig.grab()
        # time.sleep(5)
        # screenshot2 = ig.grab()

        # screenshot_diff = ic.difference(screenshot1, screenshot2)

        # screenshot_data = np.array(screenshot_diff.convert('RGB'))
        # red, green, blue = screenshot_data.T
        # non_black_areas = (red != 0) | (blue != 0) | (green != 0)
        # screenshot_data[non_black_areas.T] = (255, 0, 0)
        # screenshot_diff = img.fromarray(screenshot_data)

        # tk_image = it.PhotoImage(image=screenshot_diff)
        # window['screenshot_diff'].update(data=tk_image)
