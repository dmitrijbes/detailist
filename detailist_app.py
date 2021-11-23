import io
from base64 import b64encode
from sys import platform

import keyboard as kb
import numpy as np
import PySimpleGUI as gui
from psgtray import SystemTray
from PIL import Image as img
from PIL import ImageGrab as ig
from PIL import ImageChops as ic


class DetailistApp():
    def __init__(self):
        self.is_screenshot_1 = None
        self.is_screenshot_2 = None
        self.visible_window = None
        self.is_calculation_in_progress = False
        self.graph_1_key = None
        self.graph_2_key = None
        self.graph_diff_key = None
        self.screenshot_size = None
        self.diff_window_key = None
        self.about_window_key = None
        self.donate_window_key = None
        self.canvas_border_size = None

        self.init_assets()
        self.init_gui()
        self.init_graphs()
        self.init_tray()
        self.init_hotkeys()

    def init_assets(self):
        self.detailist_app_version = '1.0.0'
        self.icons_path = 'assets/icons/'
        with open('assets/detailist_icon.png', 'rb') as image:
            self.detailist_icon = b64encode(image.read())

    def get_diff_window(self):
        self.graph_1_key = 'graph_1'
        self.graph_2_key = 'graph_2'
        self.graph_diff_key = 'graph_diff'

        screen_one_third_h = int(gui.Window.get_screen_size()[1]//3)
        self.screenshot_size = (screen_one_third_h, screen_one_third_h)
        button_color = (gui.theme_background_color(),
                        gui.theme_background_color())
        diff_window = [
            [
                gui.Column([
                    [
                        gui.Button(image_filename=self.icons_path+'save_icon.png',
                                   button_color=button_color, button_type=gui.BUTTON_TYPE_SAVEAS_FILE, default_extension='png', enable_events=True, target='save_graph_1', tooltip='Save As', key='save_graph_1'),
                        gui.Button(image_filename=self.icons_path+'center_icon.png',
                                   button_color=button_color, tooltip='Center', key='center_graph_1'),
                        # TODO: Implement OCR.
                        gui.Button(image_filename=self.icons_path+'ocr_icon.png',
                                   button_color=button_color, disabled=True, tooltip='OCR', key='ocr_graph_1'),
                        gui.Button(image_filename=self.icons_path+'clear_icon.png',
                                   button_color=button_color, tooltip='Clear', key='clear_graph_1'),
                    ],
                    [
                        gui.Graph(
                            canvas_size=self.screenshot_size,
                            graph_bottom_left=(0, 400),
                            graph_top_right=(400, 0),
                            key=self.graph_1_key
                        )
                    ]
                ]),
                gui.Column([
                    [
                        gui.Button(image_filename=self.icons_path+'save_icon.png',
                                   button_color=button_color, button_type=gui.BUTTON_TYPE_SAVEAS_FILE, default_extension='png', enable_events=True, target='save_graph_2', tooltip='Save As', key='save_graph_2'),
                        gui.Button(image_filename=self.icons_path+'center_icon.png',
                                   button_color=button_color, tooltip='Center', key='center_graph_2'),
                        # TODO: Implement OCR.
                        gui.Button(image_filename=self.icons_path+'ocr_icon.png',
                                   button_color=button_color, disabled=True, tooltip='OCR', key='ocr_graph_2'),
                        gui.Button(image_filename=self.icons_path+'clear_icon.png',
                                   button_color=button_color, tooltip='Clear', key='clear_graph_2'),
                    ],
                    [
                        gui.Graph(
                            canvas_size=self.screenshot_size,
                            graph_bottom_left=(0, 400),
                            graph_top_right=(400, 0),
                            key=self.graph_2_key,
                        )
                    ]
                ])
            ],
            [
                gui.Column([
                    [
                        gui.Button(image_filename=self.icons_path+'save_icon.png', button_type=gui.BUTTON_TYPE_SAVEAS_FILE, default_extension='png',
                                   enable_events=True, target='save_graph_diff', button_color=button_color, tooltip='Save As', key='save_graph_diff'),
                        gui.Button(image_filename=self.icons_path+'calculate_diff_icon.png',
                                   button_color=button_color, tooltip='Calculate Difference', key='calculate_diff'),
                        # TODO: Implement Auto Centering.
                        gui.Button(image_filename=self.icons_path+'auto_center_icon.png', disabled=True,
                                   button_color=button_color, tooltip='Auto Center', key='auto_center'),
                    ],
                    [
                        gui.Graph(
                            canvas_size=self.screenshot_size,
                            graph_bottom_left=(0, 400),
                            graph_top_right=(400, 0),
                            key=self.graph_diff_key
                        )
                    ]
                ]),
                gui.Column(
                    [
                        [
                            gui.Text('Comparison:'),
                            gui.Combo(['Heatmap', 'Opacity'],
                                      default_value='Heatmap', tooltip='Comparison Mode', readonly=True),
                            gui.Slider(range=(1, 100), orientation='h', disable_number_display=True,
                                       default_value=50, tooltip='Comparison Strenght')
                        ],
                        [
                            gui.Multiline(
                                disabled=True,
                                size=(int(screen_one_third_h//7.5), 12),
                                default_text='Drag an image using mouse.\nClick on image and move it using arrow keys.\nHold Ctrl while using arrow keys to increase movement speed.')
                        ]
                    ],
                    vertical_alignment='bottom'
                )
            ]
        ]

        self.diff_window_key = 'diff_window'
        return diff_window

    def get_about_window(self):
        # TODO: Add info about Detailist.
        about_window = [
            [
                gui.Image(self.detailist_icon)
            ],
            [
                gui.Text('ver. ' + self.detailist_app_version)
            ],
            [
                gui.Text(
                    text='Detailist is a simple tool that allows to take screenshots,'
                    ' compare images using heatmap of differences and extract images text (OCR).',
                    size=self.text_size)
            ]]

        self.about_window_key = 'about_window'
        return about_window

    def get_donate_window(self):
        # TODO: Add donation info.
        donate_window = [
            [
                gui.Image(self.icons_path+'donate_icon.png')
            ],
            [
                gui.Text(
                    'Ipsum exercitation labore adipisicing laboris eu occaecat tempor qui nostrud cupidatat est.', size=self.text_size)
            ]
        ]

        self.donate_window_key = 'donate_window'
        return donate_window

    def fix_taskbar_icon(self):
        # Fix taskbar icon for Windows.
        if platform.startswith('win'):
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                u'detailist')  # Arbitrary string.

    def init_gui(self):
        gui.theme('Material1')
        gui.set_global_icon(self.detailist_icon)
        self.fix_taskbar_icon()

        self.text_size = (60, 3)
        about_window = self.get_about_window()
        donate_window = self.get_donate_window()
        diff_window = self.get_diff_window()

        self.visible_window = self.about_window_key
        layout = [[gui.Column(about_window, element_justification='center', visible=False, key=self.about_window_key),
                   gui.Column(donate_window, element_justification='center',
                              visible=False, key=self.donate_window_key),
                   gui.Column(diff_window, visible=False, key=self.diff_window_key)]]

        screen_quarter_w = int(gui.Window.get_screen_size()[0]//4)
        self.window = gui.Window('Detailist', layout, finalize=True,
                                 enable_close_attempted_event=True, location=(screen_quarter_w, 50))

        # TODO: Do not show a window at startup.
        self.window.hide()

    def canvas_click(self, event, canvas):
        canvas.scan_mark(event.x, event.y)
        canvas.focus_set()

    def init_canvas(self, canvas):
        self.canvas_border_size = 1
        canvas.config(highlightthickness=self.canvas_border_size)
        canvas.configure(xscrollincrement='1')
        canvas.configure(yscrollincrement='1')
        canvas.bind('<ButtonPress-1>',
                    lambda event: self.canvas_click(event, canvas))
        canvas.bind('<B1-Motion>',
                    lambda event: canvas.scan_dragto(event.x, event.y, gain=1))
        canvas.bind('<ButtonRelease-1>',
                    lambda _: self.calculate_screenshots_diff())
        canvas.bind('<Left>',
                    lambda _: [canvas.xview_scroll(-1, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Right>',
                    lambda _: [canvas.xview_scroll(1, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Up>',
                    lambda _: [canvas.yview_scroll(-1, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Down>',
                    lambda _: [canvas.yview_scroll(1, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Control-Key-Left>',
                    lambda _: [canvas.xview_scroll(-10, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Control-Key-Right>',
                    lambda _: [canvas.xview_scroll(10, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Control-Key-Up>',
                    lambda _: [canvas.yview_scroll(-10, 'units'), self.calculate_screenshots_diff()])
        canvas.bind('<Control-Key-Down>',
                    lambda _: [canvas.yview_scroll(10, 'units'), self.calculate_screenshots_diff()])

    def init_graphs(self):
        self.graph_1 = self.window.Element(self.graph_1_key)
        self.init_canvas(self.graph_1.tk_canvas)
        self.is_screenshot_1 = False

        self.graph_2 = self.window.Element(self.graph_2_key)
        self.init_canvas(self.graph_2.tk_canvas)
        self.is_screenshot_2 = False

        self.graph_diff = self.window.Element(self.graph_diff_key)
        self.graph_diff.tk_canvas.config(highlightthickness=1)

        if len(self.screenshot_size) >= 2:
            graph_help_text = 'Press Ctrl + Print Screen to Take a Screenshot\nPress Ctrl + Alt + Print Screen to Clear the last Screenshot'
            graph_help_location = (self.screenshot_size[0]/2,
                                   self.screenshot_size[1]/2)
            self.graph_1.draw_text(graph_help_text, graph_help_location)
            self.graph_2.draw_text(graph_help_text, graph_help_location)

            graph_diff_help_text = 'Take two Screenshots to Compare them'
            self.graph_diff.draw_text(
                graph_diff_help_text, graph_help_location)

    def init_tray(self):
        # psgtray throws exception without first empty element.
        tray_menu = ['', ['Compare Screenshots', 'Donate', 'About', 'Exit']]
        # TODO: Change icon.
        self.tray = SystemTray(tray_menu, single_click_events=False,
                               window=self.window, tooltip='Detailist', icon=self.detailist_icon)

    def init_hotkeys(self):
        kb.add_hotkey('ctrl+print screen', self.create_screenshot)
        kb.add_hotkey('ctrl+alt+print screen', self.clear_screenshot)

    def start(self):
        while True:
            event, values = self.window.read()

            print('~~EVENT~~')
            print(event)
            print(values)

            if event == self.tray.key and values:
                event = values[event]
            if event in ('Exit', gui.WIN_CLOSED):
                break

            if event in ('Compare Screenshots', gui.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self.open_window(self.diff_window_key)
            elif event == 'Donate':
                self.open_window(self.donate_window_key)
            elif event == 'About':
                self.open_window(self.about_window_key)
            elif event == gui.WIN_CLOSE_ATTEMPTED_EVENT:
                self.window.hide()
                self.tray.show_icon()
            elif event in ('save_graph_1', 'save_graph_2', 'save_graph_diff'):
                self.save_graph(event, values[event])
            elif event in ('center_graph_1', 'center_graph_2'):
                self.center_graph(event)
            elif event == 'calculate_diff':
                self.calculate_screenshots_diff()
            elif event in ('clear_graph_1', 'clear_graph_2'):
                self.clear_graph(event)

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

    def clear_graph(self, event):
        is_clear = gui.popup_yes_no(
            'Are you sure you want to clear screenshot?')
        if is_clear != 'Yes':
            return

        if event == 'clear_graph_1':
            self.graph_1.erase()
            self.is_screenshot_1 = False
        elif event == 'clear_graph_2':
            self.graph_2.erase()
            self.is_screenshot_2 = False

    def center_graph(self, event):
        if event == 'center_graph_1':
            self.graph_1.tk_canvas.xview_moveto(self.canvas_border_size)
            self.graph_1.tk_canvas.yview_moveto(self.canvas_border_size)
        elif event == 'center_graph_2':
            self.graph_2.tk_canvas.xview_moveto(self.canvas_border_size)
            self.graph_2.tk_canvas.yview_moveto(self.canvas_border_size)

    def save_graph(self, event, path):
        if not path:
            return

        if event == 'save_graph_1':
            graph = self.graph_1
        elif event == 'save_graph_2':
            graph = self.graph_2
        elif event == 'save_graph_diff':
            graph = self.graph_diff

        graph_image = self.get_element_image(graph)
        graph_image.save(path, format='PNG')

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
        graph.erase()
        graph.draw_image(
            data=screenshot_data.getvalue(), location=(0, 0))
        self.tray.show_message('Detailist', 'Screenshot captured.')

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

        screenshot_data = io.BytesIO()
        screenshot_diff.save(screenshot_data, format='PNG')

        self.graph_diff.erase()
        self.graph_diff.draw_image(
            data=screenshot_data.getvalue(), location=(0, 0))
        self.is_calculation_in_progress = False
