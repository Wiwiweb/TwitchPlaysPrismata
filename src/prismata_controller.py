from time import sleep

import pyautogui
import pywinauto
import pyscreenshot as ImageGrab

from globals import config, log, test_mode

class PrismataController:

    prismata_window = pywinauto.Application(backend='uia').connect(title='Prismata').Prismata

    @staticmethod
    def press(key):
        PrismataController.prismata_window.set_focus()
        pyautogui.press(key)

    @staticmethod
    def click(column, horizontal):
        # Map the command coordinate of range 0-1000
        # to a pixel from the range horizontal_start to horizontal_end
        horizontal_start = int(config['Screen positions']['horizontal_start'])
        horizontal_end = int(config['Screen positions']['horizontal_end'])
        horizontal_range = horizontal_end - horizontal_start
        x = round((horizontal * horizontal_range / 1000) + horizontal_start)
        y = int(config['Screen positions']['column_{}'.format(column)])
        PrismataController.prismata_window.set_focus()
        pyautogui.click(x=x, y=y)

    @staticmethod
    def hotkey(modifier, key):
        PrismataController.prismata_window.set_focus()
        pyautogui.hotkey(modifier, key)

    @staticmethod
    def post_startup():
        PrismataController.prismata_window.set_focus()
        # PrismataController.click_position('dismiss_patch_notes')

    @staticmethod
    def vs_computer():
        PrismataController.prismata_window.set_focus()
        PrismataController.click_position('battle_tab')
        PrismataController.click_position('vs_computer')
        PrismataController.click_position('select_cpu')
        PrismataController.click_position('select_masterbot_7s')
        PrismataController.click_position('standard_set')
        PrismataController.click_position('select_time_limit')
        pyautogui.typewrite('60')
        PrismataController.click_position('vs_cpu_start_match')

    @staticmethod
    def split_unit_tab():
        while not PrismataController.pixel_equals_colour('unit_tab_separator'):
            pyautogui.hotkey('ctrl', 'tab')

    @staticmethod
    def check_and_restart_match():
        if PrismataController.pixel_equals_colour('return_to_lobby'):
            PrismataController.click_position('return_to_lobby')
            sleep(2)
            PrismataController.click_position('vs_cpu_start_match')

    @staticmethod
    def click_position(position_name):
        coordinates = config['Screen positions'][position_name]
        x, y = coordinates.split(',')
        log.debug('clicking {}'.format(position_name))
        pyautogui.click(x=int(x), y=int(y))

    @staticmethod
    def pixel_colour(coordinates):
        box = coordinates + (coordinates[0] + 1, coordinates[1] + 1)
        image = ImageGrab.grab(bbox=box)
        return image.getpixel((0, 0))

    @staticmethod
    def pixel_equals_colour(position_name):
        coordinates = config['Screen positions'][position_name]
        coordinates = tuple(map(int, coordinates.split(',')))
        colours = PrismataController.pixel_colour(coordinates)
        expected_colours = config['Colours'][position_name]
        expected_colours = tuple(map(int, expected_colours.split(',')))
        log.debug('{}: expected {} got {}'.format(position_name, colours, expected_colours))
        return colours == expected_colours
60