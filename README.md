# RFB Annotation Visualizer 

This tool provides an interface for qualitative analysis of the agreement between annotators within the Role-Filler Binding schema currently in development by the Brandeis CLAMS team.
The app has been re-written in streamlit, as this library is more intuitive and extensible than Tk within the context of rapid deployment.

Currently, the app displays frame images from a predetermined data directory, as well as RFB annotations on those frames. This allows us to refine our understanding of edge cases and sources of disagreement, and improve both the RFB spec/guidelines and our evaluation metrics for this specification. 

## Installation 

The visualizer requires the `streamlit` library, as well as several dependencies that it should pull in automatically (i.e., `numpy` and `scipy`). Once installed, you can run the app from the project ROOT using the command:

``` sh
$ streamlit run src/streamlit_app.py
```

## Running the App 

### Visualization
The visualizer should launch automatically when the above command is run. This portion of the guide assumes a small amount of familiarity with the RFB project, its goals, and the nature of its data - primarily in the assumptions we make about what you have and where it should go:

- data: a set of data for RFB is a directory of annotations in .JSON format. The name of this directory should be the instance id of the annotator (e.g., 20007). Files should be of the form (`guid.frame_num.json`). The data folder also contains a csv with the names of frames within the directories which are dual annotated (we provide a function for retrieving this information in `rfb_process.py`).

- images: a directory of images of the same title convention as above (`guid.framenum`)

### Adjudication

The other primary goal of this tool is the adjudication of dual-annotated data into a Gold standard. The visualizer provides a simple interface for copying these annotations into an `adjudicated` directory. The json annotations are *copied* into the adjudication folder, and the instance ID used for adjudication is encoded into the filename in order to maintain a throughline of annotation to annotator. 
 
