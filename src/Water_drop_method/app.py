import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.filedialog as fd
from PIL import Image, ImageTk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import cv2
import math
import statistics
import threading
try:
    from .paths import get_hole_area_file, get_threshold_file
    from .camera_device import CameraOpenCV as cam
    from .data_acquisition import NIUSB6009, ArduinoUno
except ImportError:
    # Allows running this file directly during local debugging.
    from paths import get_hole_area_file, get_threshold_file
    from camera_device import CameraOpenCV as cam
    from data_acquisition import NIUSB6009, ArduinoUno


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
        self.help_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.camera_frame, text="Camera")
        self.notebook.add(self.threshold_frame, text="Set Threshold")
        self.notebook.add(self.measurement_frame, text="Measurement")
        self.notebook.add(self.drop_energy_frame, text="Drop Energy")
        self.notebook.add(self.video_processing_frame, text="Video Processing")
        self.notebook.add(self.help_frame, text="Help")
        
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

        # Setup Help tab
        self.setup_help_tab()
        
        # Global camera variable
        self.camera = None
        
        # Variable to store threshold value
        self.threshold_value = None

        # Variable indicating measurement in progress
        self.is_measuring = False
        self.measurer = None

        # Canvas to display the image and draw the hole area
        self.canvas_hole_area = None
        self.selected_image_hole_area = None

        # Frame display the video video for hole area selection
        self.video_label_hole_area = None

        # Widgets created dynamically in Video Processing tab
        self.slider = None
        self.hole_area_confirm_button = None

#STARTS THE TABS DEFINITIONS
    def setup_camera_tab(self):
        camera_buttons_frame = ttk.Frame(self.camera_frame)
        camera_buttons_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
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
        
        self.preview_frame = ttk.Frame(self.camera_frame)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

    def setup_threshold_tab(self):
        threshold_controls_frame = ttk.Frame(self.threshold_frame)
        threshold_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        DAC_frame_threshold = ttk.Frame(threshold_controls_frame)
        DAC_frame_threshold.pack(pady=5)
        
        DAC_label_threshold = ttk.Label(DAC_frame_threshold, text="DAC Device:")
        DAC_label_threshold.pack(side=tk.TOP)
        
        self.DAC_var_threshold = tk.StringVar(value="Test")
        self.DAC_combo_threshold = ttk.Combobox(
            DAC_frame_threshold,
            textvariable=self.DAC_var_threshold,
            values=["Test", "NIUSB6009", "ArduinoUno"],
            width=12,
            state="readonly"
        )
        self.DAC_combo_threshold.pack(side=tk.TOP)

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
        
        set_threshold_button = ttk.Button(
            threshold_controls_frame,
            text='Set Threshold',
            command=self.set_threshold
        )
        set_threshold_button.pack(pady=5)
        
        self.confirm_frame = ttk.Frame(threshold_controls_frame)
        self.confirm_frame.pack(pady=5, fill=tk.X)
        
        self.threshold_confirm_button = ttk.Button(
            self.confirm_frame,
            text='Confirm Threshold',
            command=self.confirm_threshold,
            state=tk.DISABLED
        )
        self.threshold_confirm_button.pack(side=tk.LEFT, padx=2)
        
        self.threshold_plot_frame = ttk.Frame(self.threshold_frame)
        self.threshold_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_measurement_tab(self):
        measurement_controls_frame = ttk.Frame(self.measurement_frame)
        measurement_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
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
        
        DAC_frame_measure = ttk.Frame(measurement_controls_frame)
        DAC_frame_measure.pack(pady=5)
        
        DAC_label = ttk.Label(DAC_frame_measure, text="DAC Device:")
        DAC_label.pack(side=tk.TOP)
        
        self.DAC_var_measure = tk.StringVar(value="Test")
        self.DAC_combo_measure = ttk.Combobox(
            DAC_frame_measure,
            textvariable=self.DAC_var_measure,
            values=["Test", "NIUSB6009", "ArduinoUno"],
            width=12,
            state="readonly"
        )
        self.DAC_combo_measure.pack(side=tk.TOP)
        
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

        self.save_file_button = ttk.Button(
            measurement_controls_frame,
            text='Save File As',
            command=self.save_file_as
        )
        self.save_file_button.pack(pady=5)

        self.start_measurement_button = ttk.Button(
            measurement_controls_frame,
            text='Start Measurement',
            command=self.start_measurement,
            state=tk.DISABLED
        )
        self.start_measurement_button.pack(pady=5)

        self.stop_measurement_button = ttk.Button(
            measurement_controls_frame,
            text='Stop Measurement',
            command=self.stop_measurement,
            state=tk.DISABLED
        )
        self.stop_measurement_button.pack(pady=5)

        measured_drops_frame = ttk.Frame(self.measurement_frame)
        measured_drops_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.measured_drops_label = ttk.Label(
            measured_drops_frame,
            text='Number of drops registered: 0'
        )
        self.measured_drops_label.pack(pady=(50, 5))

    def setup_drop_energy_tab(self):
        drop_energy_controls_frame = ttk.Frame(self.drop_energy_frame)
        drop_energy_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

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

        self.start_simulation_button = ttk.Button(
            drop_energy_controls_frame,
            text='Start Simulation',
            command=self.start_simulation
        )
        self.start_simulation_button.pack(pady=5)

        self.simulation_plot_frame = ttk.Frame(self.drop_energy_frame)
        self.simulation_plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_video_proc_tab(self):
        video_proc_controls_frame = ttk.Frame(self.video_processing_frame)
        video_proc_controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.load_video_button = ttk.Button(
            video_proc_controls_frame,
            text='Load Videos Folder',
            command=self.load_video_folder
        )
        self.load_video_button.pack(pady=(0,15))

        hole_area_label = ttk.Label(
            video_proc_controls_frame,
            text='Hole Area (px^2)'
        )
        hole_area_label.pack(pady=(0, 5))

        hole_area_frame = ttk.Frame(video_proc_controls_frame)
        hole_area_frame.pack(pady=(0, 5))

        default_hole_area = self.load_hole_area_default() or 4000
        self.hole_area = tk.IntVar(value=default_hole_area)
        self.hole_area_input = ttk.Entry(
            hole_area_frame,
            textvariable=self.hole_area,
            justify='center',
            width=8,
            state='disabled'
        )
        self.hole_area_input.pack(side=tk.LEFT, pady=(0, 5))

        check_var = tk.IntVar()
        self.hole_area_check = ttk.Checkbutton(
            hole_area_frame,
            text='Use this, or...',
            command=self.check_action,
            variable=check_var,
            state='disabled'
        )
        self.hole_area_check.pack(side=tk.RIGHT, pady=(0, 5))

        self.set_hole_area_label = ttk.Label(
            video_proc_controls_frame,
            text='Select video to set hole area'
        )
        self.set_hole_area_label.pack(pady=(0, 5))

        self.video_selection = tk.StringVar()
        self.video_selection_dropdown = ttk.Combobox(
            video_proc_controls_frame,
            textvariable=self.video_selection,
            state='disabled'
        )
        self.video_selection_dropdown.pack(pady=(0, 5))

        self.video_selection_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda event: self.process_videos_button.config(state=tk.NORMAL)
        )

        self.process_videos_button = ttk.Button(
            video_proc_controls_frame,
            text='Process Videos',
            command=self.process_videos
        )
        self.process_videos_button.pack(pady=(0, 5))
        self.process_videos_button.config(state=tk.DISABLED)

        self.video_output_frame = ttk.Frame(self.video_processing_frame)
        self.video_output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def setup_help_tab(self):
        self.help_sections = [
            (
                "overview",
                "Quick Start",
                {
                    "intro": "Use this tab as the guided map for the whole app. Start with Camera, continue with Set Threshold, then Measurement, and finish with Drop Energy or Video Processing depending on what you need.",
                    "cards": [
                        {
                            "title": "Recommended flow",
                            "items": [
                                "1. Open Camera and verify framing before capturing data.",
                                "2. Set Threshold to store the photodiode cutoff used by Measurement.",
                                "3. Run Measurement to record drops and save the video file.",
                                "4. Use Drop Energy for the physical simulation or Video Processing for batch analysis.",
                            ],
                        },
                        {
                            "title": "What this app keeps for you",
                            "items": [
                                "Threshold and hole area values are stored in the user state folder.",
                                "The Measurement tab reuses the saved threshold automatically.",
                                "Video Processing can reuse a typed hole area or a selected ellipse from a frame.",
                            ],
                        },
                    ],
                    "tips": [
                        "If a control is disabled, check whether the previous step was completed first.",
                        "The left navigation lets you jump directly to the help for each tab.",
                    ],
                },
            ),
            (
                "camera",
                "Camera",
                {
                    "intro": "Preview the live camera feed and confirm that the scene is aligned before starting any measurement workflow.",
                    "cards": [
                        {
                            "title": "Main actions",
                            "items": [
                                "Select the camera device from the dropdown.",
                                "Press Start Preview to open the live feed.",
                                "Press Stop Preview when you are done or before switching workflows.",
                            ],
                        },
                        {
                            "title": "Good practice",
                            "items": [
                                "Keep the sample centered and stable while checking the preview.",
                                "Stop the preview before moving to thresholding or measurement if the camera is still active.",
                            ],
                        },
                    ],
                    "tips": [
                        "If the preview looks frozen, stop it and start it again with the correct device.",
                    ],
                },
            ),
            (
                "threshold",
                "Set Threshold",
                {
                    "intro": "Capture photodiode samples, click the plot to choose the threshold, and confirm it so the value is saved for later measurements.",
                    "cards": [
                        {
                            "title": "Main actions",
                            "items": [
                                "Choose the DAC device: Test, NIUSB6009 or ArduinoUno.",
                                "Enter the number of measures to collect.",
                                "Click Set Threshold to build the plot.",
                                "Click on the graph to place the red threshold line and then confirm it.",
                            ],
                        },
                        {
                            "title": "Result",
                            "items": [
                                "The selected threshold is written to the persistent threshold file.",
                                "Measurement reads this stored value automatically.",
                            ],
                        },
                    ],
                    "tips": [
                        "Use the Test source when you want to explore the workflow without hardware.",
                    ],
                },
            ),
            (
                "measurement",
                "Measurement",
                {
                    "intro": "Record the drop events after the threshold is defined, while the app counts detections and writes the capture video.",
                    "cards": [
                        {
                            "title": "Main actions",
                            "items": [
                                "Choose the camera and DAC devices.",
                                "Set the number of drops to record and the number of previous frames.",
                                "Use Save File As to choose the output video path.",
                                "Start Measurement to begin the acquisition loop and use Stop Measurement to interrupt it.",
                            ],
                        },
                        {
                            "title": "How it behaves",
                            "items": [
                                "The app collects initial frames first, then waits for the drop event.",
                                "Each detection updates the counter shown on the right.",
                                "The saved threshold must exist before measurement starts.",
                            ],
                        },
                    ],
                    "tips": [
                        "If Start Measurement stays disabled, first choose an output file with Save File As.",
                    ],
                },
            ),
            (
                "drop_energy",
                "Drop Energy",
                {
                    "intro": "Estimate the velocity curve and impact energy from the physical parameters of the drop and the environment.",
                    "cards": [
                        {
                            "title": "Main inputs",
                            "items": [
                                "Drop weight in mg.",
                                "Water density and air density.",
                                "Drag coefficient.",
                                "Drop height in cm.",
                            ],
                        },
                        {
                            "title": "Output",
                            "items": [
                                "Press Start Simulation to render the velocity curve.",
                                "The title shows the estimated drop energy in mJ.",
                            ],
                        },
                    ],
                    "tips": [
                        "If you are comparing scenarios, change one value at a time so the curve is easier to interpret.",
                    ],
                },
            ),
            (
                "video_processing",
                "Video Processing",
                {
                    "intro": "Batch-process videos to measure the normalized area over time, either by selecting the hole ellipse manually or by typing its area directly.",
                    "cards": [
                        {
                            "title": "Main actions",
                            "items": [
                                "Load Videos Folder to read the video list.",
                                "Choose a video when you want to draw the hole ellipse from a frame.",
                                "Use the hole area input and checkbox if you want to skip manual selection.",
                                "Press Process Videos to generate the plots and outputs.",
                            ],
                        },
                        {
                            "title": "Manual selection",
                            "items": [
                                "Move the slider to locate a representative frame.",
                                "Confirm the frame, adjust the ellipse, and then confirm the ellipse.",
                                "The selected area is saved for future sessions.",
                            ],
                        },
                    ],
                    "tips": [
                        "The Cancel button is available while batch processing is running.",
                        "If you already know the hole area, the checkbox is the fastest path.",
                    ],
                },
            ),
        ]
        self.help_section_lookup = {key: {"title": title, **payload} for key, title, payload in self.help_sections}
        self.help_selected_key = None

        help_outer = tk.Frame(self.help_frame, bg="#eef4fb")
        help_outer.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(help_outer, bg="#17324d", width=260)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        title_label = tk.Label(
            left_panel,
            text="Help",
            bg="#17324d",
            fg="white",
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        )
        title_label.pack(fill=tk.X, padx=18, pady=(18, 4))

        subtitle_label = tk.Label(
            left_panel,
            text="Choose a tab to see what it does and how to use it.",
            bg="#17324d",
            fg="#d6e4f5",
            wraplength=220,
            justify=tk.LEFT,
            anchor="w",
        )
        subtitle_label.pack(fill=tk.X, padx=18, pady=(0, 12))
        self._bind_help_wrap(subtitle_label, left_panel, horizontal_padding=40, min_wrap=140)

        nav_label = tk.Label(
            left_panel,
            text="Navigate",
            bg="#17324d",
            fg="#8fb3d9",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        nav_label.pack(fill=tk.X, padx=18, pady=(0, 8))

        nav_container = tk.Frame(left_panel, bg="#17324d")
        nav_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.help_nav_buttons = {}
        for key, title, _ in self.help_sections:
            button = tk.Button(
                nav_container,
                text=title,
                command=lambda section_key=key: self.show_help_section(section_key),
                anchor="w",
                justify=tk.LEFT,
                relief=tk.FLAT,
                bd=0,
                padx=14,
                pady=10,
                bg="#edf2f7",
                fg="#17324d",
                activebackground="#dbeafe",
                activeforeground="#0f172a",
                highlightthickness=0,
                font=("Segoe UI", 10, "bold"),
            )
            button.pack(fill=tk.X, pady=4)
            self.help_nav_buttons[key] = button

        footer_label = tk.Label(
            left_panel,
            text="The help panel stays inside the app, so you can switch tabs without losing context.",
            bg="#17324d",
            fg="#a7bed6",
            wraplength=220,
            justify=tk.LEFT,
            anchor="w",
            font=("Segoe UI", 9),
        )
        footer_label.pack(fill=tk.X, padx=18, pady=(0, 18))
        self._bind_help_wrap(footer_label, left_panel, horizontal_padding=40, min_wrap=140)

        right_panel = tk.Frame(help_outer, bg="#f8fafc")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.help_canvas = tk.Canvas(right_panel, bg="#f8fafc", highlightthickness=0)
        help_scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.help_canvas.yview)
        self.help_canvas.configure(yscrollcommand=help_scrollbar.set)
        help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.help_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.help_content_host = tk.Frame(self.help_canvas, bg="#f8fafc")
        self.help_content_window = self.help_canvas.create_window((0, 0), window=self.help_content_host, anchor="nw")

        def _sync_help_scrollregion(event):
            self.help_canvas.configure(scrollregion=self.help_canvas.bbox("all"))

        def _sync_help_width(event):
            self.help_canvas.itemconfigure(self.help_content_window, width=event.width)

        self.help_content_host.bind("<Configure>", _sync_help_scrollregion)
        self.help_canvas.bind("<Configure>", _sync_help_width)
        self.root.bind_all("<MouseWheel>", self._on_help_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_help_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._on_help_mousewheel, add="+")

        self.show_help_section("overview")

    def show_help_section(self, section_key):
        section = self.help_section_lookup[section_key]
        self.help_selected_key = section_key

        for widget in self.help_content_host.winfo_children():
            widget.destroy()

        for key, button in self.help_nav_buttons.items():
            if key == section_key:
                button.configure(bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white")
            else:
                button.configure(bg="#edf2f7", fg="#17324d", activebackground="#dbeafe", activeforeground="#0f172a")

        header_card = tk.Frame(self.help_content_host, bg="white", bd=1, relief=tk.SOLID)
        header_card.pack(fill=tk.X, padx=20, pady=(20, 12))

        header_title = tk.Label(
            header_card,
            text=section["title"],
            bg="white",
            fg="#0f172a",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
            justify=tk.LEFT,
            wraplength=560,
        )
        header_title.pack(fill=tk.X, padx=20, pady=(16, 6))
        self._bind_help_wrap(header_title, header_card, horizontal_padding=48, min_wrap=180)

        header_intro = tk.Label(
            header_card,
            text=section["intro"],
            bg="white",
            fg="#334155",
            font=("Segoe UI", 11),
            wraplength=620,
            justify=tk.LEFT,
            anchor="w",
        )
        header_intro.pack(fill=tk.X, padx=20, pady=(0, 16))
        self._bind_help_wrap(header_intro, header_card, horizontal_padding=48, min_wrap=200)

        body_frame = tk.Frame(self.help_content_host, bg="#f8fafc")
        body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        for card in section["cards"]:
            self._create_help_card(body_frame, card["title"], card["items"])

        tips_card = tk.Frame(body_frame, bg="#eff6ff", bd=1, relief=tk.SOLID)
        tips_card.pack(fill=tk.X, pady=(0, 14))

        tips_title = tk.Label(
            tips_card,
            text="Tips",
            bg="#eff6ff",
            fg="#1d4ed8",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        tips_title.pack(fill=tk.X, padx=16, pady=(12, 4))

        for tip in section["tips"]:
            tip_label = tk.Label(
                tips_card,
                text=f"• {tip}",
                bg="#eff6ff",
                fg="#1e293b",
                wraplength=620,
                justify=tk.LEFT,
                anchor="w",
                font=("Segoe UI", 10),
            )
            tip_label.pack(fill=tk.X, padx=16, pady=(0, 10))
            self._bind_help_wrap(tip_label, tips_card, horizontal_padding=40, min_wrap=200)

    def _create_help_card(self, parent, title, items):
        card = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, pady=(0, 14))

        card_title = tk.Label(
            card,
            text=title,
            bg="white",
            fg="#0f172a",
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        card_title.pack(fill=tk.X, padx=16, pady=(12, 6))

        for item in items:
            item_label = tk.Label(
                card,
                text=f"• {item}",
                bg="white",
                fg="#334155",
                wraplength=620,
                justify=tk.LEFT,
                anchor="w",
                font=("Segoe UI", 10),
            )
            item_label.pack(fill=tk.X, padx=16, pady=(0, 8))
            self._bind_help_wrap(item_label, card, horizontal_padding=40, min_wrap=200)

    def _bind_help_wrap(self, label, container, horizontal_padding=32, min_wrap=180):
        def _update_wrap(event=None):
            width = container.winfo_width()
            if event is not None and getattr(event, "width", 0) > 0:
                width = event.width
            if width <= 1:
                return
            label.configure(wraplength=max(min_wrap, width - horizontal_padding))

        container.bind("<Configure>", _update_wrap, add="+")
        self.root.after(0, _update_wrap)

    def _on_help_mousewheel(self, event):
        if self.notebook.select() != str(self.help_frame):
            return

        hovered_widget = self.root.winfo_containing(event.x_root, event.y_root)
        if hovered_widget is None:
            return
        if not self._is_descendant_widget(hovered_widget, self.help_canvas):
            return

        if getattr(event, "num", None) == 4:
            step = -1
        elif getattr(event, "num", None) == 5:
            step = 1
        else:
            if event.delta == 0:
                return
            step = -1 if event.delta > 0 else 1

        self.help_canvas.yview_scroll(step, "units")
        return "break"

    def _is_descendant_widget(self, widget, ancestor):
        current = widget
        while current is not None:
            if current == ancestor:
                return True
            parent_name = current.winfo_parent()
            if not parent_name:
                break
            try:
                current = current.nametowidget(parent_name)
            except Exception:
                break
        return False

#Functions for the camera tab
    def start_preview(self, *args):
        self.cleanup_camera()
        self.cleanup_dac()
        
        selected_device = int(self.device_var.get())
        
        if not hasattr(self, 'camera') or not self.camera:
            self.camera = cam(fps=1, width=640, height=480)
            self.camera.start(device=selected_device)
        
        self.conti = True
        self.update_camera_preview()
    
    def stop_preview(self, *args):
        self.conti = False
        self.cleanup_camera()
        self.preview_label.configure(image='')

    def update_camera_preview(self):
        if hasattr(self, 'conti') and self.conti and hasattr(self, 'camera') and self.camera:
            try:
                img, wait_key = self.camera.preview_camera()
                pil_img = Image.fromarray(img)
                tk_img = ImageTk.PhotoImage(image=pil_img)
                self.preview_label.configure(image=tk_img)
                self.preview_label.image = tk_img
                self.root.after(30, self.update_camera_preview)
            except Exception:
                pass

#Functions of the threshold tab   
    def set_threshold(self, *args):
        self.cleanup_camera()
        self.cleanup_dac()

        try:
            measures = int(self.measures_var.get())
            if measures <= 0:
                raise ValueError("Number of measures must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for measures.")
            return

        selected_dac = self.DAC_var_threshold.get()

        def _acquisition_worker():
            values = None
            error_msg = None

            try:
                if selected_dac == "NIUSB6009":
                    measurer = NIUSB6009(device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=10000)
                    measurer.start()
                    
                    i = 0
                    temp_values = []
                    while i < measures:
                        value = measurer.measure()
                        temp_values.append([i, value])
                        i += 1

                    values = np.array(temp_values)
                    measurer.stop()
                    measurer.close()

                elif selected_dac == "ArduinoUno":
                    measurer = ArduinoUno(port="COM3", baudrate=115200)
                    measurer.start()
                    
                    i = 0
                    temp_values = []
                    while i < measures:
                        value = measurer.measure()
                        if value is not None:
                            temp_values.append([i, value])
                            i += 1

                    values = np.array(temp_values)
                    measurer.stop()
                    measurer.close()

                elif selected_dac == "Test":
                    file_path = os.path.join(os.path.dirname(__file__), "for_test.tsv")
                    with open(file_path) as f:
                        lines = f.readlines()
                        values = np.array([list(map(float, line.split())) for line in lines])[:measures]

            except Exception as e:
                error_msg = str(e)

            self.root.after(0, lambda: self._on_set_threshold_finished(values, error_msg))

        threading.Thread(target=_acquisition_worker, daemon=True).start()

    def _on_set_threshold_finished(self, values, error_msg):
        if error_msg:
            messagebox.showerror("Error", f"An error occurred while measuring: {error_msg}")
            return

        if values is None or len(values) == 0:
            return

        self.measurement_values = values
        
        for widget in self.threshold_plot_frame.winfo_children():
            widget.destroy()
        
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.ax.plot(values[:, 0], values[:, 1])
        self.ax.set_title("Click to set threshold level")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.threshold_plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.threshold_confirm_button.config(state=tk.DISABLED)
    
    def on_plot_click(self, event):
        if event.ydata is not None:
            self.threshold_value = event.ydata
            self.ax.clear()
            self.ax.plot(self.measurement_values[:, 0], self.measurement_values[:, 1])
            self.ax.axhline(y=self.threshold_value, color='r', linestyle='-')
            self.ax.set_title(f"Threshold set at y = {self.threshold_value:.4f}")
            self.canvas.draw()
            self.threshold_confirm_button.config(state=tk.NORMAL)
    
    def confirm_threshold(self):
        if self.threshold_value is not None:
            messagebox.showinfo("Threshold Confirmed", f"Threshold value {self.threshold_value:.4f} has been set.")
            self.threshold_confirm_button.config(state=tk.DISABLED)
            threshold_file = get_threshold_file()
            with open(threshold_file, "w", encoding="utf-8") as f:
                f.write(f"{self.threshold_value}\n")

#Functions of the measurement tab    
    def save_file_as(self):
        self.nombrevid = fd.asksaveasfilename(
            defaultextension='avi',
            filetypes=[('Avi Files', '*.avi'), ('All Files', '*.*')]
        )
        if self.nombrevid:
            self.start_measurement_button.config(state=tk.NORMAL)
            self.measured_drops_label.config(text='Number of drops registered: 0')

    def cleanup_camera(self):
        if hasattr(self, 'camera') and self.camera:
            try:
                self.camera.stop()
                self.camera.close_window()
            except Exception:
                pass
            self.camera = None

    def cleanup_dac(self):
        if hasattr(self, 'measurer') and self.measurer:
            try:
                self.measurer.stop()
                self.measurer.close()
            except Exception:
                pass
            self.measurer = None            

    def start_measurement(self):
        """Start the measurement process."""
        self._already_finished = False

        self.cleanup_camera()
        self.cleanup_dac()

        try:
            self.total_drops = int(self.measures_drops.get())
            if self.total_drops <= 0:
                raise ValueError("Number of drops must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for drops.")
            return

        try:
            frames = int(self.measures_frames.get())
            if frames <= 0:
                raise ValueError("Number of previous frames must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for previous frames.")
            return

        if not hasattr(self, 'nombrevid') or not self.nombrevid:
            messagebox.showerror("Error", "Please select a destination video file using 'Save File As' first.")
            return

        # Load saved threshold
        try:
            threshold_file = get_threshold_file()
            if not os.path.exists(threshold_file):
                raise FileNotFoundError("Threshold file not found.")
            with open(threshold_file, "r", encoding="utf-8") as f:
                content = f.readline().strip()
                if not content:
                    raise ValueError("Threshold file is empty.")
                self.threshold = float(content)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Cannot start measurement: No valid threshold value saved.\n"
                f"Please set and confirm threshold first.\nDetail: {e}"
            )
            return

        # Adjust UI states
        self.save_file_button.config(state=tk.DISABLED)
        self.start_measurement_button.config(state=tk.DISABLED)
        self.stop_measurement_button.config(state=tk.NORMAL)

        self.selected_dac = self.DAC_var_measure.get()
        selected_device = int(self.device_var_measure.get())

        try:
            self.camera = cam(fps=1, width=640, height=480)
            self.camera.start(device=selected_device)
        except Exception as e:
            messagebox.showerror("Error", f"Could not initialize camera device {selected_device}: {e}")
            self.finish_measurement()
            return

        self.captured_frames = []
        self.camera.path_name_save_video = self.nombrevid
        self.camera.set_path_name_save_video()

        self.current_drops = 0
        self.drop_in_progress = False
        self.measuring = True

        self.frame_count = 0
        self.total_frames = frames
        self.write_initial_frames()

    def write_initial_frames(self):
        """Write initial frames to the video file in a non-blocking way."""
        if not self.measuring:
            self.finish_measurement()
            return

        if self.frame_count < self.total_frames and hasattr(self, 'camera') and self.camera:
            try:
                self.camera.take_write_snapshot()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during initial frame acquisition: {e}")
                self.finish_measurement()
                return
            self.frame_count += 1
            self.root.after(1, self.write_initial_frames)
        else:
            if not self.measuring:
                self.finish_measurement()
                return

            try:
                if self.selected_dac == "NIUSB6009":
                    self.measurer = NIUSB6009(device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=10000)
                    self.measurer.start()
                elif self.selected_dac == "ArduinoUno":
                    self.measurer = ArduinoUno(port="COM3", baudrate=115200)
                    self.measurer.start()
                elif self.selected_dac == "Test":
                    self.rng = np.random.default_rng()
            except Exception as e:
                messagebox.showerror("Error", f"Could not start DAC device ({self.selected_dac}): {e}")
                self.finish_measurement()
                return

            self.process_measurement()

    def process_measurement(self):
        """Process measurements in a non-blocking way with hysteresis trigger for drops."""
        if not self.measuring or self.current_drops >= self.total_drops:
            self.finish_measurement()
            return

        try:
            # Clear input buffer if serial connection exists to ensure fresh data
            if hasattr(self, 'measurer') and self.measurer and hasattr(self.measurer, 'ser'):
                try:
                    if self.measurer.ser and self.measurer.ser.is_open:
                        self.measurer.ser.reset_input_buffer()
                except Exception:
                    pass

            if self.selected_dac == "Test":
                value = self.rng.random()
            else:
                value = self.measurer.measure()

            if value is not None:
                if self.drop_in_progress:
                    # Drop is passing; wait until signal goes back above threshold before re-arming
                    if value >= self.threshold:
                        self.drop_in_progress = False
                else:
                    # Signal is normal; check if a new drop is detected
                    if value < self.threshold:
                        self.drop_in_progress = True
                        self.take_snapshot()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during measurement: {e}")
            self.finish_measurement()
            return

        if self.measuring and self.current_drops < self.total_drops:
            self.root.after(1, self.process_measurement)
        else:
            self.finish_measurement()

    def take_snapshot(self):
        """Take a single snapshot for the detected drop and update UI label."""
        if hasattr(self, 'camera') and self.camera:
            frame = self.camera.get_frame()
            if frame is not None:
                self.captured_frames.append({
                    'drop_number': self.current_drops + 1,
                    'frame': frame.copy()
                })

        self.current_drops += 1
        self.measured_drops_label.config(text=f'Number of drops registered: {self.current_drops}')

    def save_captured_frames_to_disk(self):
        """Save the captured frames stored in RAM to disk in a separate thread."""
        if not hasattr(self, 'captured_frames') or not self.captured_frames:
            self.cleanup_camera()
            return

        frames_to_save = list(self.captured_frames)
        self.captured_frames = []

        camera_ref = self.camera
        self.camera = None

        def _writer_thread():
            print(f"Saving {len(frames_to_save)} images to disk...")
            if camera_ref:
                try:
                    camera_ref.save_frames_to_avi(frames_to_save)
                    camera_ref.stop()
                    camera_ref.close_window()
                except Exception as e:
                    print(f"Error saving video: {e}")
            print("Video saved successfully!")

        threading.Thread(target=_writer_thread, daemon=True).start()

    def stop_measurement(self):
        """Stop the measurement manually."""
        if self.measuring:
            self.measuring = False
            self.finish_measurement()

    def finish_measurement(self):
        """Clean up after measurement stops or completes, and reset GUI controls."""
        if getattr(self, '_already_finished', False):
            return
        self._already_finished = True
        self.measuring = False

        # Stop and close DAC device
        self.cleanup_dac()

        # Show notification message
        if self.current_drops >= getattr(self, 'total_drops', 0) and getattr(self, 'total_drops', 0) > 0:
            messagebox.showinfo("Measurement Complete", f"Measurement finished successfully.\nDrops registered: {self.current_drops}")
        else:
            messagebox.showinfo("Measurement Stopped", f"Measurement stopped.\nDrops registered: {self.current_drops}")

        # Reset button states back to initial state
        self.save_file_button.config(state=tk.NORMAL)
        self.start_measurement_button.config(state=tk.DISABLED)
        self.stop_measurement_button.config(state=tk.DISABLED)

        # Save frames to disk in background and close camera
        self.save_captured_frames_to_disk()

#Functions of the drop energy tab
    def start_simulation(self):
        g = 9.81
        dt = 0.0001

        rho_w = float(self.water_density.get())
        rho_a = float(self.air_density.get())
        C_d = float(self.drag_coefficient.get())
        distTOT = 0.01 * float(self.drop_height.get())
        mass = 0.000001 * float(self.drops_weight.get())
        
        a = np.pi * (3/4 * mass / rho_w / np.pi)**(2/3)
        
        Fg = mass * g * (1 - rho_a / rho_w)
        
        time_list = [0.0]
        dist_list = [0.0]
        vel_list = [0.0]
        nrg_list = [0.0]
        accl_list = []
        dragF_list = []
        
        i = 0
        while True:
            df = -0.5 * C_d * rho_a * a * vel_list[i]**2
            acc = (df + Fg) / mass
            dragF_list.append(df)
            accl_list.append(acc)

            v_next = vel_list[i] + dt * acc
            vel_list.append(v_next)
            nrg_list.append(0.5 * mass * (vel_list[i]**2))

            d_next = dist_list[i] + dt * vel_list[i] + 0.5 * acc * (dt**2)
            dist_list.append(d_next)
            time_list.append(time_list[i] + dt)
            
            if (dist_list[i] > distTOT) or (i > 100000):
                dist = np.array(dist_list)
                vel = np.array(vel_list)
                nrg = np.array(nrg_list)

                for widget in self.simulation_plot_frame.winfo_children():
                    widget.destroy()
                
                self.fig = Figure(figsize=(6, 4), dpi=100)
                self.ax = self.fig.add_subplot(111)
                
                self.ax.plot(dist * 100, vel, linewidth=1.0) 
                self.ax.set_title(f"Water Drop Energy = {1000 * (nrg[i] + nrg[i-1]) / 2:.5f} mJ", fontsize=16)
                self.ax.set_xlabel('Distance (cm)', fontsize=12)
                self.ax.set_ylabel('Drop velocity (m/s)', fontsize=12)
                self.ax.grid(True)

                self.canvas = FigureCanvasTkAgg(self.fig, master=self.simulation_plot_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                break
            i += 1

#Functions of the video processing tab
    def load_video_folder(self):
        self.video_folder_path = fd.askdirectory(
            title="Select Video Folder",
            mustexist=True
        )
        if not self.video_folder_path:
            return
        
        self.video_files = [f for f in os.listdir(self.video_folder_path) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if not self.video_files:
            messagebox.showerror("Error", "No video files found in the selected folder.")
            return
        self.video_selection_dropdown['values'] = self.video_files
        self.hole_area_check.config(state='normal')
        self.hole_area_input.config(state='normal')

    def check_action(self):
        if self.hole_area_check.instate(['selected']):
            self.video_selection_dropdown.config(state='disabled')
            self.process_videos_button.config(state=tk.NORMAL)
        else:
            self.video_selection_dropdown.config(state='readonly')
            self.process_videos_button.config(state=tk.DISABLED)        

    def process_videos(self):
        if self.hole_area_check.instate(['selected']):
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
            if hasattr(self, 'hole_area_confirm_button') and self.hole_area_confirm_button:
                self.hole_area_confirm_button.pack_forget()

        self.cap = cv2.VideoCapture(os.path.join(self.video_folder_path, self.video_selection.get()))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_idx = 0

        self.video_label_hole_area = tk.Label(self.video_output_frame)
        self.video_label_hole_area.pack()

        self.slider = ttk.Scale(
            self.video_output_frame,
            from_=0,
            to=self.total_frames - 1,
            orient="horizontal",
            command=self.on_slider_move,
            length=400
        )
        self.slider.pack(pady=10)

        self.hole_area_confirm_button = tk.Button(
            self.video_output_frame, 
            text="Confirm", 
            command=self.confirm_frame_for_hole_area_selection
        )
        self.hole_area_confirm_button.pack(pady=5)

        self.show_frame(0)

    def on_slider_move(self, val):
        frame_idx = int(float(val))
        self.current_frame_idx = frame_idx
        self.show_frame(frame_idx)

    def show_frame(self, frame_idx):
        img = self.get_frame(frame_idx)
        if img is None:
            return
        self.selected_image_hole_area = img
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label_hole_area.imgtk = imgtk
        self.video_label_hole_area.configure(image=imgtk)

    def get_frame(self, frame_idx):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if not ret:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    def confirm_frame_for_hole_area_selection(self):
        self.video_label_hole_area.pack_forget()
        self.slider.pack_forget()
        if hasattr(self, 'hole_area_confirm_button') and self.hole_area_confirm_button:
            self.hole_area_confirm_button.pack_forget()

        self.canvas_hole_area = tk.Canvas(
            self.video_output_frame, 
            width=self.selected_image_hole_area.width, 
            height=self.selected_image_hole_area.height
        )
        self.canvas_hole_area.pack()

        self.bg_image = ImageTk.PhotoImage(self.selected_image_hole_area)
        self.canvas_hole_area.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.btn_elipse_confirmation = tk.Button(self.video_output_frame, text="Confirm ellipse", command=self.confirm_ellipse)
        self.btn_elipse_confirmation.pack(pady=10)

        self.draw_ellipse_on_hole()

    def draw_ellipse_on_hole(self):
        self.center = [self.bg_image.width() / 2, self.bg_image.height() / 2]
        self.rx, self.ry = 100, 60
        self.angle = 0
        self.ellipse = None

        self.dragging_center = False
        self.rotating = False
        self.resizing_x = False
        self.resizing_y = False

        self.draw_ellipse()

        self.canvas_hole_area.bind("<Button-1>", self.on_click)
        self.canvas_hole_area.bind("<B1-Motion>", self.on_drag)
        self.canvas_hole_area.bind("<ButtonRelease-1>", self.on_release)

    def draw_ellipse(self):
        if self.ellipse:
            self.canvas_hole_area.delete(self.ellipse)

        points = []
        for t in range(0, 360, 3):
            x = self.rx * math.cos(math.radians(t))
            y = self.ry * math.sin(math.radians(t))

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
            edge_x = self.center[0] + self.rx * math.cos(math.radians(self.angle))
            edge_y = self.center[1] + self.rx * math.sin(math.radians(self.angle))
            if abs(event.x - edge_x) < 15 and abs(event.y - edge_y) < 15:
                self.rotating = True
            elif abs(event.x - (self.center[0] - self.ry * math.cos(math.radians(self.angle-90)))) < 15 and \
                    abs(event.y - (self.center[1] - self.ry * math.sin(math.radians(self.angle-90)))) < 15:
                self.resizing_y = True
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
        self.hole_area.set(round(math.pi * self.rx * self.ry))
        try:
            self.save_hole_area(self.hole_area.get())
        except Exception as e:
            messagebox.showwarning("Warning", f"Couldn't save hole area: {e}")
        
        self.canvas_hole_area.pack_forget()
        self.canvas_hole_area = None
        self.btn_elipse_confirmation.pack_forget()
        self.btn_elipse_confirmation = None

        for w in self.video_output_frame.winfo_children():
            w.destroy()
        self.start_processing_all_videos()

    # Batch Video Processing
    def start_processing_all_videos(self):
        if not getattr(self, 'video_folder_path', None):
            messagebox.showerror("Error", "Please load a video folder first.")
            return
        if not getattr(self, 'video_files', None):
            messagebox.showerror("Error", "No videos found to process.")
            return

        try:
            self.process_videos_button.config(state=tk.DISABLED)
        except Exception:
            pass

        base_folder_name = os.path.basename(os.path.normpath(self.video_folder_path))
        out_folder = os.path.join(self.video_folder_path, f"{base_folder_name}_PROC")
        try:
            os.makedirs(out_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output folder: {e}")
            try:
                self.process_videos_button.config(state=tk.NORMAL)
            except Exception:
                pass
            return

        for w in self.video_output_frame.winfo_children():
            w.destroy()
        self.proc_fig = Figure(figsize=(6, 4), dpi=100)
        self.proc_ax = self.proc_fig.add_subplot(111)
        self.proc_ax.set_xlabel("Image number")
        self.proc_ax.set_ylabel("Normalized area")
        self.proc_ax.set_ylim(-0.1, 1.1)
        self.proc_ax.grid(True)
        self.proc_canvas = FigureCanvasTkAgg(self.proc_fig, master=self.video_output_frame)
        self.proc_canvas.draw()
        self.proc_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.video_output_frame, variable=self.progress_var, maximum=len(self.video_files))
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        self.cancel_processing = False
        self.cancel_button = ttk.Button(self.video_output_frame, text='Cancel', command=self.cancel_video_processing)
        self.cancel_button.pack(padx=5, pady=(0,5))

        results = {}
        rupture_points = {}
        Agu = int(self.hole_area.get()) if hasattr(self, 'hole_area') else 4000

        for idx, video_file in enumerate(self.video_files, start=1):
            if self.cancel_processing:
                break
            video_path = os.path.join(self.video_folder_path, video_file)
            try:
                name, areas = self._process_single_video(video_path, out_folder)
            except Exception as e:
                messagebox.showwarning("Warning", f"Error processing {video_file}: {e}")
                continue

            if not areas:
                continue

            image_numbers, normalized = self._compute_normalized_series(areas, Agu, window=5)
            results[name] = normalized

            rupture_idx = None
            for i, val in enumerate(normalized):
                if isinstance(val, float) and not np.isnan(val) and val < 0:
                    rupture_idx = image_numbers[i]
                    break
            if rupture_idx is None:
                rupture_idx = image_numbers[-1] if image_numbers else 0
            rupture_points[name] = rupture_idx

            self.proc_ax.plot(image_numbers, normalized, label=name, linewidth=1.0)
            self.proc_ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=8, frameon=False)
            self.proc_canvas.draw()
            self.root.update_idletasks()
            self.progress_var.set(idx)
            self.progress_bar.update()

        processed_videos = len(results)

        rupture_median = None
        if processed_videos > 0:
            try:
                rupture_median = statistics.median(rupture_points.values())
            except Exception:
                rupture_median = None

        if rupture_median is not None and processed_videos > 0:
            self.proc_ax.axvline(rupture_median, color='black', linestyle='--', label='Rupture')
            self.proc_ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=8, frameon=False)
            self.proc_canvas.draw()

        try:
            self._write_results_table(results, out_folder, rupture_median, os.path.basename(os.path.normpath(self.video_folder_path)))
        except Exception as e:
            messagebox.showwarning("Warning", f"Couldn't write results table: {e}")

        if self.cancel_processing:
            messagebox.showinfo("Canceled", f"Processing canceled after {processed_videos} videos. Output folder:\n{out_folder}")
        else:
            messagebox.showinfo("Done", f"Processed {processed_videos} videos. Output folder:\n{out_folder}")

        try:
            self.process_videos_button.config(state=tk.NORMAL)
        except Exception:
            pass
        try:
            self.cancel_button.config(state=tk.DISABLED)
        except Exception:
            pass

    def _process_single_video(self, video_path: str, out_folder: str):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video")

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
        return base, areas

    def _compute_normalized_series(self, areas, Agu: float, window: int = 5):
        if not areas:
            return [], []
        arr = np.array(areas, dtype=float)
        n = len(arr)
        rolling_vals = []
        image_numbers = []
        for i in range(window - 1, n):
            window_slice = arr[i - window + 1: i + 1]
            rolling_vals.append(float(np.mean(window_slice)))
            image_numbers.append(len(rolling_vals))
        if not rolling_vals:
            return [], []
        first_mean = rolling_vals[0]
        denom = first_mean - Agu
        if abs(denom) <= 1e-12:
            denom = 1.0
        normalized = [(v - Agu) / denom for v in rolling_vals]
        normalized[0] = 1.0
        return image_numbers, normalized

    def _write_results_table(self, results: dict, out_folder: str, rupture_median, folder_basename: str):
        max_len = max((len(v) for v in results.values()), default=0)
        headers = ["Image number"] + list(results.keys())
        rows = []
        for i in range(max_len):
            row = [i + 1]
            for name in results.keys():
                series = results[name]
                row.append(series[i] if i < len(series) else '')
            rows.append(row)

        try:
            import pandas as pd
            try:
                import openpyxl
                excel_engine = "openpyxl"
            except ImportError:
                try:
                    import xlsxwriter
                    excel_engine = "xlsxwriter"
                except ImportError:
                    raise RuntimeError("Excel export requires 'openpyxl' or 'xlsxwriter'.")

            data = {"Image number": [r[0] for r in rows]}
            for idx, name in enumerate(results.keys()):
                data[name] = [r[idx + 1] for r in rows]
            df = pd.DataFrame(data)
            excel_path = os.path.join(out_folder, "Results_PROC.xlsx")
            try:
                with pd.ExcelWriter(excel_path, engine=excel_engine) as writer:
                    df.to_excel(writer, sheet_name="Results_PROC", index=False)
                    rupture_df = pd.DataFrame([[folder_basename, rupture_median if rupture_median is not None else ""]])
                    rupture_df.to_excel(writer, sheet_name="Rupture", index=False, header=False)
                return
            except Exception as e:
                try:
                    messagebox.showwarning("Excel export failed", f"Could not create Excel file (will create CSV instead):\n{e}")
                except Exception:
                    pass
        except Exception as e:
            try:
                messagebox.showwarning("Excel export unavailable", f"Pandas/engine not available (will create CSV instead):\n{e}")
            except Exception:
                pass

        import csv
        csv_path = os.path.join(out_folder, "Results_PROC.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        if rupture_median is not None:
            with open(os.path.join(out_folder, "Results_PROC_Rupture.txt"), 'w', encoding='utf-8') as rf:
                rf.write(f"{folder_basename},{rupture_median}\n")

    def cancel_video_processing(self):
        self.cancel_processing = True
        try:
            self.cancel_button.config(state=tk.DISABLED)
        except Exception:
            pass

    def load_hole_area_default(self):
        try:
            with open(get_hole_area_file(), "r", encoding="utf-8") as f:
                line = f.readline().strip()
                val = int(float(line))
                if val > 0:
                    return val
        except Exception:
            return None
        return None

    def save_hole_area(self, value: int):
        with open(get_hole_area_file(), "w", encoding="utf-8") as f:
            f.write(f"{int(value)}\n")

def main():
    root = tk.Tk()
    app = WaterDropMethod(root)

    class _Launcher:
        def __init__(self, root_ref, app_ref):
            self._root = root_ref
            self._app = app_ref

        def main_loop(self):
            self._root.mainloop()

    return _Launcher(root, app)


if __name__ == "__main__":
    main().main_loop()