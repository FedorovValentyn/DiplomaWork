import os
import sys
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk


class LibraryPage(ctk.CTkFrame):
    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for both dev and PyInstaller """
        try:
            # When using PyInstaller, _MEIPASS is where the temporary files are extracted
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Set dark mode background color
        self.configure(fg_color='gray18')

        # Search bar
        self.search_bar = ctk.CTkEntry(self, placeholder_text="Search actions...", fg_color='gray28', text_color='white')
        self.search_bar.pack(pady=10, padx=10, fill=tk.X)
        self.search_bar.bind("<KeyRelease>", self.update_search)

        self.videos = {
            "action1": (self.resource_path("assets/GIFs/black.gif"), "Black"),
            "action2": (self.resource_path("assets/GIFs/green.gif"), "Green"),
            "action3": (self.resource_path("assets/GIFs/coffee.gif"), "Coffee"),
            "action4": (self.resource_path("assets/GIFs/hello.gif"), "Hello"),
            "action5": (self.resource_path("assets/GIFs/tea.gif"), "Tea"),
            "action6": (self.resource_path("assets/GIFs/sorry.gif"), "Sorry"),
            "action7": (self.resource_path("assets/GIFs/sugar.gif"), "Sugar"),
            "action8": (self.resource_path("assets/GIFs/please.gif"), "Please"),
            "action9": (self.resource_path("assets/GIFs/milk.gif"), "Milk")
        }

        self.filtered_videos = self.videos.copy()

        self.canvas = tk.Canvas(self, bg='gray18', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ctk.CTkScrollbar(self, orientation=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.content_frame = ctk.CTkFrame(self.canvas, fg_color='gray18')
        self.canvas.create_window((0, 0), window=self.content_frame, anchor='nw')

        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.display_gifs_and_descriptions()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def display_gifs_and_descriptions(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.gifs = []
        row_index = 0

        for action, (gif_path, description) in self.filtered_videos.items():
            try:
                gif_frame = ctk.CTkFrame(self.content_frame, fg_color='gray18')
                gif_frame.grid(row=row_index, column=0, padx=10, pady=10, sticky='nsew')

                canvas = tk.Canvas(gif_frame, width=640, height=360, bg='gray18', highlightthickness=0)
                canvas.pack()

                gif = Image.open(gif_path)
                frames = []
                delays = []
                try:
                    while True:
                        frame = gif.copy()
                        frames.append(frame)
                        delays.append(gif.info['duration'])
                        gif.seek(gif.tell() + 1)
                except EOFError:
                    pass

                print(f"Loaded {len(frames)} frames with delays: {delays}")

                if not frames or not delays:
                    raise ValueError(f"No frames or delays found for GIF {gif_path}")

                self.gifs.append({
                    'canvas': canvas,
                    'frames': frames,
                    'delays': delays
                })

                desc_label = ctk.CTkLabel(
                    gif_frame,
                    text=description,
                    wraplength=200,
                    font=("Arial", 24),
                    text_color='white'
                )
                desc_label.pack(pady=10)

                separator = ctk.CTkFrame(gif_frame, height=2, width=640, fg_color='gray28')
                separator.pack(fill='x', pady=10)

                row_index += 1

            except Exception as e:
                print(f"Error loading GIF {gif_path}: {e}")

        def update_gif(gif_data, frame_index=0):
            canvas = gif_data['canvas']
            frames = gif_data['frames']
            delays = gif_data['delays']

            if frames:
                frame = frames[frame_index % len(frames)]
                img_tk = ImageTk.PhotoImage(image=frame)
                canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                canvas.img_tk = img_tk

                next_index = (frame_index + 1) % len(frames)
                delay = delays[frame_index % len(delays)] if frame_index < len(delays) else 100
                self.after(delay, update_gif, gif_data, next_index)

        for gif_data in self.gifs:
            update_gif(gif_data)

    def update_search(self, event):
        search_query = self.search_bar.get().lower()
        self.filtered_videos = {action: data for action, data in self.videos.items() if search_query in data[1].lower()}
        self.display_gifs_and_descriptions()
