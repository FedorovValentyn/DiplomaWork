import customtkinter as ctk

class NavBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = parent

        # Configure grid layout to center the buttons
        self.grid_rowconfigure(0, weight=1)  # Center vertically
        self.grid_columnconfigure(0, weight=1)  # Left empty to center buttons
        self.grid_columnconfigure(1, weight=1)  # Home button column
        self.grid_columnconfigure(2, weight=1)  # Library button column
        self.grid_columnconfigure(3, weight=1)  # Detection button column
        self.grid_columnconfigure(4, weight=1)  # Right empty to center buttons

        # Home button
        home_button = ctk.CTkButton(self, text="Home", command=lambda: self.controller.show_page("HomePage"),
                                    fg_color="blue", text_color="white", width=200, height=50)
        home_button.grid(row=0, column=1, padx=10, pady=10)

        # Library button
        library_button = ctk.CTkButton(self, text="Library", command=lambda: self.controller.show_page("LibraryPage"),
                                       fg_color="green", text_color="white", width=200, height=50)
        library_button.grid(row=0, column=2, padx=10, pady=10)

        # Detection button
        detection_button = ctk.CTkButton(self, text="Detection", command=lambda: self.controller.show_page("DetectionPage"),
                                         fg_color="red", text_color="white", width=200, height=50)
        detection_button.grid(row=0, column=3, padx=10, pady=10)

        # Pack the navbar to fill the top of the window
        self.pack(side="top", fill="x")
