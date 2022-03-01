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
        s = max([dummy_dir+"/"+f for f in os.listdir(dummy_dir)], key=os.path.getctime)
        print(s)
        return s

    while '.part' in get_last_downloaded_file_path(dummy_dir):
        time.sleep(2)
    
    shutil.move(get_last_downloaded_file_path(dummy_dir), destination_dir+"/"+new_file_name)

API_URL ="https://hulms.instructure.com"
API_KEY = input("Enter API Access token key:\n")
API_KEY = "17361~xZyAHOzoJktetSdyDs4kcg4Tj13q00qtQ7p5vUb07B3SqUgJi5yntFG5stU87Vgi"
canvas = Canvas(API_URL, API_KEY)
# courseUrl = input("Enter course URL:\n")
courseUrl="https://hulms.instructure.com/courses/1923"
dummypath = "C:/Users/fizza/Documents/dummy"
if not os.path.exists(dummypath):
    os.makedirs(dummypath)
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
# chrome_options.add_argument('--headless')
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
os.makedirs(path)
subfolders = ["a. Course Contents", "b.  Course Objectives", "c. Weekly plan of contents of lectures delivered",
"d. Attendance Record", "e. Copy of lecture notes", "f.  List of Reference Material", 
"g. Copy of assignment,Quizzes, Midterm and Final Examination", "h. Model solutions of all assessments tests given in previous section",
"i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks",
"j. Marks distribution and Grading Model", "k.Complete result of the course", "l. Outcomes Assessment",
"m. Detail of technology involved", "n. Design skills-techniques practiced", "o. Complete analysis of effectiveness of course and level of silks ensured in Technology, Emerging Development Paradigms, Pertaining to Industry, Mod",
"Syllabus"]
parent_dir = path
for folder in subfolders:
    os.makedirs(os.path.join(parent_dir,folder))
print("[-] made the folders")
inthesyllabus = ["a. Course Contents", "b.  Course Objectives", "c. Weekly plan of contents of lectures delivered",
"f.  List of Reference Material","j. Marks distribution and Grading Model"]
for dest in inthesyllabus:
    shutil.copyfile("./InTheSyllabus.pdf", str(os.path.join(parent_dir,dest+"/InTheSyllabus.pdf")))
print("[-] copied files")
    
f  = (course.get_files())
for i in f:
    if str(i)=="syllabus.pdf":
        i.download(path+"/Syllabus/" + str(i))
        print("[-] Syllabus downloaded")
        break
    
foldersCheck = [False, False]
folders = course.get_folders()
lectureFolder, solutionsFolder = None, None
folderid = 0
for m in range(len(list(folders))):
    if foldersCheck[0] and foldersCheck[1]:
        break
    if folders[m].__dict__['name']=="Lecture notes":
        lectureFolder = folders[m]
        lfid = folders[m].__dict__["id"]
        foldersCheck[0] = True
    if folders[m].__dict__['name']=="Solutions":
        solutionsFolder =folders[m]
        sfid = folders[m].__dict__["id"]
        foldersCheck[1] = True
if lectureFolder is not None:
    files_url = lectureFolder.__dict__["files_url"]
    headers ={"Authorization":"Bearer "+API_KEY}
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    for f in filesdata:
        response = requests.get(f["url"], allow_redirects=True)
        open(path+"/e. Copy of lecture notes/" + f["filename"], 'wb').write(response.content)
    print("Lecture Notes Downloaded")
os.makedirs(path + "/h. Model solutions of all assessments tests given in previous section/Assignments/Solutions/")
if solutionsFolder is not None:
    files_url = solutionsFolder.__dict__["files_url"]
    headers ={"Authorization":"Bearer "+API_KEY}
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    for f in filesdata:
        response = requests.get(f["url"], allow_redirects=True)
        open(path + "/h. Model solutions of all assessments tests given in previous section/Assignments/Solutions/" + f["filename"], 'wb').write(response.content)

    print("Solutions downloaded")

# # Get Read only copy of all quizzes
# quizzespath = path + "/g. Copy of assignment,Quizzes, Midterm and Final Examination/Quizzes"
# os.makedirs(quizzespath)
quizzes = course.get_quizzes()
# for q in quizzes:
#     url = (q.__dict__)["html_url"]
#     url+="/read_only"
#     driver.get(url)
#     driver.execute_script("document.getElementById('questions').classList.remove('brief');")
#     time.sleep(2)
#     driver.execute_script("window.print();")
#     rename_last_downloaded_file(dummypath, quizzespath+'/', str((q.__dict__)["title"])+'.pdf')

# print("[-] Quizzes Preview done")



# # Get model solution for all quizzes
# quizzesmodelpath = path + "/h. Model solutions of all assessments tests given in previous section/Quizzes"
# os.makedirs(quizzesmodelpath)
# for q in quizzes:
#     try:
#         driver.get(q.__dict__["html_url"]+'/edit#questions_tab')
#         try:
#             driver.execute_script("""document.getElementById('questions').classList.remove('brief');sp = document.getElementsByClassName('correct_answer');for(var i = 0; i < sp.length; i++){sp[i].style.color = 'Green'; sp[i].style.border = 'solid #00FF00'};document.getElementById("flash_message_holder").remove();""")
#         except:
#             pass
#         time.sleep(2)  
#         driver.execute_script("window.print();")
#         time.sleep(1)
#         rename_last_downloaded_file(dummypath, quizzesmodelpath+'/', str((q.__dict__)["title"])+'-solution.pdf')
#     except Exception as why:
#         sys.stderr.write('Chromedriver Error: {}\n'.format(why))
#         raise
# print("[-] Quizzes Model Solution is done")

# # Get 3 sample graded student submissions of each quiz
quizsubmissionspath = path + "/i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks/Quizzes"
os.makedirs(quizsubmissionspath)
for q in quizzes:
    questions = q.get_questions()
    attachments = False
    for ques in questions:
        if ques.__dict__["question_type"]=="file_upload_question":
            attachments = True
            break

    
    print(q.__dict__)
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
    if len(s)>2:
        if averagesub==lowestsub and averagesub!=highestsub:
            print(averagesub, lowestsub)
            averagesub = s[1]
        elif averagesub!=lowestsub and averagesub==highestsub:
            print(averagesub, highestsub)
            averagesub = s[-2]
        flag = False
    print(lowestsub.__dict__)
    currentquizsubmissionspath = quizsubmissionspath + "/" + str((q.__dict__)["title"])
    os.makedirs(currentquizsubmissionspath)
    time.sleep(1.5)
    try:
        driver.get(lowestsub.__dict__["html_url"])
        time.sleep(0.5)  
        driver.execute_script("window.print();")
        time.sleep(0.5)
        rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', str((q.__dict__)["title"])+'-min.pdf')
        
        driver.get(highestsub.__dict__["html_url"])
        time.sleep(0.5)  
        driver.execute_script("window.print();")
        time.sleep(0.5)
        rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', str((q.__dict__)["title"])+'-max.pdf')
        driver.get(averagesub.__dict__["html_url"])
        time.sleep(0.5)  
        driver.execute_script("window.print();")
        time.sleep(0.5)
        rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', str((q.__dict__)["title"])+'-avg.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        raise
print("[-] Quizzes 3 Graded Assessments are done")

# # # Get read only copy for an assignments
# assignpath = path + "/g. Copy of assignment,Quizzes, Midterm and Final Examination/Assignments"
# os.makedirs(assignpath)
# assigns = course.get_assignments()  

# for i in assigns:
#     print(i.__dict__)
#     if i.__dict__["is_quiz_assignment"]==False and "online_quiz" not in i.__dict__["submission_types"] and "external_tool" not in i.__dict__["submission_types"]:
#         print(i)
#         url = i.__dict__["html_url"]
#         t = str(i.__dict__["name"])
#         t = t.replace(":", "")
#         t = t.replace('"', "")
#         t = t.replace("'", "")
#         t = t.replace(".", "")
#         t = t.replace("?", "")
#         t+='.pdf'
#         try:
#             driver.get(url)
#             time.sleep(1)  
#             driver.execute_script("window.print();")
#             time.sleep(1)
#             rename_last_downloaded_file(dummypath, assignpath+'/', t)
#         except Exception as why:
#             sys.stderr.write('Chromedriver Error: {}\n'.format(why))
#             raise
# print("[-] Assignments Preview Copies Done")        

# # Get 3 submissions for each assignments
# assignsubmissionspath = path + "/i. Three sample graded assignments, quizzes, midterms and final examination securing max, min and average marks/Assignments"
# os.makedirs(assignsubmissionspath)
# for a in assigns:
#     if ((not a.__dict__['is_quiz_assignment'])) and ("none" not in a.__dict__['submission_types']) and "online_quiz" not in a.__dict__["submission_types"] and "external_tool" not in a.__dict__["submission_types"]:
#         submissions = a.get_submissions()
#         s = [] 
#         for x in submissions:
#             if x.score!=None and x.__dict__['submission_type']!=None:
#                 s.append(x)
#         if len(s)==0: continue
#         s.sort(key=lambda x: x.score)
#         lowestsub = s[0]
#         highestsub = s[-1]
#         Sum = 0
#         count = 0
#         for i in s:
#             if i.score!=None:
#                 Sum+=i.score
#                 count+=1
#         average = Sum/count
#         averagesub = min(s, key=lambda x:abs(x.score-average))
#         if len(s)>2:
#             if averagesub==lowestsub and averagesub!=highestsub:
#                 averagesub = s[1]
#             elif averagesub!=lowestsub and averagesub==highestsub:
#                 averagesub = s[-2]
#         subs = [lowestsub, highestsub, averagesub]
#         str((a.__dict__)["name"])
#         subsname = ["min", "max", "avg"]
#         currentassignsubmissionspath = assignsubmissionspath + "/" + str((a.__dict__)["name"])
#         os.makedirs(currentassignsubmissionspath)
#         for count in range(3):
#             if subs[count].__dict__["submission_type"]=="online_text_entry":
#                 try:
#                     driver.get(subs[count].__dict__["preview_url"])
#                     time.sleep(1)  
#                     driver.execute_script("window.print();")
#                     time.sleep(1)
#                     rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', str((a.__dict__)["name"])+'-'+subsname[count]+'.pdf')
#                 except Exception as why:
#                     sys.stderr.write('Chromedriver Error: {}\n'.format(why))
#                     raise
#             elif subs[count].__dict__["submission_type"]=="online_upload":
#                 attachments = subs[count].__dict__["attachments"]
#                 for j in attachments:
#                     url = j["url"]
#                     r = requests.get(url, allow_redirects=True)
#                     Index = j["filename"][::-1].index(".")
#                     extname = j["filename"][len(j["filename"])-Index:]
#                     open(currentassignsubmissionspath+"/"+str((a.__dict__)["name"]) + "-" + subsname[count] +"."+extname, 'wb').write(r.content)
#             elif subs[count].__dict__["submission_type"]=="online_url":
#                 open(currentassignsubmissionspaths+"/"+str((a.__dict__)["name"]) + "-" + subsname[count] +".txt", 'w').write(subs[count].__dict__["url"])
# print("[-] Assignment graded assessments are done")                
# discussionspath = path+"/Discussions"
# os.makedirs(discussionspath)
# discussions  = course.get_discussion_topics()
# for i in discussions:
#     url = (i.__dict__)["html_url"]
#     driver.get(url)
#     time.sleep(1)
#     driver.execute_script("window.print();")
#     time.sleep(1)
#     rename_last_downloaded_file(dummypath, discussionspath+'/', str((i.__dict__)["title"])+'.pdf')

driver.close()
driver.quit()