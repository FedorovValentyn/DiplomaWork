import os
import sys
import customtkinter as ctk
import logging
from navbar import NavBar
from pages.library import LibraryPage
from pages.detection import DetectionPage
from pages.home import HomePage
from keras.models import load_model


class App(ctk.CTk):
    os.environ['MEDIAPIPE_BINARY_GRAPH_PATH'] = r'D:\EXE\env\exe\Lib\site-packages\mediapipe\modules'

    def __init__(self):
        super().__init__()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Set the window size
        self.geometry("1280x720")  # Smaller resolution
        self.title("Action Detection App")
        self.resizable(False, False)

        # Create a container for the pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Initialize the NavBar
        self.navbar = NavBar(self)
        self.navbar.pack(side="top", fill="x")

        # Initialize pages and store them in a dictionary
        self.pages = {}

        # Load the model using the correct path
        self.model = self.load_model()

        # Define the actions that correspond to your model's predictions
        self.actions = ['tea', 'sugar', 'coffee', 'please', 'sorry', 'milk', 'hello', 'black',
                        'green']  # Replace with your actual action names

        # Create instances of all pages at the start to avoid recreation
        self.pages["HomePage"] = HomePage(parent=self.container, controller=self)
        self.pages["LibraryPage"] = LibraryPage(parent=self.container, controller=self)
        self.pages["DetectionPage"] = DetectionPage(parent=self.container, controller=self,
                                                    model=self.model, actions=self.actions)

        # Show the initial page
        self.show_page("HomePage")

        # Start the window updating loop
        self.update_window()

    def load_model(self):
        def resource_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        model_path = resource_path('action.h5')
        return load_model(model_path)

    def show_page(self, page_name):
        # Log page transitions
        self.logger.info(f"Switching to page: {page_name}")

        current_page = next((page for page in self.pages.values() if page.winfo_viewable()), None)
        if current_page:
            self.logger.info(f"Hiding current page: {current_page.__class__.__name__}")
            if hasattr(current_page, 'on_hide'):
                current_page.on_hide()
            current_page.pack_forget()

        page = self.pages.get(page_name)
        if page:
            self.logger.info(f"Showing page: {page.__class__.__name__}")
            page.pack(fill="both", expand=True)
            if hasattr(page, 'on_show'):
                page.on_show()

    def update_window(self):
        # This method will continuously update the window, refreshing all elements
        self.logger.debug("Updating window...")

        # Trigger updates for current visible page if needed
        current_page = next((page for page in self.pages.values() if page.winfo_viewable()), None)
        if current_page and hasattr(current_page, 'update_frame'):
            current_page.update_frame()

        # Call this method again after 16 ms (~60 FPS)
        self.after(16, self.update_window)


if __name__ == "__main__":
    app = App()
    app.mainloop()
