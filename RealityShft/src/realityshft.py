# Chris W.
# For VT Hacks X 2022
# RealityShft
#   -A basic translator for the real world to fiction
# Using Tkinter, Python, google api's, and dream studio's stable diffusion api

#Dont even try to use the very unsecure api keys just left here. They no longer will work

import io
import os
import warnings
import tkinter
import tkintermapview
import google_streetview.api
import numpy as np
import cv2
import glob
import imutils
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import customtkinter
from tkintermapview import TkinterMapView

customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):

    WINDOWNAME = "RealityShft"
    WIDTH = 800
    HEIGHT = 600

    #set up gui frames
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.title(App.WINDOWNAME)
        self.geometry(str(width) + "x" + str(height))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        #frame_left

        self.frame_left.grid_rowconfigure(2, weight=1)

        '''
        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Set Marker",
                                                command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Clear Markers",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)
        '''

        self.loading_text = customtkinter.CTkLabel(self.frame_left, text="Nothing Loading")
        self.loading_text.grid(row=0, column=0, padx=(20, 20), pady=(10, 0))
        self.loading = customtkinter.CTkProgressBar(self.frame_left, mode="indeterminate")
        self.loading.grid(row=1, column=0, padx=(20, 20), pady=(10, 50))
        self.loading.set(0)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Style view:", anchor="w")
        self.map_label.grid(row=3, column=0, padx=(20, 20), pady=(10, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Normal", "Satellite"], command=self.change_map) 
        self.map_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"], command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 0))

        self.shift_type = customtkinter.CTkLabel(self.frame_left, text="Shift Style:", anchor="w")
        self.shift_type .grid(row=7, column=0, padx=(20, 20), pady=(10, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["Fantasy", "Futuristic", "Steampunk"],command=self.change_style)
        self.map_option_menu.grid(row=8, column=0, padx=(20, 20), pady=(10, 10))

        #frame_right

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right, placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,text="Search",width=90, command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_address("Blacksburg")
        self.map_option_menu.set("Normal")
        self.appearance_mode_optionemenu.set("Dark")
        self.style = "Fantasy"

        self.map_widget.add_left_click_map_command(self.open_view)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def start_loading(self):
        self.loading_text.configure(text="Loading...")
        self.loading.set(0)
        self.loading.start()
    def stop_loading(self):
        self.loading_text.configure(text="Finished")
        self.loading.stop()
        self.loading.set(100)

    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_style(self, style: str):
        if style == "Fantasy":
            self.style = "Fantasy Digital Art"
        elif style == "Futuristic":
            self.style = "Futuristic realism"            
        elif style == "Steampunk":
            self.style = "Steampunk Digital Art"
            

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    #download and generate images
    def open_view(self, coord_tuple):
        self.set_marker_event()
        self.start_loading()
        location = "{}, {}".format(coord_tuple[0], coord_tuple[1])
        PIXELS = "640x640"
        KEY = 'AIzaSyB_7g1eVnt9ZU-GPUXCHRPmsO-7S0cfPGc'
        STEPANGLE = 45
        params = []
        for i in range(0, 360, STEPANGLE):
            params.append({'size': PIXELS, 'location': location, 'heading': str(i), 'pitch': '0', 'key': KEY})
        results = google_streetview.api.results(params)

        # Download images to directory 'downloads'
        results.download_links('../downloads')
        img_paths = glob.glob('../downloads/*.jpg')
        images = []

        for image in img_paths:
            img = cv2.imread(image)
            images.append(img)

        imageStitcher = cv2.Stitcher_create()
        error, stitched_image = imageStitcher.stitch(images)

        if not error:
            cv2.imwrite("../downloads/stitchOut.png", stitched_image)
            image = Image.open("../downloads/stitchOut.png")
            self.diffuse(image)
            cv2.imshow("Stitched Image", stitched_image)
        else:
            print("Error stitching images")

        self.stop_loading()

    # diffuse the image using dream studio
    def diffuse(self, image):
        h = image.height
        w = image.width
        h = h - h % 64
        w = w - w % 64
        image = image.crop((0,0,w,h))
        
        stability_api_key = 'sk-ihk7pVpQe9Jtq2v5NuwcTdgJ8fsHXIULQ6kzoE6fDodmvGNl'
        stability_api = client.StabilityInference(key=stability_api_key, verbose=True,)
        answers = stability_api.generate(prompt=self.style, init_image=image, start_schedule=0.6)

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.show()
                    img.write("../downloads/generated_image.jpg")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

# init
if __name__ == "__main__":
    app = App()
    app.start()

