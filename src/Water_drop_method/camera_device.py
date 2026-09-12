class CameraOpenCV:
    global cv2
    import cv2

    global fourcc
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

    global out
    out = False

    def __init__(self, fps=None, width=None, height=None):
        self.fps = fps if fps is not None else 1
        self.width = width if width is not None else 640
        self.height = height if height is not None else 480
        self.path_name_save_video = "captured_video.avi"

    def set_path_name_save_video(self):
        global out
        out = cv2.VideoWriter(self.path_name_save_video, fourcc, self.fps, (self.width, self.height))

    def start(self, device=None):
        self.device = device if device is not None else 0

        global cap
        cap = cv2.VideoCapture(self.device)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        # Fix image temperature
        cap.set(cv2.CAP_PROP_TEMPERATURE, 6500)

    def preview_camera(self, winname=None):
        self.winname = winname if winname is not None else "Preview"

        ret, frame = cap.read()

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cv2.waitKey(1)

    def take_write_snapshot(self):
        if not out:
            self.set_path_name_save_video()
        try:
            ret, frame = cap.read()
            if not ret:
                raise ValueError("Failed to read frame from camera")
            out.write(frame)
        except Exception as e:
            return e

    def get_frame(self):
        ret, frame = cap.read()
        if not ret:
            raise ValueError("Failed to read frame from camera")
        return frame

    def save_frames_to_avi(self, frames, output_path="captured_video.avi", fps=None):
        """ Write a list of frames to an AVI video file.
        """
        global out
        if not frames or not out:
            return

        # Write each frame to the video file
        for item in frames:
        # Extract the array if the element is a dictionary {'drop_number': x, 'frame': img}
            frame = item['frame'] if isinstance(item, dict) else item
            out.write(frame)

        # Close and release the video file
        out.release()
        out = False

    def close_window(self):
        cv2.destroyAllWindows()

    def stop(self):
       """Free camera and video writer safely."""
       if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            
       if self.out and hasattr(self.out, 'release'):
            self.out.release()
            self.out = None
