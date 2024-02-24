# RFB Annotation Visualizer
'''
File: RFB Annotation Visualizer
V: 2
v1 Author: Dean Cahill
v2 Added Adjudication buttons: Jeremy Huey

Known Issues:
1. (v1) Upon opening, first image won't load. Perhaps adding a self.load_annotations(None) may help
2. (v2) You will need to resize the window frame because the grid alignments are not right with the added buttons.
3. Need explanation/readme of how to use UI/buttons to adjudicate.

How to use:
(add usage here)
For v2 button use to adjudicate, please note that the intent is to overwrite Annotator 1's files until you get
a fully adjudicated set of annotations.

'''


# TODO: timeline of frames

# ====================================|
# Imports
# ====================================|
import argparse
import csv
import os
import json
import subprocess
import pyperclip

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import webbrowser

# ====================================|
# Visualizer
# ====================================|
class Visualizer:
    def __init__(self, **params):
        self.window = ThemedTk(theme=params["theme"])
        self.window.title("RFB Annotation Visualizer")
        self.window.geometry("1600x900") # problem: need to arrange these buttons into a better format.

        # Parameters
        self.agg_type = params["aggtype"]
        self.skip_type = params["skiptype"]
        self.annotator_dir = params["data_directory"]
        self.results_dir = f"{params['agreement_directory']}/{self.skip_type}"
        self.images_dir = params["image_directory"]
        self.anno_one = params["anno_one"]
        self.anno_two = params["anno_two"]

        # GUIDs
        self.guid_dropdown = ttk.Combobox(master=self.window, values=self.get_guids())
        self.guid_dropdown.current(0)
        self.guid_dropdown.grid(row=0, column=0)
        self.guid_dropdown.bind("<<ComboboxSelected>>", self.load_page)

        # Frames
        self.frame_dropdown = ttk.Combobox(
            master=self.window, values=self.get_frames(self.guid_dropdown.get())
        )
        self.frame_dropdown.current(0)
        self.frame_dropdown.grid(row=1, column=0)
        self.frame_dropdown.bind("<<ComboboxSelected>>", self.load_annotations)

        # Boxes & Such
        self.annotations = tk.Frame(master=self.window)
        self.text_one = tk.Text(master=self.annotations)
        self.text_two = tk.Text(master=self.annotations)
        self.metrics = tk.Text(master=self.annotations)
        self.t1_label = tk.Label(self.annotations, text=f"instance ID: {self.anno_one}")
        self.t2_label = tk.Label(self.annotations, text=f"instance ID: {self.anno_two}")
        self.annotations.grid(row=10, column=3)

        # Buttons for opening annotation files
        self.open_anno_one_button = tk.Button(
            master=self.window,
            text="Open Annotator One",
            command=lambda: self.open_annotation_file(self.anno_one)
        )
        self.open_anno_one_button.grid(row=3, column=0, padx=5, pady=5)
        self.open_anno_two_button = tk.Button(
            master=self.window,
            text="Open Annotator Two",
            command=lambda: self.open_annotation_file(self.anno_two)
        )
        self.open_anno_two_button.grid(row=3, column=1, padx=5, pady=5)

        # Button for moving to next frame
        self.next_frame_button = tk.Button(
            master=self.window,
            text="Next Frame",
            command=self.next_frame
        )
        self.next_frame_button.grid(row=4, column=0, padx=5, pady=5)

        # Button for moving to prev frame
        self.prev_frame_button = tk.Button(
            master=self.window,
            text="Prev Frame",
            command=self.prev_frame
        )
        self.prev_frame_button.grid(row=4, column=1, padx=5, pady=5)

        # Button for replacing and opening annotation file
        self.replace_anno1_and_open_button = tk.Button(
            master=self.window,
            text="Replace Anno1 w Anno2",
            command=self.replace_and_open_files
        )
        self.replace_anno1_and_open_button.grid(row=5, column=0, padx=5, pady=5)

    # =====================|
    # Getters
    # =====================|
    def get_guids(self):
        """Retrieve GUID list from results file"""
        out = set()
        with open(f"{self.results_dir}/{self.agg_type}-results.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "guid":
                    continue
                out.add(row[0].split(".")[0])
        return sorted(list(out))

    def get_frames(self, guid):
        """Retrieve the frame list for a given GUID
        from the results file"""
        out = []
        with open(f"{self.results_dir}/{self.agg_type}-results.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == "guid":
                    continue
                curr_guid, framenum = row[0].split(".")
                if curr_guid == guid:
                    out.append(framenum)
        return sorted(out, key=lambda x: int(x))

    def get_metrics(self, guid, frame_num):
        """Retrieve the annotation metrics for a given guid + frame
        from the results file"""
        with open(f"{self.results_dir}/{self.agg_type}-results.csv") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == f"{guid}.{frame_num}":
                    return f"Key IOU: {row[1]}\nValue IOU: {row[2]}\nPair IOU: {row[3]}\nAggregated IOU: {row[4]}\n"
        raise ValueError(f"{guid}.{frame_num} cannot be found")

    def get_annotations(self, annotator, guid, frame_num):
        """Retrieve the annotation json for a given anno/guid/frame"""
        anno_path = f"{self.annotator_dir}/{annotator}/{guid}.{frame_num}.json"
        with open(anno_path) as f:
            json_obj = json.load(f)
        return json.dumps(json_obj, indent=4)

    # =====================|
    # Event Helpers
    # =====================|
    def clear_frame(self):
        """Clear content from text boxes to swap to different GUID / frame"""
        self.text_one.delete(1.0, tk.END)
        self.text_two.delete(1.0, tk.END)
        self.metrics.delete(1.0, tk.END)

    def load_page(self, event):
        """Function for loading entire page"""
        self.clear_frame()
        self.load_frame_info(event)
        self.load_annotations(event)

    def load_frame_info(self, event):
        """Function for loading frames"""
        guid = self.guid_dropdown.get()
        self.frame_dropdown.config(value=self.get_frames(guid))
        self.frame_dropdown.current(0)

    def load_annotations(self, event):
        """Function for loading annotations"""
        guid = self.guid_dropdown.get()
        frame_num = self.frame_dropdown.get()
        self.clear_frame()
        self.text_one.insert(
            tk.END, self.get_annotations(self.anno_one, guid, frame_num)
        )
        self.text_two.insert(
            tk.END, self.get_annotations(self.anno_two, guid, frame_num)
        )
        self.metrics.insert(tk.END, self.get_metrics(guid, frame_num))

        self.t1_label.grid(row=0, column=0)
        self.text_one.grid(row=1, column=0)

        self.text_two.grid(row=1, column=1)
        self.t2_label.grid(row=0, column=1)

        self.metrics.grid(row=2, column=1)

        pic = ImageTk.PhotoImage(
            Image.open(f"{self.images_dir}/{guid}.{frame_num}.png").resize((500, 300))
        )

        image = tk.Label(self.annotations, image=pic, text=f"{guid}.{frame_num}")
        image.image = pic
        image.grid(row=2, column=0)

    # =====================|
    # Button Event Helpers (added v2)
    # =====================|
    # Callback function for replacing and opening annotation files
    def replace_and_open_files(self):
        guid = self.guid_dropdown.get()
        frame_num = self.frame_dropdown.get()
        anno_one_file = f"{self.annotator_dir}/{self.anno_one}/{guid}.{frame_num}.json"
        anno_two_file = f"{self.annotator_dir}/{self.anno_two}/{guid}.{frame_num}.json"
        # Read contents of annotator two's file
        with open(anno_two_file, 'r') as f:
            content = f.read()
        # Replace contents of annotator one's file with annotator two's file
        with open(anno_one_file, 'r') as f:
            old_content = f.read()
            pyperclip.copy(old_content)  # make a copy of the old content from anno1 to your clipboard, in case
        with open(anno_one_file, 'w') as f:
            f.write(content)
        # Open annotator one's file
        webbrowser.open(anno_one_file)  # Open file using default application
        # COMMENT ^ THIS ABOVE LINE if don't want to see it; to be faster!

    # Callback function for moving to next frame
    def next_frame(self):
        current_index = self.frame_dropdown.current()
        if current_index < len(self.frame_dropdown["values"]) - 1:
            self.frame_dropdown.current(current_index + 1)
            self.load_annotations(None)  # Reload annotations for the new frame

    # Callback function for moving to prev frame
    def prev_frame(self):
        current_index = self.frame_dropdown.current()
        if current_index > 0:
            self.frame_dropdown.current(current_index - 1)
            self.load_annotations(None)  # Reload annotations for the new frame

    # Callback function to open annotation file
    def open_annotation_file(self, annotator):
        guid = self.guid_dropdown.get()
        frame_num = self.frame_dropdown.get()
        annotation_file_path = f"{self.annotator_dir}/{annotator}/{guid}.{frame_num}.json"
        webbrowser.open(annotation_file_path)  # Open file using default application # THIS WORKED!
        # os.system(f"notepad.exe {annotation_file_path}")  # Open file using Notepad
        # subprocess.Popen(["notepad.exe", annotation_file_path])  # Open file using Notepad
        # os.system(f"start {annotation_file_path}")  # Open file using default application # this did not


# ====================================|
# Main
# ====================================|
def parse_arguments() -> argparse.Namespace:
    """
    Parses runtime arguments
    """
    parser = argparse.ArgumentParser()

    # Directories and File Info
    parser.add_argument(
        "--data_directory",
        help="Directory containing human or model annotations",
        default="./data/rfb-r2-annotations.231117",
    )
    parser.add_argument(
        "--agreement_directory",
        help="Directory containing agreement metrics",
        default="./results",
    )
    parser.add_argument(
        "--image_directory",
        help="file location of frame images",
        default="./images",
        # default="./images/images-R2-fewshot-credits",
    ) #changed default
    parser.add_argument(
        "--anno_one", help="First annotator instance ID number", default=20007
    )
    parser.add_argument(
        "--anno_two", help="Second annotator instance ID number", default=20008
    )
    parser.add_argument(
        "--skiptype",
        help="whether or not to include skips in the performance metrics",
        default="skips",
    )
    parser.add_argument(
        "--aggtype",
        help="The method of aggregation for metrics",
        default="product",
    )

    # Visual Parameters
    parser.add_argument(
        "--theme", help="visual theme to use in the GUI", default="adapta"
    )
    return parser.parse_args()


if __name__ == "__main__":
    runtime_args = parse_arguments()
    anno_viz = Visualizer(**vars(runtime_args))
    anno_viz.window.mainloop()
