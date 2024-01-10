# RFB Annotation Visualizer

# TODO: timeline of frames

# ====================================|
# Imports
# ====================================|
import argparse
import csv
import os
import json

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk


# ====================================|
# Visualizer
# ====================================|
class Visualizer:
    def __init__(self, **params):
        self.window = ThemedTk(theme=params["theme"])
        self.window.title("RFB Annotation Visualizer")
        self.window.geometry("1600x900")

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
    )
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
