"""
A colection of scripts to implement the Water drop method to determine the strutural stability of soil aggregates
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from Camera import CameraOpenCV as cam
from DAC import NIUSB6009 as dac
from PIL import Image
import time

class WaterDropMethod(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window."""
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.show()

        
        camera_box = toga.Box(style=Pack(direction=ROW, margin=2, background_color='#f0f0f0'))
        set_threshold = toga.Box()
        meaurement = toga.Box()
        
        container = toga.OptionContainer(
            content=[
                toga.OptionItem("Camera", camera_box),
                toga.OptionItem("Set Threshold", set_threshold),
                toga.OptionItem("Measurement", meaurement)

            ]
        )

        self.main_window.content = container

        # Create the camera container
        camera_box_buttons = toga.Box(style=Pack(direction=COLUMN, margin=5))
        global camera
        camera = False
        start_preview_button = toga.Button(
            'Start Preview',
            on_press=self.start_preview,
            style=Pack(margin=5)
        )
        camera_box_buttons.add(start_preview_button)

        stop_preview_button = toga.Button(
            'Stop Preview',
            on_press=self.stop_preview,
            style=Pack(margin=5)
        )
        camera_box_buttons.add(stop_preview_button)
        camera_box.add(camera_box_buttons)

        self.preview = toga.ImageView()
        camera_box.add(self.preview)
#Ends main window content

#Starts funtion definitions
    def start_preview(self, widget):
        """Start the camera preview."""
        global camera
        if not camera:
            camera = cam(fps=1, width=640, height=480)
            camera.start(device=0)
        
        global conti
        conti = True
        while conti:
            img, wait_key = camera.preview_camera()
            self.preview.image = Image.fromarray(img)
            if wait_key == ord('q'):
                break
            

    def stop_preview(self, widget):
        """Stop the camera preview."""
        #global camera
        #if camera:
        global conti
        conti = False
        cam.close_window
        cam.stop
            #camera = False

        
        

    

def main():
    return WaterDropMethod('Water Drop Method', 'ar.edu.unicen.faa.azul.waterdropmethod')

if __name__ == "__main__":
    main().main_loop()

"""
x = cam(fps=1, width=640, height=480)

x.start(device=0)
print(x.path_name_save_video)
#x.take_write_snapshot()
x.path_name_save_video = "video.avi"
print(x.path_name_save_video)
x.preview_camera()

for i in range(10):
    x.take_write_snapshot()
    print(i)

#x.take_write_snapshot()
x.close_window
x.stop
"""
