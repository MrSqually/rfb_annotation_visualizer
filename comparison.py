# Imports
import argparse
import csv
import os
import json

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
# ====================================|
window = ThemedTk(theme="adapta")
window.title("RFB Annotation Visualizer")
window.geometry("1600x900")


# ====================================|
# CLI Arguments
def parse_arguments():
    """
    Parses runtime arguments
    """
    parser = argparse.ArgumentParser()

    # Directories and File Info
    data_directory = parser.add_argument(
        "--data_directory",
        help="Directory containing human or model annotations",
        default="./data/rfb-r2-annotations.231117/",
    )
    iaa_directory = parser.add_argument(
        "--agreement_directory",
        help="Directory containing agreement metrics",
        default="./results/",
    )
    image_directory = parser.add_argument(
        "--image_directory",
        help="file location of frame images",
        default="./data/images",
    )
    annotator_one = parser.add_argument(
        "--anno_one", help="First annotator instance ID number", default=20007
    )
    annotator_two = parser.add_argument(
        "--anno_two", help="Second annotator instance ID number", default=20008
    )
    skiptype = parser.add_argument(
        "--skiptype",
        help="whether or not to include skips in the performance metrics",
        default="skips",
    )
    aggtype = parser.add_argument(
        "--aggtype",
        help="The method of aggregation for metrics",
        default="product",
    )

    # Visual Parameters

    return parser.parse_args()


# ====================================|
def get_aggregation(agg_type):

    agg = agg_type

    aggregation = {"average": "total IOU = (keyIOU * valIOU * pairIOU) / 3",
                   "product": "total IOU = keyIOU * valIOU * pairIOU"}
    
    fuzzy_match = {"nofuzzy": "perfect matches are considered 1.0, else 0.0",
                    "simplefuzzy": "matches above threshold are considered 1.0",
                    "complexfuzzy": "fuzzy match value is used directly"}
    
    return f"{aggregation[agg]}"

def get_guids(agg_type, skip_type):
    out = set()
    with open(f"results/{skip_type}/{agg_type}-results.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "guid":
                continue
            out.add(row[0].split(".")[0])
    return sorted(list(out))


def get_frame_metrics(guid, frame_num, agg_type, skip_type):
    with open(f"results/{skip_type}/{agg_type}-results.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == f"{guid}.{frame_num}":
                return f"Key IOU: {row[1]}\nValue IOU: {row[2]}\nPair IOU: {row[3]}\nAggregated IOU: {row[4]}\n"
    raise ValueError(f"{guid}.{frame_num} cannot be found")


def get_annotator_response(annotator, guid, framenum):
    anno_path = f"data/rfb-r2-annotations.231117/{annotator}/{guid}.{framenum}.json"
    with open(anno_path) as f:
        json_obj = json.load(f)

    return json.dumps(json_obj, indent=4)


def get_frames(guid, agg, skip):
    out = []
    with open(f"results/{skip}/{agg}-results.csv") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "guid":
                continue
            else:
                curr_guid, framenum = row[0].split(".")
                if curr_guid == guid:
                    out.append(framenum)
    return sorted(out, key=lambda x: int(x))


def load_frame():
    annotations = tk.Frame(master=window)
    text_box1 = tk.Text(master=annotations, height=16)
    text_box2 = tk.Text(master=annotations, height=16)
    metrics = tk.Text(master=annotations, height=10)
    
    text_box1.delete(1.0, tk.END)
    text_box2.delete(1.0, tk.END)
    metrics.delete(1.0, tk.END)


def load_page(event):
    """
    wrapper function for loading the page.
    """
    load_guid_info(event)
    load_annotations(event)


def load_guid_info(event):
    """
    function for GUID
    """
    load_frame()

    guid = guid_dropdown.get()
    frame_dropdown.config(value=get_frames(guid, agg_type, skip_type))
    frame_dropdown.current(0)


def load_annotations(event):
    """
    load the frame annotations + metrics
    """
    guid = guid_dropdown.get()
    frame_num = frame_dropdown.get()
    text_box1.delete(1.0, tk.END)
    text_box2.delete(1.0, tk.END)
    metrics.delete(1.0, tk.END)

    text_box1.insert(tk.END, get_annotator_response(ANNO_ONE, guid, frame_num))
    text_box1.grid(row=0, column=0)
    text_box2.insert(tk.END, get_annotator_response(ANNO_TWO, guid, frame_num))
    text_box2.grid(row=0, column=1)

    metrics.insert(tk.END, get_frame_metrics(guid, frame_num, agg_type, skip_type))
    metrics.insert(tk.END, get_aggregation(agg_type))
    metrics.grid(row=1, column=1)

    pic = ImageTk.PhotoImage(Image.open(f"{IMG_DIR}/{guid}.{frame_num}.png").resize((300,300)))
    
    image = tk.Label(annotations, image=pic)
    image.grid(row=2, column=0)

# Main
if __name__ == "__main__":
    # Get CLI
    args = parse_arguments()
    DATA_DIR   = args.data_directory
    RESULT_DIR = args.agreement_directory
    IMG_DIR    = args.image_directory
    ANNO_ONE   = args.anno_one
    ANNO_TWO   = args.anno_two
    agg_type   = args.aggtype
    skip_type  = args.skiptype

    # GUID Box
    guids = get_guids(agg_type, skip_type)
    guid_dropdown = ttk.Combobox(master=window, values=guids)
    guid_dropdown.current(0)
    guid_dropdown.grid(row=0, column=0)
    guid_dropdown.bind("<<ComboboxSelected>>", load_page)

    # Image Box
    frame_dropdown = ttk.Combobox(
        master=window, values=get_frames(guid_dropdown.get(), agg_type, skip_type)
    )
    frame_dropdown.current(0)
    frame_dropdown.grid(row=1, column=0)
    frame_dropdown.bind("<<ComboboxSelected>>", load_annotations)

    # Text Boxes
    annotations = tk.Frame(master=window)
    text_box1 = tk.Text(master=annotations)
    text_box2 = tk.Text(master=annotations)
    metrics = tk.Text(master=annotations)


    annotations.grid(row=10, column=3)
    window.mainloop()
