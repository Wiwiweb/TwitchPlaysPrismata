import pyautogui
import pywinauto

class PrismataController:

    prismata_window = pywinauto.Application(backend='uia').connect(title='Prismata').Prismata

    @staticmethod
    def press(key):
        PrismataController.prismata_window.set_focus()
        pyautogui.press(key)

    # @staticmethod
    # def click(x, y):
    #     pyautogui.click(x=x, y=y)
