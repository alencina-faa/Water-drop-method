"""
A collection of scripts to implement the Water drop method to determine the strutural stability of soil aggregates
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from Camera import CameraOpenCV as cam
from DAC import NIUSB6009 as dac
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class WaterDropMethod(toga.App):
    def startup(self):
        """Create the main window and set its content."""        
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

        #Create the set threshold container
        threshold_box_buttons = toga.Box(style=Pack(direction=COLUMN, margin=5))
        measures_label = toga.Label(
            'Number of measures',
            style=Pack(margin=(0, 5))
        )
        threshold_box_buttons.add(measures_label)

        self.measures_input = toga.TextInput(
            value=5000,
            placeholder='5000',
            style=Pack(flex=1, margin=(0, 5))
        )
        threshold_box_buttons.add(self.measures_input)

        start_measure_button = toga.Button(
            'Start Measure',
            on_press=self.start_measure,
            style=Pack(margin=5)
        )
        threshold_box_buttons.add(start_measure_button)

        set_threshold.add(threshold_box_buttons)

        self.threshold = toga.ImageView()
        set_threshold.add(self.threshold)

#Ends main window content

#Starts funtion definitions
    #Functions of the camera container
    def start_preview(self, widget):
        """Start the camera preview."""
        cam.close_window
        cam.stop
        dac.stop
        dac.close
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
        global conti
        conti = False
        self.preview.image = None
        cam.close_window
        cam.stop
        


    #Functions of the set threshold container
    def start_measure(self, widget):
        """Start the measurement."""
        # Get the number of measures from the input field
        try:
            measures = int(self.measures_input.value)
            if measures <= 0:
                raise ValueError("Number of measures must be positive.")
        except ValueError:
            self.measures_input.value = "Invalid input!"
            return

        # Start the measurement process
        #measurer = dac(device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=measures)
        #measurer.start()
        #Desabilitados para prueba
        rng = np.random.default_rng()
        i = 0
        values=[]
        while i < int(self.measures_input.value):
                
            value =rng.random()#measurer.measure()
            
            values.append([i,value])
            
            
            
            i += 1

        values = np.array(values)
        #measurer.stop()
        #measurer.close()

        def onclick(event):
            global iy
            iy = event.ydata
            
            fig.canvas.mpl_disconnect(cid)
            return

        isok = 'n'
        while isok == 'n':
            plt.ion()
            fig = plt.figure(1)
            ax = fig.add_subplot(111)
            ax.plot(values[:,0],values[:,1])
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #self.threshold.image = fig.show()
            #cid = fig.canvas.mpl_connect('button_press_event', onclick)
            #plt.pause(10)
            
            
            #ax.plot(values[:,0],values[:,1]*0+iy)
            #plt.pause(10)

            resp= input("\n¿Estás de acuerdo con el umbral seleccionado? Sí (s); No (n): ")
            if resp == 's':
                isok = 's'
            
            plt.close()

        

    

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
