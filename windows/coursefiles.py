from canvasapi import *
import os
import shutil
from datetime import datetime
from datetime import timezone
import requests
import sys
import subprocess
import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def rename_last_downloaded_file(dummy_dir, destination_dir, new_file_name):
    def get_last_downloaded_file_path(dummy_dir):
        """ Return the last modified -in this case last downloaded- file path.

            This function is going to loop as long as the directory is empty.
        """
        while not os.listdir(dummy_dir):
            time.sleep(2)
        return max([dummy_dir+"/"+f for f in os.listdir(dummy_dir)], key=os.path.getctime)

    while '.part' in get_last_downloaded_file_path(dummy_dir):
        time.sleep(2)
    shutil.move(get_last_downloaded_file_path(dummy_dir), destination_dir+"/"+new_file_name)

API_URL ="https://hulms.instructure.com"
API_KEY = input("Enter API Access token key:\n")
# API_KEY = "17361~Mqdn4rB8xG24lXim7kwhCXcpcsQqgSpsBlC4Sv6bJWJtK2QSMQn34GN4SA1cHb7n"
canvas = Canvas(API_URL, API_KEY)
courseUrl = input("Enter course URL:\n")
# courseUrl="https://hulms.instructure.com/courses/1282"
dummypath = "C:/Users/fizza/Documents/dummy"
if not os.path.exists(dummypath):
    os.mkdir(dummypath)
else:
    for f in os.listdir(dummypath):
        os.remove(dummypath+"/"+f)

appState = {
    "recentDestinations": [
        {
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}
profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),
           'savefile.default_directory': dummypath}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', profile)
chrome_options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(options=chrome_options, executable_path="C:\chromedriver_win32\chromedriver.exe")
driver.get("https://hulms.instructure.com/")
element = WebDriverWait(driver, 2000).until(
        EC.title_is("Dashboard")
    )
courseID = int(courseUrl.split("/")[-1])

course = canvas.get_course(courseID)
courseDict = course.__dict__
d = courseDict["created_at"]
dt = datetime.fromisoformat(d[:-1]).astimezone(timezone.utc)
if int(dt.strftime("%m"))>=5 and int(dt.strftime("%m"))<=8:
    term = "Fall"
else:
    term = "Spring"
cname = courseDict['name'] +" " + term +" " + str(dt.year)
parent_dir = "D:/"
path = os.path.join(parent_dir, cname)
os.mkdir(path)
subfolders = ["a. Course Contents", "b.  Course Objectives", "c. Weekly plan of contents of lectures delivered",
"d. Attendance Record", "e. Copy of lecture notes", "f.  List of Reference Material", 
"g. Copy of assignment,Quizzes, Midterm and Final Examination", "h. Model solutions of all assessments tests given in previous section",
"i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks",
"j. Marks distribution and Grading Model", "k.Complete result of the course", "l. Outcomes Assessment",
"m. Detail of technology involved", "n. Design skills-techniques practiced", "o. Complete analysis of effectiveness of course and level of silks ensured in Technology, Emerging Development Paradigms, Pertaining to Industry, Mod",
"Syllabus"]
parent_dir = path
for folder in subfolders:
    os.mkdir(os.path.join(parent_dir,folder))
print("[-] made the folders")
inthesyllabus = ["a. Course Contents", "b.  Course Objectives", "c. Weekly plan of contents of lectures delivered",
"f.  List of Reference Material"]
for dest in inthesyllabus:
    shutil.copyfile("./InTheSyllabus.pdf", str(os.path.join(parent_dir,dest+"/InTheSyllabus.pdf")))
print("[-] copied files")
    
f  = (course.get_files())
for i in f:
    if str(i)=="syllabus.pdf":
        i.download(path+"/Syllabus/" + str(i))
        print("[-] Syllabus downloaded")
        break

# Get Read only copy of all quizzes
quizzespath = path + "/g. Copy of assignment,Quizzes, Midterm and Final Examination/Quizzes"
os.mkdir(quizzespath)
quizzes = course.get_quizzes()
for q in quizzes:
    url = (q.__dict__)["html_url"]
    url+="/read_only"
    driver.get(url)
    driver.execute_script("document.getElementById('questions').classList.remove('brief');")
    driver.execute_script("window.print();")
    rename_last_downloaded_file(dummypath, quizzespath+'/', str((q.__dict__)["title"])+'.pdf')

print("[-] Quizzes Preview done")



# # Get model solution for all quizzes
quizzesmodelpath = path + "/h. Model solutions of all assessments tests given in previous section/Quizzes"
os.mkdir(quizzesmodelpath)
for q in quizzes:
    try:
        driver.get(q.__dict__["html_url"]+'/edit#questions_tab')
        try:
            driver.execute_script("""document.getElementById('questions').classList.remove('brief');sp = document.getElementsByClassName('correct_answer');for(var i = 0; i < sp.length; i++){sp[i].style.color = 'Green'; sp[i].style.border = 'solid #00FF00'};""")
        except:
            pass
        time.sleep(2)  
        driver.execute_script("window.print();")
        time.sleep(1)
        rename_last_downloaded_file(dummypath, quizzesmodelpath+'/', str((q.__dict__)["title"])+'-solution.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        raise
print("[-] Quizzes Model Solution is done")

# Get 3 sample graded student submissions of each quiz
quizsubmissionspath = path + "/i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks/Quizzes"
os.mkdir(quizsubmissionspath)
for q in quizzes:
    submissions = q.get_submissions()
    s = sorted([i for i in submissions if i.score!=None], key=lambda d: d.__dict__['score'])
    if s==[]:
        continue
    lowestsub = s[0]
    highestsub = s[-1]
    Sum = 0
    count = 0
    for i in s:
        if i.score!=None:
            Sum+=i.score
            count+=1
    average = Sum/count
    averagesub = min(s, key=lambda x:abs(x.score-average))
    try:
        driver.get(lowestsub.__dict__["html_url"])
        time.sleep(2)  
        driver.execute_script("window.print();")
        time.sleep(1)
        rename_last_downloaded_file(dummypath, quizsubmissionspath+'/', str((q.__dict__)["title"])+'-min.pdf')
        time.sleep(1)
        driver.get(highestsub.__dict__["html_url"])
        time.sleep(2)  
        driver.execute_script("window.print();")
        time.sleep(1)
        rename_last_downloaded_file(dummypath, quizsubmissionspath+'/', str((q.__dict__)["title"])+'-max.pdf')
        time.sleep(1)
        driver.get(averagesub.__dict__["html_url"])
        time.sleep(2)  
        driver.execute_script("window.print();")
        time.sleep(1)
        rename_last_downloaded_file(dummypath, quizsubmissionspath+'/', str((q.__dict__)["title"])+'-avg.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        raise
print("[-] Quizzes 3 Graded Assessments are done")

# Get read only copy for an assignments
assignpath = path + "/g. Copy of assignment,Quizzes, Midterm and Final Examination/Assignments"
os.mkdir(assignpath)
assigns = course.get_assignments()  

for i in assigns:
    if i.__dict__["is_quiz_assignment"]==False:
        print(i)
        url = i.__dict__["html_url"]
        t = str(i.__dict__["name"]) + '.pdf'
        t = t.replace(":", "")
        try:
            driver.get(url)
            time.sleep(2)  
            driver.execute_script("window.print();")
            time.sleep(1)
            rename_last_downloaded_file(dummypath, assignpath+'/', t)
        except Exception as why:
            sys.stderr.write('Chromedriver Error: {}\n'.format(why))
            raise
print("[-] Assignments Preview Copies Done")        

# Get 3 submissions for each assignments
assignsubmissionspath = path + "/i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks/Assignments"
os.mkdir(assignsubmissionspath)
for a in assigns:
    if ((not a.__dict__['is_quiz_assignment'])) or ("none" not in a.__dict__['submission_types']):
        submissions = a.get_submissions()
        s = [x for x in submissions if x.score!=None]
        if len(s)==0: continue
        lowestsub = min(s, key=lambda x: x.score)
        highestsub = max(s, key=lambda x: x.score)
        Sum = 0
        count = 0
        for i in s:
            if i.score!=None:   
                Sum+=i.score
                count+=1
        average = Sum/count
        averagesub = min(s, key=lambda x:abs(x.score-average))
        subs = [lowestsub, highestsub, averagesub]
        subsname = ["min", "max", "avg"]
        for count in range(3):
            if subs[count].__dict__["submission_type"]=="online_text_entry":
                try:
                    driver.get(subs[count].__dict__["preview_url"])
                    time.sleep(2)  
                    driver.execute_script("window.print();")
                    time.sleep(1)
                    rename_last_downloaded_file(dummypath, assignsubmissionspath+'/', str((a.__dict__)["name"])+'-'+subsname[count]+'.pdf')
                except Exception as why:
                    sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                    raise
            elif subs[count].__dict__["submission_type"]=="online_upload":
                attachments = subs[count].__dict__["attachments"]
                print(attachments)
                for j in attachments:
                    url = j["url"]
                    r = requests.get(url, allow_redirects=True)
                    open(assignsubmissionspath+"/"+subsname[count] + "- " +str((a.__dict__)["name"]) + "-" + j["filename"], 'wb').write(r.content)

print("[-] Assignment graded assessments are done")                
# Make an empty folder for model solutions of assignments - To be added by instructor
assignmodelpath = path + "/h. Model solutions of all assessments tests given in previous section/Assignments"
os.mkdir(assignmodelpath)

driver.close()
driver.quit()