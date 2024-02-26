#!/usr/bin/env python3
""" RFB Annotation Visualizer
Streamlit Implementation

The original version of this visualization app
using the python TCL API (tkinter) for its frontend.
I am electing not to explain why we needed to replace this
(as it should be obvious).

This implementation uses streamlit for quick visualization,
and provides a more fluid interface to look at an entire set
of annotations.
"""

# =================================|
# Imports
# =================================|
import argparse
import os

import streamlit as st
import numpy as np
import pandas as pd

import rfb_process

# =================================|
# RFB Backend - Data Access
# =================================|
rfb_data = rfb_process.RoleFillerData("data/annotations.csv")
ANNO_1 = 20007
ANNO_2 = 20008

# =================================|
# Front End - Visual Structure
# =================================|
st.title("Role Filler Binder - Annotation Visualization")


def set_frame_num(frame_num):
    st.session_state.frame = framelist[frame_num]


# GUID Dropdown
guid = st.selectbox(label="GUIDS", options=rfb_data.guids, key="guid")

# Frame Rotary
framelist = rfb_data.frames(guid)
frame = st.selectbox(label="FRAME NUMBER", options=framelist, key="frame")

frame_idx = 0

# Buttons
left, right = st.columns(2)
with st.container():
    with left:
        prev_frame_value = (frame_idx - 1) % len(framelist)
        frame_idx = prev_frame_value
        if st.button(
            "Prev Frame", on_click=set_frame_num, args=[prev_frame_value], key="prev"
        ):
            frame_idx = prev_frame_value
    with right:
        next_frame_value = (frame_idx + 1) % len(framelist)
        frame_idx = next_frame_value
        if st.button(
            "Next Frame", on_click=set_frame_num, args=[next_frame_value], key="next"
        ):
            frame_idx = next_frame_value
# Center Frame
centerL, centerR = st.columns(2)
with centerL:
    # Annotation Text
    with st.container():
        st.header(frame)
        with st.container():
            st.write(f"Annotator {ANNO_1}")
            st.write(rfb_data.annotations(ANNO_1, guid, framelist[frame_idx]))
        with st.container():
            st.write(f"Annotator {ANNO_2}")
            st.write(rfb_data.annotations(ANNO_2, guid, framelist[frame_idx]))
with centerR:
    # Frame Image
    with st.container():
        image_id = rfb_data.frame_image(guid, frame)
        if image_id:
            st.image(image_id)
    # Adjudication
    with st.container():
        st.header("Adjudication")
        if st.button(f"Adjudicate frame in favor of {ANNO_1}"):
            if not rfb_data.check_adjudication(guid, frame):
                rfb_data.write_adjudicated_data(guid, frame, ANNO_1)
        if st.button(f"Adjudicate frame in favor of {ANNO_2}"):
            if not rfb_data.check_adjudication(guid, frame):
                rfb_data.write_adjudicated_data(guid, frame, ANNO_2)
        st.metric(
            "Has this frame been adjudicated?",
            value="✅" if rfb_data.check_adjudication(guid, frame) else "🇽",
        )
