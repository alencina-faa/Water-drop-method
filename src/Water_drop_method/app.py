import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.filedialog as fd
from PIL import Image, ImageTk
from Camera import CameraOpenCV as cam
from DAC import NIUSB6009 as dac
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import cv2
import math


class WaterDropMethod:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Drop Method")
        self.root.geometry("800x600")
        
        # Create notebook (tab container)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create the three tabs
        self.camera_frame = ttk.Frame(self.notebook)
        self.threshold_frame = ttk.Frame(self.notebook)
        self.measurement_frame = ttk.Frame(self.notebook)
        self.drop_energy_frame = ttk.Frame(self.notebook)
        self.video_processing_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.camera_frame, text="Camera")
        self.notebook.add(self.threshold_frame, text="Set Threshold")
        self.notebook.add(self.measurement_frame, text="Measurement")
        self.notebook.add(self.drop_energy_frame, text="Drop Energy")
        self.notebook.add(self.video_processing_frame, text="Video Processing")
        
        # Setup Camera tab
        self.setup_camera_tab()
        
        # Setup Threshold tab
        self.setup_threshold_tab()

        # Setup Measurement tab
        self.setup_measurement_tab()
        
        # Setup Drop energy tab
        self.setup_drop_energy_tab()
        
        # Setup Video processing tab
        self.setup_video_proc_tab()
        
        # Global camera variable
        self.camera = False
        
        # Variable to store threshold value
        self.threshold_value = None

        # Canvas to display the image and draw the hole area
        self.canvas_hole_area = None
        self.selected_image_hole_area = None

        # Frame display the video video for hole area selection
        self.video_label_hole_area = None

        # Widgets created dynamically in Video Processing tab
        self.slider = None
        self.hole_area_confirm_button = None
#Ends the mainwindow definitions

#STARTS THE TABS DEFINITIONS
# Setup the camera tab
    def setup_camera_tab(self):
        # Create a frame for buttons
        camera_buttons_frame = ttk.Frame(self.camera_frame)
        camera_buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add buttons
        start_preview_button = ttk.Button(
            camera_buttons_frame,
            text='Start Preview',
            command=self.start_preview
        )
        start_preview_button.pack(pady=5)
        
        stop_preview_button = ttk.Button(
            camera_buttons_frame,
            text='Stop Preview',
            command=self.stop_preview
        )
        stop_preview_button.pack(pady=5)

        # Add device selection dropdown
        device_frame = ttk.Frame(camera_buttons_frame)
        device_frame.pack(pady=5)
        
        device_label = ttk.Label(device_frame, text="Camera Device:")
        device_label.pack(side=tk.TOP)
        
        self.device_var = tk.StringVar(value="0")
        self.device_combo = ttk.Combobox(
            device_frame,
            textvariable=self.device_var,
            values=["0", "1", "2"],
            width=5,
            state="readonly"
        )
        self.device_combo.pack(side=tk.TOP)
        
        # Create a frame for the preview image
        self.preview_frame = ttk.Frame(self.camera_frame)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create a label to display the camera preview
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

# Setup the threshold tab    
    def setup_threshold_tab(self):
        # Create a frame for controls
        threshold_controls_frame = ttk.Frame(self.threshold_frame)
        threshold_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add DAC selection dropdown
        DAC_frame_threshold = ttk.Frame(threshold_controls_frame)
        DAC_frame_threshold.pack(pady=5)
        
        DAC_label_threshold = ttk.Label(DAC_frame_threshold, text="DAC Device:")
        DAC_label_threshold.pack(side=tk.TOP)
        
        self.DAC_var_threshold = tk.StringVar(value="Test")
        self.DAC_combo_threshold = ttk.Combobox(
            DAC_frame_threshold,
            textvariable=self.DAC_var_threshold,
            values=["Test", "NIUSB6009"],
            width=10,
            state="readonly"
        )
        self.DAC_combo_threshold.pack(side=tk.TOP)

        # Add label and input for number of measures
        measures_label = ttk.Label(
            threshold_controls_frame,
            text='Number of measures'
        )
        measures_label.pack(pady=(0, 5))
        
        self.measures_var = tk.StringVar(value="5000")
        self.measures_input = ttk.Entry(
            threshold_controls_frame,
            textvariable=self.measures_var
        )
        self.measures_input.pack(pady=(0, 5), fill=tk.X)
        
        # Add set threshold button
        set_threshold_button = ttk.Button(
            threshold_controls_frame,
            text='Set Threshold',
            command=self.set_threshold
        )
        set_threshold_button.pack(pady=5)
        
        # Add confirmation buttons for threshold
        self.confirm_frame = ttk.Frame(threshold_controls_frame)
        self.confirm_frame.pack(pady=5, fill=tk.X)
        
        # Use a dedicated name to avoid conflicts with other tabs
        self.threshold_confirm_button = ttk.Button(
            self.confirm_frame,
            text='Confirm Threshold',
            command=self.confirm_threshold,
            state=tk.DISABLED
        )
        self.threshold_confirm_button.pack(side=tk.LEFT, padx=2)
        
        # Create a frame for the threshold plot
        self.threshold_plot_frame = ttk.Frame(self.threshold_frame)
        self.threshold_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Setup the measurement tab
    def setup_measurement_tab(self):
        # Create a frame for controls
        measurement_controls_frame = ttk.Frame(self.measurement_frame)
        measurement_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add camera selection dropdown
        device_frame_measure = ttk.Frame(measurement_controls_frame)
        device_frame_measure.pack(pady=5)
        
        device_label = ttk.Label(device_frame_measure, text="Camera Device:")
        device_label.pack(side=tk.TOP)
        
        self.device_var_measure = tk.StringVar(value="0")
        self.device_combo_measure = ttk.Combobox(
            device_frame_measure,
            textvariable=self.device_var_measure,
            values=["0", "1", "2"],
            width=5,
            state="readonly"
        )
        self.device_combo_measure.pack(side=tk.TOP)
        
        # Add DAC selection dropdown
        DAC_frame_measure = ttk.Frame(measurement_controls_frame)
        DAC_frame_measure.pack(pady=5)
        
        DAC_label = ttk.Label(DAC_frame_measure, text="DAC Device:")
        DAC_label.pack(side=tk.TOP)
        
        self.DAC_var_measure = tk.StringVar(value="Test")
        self.DAC_combo_measure = ttk.Combobox(
            DAC_frame_measure,
            textvariable=self.DAC_var_measure,
            values=["Test", "NIUSB6009"],
            width=10,
            state="readonly"
        )
        self.DAC_combo_measure.pack(side=tk.TOP)
        
        # Add label and input for number of drops
        measures_drops_label = ttk.Label(
            measurement_controls_frame,
            text='Number of drops'
        )
        measures_drops_label.pack(pady=(0, 5))
        
        self.measures_drops = tk.StringVar(value="500")
        self.measures_drops_input = ttk.Entry(
            measurement_controls_frame,
            textvariable=self.measures_drops
        )
        self.measures_drops_input.pack(pady=(0, 5), fill=tk.X)

        # Add label and input for number of previous frames
        measures_frames_label = ttk.Label(
            measurement_controls_frame,
            text='Number of previous frames'
        )
        measures_frames_label.pack(pady=(0, 5))
        
        self.measures_frames = tk.StringVar(value="20")
        self.measures_frames_input = ttk.Entry(
            measurement_controls_frame,
            textvariable=self.measures_frames
        )
        self.measures_frames_input.pack(pady=(0, 5), fill=tk.X)

        # Add Save file button
        self.save_file_button = ttk.Button(
            measurement_controls_frame,
            text='Save File As',
            command=self.save_file_as
        )
        self.save_file_button.pack(pady=5)

        # Add Start Measurement button
        self.start_measurement_button = ttk.Button(
            measurement_controls_frame,
            text='Start Measurement',
            command=self.start_measurement,
            state=tk.DISABLED  # Initially disabled
        )
        self.start_measurement_button.pack(pady=5)

        # Add Stop Measurement button
        self.stop_measurement_button = ttk.Button(
            measurement_controls_frame,
            text='Stop Measurement',
            command=self.stop_measurement,
            state=tk.DISABLED  # Initially disabled
        )
        self.stop_measurement_button.pack(pady=5)

        # Create a frame for the measurement
        measured_drops_frame = ttk.Frame(self.measurement_frame)
        measured_drops_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add label output for number of drops registered
        self.measured_drops_label = ttk.Label(
            measured_drops_frame,
            text='Number of drops registered: ' + str(0)
        )
        self.measured_drops_label.pack(pady=(50, 5))

#Setup the drop energy tab
    def setup_drop_energy_tab(self):
        # Create a frame for controls
        drop_energy_controls_frame = ttk.Frame(self.drop_energy_frame)
        drop_energy_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Add label and input for Drop weight
        drops_weight_label = ttk.Label(
            drop_energy_controls_frame,
            text='Drop weight (mg)'
        )
        drops_weight_label.pack(pady=(0, 5))

        self.drops_weight = tk.StringVar(value="20.90395")
        self.drop_weight_input = ttk.Entry(
            drop_energy_controls_frame,
            textvariable=self.drops_weight
        )
        self.drop_weight_input.pack(pady=(0, 5), fill=tk.X)

        # Add label and input for Water density
        water_density_label = ttk.Label(
            drop_energy_controls_frame,
            text='Water density (kg)'
        )
        water_density_label.pack(pady=(0, 5))

        self.water_density = tk.StringVar(value="1000.0")
        self.water_density_input = ttk.Entry(
            drop_energy_controls_frame,
            textvariable=self.water_density
        )
        self.water_density_input.pack(pady=(0, 5), fill=tk.X)

        # Add label and input for Air density
        air_density_label = ttk.Label(
            drop_energy_controls_frame,
            text='Air density (kg)'
        )
        air_density_label.pack(pady=(0, 5))

        self.air_density = tk.StringVar(value="1.225")  
        self.air_density_input = ttk.Entry(
            drop_energy_controls_frame,
            textvariable=self.air_density
        )
        self.air_density_input.pack(pady=(0, 5), fill=tk.X)

        # Add label and input for Drag coefficient
        drag_coefficient_label = ttk.Label(
            drop_energy_controls_frame,
            text='Drag coefficient'
        )
        drag_coefficient_label.pack(pady=(0, 5))

        self.drag_coefficient = tk.StringVar(value="0.5207")  
        self.drag_coefficient_input = ttk.Entry(
            drop_energy_controls_frame,
            textvariable=self.drag_coefficient
        )
        self.drag_coefficient_input.pack(pady=(0, 5), fill=tk.X)

        # Add label and input for Drop height
        drop_height_label = ttk.Label(
            drop_energy_controls_frame,
            text='Drop height (cm)'
        )
        drop_height_label.pack(pady=(0, 5))

        self.drop_height = tk.StringVar(value="53")  
        self.drop_height_input = ttk.Entry(
            drop_energy_controls_frame,
            textvariable=self.drop_height
        )
        self.drop_height_input.pack(pady=(0, 5), fill=tk.X)

        # Add Start simulation button
        self.start_simulation_button = ttk.Button(
            drop_energy_controls_frame,
            text='Start Simulation',
            command=self.start_simulation
        )
        self.start_simulation_button.pack(pady=5)

        # Create a frame for the threshold plot
        self.simulation_plot_frame = ttk.Frame(self.drop_energy_frame)
        self.simulation_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Setup the video processing tab
    def setup_video_proc_tab(self):
        # Create a frame for video processing controls
        video_proc_controls_frame = ttk.Frame(self.video_processing_frame)
        video_proc_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Add Load Videos Folder button
        self.load_video_button = ttk.Button(
            video_proc_controls_frame,
            text='Load Videos Folder',
            command=self.load_video_folder
        )
        self.load_video_button.pack(pady=(0,15))
        


        # Add label, check and input for hole area
        hole_area_label = ttk.Label(
            video_proc_controls_frame,
            text='Hole Area (px^2)'
        )
        hole_area_label.pack(pady=(0, 5))

        # Create frame for input and check hole area controls
        hole_area_frame = ttk.Frame(video_proc_controls_frame)
        hole_area_frame.pack(pady=(0, 5))

        # Add input for hole area (load saved default if available)
        default_hole_area = self.load_hole_area_default() or 4000
        self.hole_area = tk.IntVar(value=default_hole_area)  # Use IntVar for numeric input
        self.hole_area_input = ttk.Entry(
            hole_area_frame,
            textvariable=self.hole_area,
            justify='center',
            width=8,
            state='disabled'  # Initially disabled
        )
        self.hole_area_input.pack(side=tk.LEFT, pady=(0, 5))

        check_var = tk.IntVar()
        self.hole_area_check = ttk.Checkbutton(
            hole_area_frame,
            text='Use this, or...',
            command= self.check_action,
            variable=check_var,  # Use IntVar for checkbox state
            state='disabled'  # Initially disabled
        )
        self.hole_area_check.pack(side=tk.RIGHT, pady=(0, 5))

        #Add label and drop down for Select video to set hole area
        self.set_hole_area_label = ttk.Label(
            video_proc_controls_frame,
            text='Select video to set hole area'
        )
        self.set_hole_area_label.pack(pady=(0, 5))

        self.video_selection = tk.StringVar()
        self.video_selection_dropdown = ttk.Combobox(
            video_proc_controls_frame,
            textvariable=self.video_selection,
            state= 'disabled' # Initially disabled
        )
        self.video_selection_dropdown.pack(pady=(0, 5))

        # Enable processing when a video is selected
        self.video_selection_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda event: self.process_videos_button.config(state=tk.NORMAL)
            )

        # Add process video button
        self.process_videos_button = ttk.Button(
            video_proc_controls_frame,
            text='Process Videos',
            command=self.process_videos
        )
        self.process_videos_button.pack(pady=(0, 5))
        self.process_videos_button.config(state=tk.DISABLED)  # Initially disabled


        # Create a frame for the video processing output
        self.video_output_frame = ttk.Frame(self.video_processing_frame)
        self.video_output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#ENDS THE TABS DEFINITIONS

#Functions for the camera tab
    def start_preview(self, *args):
        """Start the camera preview."""
        # Close any existing resources
        cam.close_window
        cam.stop
        dac.stop
        dac.close

        
        # Get selected device
        selected_device = int(self.device_var.get())
        
        # Initialize camera if not already done
        if not hasattr(self, 'camera') or not self.camera:
            self.camera = cam(fps=1, width=640, height=480)
            self.camera.start(device=selected_device)
        
        # Set flag to continue preview
        self.conti = True
        
        # Start the non-blocking update loop
        self.update_camera_preview()
    
    def stop_preview(self, *args):
        """Stop the camera preview."""
        # Set flag to stop the preview loop
        self.conti = False
        
        # Stop and close the camera if needed
        if hasattr(self, 'camera') and self.camera:
            self.camera.stop
            self.camera.close_window
            self.camera = None
            
        # Clear the preview image
        self.preview_label.configure(image='')

    def update_camera_preview(self):
        """Update the camera preview in a non-blocking way."""
        if hasattr(self, 'conti') and self.conti and hasattr(self, 'camera'):
            # Get frame from camera
            img, wait_key = self.camera.preview_camera()
            
            # Convert numpy array to PIL Image
            pil_img = Image.fromarray(img)
            
            # Convert PIL Image to Tkinter PhotoImage
            tk_img = ImageTk.PhotoImage(image=pil_img)
            
            # Update the label with the new image
            self.preview_label.configure(image=tk_img)
            self.preview_label.image = tk_img  # Keep a reference to prevent garbage collection
            
            # Schedule the next update
            self.root.after(30, self.update_camera_preview)  # ~33 FPS

 #Functions of the threshold tab   
    def set_threshold(self, *args):
        """Start the measurement and display the plot for threshold selection."""
        # Close any existing resources
        cam.close_window
        cam.stop
        dac.stop
        dac.close

        # Get the number of measures from the input field
        try:
            measures = int(self.measures_var.get())
            if measures <= 0:
                raise ValueError("Number of measures must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for measures.")
            return

        #Set procedure acording to the selected DAC
        if self.DAC_var_threshold.get() == "NIUSB6009":
            
            try:
                # Start the measurement process
                measurer = dac(device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=10000)
                measurer.start()
                
                i = 0
                values=[]
                while i < int(measures):
                        
                    value = measurer.measure()
                    
                    values.append([i,value])
                    
                    
                    
                    i += 1

                values = np.array(values)
                measurer.stop()
                measurer.close()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while measuring: {e}")
                return

        elif self.DAC_var_threshold.get() == "Test":
            # Start the test process
            file_path = os.path.join(os.path.dirname(__file__), "for_test.tsv")
            with open(file_path) as f:
                lines = f.readlines()
                values = np.array([list(map(float, line.split())) for line in lines])[:measures]

        # Store the values for later use
        self.measurement_values = values
        
        # Clear any existing plot
        for widget in self.threshold_plot_frame.winfo_children():
            widget.destroy()
        
        # Create a new matplotlib figure
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Plot the data
        self.ax.plot(values[:, 0], values[:, 1])
        self.ax.set_title("Click to set threshold level")
        
        # Create a canvas to display the figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.threshold_plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect the click event
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        
        # Disable the confirm button initially
        self.threshold_confirm_button.config(state=tk.DISABLED)
    
    def on_plot_click(self, event):
        """Handle click events on the plot."""
        if event.ydata is not None:
            # Store the threshold value
            self.threshold_value = event.ydata
            
            # Clear the previous plot
            self.ax.clear()
            
            # Redraw the data
            self.ax.plot(self.measurement_values[:, 0], self.measurement_values[:, 1])
            
            # Draw the threshold line
            self.ax.axhline(y=self.threshold_value, color='r', linestyle='-')
            self.ax.set_title(f"Threshold set at y = {self.threshold_value:.4f}")
            
            # Update the canvas
            self.canvas.draw()
            
            # Enable the confirm button
            self.threshold_confirm_button.config(state=tk.NORMAL)
    
    def confirm_threshold(self):
        """Confirm the selected threshold."""
        if self.threshold_value is not None:
            messagebox.showinfo("Threshold Confirmed", f"Threshold value {self.threshold_value:.4f} has been set.")
            
            # Disable the threshold confirm button
            self.threshold_confirm_button.config(state=tk.DISABLED)
            
            # Here you would typically store the threshold for later use
            # or proceed to the next step in your application
            f = open("threshold.txt", "w")

            f.write(f"{self.threshold_value}\n")

            f.close()

#Functions of the measurement tab    
    def save_file_as(self):
        self.nombrevid = fd.asksaveasfilename(defaultextension = 'avi',filetypes=[('Avi Files', '*.avi'), ('All Files', '*.*')])
        if self.nombrevid:
            self.start_measurement_button.config(state=tk.NORMAL)
            self.measured_drops_label.config(text='Number of drops registered: ' + str(0))
            

    def start_measurement(self):
        """Start the measurement process."""
        # Close any existing resources
        cam.close_window
        cam.stop
        dac.stop
        dac.close
        # Stop and close the camera if needed
        if hasattr(self, 'camera') and self.camera:
            self.camera.stop
            self.camera.close_window
            self.camera = None

        # Get the number of drops from the input field
        try:
            self.total_drops = int(self.measures_drops.get())
            if self.total_drops <= 0:
                raise ValueError("Number of drops must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for drops.")
            return

        # Get the number of previous frames from the input field
        try:
            frames = int(self.measures_frames.get())
            if frames <= 0:
                raise ValueError("Number of previous frames must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for previous frames.")
            return
        
        #Load the threshold value from the file
        try:
            with open("threshold.txt", "r") as f:
                self.threshold = float(f.readline())
        except FileNotFoundError:
            messagebox.showerror("Error", "Threshold file not found. Please set the threshold first.")
            return

        # Disable the start button to prevent multiple clicks
        self.start_measurement_button.config(state=tk.DISABLED)
        # Enable the stop button
        self.stop_measurement_button.config(state=tk.NORMAL)
        
        # Get selected device
        selected_device = int(self.device_var_measure.get())
        
        # Initialize camera if not already done
        if not hasattr(self, 'camera') or not self.camera:
            self.camera = cam(fps=1, width=640, height=480)
            self.camera.start(device=selected_device)

        self.camera.path_name_save_video = self.nombrevid
        self.camera.set_path_name_save_video()

        # Initialize drop counter
        self.current_drops = 0
        self.measuring = True
        
        # Write initial frames to the video file
        self.frame_count = 0
        self.total_frames = frames
        self.write_initial_frames()
    
    def write_initial_frames(self):
        """Write initial frames to the video file in a non-blocking way."""
        if self.frame_count < self.total_frames and hasattr(self, 'camera'):
            try:
                self.camera.take_write_snapshot()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during measurement: {e}")
                self.finish_measurement()
                return
            self.frame_count += 1
            # Schedule the next frame capture
            self.root.after(1, self.write_initial_frames)  #1ms delay between frames
        else:
            # All initial frames written, show message and start measurement
            messagebox.showinfo("Start measurement", "If drops are ready, press OK to start measurement.")
            
            #Set procedure acording to the selected DAC
            if self.DAC_var_measure.get() == "NIUSB6009":
                # Start the measurement process
                self.measurer = dac(device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=10000)
                self.measurer.start()

            elif self.DAC_var_measure.get() == "Test":
                # Start the test process
                self.rng = np.random.default_rng()
                

            # Start the actual measurement process
            self.process_measurement()
    
    def process_measurement(self):
        """Process measurements in a non-blocking way."""
        if self.current_drops >= self.total_drops:
            # Measurement complete or stopped
            self.finish_measurement()
            return
        elif not self.measuring:
            # Measurement stopped by user
            self.finish_measurement()
            return 
        
        if self.DAC_var_measure.get() == "Test":
            value = self.rng.random()   

        else:
            value = self.measurer.measure()
        
        try:    
            # Check if value is below threshold
            if value < self.threshold:
                
                if self.DAC_var_measure.get() != "Test":
                    #Stop the measurer task
                    self.measurer.stop()

                # Capture and write a frame after a short delay
                if hasattr(self, 'camera'):
                    # Correctly delay the snapshot by 50ms
                    self.take_snapshot_and_continue()#root.after(1, lambda: self.take_snapshot_and_continue())
                else:
                    # If no camera, just continue
                    self.process_measurement()
            else:
                # No drop detected, check again immediately without delay
                self.root.after(1, lambda:self.process_measurement())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during measurement: {e}")
            self.finish_measurement()
            return

    def take_snapshot_and_continue(self):
        """Take a snapshot and then continue processing."""
        if hasattr(self, 'camera'):
            self.camera.take_write_snapshot()
    
        # Update counter and label
        self.current_drops += 1
        self.measured_drops_label.config(text='Number of drops registered: ' + str(self.current_drops))
    
        if self.DAC_var_measure.get() != "Test":
            #Starts the measurer task again
            self.measurer.start()

        # Continue processing
        self.process_measurement()
    
    def finish_measurement(self):
        """Clean up after measurement is complete."""
        # Show completion message
        if self.current_drops >= self.total_drops:
            messagebox.showinfo("Measurement Complete", f"Successfully recorded {self.current_drops} drops.")
        else:
            messagebox.showinfo("Measurement Stopped", f"Measurement stopped after recording {self.current_drops} drops.")
    
        
        #Stop and close the measurer task
        if self.DAC_var_measure.get() == "NIUSB6009": 
            self.measurer.stop()
            self.measurer.close()
        
        #Stops all process in cam
        cam.stop()
            
        # Stop and close the camera if needed
        if hasattr(self, 'camera') and self.camera:
            self.camera.stop
            self.camera.close_window
            self.camera = None
        
        # Re-enable the start button
        #self.start_measurement_button.config(state=tk.NORMAL)
        # Disable the stop button
        self.stop_measurement_button.config(state=tk.DISABLED)

    def stop_measurement(self):
        """Stop the measurement."""
        # Set flag to stop the measurement process
        self.measuring = False
    
#Functions of the drop energy tab
    def start_simulation(self):
        g = 9.81  # Gravitational acceleration (m/s^2)
        
        dt = 0.0001 # Time step (s)

        # Set the initial conditions
        rho_w = float(self.water_density.get())  # Water density (kg/m^3)
        rho_a = float(self.air_density.get()) #Air density (Kg/m^3)
        C_d = float(self.drag_coefficient.get())  # Drag coefficient (dimensionless)
        distTOT = 0.01 * float(self.drop_height.get())  # Drop height (m)
        mass = 0.000001 * float(self.drops_weight.get())  # Drop weight (kg)
        
        a = np.pi * (3/4 * mass / rho_w / np.pi)**(2/3) # Cross-sectional area of the drop (assumed spherical) (m^2)
        
        ''' --- START OF APPROXIMATE SOLUTION ----'''
        # Set the simulation parameters        
        Fg = mass * g * (1- rho_a / rho_w) # Gravitational force reduced by buoyancy force(N)
        
        # Initialize arrays to store time, distance, velocity, acceleration, and drag force    
        time = np.array([0])
        dist = np.array([0.0])
        vel = np.array([0.0])
        nrg = np.array([0.0])
        accl = np.array([])
        dragF = np.array([])
        
        i = 0
        while True:
            dragF = np.append(dragF, -0.5*C_d*rho_a*a*vel[i]**2)
            accl = np.append(accl, (dragF[i] + Fg)/mass)
            #print(i, dist[i], vel[i], accl[i], dragF[i])
            vel = np.append(vel, vel[i] + dt*accl[i])
            nrg = np.append(nrg, 0.5 * mass * vel[i]**2)
            dist = np.append(dist, dist[i] + dt*vel[i] + 0.5*accl[i]*dt**2)
            time = np.append(time, time[i] + dt)
            if dist[i] > distTOT:
                # Stop the simulation if the drop has reached the aggregate
                
                # Clear any existing plot
                for widget in self.simulation_plot_frame.winfo_children():
                    widget.destroy()
                
                # Create a new matplotlib figure
                self.fig = Figure(figsize=(6, 4), dpi=100)
                self.ax = self.fig.add_subplot(111)
                
                # Plot the data
                self.ax.plot(dist*100, vel, linewidth=1.0) 
                self.ax.set_title(f"Water Drop Energy = {1000 * (nrg[i] + nrg[i-1]) / 2:.2f} mJ", fontsize=16)
                self.ax.set_xlabel('Distance (cm)', fontsize=12)
                self.ax.set_ylabel('Drop velocity (m/s)', fontsize=12)
                self.ax.grid(True)

                # Create a canvas to display the figure in Tkinter
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.simulation_plot_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                break
            i += 1
        ''' --- END OF APPROXIMATE SOLUTION ----'''        
        
#Functions of the video processing tab
    def load_video_folder(self):
        """Load a video file and process it."""
        self.video_folder_path = fd.askdirectory(
            title="Select Video Folder",
            mustexist=True
        )
        if not self.video_folder_path:
            return  # User cancelled the file dialog
        
        # Get all video files in the selected folder
        self.video_files = [f for f in os.listdir(self.video_folder_path) if f.endswith(('.mp4', '.avi', '.mov'))]
        if not self.video_files:
            messagebox.showerror("Error", "No video files found in the selected folder.")
            return
        self.video_selection_dropdown['values'] = self.video_files
        self.hole_area_check.config(state='normal')  # Enable the checkbox
        self.hole_area_input.config(state='normal')  # Enable the input field

    def check_action(self):
        """Enable or disable the video selection dropdown based on the checkbox state."""
        if self.hole_area_check.instate(['selected']):
            self.video_selection_dropdown.config(state='disabled')
            self.process_videos_button.config(state=tk.NORMAL)
        else:
            self.video_selection_dropdown.config(state='readonly')
            self.process_videos_button.config(state=tk.DISABLED)        

    def process_videos(self):
        """
        Process the selected video to set the hole area
        """     
        # If the user opted to use the typed-in hole area directly, start batch processing
        if self.hole_area_check.instate(['selected']):
            # Clear right panel
            for w in self.video_output_frame.winfo_children():
                w.destroy()
            self.start_processing_all_videos()
            return

        if self.canvas_hole_area:
            self.canvas_hole_area.pack_forget()
            self.canvas_hole_area = None
        if self.video_label_hole_area:
            self.video_label_hole_area.pack_forget()
            self.video_label_hole_area = None
            if hasattr(self, 'slider') and self.slider:
                self.slider.pack_forget()
            # Only hide the video processing confirm if it exists
            if hasattr(self, 'hole_area_confirm_button') and self.hole_area_confirm_button:
                self.hole_area_confirm_button.pack_forget()

        # Load video
        self.cap = cv2.VideoCapture(self.video_folder_path + '/' + self.video_selection.get())
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_idx = 0

        # Frame display the video video for hole area selection
        self.video_label_hole_area = tk.Label(self.video_output_frame)
        self.video_label_hole_area.pack()

        # Slider to navigate between frames
        self.slider = ttk.Scale(
            self.video_output_frame,
            from_=0,
            to=self.total_frames - 1,
            orient="horizontal",
            command=self.on_slider_move,
            length=400
        )
        self.slider.pack(pady=10)

        # Confirmation button for selecting frame (distinct from threshold confirm)
        self.hole_area_confirm_button = tk.Button(
            self.video_output_frame, 
            text="Confirm", 
            command=self.confirm_frame_for_hole_area_selection
        )
        self.hole_area_confirm_button.pack(pady=5)



        # Show the first frame
        self.show_frame(0)

        

        
        

        



    def on_slider_move(self, val):
        """When the slider is moved, show the corresponding frame"""
        frame_idx = int(float(val))
        self.current_frame_idx = frame_idx
        self.show_frame(frame_idx)

    def show_frame(self, frame_idx):
        """Show a frame in the label"""
        img = self.get_frame(frame_idx)
        if img is None:
            return
        self.selected_image_hole_area = img
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label_hole_area.imgtk = imgtk
        self.video_label_hole_area.configure(image=imgtk)

    def get_frame(self, frame_idx):
        """Return the frame at position frame_idx"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if not ret:
            return None
        # Transform from BGR (OpenCV) to RGB (PIL)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    def confirm_frame_for_hole_area_selection(self):
        """Finalize the frame and pass to canvas"""
        # Hide video and slider widgets
        self.video_label_hole_area.pack_forget()
        self.slider.pack_forget()
        if hasattr(self, 'hole_area_confirm_button') and self.hole_area_confirm_button:
            self.hole_area_confirm_button.pack_forget()

        # Create canvas
        self.canvas_hole_area = tk.Canvas(self.video_output_frame, 
                                width=self.selected_image_hole_area.width, 
                                height=self.selected_image_hole_area.height
                                )
        self.canvas_hole_area.pack()

        # Show the image as background
        self.bg_image = ImageTk.PhotoImage(self.selected_image_hole_area)
        self.canvas_hole_area.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Elipse confirmation button
        self.btn_elipse_confirmation = tk.Button(self.video_output_frame, text="Confirmar elipse", command=self.confirm_ellipse)
        self.btn_elipse_confirmation.pack(pady=10)

        self.draw_ellipse_on_hole()


    def draw_ellipse_on_hole(self):
        """Allow the user to draw an ellipse on the canvas to select the hole area"""
        # Ellipse parameters
        self.center = [self.bg_image.width() / 2, self.bg_image.height() / 2]
        self.rx, self.ry = 100, 60
        self.angle = 0
        self.ellipse = None

        # Interaction flags
        self.dragging_center = False
        self.rotating = False
        self.resizing_x = False
        self.resizing_y = False

        # Draw initial ellipse
        self.draw_ellipse()

        # Bind mouse events
        self.canvas_hole_area.bind("<Button-1>", self.on_click)
        self.canvas_hole_area.bind("<B1-Motion>", self.on_drag)
        self.canvas_hole_area.bind("<ButtonRelease-1>", self.on_release)

    def draw_ellipse(self):
        """Draw rotated ellipse as polygon on top of image."""
        if self.ellipse:
            self.canvas_hole_area.delete(self.ellipse)

        points = []
        for t in range(0, 360, 3):  # step = resolution
            x = self.rx * math.cos(math.radians(t))
            y = self.ry * math.sin(math.radians(t))

            # apply rotation
            xr = x * math.cos(math.radians(self.angle)) - y * math.sin(math.radians(self.angle))
            yr = x * math.sin(math.radians(self.angle)) + y * math.cos(math.radians(self.angle))

            points.extend((self.center[0] + xr, self.center[1] + yr))

        self.ellipse = self.canvas_hole_area.create_polygon(points, outline="red", fill="", width=2)

    def on_click(self, event):
        dx, dy = event.x - self.center[0], event.y - self.center[1]
        dist_center = math.hypot(dx, dy)

        if dist_center < 15:
            self.dragging_center = True
        else:
            # Rightmost point (rotation handle)
            edge_x = self.center[0] + self.rx * math.cos(math.radians(self.angle))
            edge_y = self.center[1] + self.rx * math.sin(math.radians(self.angle))
            if abs(event.x - edge_x) < 15 and abs(event.y - edge_y) < 15:
                self.rotating = True
            # Bottom point (resize Y)
            elif abs(event.x - (self.center[0] - self.ry * math.cos(math.radians(self.angle-90)))) < 15 and \
                    abs(event.y - (self.center[1] - self.ry * math.sin(math.radians(self.angle-90)))) < 15:
                self.resizing_y = True
            # Left edge (resize X)
            elif abs(event.x - (self.center[0] - self.rx * math.cos(math.radians(self.angle)))) < 15 and \
                    abs(event.y - (self.center[1] - self.rx * math.sin(math.radians(self.angle)))) < 15:
                self.resizing_x = True

    def on_drag(self, event):
        if self.dragging_center:
            self.center = [event.x, event.y]
        elif self.rotating:
            dx, dy = event.x - self.center[0], event.y - self.center[1]
            self.angle = math.degrees(math.atan2(dy, dx))
        elif self.resizing_x:
            self.rx = abs(event.x - self.center[0])
        elif self.resizing_y:
            self.ry = abs(event.y - self.center[1])

        self.draw_ellipse()

    def on_release(self, event):
        self.dragging_center = False
        self.rotating = False
        self.resizing_x = False
        self.resizing_y = False

    def confirm_ellipse(self):
        """Evaluates the area of the ellipse and saves it to the input field."""
        self.hole_area.set(round(math.pi * self.rx * self.ry))
        # Persist the selected hole area for future runs
        try:
            self.save_hole_area(self.hole_area.get())
        except Exception as e:
            # Non-fatal: keep going even if persistence fails
            messagebox.showwarning("Warning", f"Couldn't save hole area: {e}")
        
        self.canvas_hole_area.pack_forget()
        self.canvas_hole_area = None
        self.btn_elipse_confirmation.pack_forget()
        self.btn_elipse_confirmation = None

        # Clear the panel and start processing all videos
        for w in self.video_output_frame.winfo_children():
            w.destroy()
        self.start_processing_all_videos()

    # -------------------- Batch Video Processing --------------------
    def start_processing_all_videos(self):
        """Process all videos in folder, save processed videos and a combined results table, and plot incrementally."""
        if not getattr(self, 'video_folder_path', None):
            messagebox.showerror("Error", "Please load a video folder first.")
            return
        if not getattr(self, 'video_files', None):
            messagebox.showerror("Error", "No videos found to process.")
            return

        # Output folder with suffix _PROC
        out_folder = self.video_folder_path + "_PROC"
        try:
            os.makedirs(out_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output folder: {e}")
            return

        # Prepare Matplotlib area in the right panel
        self.proc_fig = Figure(figsize=(6, 4), dpi=100)
        self.proc_ax = self.proc_fig.add_subplot(111)
        self.proc_ax.set_title("Normalizado vs Número de imagen")
        self.proc_ax.set_xlabel("Número de imagen")
        self.proc_ax.set_ylabel("Normalizado")
        self.proc_ax.grid(True)
        self.proc_canvas = FigureCanvasTkAgg(self.proc_fig, master=self.video_output_frame)
        self.proc_canvas.draw()
        self.proc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        results = {}  # video_name -> normalized list
        Agu = int(self.hole_area.get()) if hasattr(self, 'hole_area') else 4000

        for video_file in self.video_files:
            video_path = os.path.join(self.video_folder_path, video_file)
            try:
                name, areas = self._process_single_video(video_path, out_folder)
            except Exception as e:
                messagebox.showwarning("Warning", f"Error processing {video_file}: {e}")
                continue

            if not areas:
                continue

            normalized = self._compute_normalized_series(areas, Agu, window=5)
            results[name] = normalized

            # Update plot incrementally
            x = list(range(1, 1 + len(normalized)))
            self.proc_ax.plot(x, normalized, label=name, linewidth=1.0)
            self.proc_ax.legend()
            self.proc_canvas.draw()
            self.root.update_idletasks()

        # Write results table
        try:
            self._write_results_table(results, out_folder)
        except Exception as e:
            messagebox.showwarning("Warning", f"Couldn't write results table: {e}")

        messagebox.showinfo("Done", f"Processed {len(results)} videos. Output folder:\n{out_folder}")

    def _process_single_video(self, video_path: str, out_folder: str):
        """Return (base_name, areas) and write processed video to out_folder."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video")

        # Read up to frame 21
        frame = None
        for _ in range(21):
            ret, frame = cap.read()
            if not ret:
                cap.release()
                raise RuntimeError("Couldn't read initial frames up to 21")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            cap.release()
            raise RuntimeError("No contours found in initial frame")
        max_contour = max(contours, key=cv2.contourArea)
        x1, y1, w1, h1 = cv2.boundingRect(max_contour)
        x1, y1 = max(x1 - 20, 0), max(y1 - 20, 0)
        w1 = min(w1 + 40, frame.shape[1] - x1)
        h1 = min(h1 + 40, frame.shape[0] - y1)
        max_area = cv2.contourArea(max_contour)

        base = os.path.splitext(os.path.basename(video_path))[0]
        out_path = os.path.join(out_folder, f"{base}_PROC.avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(out_path, fourcc, 1.0, (w1, h1))

        areas = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rec = frame[y1:y1 + h1, x1:x1 + w1]
            gray_rec = cv2.cvtColor(frame_rec, cv2.COLOR_BGR2GRAY)
            _, thr = cv2.threshold(gray_rec, 40, 255, cv2.THRESH_BINARY_INV)
            ctrs, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if ctrs:
                cmax = max(ctrs, key=cv2.contourArea)
                area = cv2.contourArea(cmax)
                if area > max_area:
                    area = max_area
                frame_draw = cv2.drawContours(frame_rec.copy(), [cmax], -1, (0, 255, 0), 2)
            else:
                area = 0.0
                frame_draw = frame_rec
            areas.append(float(area))
            out.write(frame_draw)

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return base, areas

    def _compute_normalized_series(self, areas, Agu: float, window: int = 5):
        if not areas:
            return []
        denom = (areas[0] - Agu)
        if abs(denom) <= 1e-12:
            denom = 1.0
        arr = np.array(areas, dtype=float)
        n = len(arr)
        rolling = [float('nan')] * n
        for i in range(n):
            if i + 1 < window:
                continue
            start = i + 1 - window
            rolling[i] = float(np.mean(arr[start:i+1]))
        normalized = []
        for v in rolling:
            if isinstance(v, float) and not np.isnan(v):
                normalized.append((v - Agu) / denom)
            else:
                normalized.append(float('nan'))
        return normalized

    def _write_results_table(self, results: dict, out_folder: str):
        # Determine max length across series
        max_len = max((len(v) for v in results.values()), default=0)
        headers = ["Número de imagen"] + list(results.keys())
        rows = []
        for i in range(max_len):
            row = [i + 1]
            for name in results.keys():
                series = results[name]
                row.append(series[i] if i < len(series) else '')
            rows.append(row)

        # Prefer Excel via pandas if available (lazy import)
        try:
            import pandas as pd  # type: ignore
            data = {"Número de imagen": [r[0] for r in rows]}
            for idx, name in enumerate(results.keys()):
                data[name] = [r[idx + 1] for r in rows]
            df = pd.DataFrame(data)
            excel_path = os.path.join(out_folder, "resultados_PROC.xlsx")
            df.to_excel(excel_path, index=False)
            return
        except Exception:
            pass

        # Fallback to CSV if pandas missing or write failed
        import csv
        csv_path = os.path.join(out_folder, "resultados_PROC.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    

    # ---- Persistence helpers for hole area ----
    def load_hole_area_default(self):
        """Return saved hole area from hole_area.txt if available, else None."""
        try:
            with open("hole_area.txt", "r") as f:
                line = f.readline().strip()
                # Accept int or float in file, but store as int
                val = int(float(line))
                if val > 0:
                    return val
        except FileNotFoundError:
            return None
        except Exception:
            return None
        return None

    def save_hole_area(self, value: int):
        """Persist hole area to hole_area.txt in the working directory."""
        with open("hole_area.txt", "w") as f:
            f.write(f"{int(value)}\n")

def main():
    """Create and return a launcher with a main_loop() to run the GUI."""
    root = tk.Tk()
    app = WaterDropMethod(root)

    class _Launcher:
        def __init__(self, root_ref, app_ref):
            self._root = root_ref
            self._app = app_ref  # keep a reference to prevent GC

        def main_loop(self):
            self._root.mainloop()

    return _Launcher(root, app)


if __name__ == "__main__":
    main().main_loop()
