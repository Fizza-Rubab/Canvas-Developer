# Canvas Development - Generating Course Files

This tool downloads material from your Canvas course site. Specifically, it looks in the 'Assignments', 'Quizzes', and 'Disussions' sections of the course site.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for generating the course files.

### Prerequisites

Functional requirements include Python 3.x and `pip` (Python package manager) as well as Google Chrome (any recent version) installed on your machine before hand. 

These are the python packages you would need before running the script.

- canvasapi
- webdriver-manager
- selenium
- selenium-wire

Download these modules by running one of the following commands on the command line depending on your platform.

Windows: `pip install <package-name>`

*nix: `pip3 install <package-name>`

### Retrieving the Access Token:
To run the python file `coursefiles.py` and generate course files, a canvas access token is required.

1. In Canvas, go to Account (top left) -> Settings.
1. On the Settings page, click on "+ New Access Token" button under the "Approved Integrations" section.
1. Enter the Purpose, "Automatic Course File", and leave the expiry date blank. Click on "Generate Token".
1. A token appears as a long string of characters in the next window. Copy it and paste it to a text editor. This has to be given to the program as an input.

## Additional Material
The tool can download certain folders from the Files section of the site if they are named as follows.

1. "syllabus.pdf": this file, if found, gets copied to the "Course Syllabus" sub-directory in the output folder
1. "Slides/": the contents of this folder, if found, are copied to the "Lecture Notes" sub-directory in the output folder
1. "Assignments/": the contents of this folder, if found, are copied to the "Assessments and Sample solutions/Assignment Copies/" sub-directory in the output folder
1. "Assignment Solutions/": the contents of this folder, if found, are copied to the "Assessments and Sample solutions/Model Assignment Solutions/" sub-directory in the output folder

## Running the file

Before running the program, ensure that you have a strong and stable Internet connection. Run the `coursefiles.py` python file from the command line as follows depending on your platform.

Windows: `python coursefiles.py`

*nix:  `python3 coursefiles.py`

You will then be asked for certain inputs:
1. Your access token: This is the token that you generated above. Please copy it here from your text editor where you had pasted it.
1. Your course url: This is the URL of the Canvas site of the course whose course file you want to generate. It is of the form: https://hulms.instructure.com/courses/<course-number>. You can copy-paste it from your browser.

A new Google Chrome window will now open and you will be redirected to the the Habib University's main LMS page. Please log in here to initiate the download process.

AS the program runs, various pages will automatically load and get downloaded in this Google Chrome window. You can safely ignore the winow, but take care to _NOT_ close it yet. The console from where you ran the command will show the progress. The download takes some time and the Google Chrome window closes automatically once the download is complete. You can now find the "coursefiles" folder of the same name as your course in the working directory.

## Important Instructions
1. Do not close the browser window during execution. It might come to the foreground repeatedly due to page reloads. If som dock it to the background.
1. The tool only works for an ongoing course.

## Error Instructions
Any error during the download process can be identified through the following:

1. The console gives some error message instead of the usual progress logs.
1. The browser window becomes idle for a very long time. This error will be reflected in the console.
1. The produced folder has missing items.
1. The pdfs are generated incorrectly.

Kindly take a screenshot of the console error message on the console, a screenshot of the browser window and a breif error description and mail it to `fr06161@st.habib.edu.pk`. 

