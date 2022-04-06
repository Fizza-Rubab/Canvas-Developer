# Canvas Development - Generating Course Files

This tool downloads material from your Canvas course site. Specifically, it looks in the 'Assignments', 'Quizzes', and 'Disussions' sections of the course site.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for generating the course files.

### Prerequisites

Functional requirements include Python 3.x and `pip` (Python package manager) as well as Google Chrome(any recent version) installed on your machine before hand. 

These are the python packages you would need before running the script.
- canvasapi
- webdriver-manager
- selenium
- selenium-wire

Download these modules by running one of the following commands on the command line depending on your platform.
Windows:
```
pip install <package-name>
```
*nix:
```
pip3 install <package-name>
```

### Retrieving the Access Token:
To run the python file `coursefiles.py` and generate course files, a canvas access token is required.
1. In Canvas, go to Account (top left) -> Settings.
1. On the Settings page, click on "+ New Access Token" button under the "Approved Integrations" section.
1. Enter the Purpose, "Automatic Course File", and leave the expiry date blank. Click on "Generate Token".
1. A token appears as a long string of characters in the next window. Copy it and paste it to a text editor. This has to be given to the program as an input.

## Canvas Settings
The tool can download certain folders from the Files section of the site if they are named as follows.
1. "syllabus.pdf": this gets copied to the "Course Syllabus" in the output folder
2. Ensure that the folder containing slides or lecture notes is named as "Slides"
3. Ensure that the folder containing assignment pdfs is named as "Assignments"
4. Ensure that the folder containing assignment solutions is named as "Assignment Solutions"

## Running the file

Befor running the program, ensure that you have a strong and stable intenet connection. Run the `coursefiles.py` python file. It will first ask for your access token in the console. Then it will ask for the course url for the which you want the course files. Copy paste the course url from your browser and ensure that it is in the following format before entering:
```
https://hulms.instructure.com/courses/1706
```
On entering the course URL, a chrome window will open and you will be redirected to the the Habib University's main LMS page. Log into LMS by entering your credentials and then wait while the automatic process runs. The console will show the progress. Do not close this browser window otherwise the execution will halt. Keep it running in the background as it will take a few minutes. Once the window closes you can find the coursefiles folder of the same name as your course in the code folder.

## Important Instructions
1. Do not close the browser window during execution. It might come up again and again due to page reload so dock it behind if necessary.
2. You can only run this code for an ongoing course.
3. Not setting up canvas in the above mentioned way will not produce errorss. However it will not be able to fetch the desired files because of naming mismatch.

## Error Instructions
If you encounter any logical or intepreter error. An error can be identified through the following:
1. The console gives some error message instead of the usual progress logs.
2. The browser wndow becomes idle for a very long time. This error will be reflected in the console.
3. The produced folder has missing items.
4. The pdfs are generated incorrectly.

Kindly take a screenshot of the console error message on the console, a screenshot of the browser window and a breif error description and mail it to `fr06161@st.habib.edu.pk`. 

