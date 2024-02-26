#!/usr/bin/env python3
""" RFB Annotation Visualizer
Role-Filler Backend

This script provides a series of helper functions to
be used by the RFB Annotation Visualizer.

In practice, this is a bunch of functions which parse
the data in <DATA_DIR>. These functions may be duplicates
of other functions in the RFB codebase, but as the visualizer
is intended to be a standalone tool, we permit this redundancy.
"""

# =================================|
# Imports
# =================================|
import csv
from collections import defaultdict
from dataclasses import dataclass
import json
import os
import numpy as np
import pandas as pd
import shutil

from typing import Union

DATA_DIR = "data/"


# =================================|
# RFB Data Object
# =================================|
class RoleFillerData:
    def __init__(self, fname: Union[str, os.PathLike]):
        self._guids, self._frames = self._init_data(fname)

    # * properties *
    @property
    def guids(self):
        return self._guids

    def frames(self, guid):
        return self._frames[guid]

    def annotations(self, anno_id, guid, frame):
        with open(f"data/{anno_id}/{guid}.{frame}.json", "r") as f:
            json_obj = json.load(f)
        return {k: v for k, v in json_obj.items() if k != "_image_id"}

    def frame_image(self, guid, frame):
        return f"images/{guid}.{frame}.png"

    # ==========================================|
    # Adjudication
    # ==========================================|
    def check_adjudication(self, guid, frame):
        names = [
            name.split("/")[-1].split(",")[-1]
            for name in os.listdir(f"{DATA_DIR}/adjudicated")
        ]
        if f"{guid}.{frame}.json" in names:
            return True
        return False

    def write_adjudicated_data(self, guid, frame, anno_id):
        """Copies a given annotation to the adjudicated"""
        shutil.copyfile(
            f"{DATA_DIR}/{anno_id}/{guid}.{frame}.json",
            f"{DATA_DIR}/adjudicated/{anno_id},{guid}.{frame}.json",
        )

    # * private methods *
    def _init_data(self, fpath: Union[str, os.PathLike]) -> tuple[list, dir]:
        """Expects a list of annotation titles
        in the form (guid.framenum)
        """
        guids, frames = [], defaultdict(list)
        if fpath.endswith(".csv"):
            with open(fpath, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    row, _ = os.path.splitext(row[0])
                    if row[0] == "guid":
                        continue
                    curr_guid, framenum = row.split(".")
                    if curr_guid not in guids:
                        guids.append(curr_guid)
                    frames[curr_guid].append(framenum)
        return guids, frames


def get_list_of_directories(long_dir, other_dir, oname="annotations.csv"):
    """Takes in two directories and writes a csv file
    containing the annotations which appear in both.
    Instance output is of the form `guid.framenum`
    """
    out = []
    for name in os.listdir(long_dir):
        if name in os.listdir(other_dir):
            out.append(name)
    with open(oname, "w") as f:
        writer = csv.writer(f)  # TODO there's got to be a better way...
        for name in out:
            writer.writerow(out)
