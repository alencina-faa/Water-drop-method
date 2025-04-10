class NIUSB6009:
    global nidaqmx
    import nidaqmx
    """
    Clase para la adquisición de datos de un fotodiodo conectado a una NI-USB6009.
    """
    
    def __init__(self, device_name="Dev1", channel="ai0", sample_rate=1000, samples_per_channel=10000):
        self.device_name = device_name
        self.channel = channel
        self.sample_rate = sample_rate
        self.samples_per_channel = samples_per_channel
        
        # Initialize the task
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(f"{self.device_name}/{self.channel}")
        self.task.timing.cfg_samp_clk_timing(sample_rate=self.sample_rate, samps_per_chan=self.samples_per_channel)

    def start(self):
        """Start the task for data acquisition."""
        self.task.start()
    

    def measure(self):
        """Read a single sample from the task."""
        return self.task.read()
    
    def stop_close(self):
        """Stop and close the task."""
        self.task.stop()
        self.task.close()
    


