# RFB Annotation Visualizer 

This tool provides an interface for qualitative analysis of the agreement between annotators within the Role-Filler Binding schema currently in development by the Brandeis CLAMS team. It is a basic GUI app using Python's Tk/Tcl toolkit to display frames and the relative annotations for those frames. This allows us to refine our understanding of edge cases and sources of disagreement, and improve both the RFB spec/guidelines and our evaluation metrics for this specification.

## Requirements for Installation

The visualizer requires an installation of Python which contains the Tk toolkit. On Windows and Mac machines, this should be installed by default. On Linux, the Tk interface can be installed from your package manager:

``` $sudo apt-get install python3-tk ```

All other necessary packages can be found in `requirements.txt`

## App Usage 

The visualizer pulls its data from three local directories which are, by default, positioned relative to root. If you're using different directories than the defaults, use absolute paths. 

- `./data` is the directory containing human (or machine) annotations in .json format. Each annotator instance should be in its own sub-directory, labeled by its ID. 
- `./results` is the directory containing IAA metrics for these annotations, in text format. the results file should be a single csv which contains at least each frame ID for each GUID. 
- `./images` is the directory containing still images of the frames. 

The app can be run with `$python3`, and these directories can be set using the `data_directory`, `agreement_directory`, and `image_directory` runtime arguments.

Other runtime arguments include:

- `anno_one` : the instance ID of the first annotator 
- `anno_two` : the instance ID of the second annotator
- `skip_type`: determines whether or not frames that are marked as "skip" are included in the data 
- `agg_type` : determines what form of aggregation we use to calculate IAA
- `theme`    : TTK visual theme to be used by the app

## Next Steps

This still needs some work. The original IAA calculation that this tool was built on was revealed to be flawed, so minor changes may be needed if the revised IAA ends up being formatted differently. I also want to improve the visual component with better formatting + a more intuitive way to view the frames along a timeline.
