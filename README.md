# Canvas Development - Generating Course Files

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for generating the course files.

### Prerequisites

Functional requirements include Python 3.x and pip (Python package manager) as well as Google Chrome(any recent version) installed on your machine before hand. 

These are the python packages you would need before running the script.
- canvasapi
- webdriver-manager
- selenium
- selenium-wire

Download these modules by doing
```
pip install <package-name>
```


### Retrieving the Access Token:
To run the python file`coursefiles.py` and generate course files, a canvas access token is required. Go to your account settings and click on new access token button in the Approved Integrations section. Give any name, set the date and time as you wish and save the provided token value somwehere. This has to be given to the program as an input.

## Canvas Settings
Prior to running the tool, your canvas course site should meet the following requirements.
1. Ensure that the syllabus is named as `syllabus.pdf`
2. Ensure that the folder containing slides or lecture notes is named as `Slides`
3. Ensure that the folder containing assignment pdfs is named as `Assignments`
4. Ensure that the folder containing assignment solutions is named as `Assignment Solutions`

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

