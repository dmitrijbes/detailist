import io

import keyboard as kb
import numpy as np
import PySimpleGUI as gui
from psgtray import SystemTray
from PIL import Image as img
from PIL import ImageGrab as ig
from PIL import ImageChops as ic
from PIL import ImageTk as it


class DetailistApp():
    def __init__(self):
        self.is_screenshot_1 = None
        self.is_screenshot_2 = None
        self.visible_window = None
        self.is_calculation_in_progress = False

        self.init_gui()
        self.init_graphs()
        self.init_tray()
        self.init_hotkeys()

    def init_gui(self):
        gui.theme('Material1')

        # TODO: Add info about Detailist.
        about_window = [[
            gui.Text(
                text='Detailist is a simple tool that allows to take screenshots,'
                ' compare images using heatmap of differences and extract images text (OCR).',
                size=(60, 2))
        ]]

        self.graph_1_key = 'graph_1'
        self.graph_2_key = 'graph_2'
        self.screenshot_diff_key = 'screenshot_diff'
        screenshot_size = (400, 400)
        diff_window = [
            [gui.Text('Capture two screenshots')],
            [
                gui.Graph(
                    canvas_size=screenshot_size,
                    graph_bottom_left=(0, 400),
                    graph_top_right=(400, 0),
                    key=self.graph_1_key),
                gui.Graph(
                    canvas_size=screenshot_size,
                    graph_bottom_left=(0, 400),
                    graph_top_right=(400, 0),
                    key=self.graph_2_key)
            ],
            [
                gui.Image(size=screenshot_size, visible=False,
                          key=self.screenshot_diff_key)
            ]
        ]

        self.about_window_key = 'about_window'
        self.diff_window_key = 'diff_window'
        self.visible_window = self.about_window_key
        layout = [[gui.Column(about_window, visible=False, key=self.about_window_key), gui.Column(
            diff_window, visible=False, element_justification='center', key=self.diff_window_key)]]
        self.window = gui.Window('Detailist', layout, finalize=True,
                                 enable_close_attempted_event=True)

        # TODO: Do not show a window at startup.
        self.window.hide()

    def canvas_click(self, event, canvas):
        canvas.scan_mark(event.x, event.y)
        canvas.focus_set()

    def init_canvas(self, canvas):
        canvas.configure(xscrollincrement='1')
        canvas.configure(yscrollincrement='1')
        canvas.bind('<ButtonPress-1>',
                    lambda event: self.canvas_click(event, canvas))
        canvas.bind("<B1-Motion>",
                    lambda event: canvas.scan_dragto(event.x, event.y, gain=1))
        canvas.bind("<ButtonRelease-1>",
                    lambda _: self.calculate_screenshots_diff())
        canvas.bind("<Left>",
                    lambda _: [canvas.xview_scroll(-1, "units"), self.calculate_screenshots_diff()])
        canvas.bind("<Right>",
                    lambda _: [canvas.xview_scroll(1, "units"), self.calculate_screenshots_diff()])
        canvas.bind("<Up>",
                    lambda _: [canvas.yview_scroll(-1, "units"), self.calculate_screenshots_diff()])
        canvas.bind("<Down>",
                    lambda _: [canvas.yview_scroll(1, "units"), self.calculate_screenshots_diff()])

    def init_graphs(self):
        self.graph_1 = self.window.Element(self.graph_1_key)
        self.init_canvas(self.graph_1.tk_canvas)
        self.is_screenshot_1 = False

        self.graph_2 = self.window.Element(self.graph_2_key)
        self.init_canvas(self.graph_2.tk_canvas)
        self.is_screenshot_2 = False

    def init_tray(self):
        # psgtray throws exception without first empty element.
        tray_menu = ['', ['Compare Screenshots', 'About', 'Exit']]
        # TODO: Change icon.
        self.tray = SystemTray(tray_menu, single_click_events=False,
                               window=self.window, tooltip='Detailist', icon='detailist_icon.png')

    def init_hotkeys(self):
        kb.add_hotkey('ctrl+print screen', self.create_screenshot)
        kb.add_hotkey('ctrl+alt+print screen', self.clear_screenshot)

    def start(self):
        while True:
            event, values = self.window.read()

            if event == self.tray.key and values:
                event = values[event]
            if event in ('Exit', gui.WIN_CLOSED):
                break

            if event in ('Compare Screenshots', gui.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self.open_window(self.diff_window_key)
            elif event == 'About':
                self.open_window(self.about_window_key)
            elif event == gui.WIN_CLOSE_ATTEMPTED_EVENT:
                self.window.hide()
                self.tray.show_icon()

        self.stop()

    def stop(self):
        self.tray.close()
        self.window.close()

    def open_window(self, next_window):
        self.window[self.visible_window].update(visible=False)
        self.window[next_window].update(visible=True)
        self.visible_window = next_window
        self.window.un_hide()
        self.window.bring_to_front()

    def clear_screenshot(self):
        if self.is_screenshot_2:
            self.graph_2.erase()
            self.is_screenshot_2 = False
            return

        if self.is_screenshot_1:
            self.graph_1.erase()
            self.is_screenshot_1 = False
            return

    def create_screenshot(self):
        if self.is_screenshot_1 and self.is_screenshot_2:
            self.tray.show_message(
                'Detailist', 'Clear one of the captured screenshots to take a new one.')
            return

        screenshot = ig.grab()
        screenshot_data = io.BytesIO()
        screenshot.save(screenshot_data, format='PNG')

        graph = self.graph_2 if self.is_screenshot_1 else self.graph_1
        graph.draw_image(
            data=screenshot_data.getvalue(), location=(0, 0))
        tray_message = (
            'Second screenshot saved!' if self.is_screenshot_1 else 'First screenshot saved!')
        self.tray.show_message('Detailist', tray_message)

        if self.is_screenshot_1:
            self.is_screenshot_2 = True
        else:
            self.is_screenshot_1 = True

        if self.is_screenshot_2:
            self.open_window(self.diff_window_key)
            self.calculate_screenshots_diff()

    def get_element_image(self, element):
        self.window.bring_to_front()
        widget = element.Widget
        bbox = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx(
        ) + widget.winfo_width(), widget.winfo_rooty() + widget.winfo_height())

        return ig.grab(bbox=bbox)

    def highlight_diff(self, image):
        image_data = np.array(image.convert('RGB'))
        red, green, blue = image_data.T
        non_black_areas = (red != 0) | (blue != 0) | (green != 0)
        image_data[non_black_areas.T] = (255, 0, 0)

        return img.fromarray(image_data)

    def calculate_screenshots_diff(self):
        if not self.is_screenshot_1 or not self.is_screenshot_2:
            return
        if self.is_calculation_in_progress:
            return
        self.is_calculation_in_progress = True

        screenshot_1 = self.get_element_image(self.graph_1)
        screenshot_2 = self.get_element_image(self.graph_2)
        screenshot_diff = ic.difference(screenshot_1, screenshot_2)

        screenshot_diff = self.highlight_diff(screenshot_diff)
        tk_image = it.PhotoImage(image=screenshot_diff)
        self.window[self.screenshot_diff_key].update(data=tk_image)
        self.window[self.screenshot_diff_key].update(visible=True)
        self.is_calculation_in_progress = False
