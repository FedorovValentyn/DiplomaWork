import customtkinter as ctk

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configure the main frame to have a single cell centered
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a sub-frame to hold the content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")

        # Center the label and description within the content_frame
        label = ctk.CTkLabel(content_frame, text="Welcome to the Action Detection App!", font=("Helvetica", 30, "bold"))
        label.pack(pady=20)

        description = ctk.CTkLabel(content_frame, text="This app is designed to detect actions using video input.",
                                   font=("Helvetica", 20))
        description.pack(pady=10)

        # Ensure the content_frame is also centered within the main window
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Pack the content in the center
        label.pack(anchor="center")
        description.pack(anchor="center")

        content_frame.pack(expand=True)  # Center the content frame
