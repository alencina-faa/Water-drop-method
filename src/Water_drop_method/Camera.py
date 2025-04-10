class CameraOpenCV:
    global cv2
    import cv2

    global fourcc
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')

    global out
    out = False

    def __init__(self, fps=None, width=None, height=None):#, path_name_save_video=None):
        self.fps = fps if fps is not None else 1
        self.width = width if width is not None else 640
        self.height = height if height is not None else 480
        self.path_name_save_video = "captured_video.avi"#path_name_save_video if path_name_save_video is not None else "captured_video.avi"

        #global out
        #out = cv2.VideoWriter(self.path_name_save_video, fourcc, self.fps, (self.width, self.height))    
    

    def set_path_name_save_video(self):#, path_name_save_video=None):
        #self.path_name_save_video = path_name_save_video if path_name_save_video is not None else path_name_save_video
        
        global out
        out = cv2.VideoWriter(self.path_name_save_video, fourcc, self.fps, (self.width, self.height))    
               

    def start(self, device=None):
        self.device = device if device is not None else 0

        global cap 
        cap = cv2.VideoCapture(self.device)
        if not cap.isOpened():
            print("Cannot open camera")    
            exit()
    

    def preview_camera(self, winname=None):
        self.winname = winname if winname is not None else "Preview"
        #while True:
            # Capture frame-by-frame
        ret, frame = cap.read()

            # if frame is read correctly ret is True
        #    if not ret:
        #        print("Can't receive frame (stream end?). Exiting ...")
        #        break
    
            # Display the resulting frame
        #    cv2.imshow(self.winname, frame)
        #    if cv2.waitKey(1) == ord('q'):
        #        break
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cv2.waitKey(1)


    def take_write_snapshot(self):
        if not out:
            self.set_path_name_save_video()
        ret, frame = cap.read()
        out.write(frame)

    
    def close_window():
        cv2.destroyAllWindows()


    def stop():
        cap.release()
        out.release()