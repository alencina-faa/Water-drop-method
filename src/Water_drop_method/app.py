"""
A colection of scripts to implement the Water drop method to determine the strutural stability of soil aggregates
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class WaterDropMethod(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.show()

        
        camera = toga.Box()
        set_threshold = toga.Box()
        meaurement = toga.Box()
        
        container = toga.OptionContainer(
            content=[
                toga.OptionItem("Camera", camera),
                toga.OptionItem("Set Threshold", set_threshold),
                toga.OptionItem("Measurement", meaurement)

            ]
        )

        self.main_window.content = container




def main():
    return WaterDropMethod('Water Drop Method', 'ar.edu.unicen.faa.azul.waterdropmethod')

if __name__ == "__main__":
    main().main_loop()
