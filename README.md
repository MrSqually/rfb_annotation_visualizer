# RFB Annotation Visualizer 

This tool provides an interface for qualitative analysis of the agreement between annotators within the Role-Filler Binding schema currently in development by the Brandeis CLAMS team. It is a basic GUI app using Python's Tk/Tcl toolkit to display frames and the relative annotations for those frames. This allows us to refine our understanding of edge cases and sources of disagreement, and improve both the RFB spec/guidelines and our evaluation metrics for this specification.  
See RFB Visualizer v2 Adjudication Buttons section below for adjudication process updates. 

## Requirements for Installation

The visualizer requires an installation of Python which contains the Tk toolkit. On Windows and Mac machines, this should be installed by default. On Linux, the Tk interface can be installed from your package manager:

``` $sudo apt-get install python3-tk ```

All other necessary packages can be found in `requirements.txt`

## App Usage 

The visualizer pulls its data from three local directories which are, by default, positioned relative to root. If you're using different directories than the defaults, use absolute paths. 

- `./data` is the directory containing human (or machine) annotations in .json format. Each annotator instance should be in its own sub-directory, labeled by its ID. 
- `./results` is the directory containing IAA metrics for these annotations, in text format. the results file should be a single csv which contains at least each frame ID for each GUID. 
- `./images` is the directory containing still images of the frames. 
  - [!Important] - add the image sets into the `./images`

The app can be run with `$python3`, and these directories can be set using the `data_directory`, `agreement_directory`, and `image_directory` runtime arguments.

Other runtime arguments include:

- `anno_one` : the instance ID of the first annotator 
- `anno_two` : the instance ID of the second annotator
- `skip_type`: determines whether or not frames that are marked as "skip" are included in the data 
- `agg_type` : determines what form of aggregation we use to calculate IAA
- `theme`    : TTK visual theme to be used by the app

## Next Steps

This still needs some work. The original IAA calculation that this tool was built on was revealed to be flawed, so minor changes may be needed if the revised IAA ends up being formatted differently. I also want to improve the visual component with better formatting + a more intuitive way to view the frames along a timeline.



# RFB Visualizer v2 Adjudication Buttons
This is an update to the tool to add buttons that allow the manual adjudication process. 
You will also need to run the IAA agreement code from 
[RFB Annotation Env](https://github.com/clamsproject/aapb-annenv-role-filler-binder) repo. 
For future repo managers, please consider integrating this repo(RFB_annotation_visualizer) into RFB Annotation Env.  

Buttons added: 
1. Open Annotator One - Opens the `.json` file for that frame for that annotator. Uses your default option for that filetype. 
This lets you manually edit the files if needed. 
2. Open Annotator Two
3. Next Frame - (tested against first and last frames of videos)
4. Previous Frame - (tested against first and last frames of videos)
5. Replace Anno1 w Anno2 
   1. This button copies Anno1's current annotation to your computer's clipboard in case you want to undo it. (You could comment this out)
   2. Copies Anno2's annotation. 
   3. Overwrites all of Anno1 file with Anno2.
   4. Opens Anno1 file in your file editor. (You could comment this out)
   5. The intention of this is that you will create an adjudicated raw from the first annotator, so set the first annotator
      as the one you suspect will be the better set to reduce use of this button. 

Note - the current update is rudimentary and has sizing/spacing issues for the window. Workaround: expand the window of the
visualizer after it opens. 

## How to Adjudicate
1. Obtain the RFB raws from multiple annotators/server-storage. 
2. Load the raws data into the Annotation Env for RFB to do Raw Annotation InterAnnotator Agreement Assessment.
3. Run `aapb-annenv-role-filler-binder/raw_annotation_iaa_assessment/src/rfb_agreement.py` to obtain IAA results `.csv`.
   1. Optionally, run `aapb-annenv-role-filler-binder/raw_annotation_iaa_assessment/src/ragreement_report.py`
   to get a readable aggregated report. 
4. Take the IAA results `.csv` from step3, and run 
`aapb-annenv-role-filler-binder/raw_annotation_iaa_assessment/non_match_iaa_result_finder.py` to obtain a `.csv` of the 
frames/entries where the two annotators do not match completely. (Non-"1.0, 1.0, 1.0, 1.0" lines). 
5. That list gives you the frames you can go to manually in the visualizer and do adjudication for. 
6. Make decisions for the adjudication. (e.g. deciding which frame should be the first readable frame and 
which are duplicates. Spelling, *s, etc.)

### Discussing Automatic Adjudication
Manual Adjudication was done because the issues involved with deciding how to do an automated machine adjudication.
One concept was to take r2 20007's data as a base, and then copy 20008 into it when 20008 differed. 
However, a closer look into the r2 data revealed that we would still have to deal with concerns about which frame was the
first frame, and how to automatically detect that, issues with other messy errors, and that sometimes moving in 20008 
did not seem to increase the quality. 
Therefore, automatic adjudication has issues that are, as of yet, unsolved. 
