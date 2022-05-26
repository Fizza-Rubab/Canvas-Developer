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

from webdriver_manager.chrome import ChromeDriverManager
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
            time.sleep(3)
        s = max([dummy_dir+"/"+f for f in os.listdir(dummy_dir)], key=os.path.getctime)
        return s

    while '.part' in get_last_downloaded_file_path(dummy_dir):
        time.sleep(3)
    
    shutil.move(get_last_downloaded_file_path(dummy_dir), destination_dir+"/"+new_file_name)

def sanitize(name):
    filenamespecial = ["<", ">", "/", "\\", "?", "*", "|", ":", '"', "\0"]
    for i in filenamespecial:
        if i in name:
            name = name.replace(i,"")
    return name

API_URL ="https://hulms.instructure.com"

API_KEY = input("Enter API Access token key:\n")
canvas = Canvas(API_URL, API_KEY)
headers ={"Authorization":"Bearer "+API_KEY}
courseUrl = input("Enter course URL:\n")
dummypath = os.path.join(os.getcwd(), "dummy")
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
    "version": 2,
    "scalingType": 3,
    "scaling": "85"
}
profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),
           'savefile.default_directory': dummypath}

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', profile)
chrome_options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(options=chrome_options, executable_path=ChromeDriverManager().install())
driver.get("https://hulms.instructure.com/")
element = WebDriverWait(driver, 2000).until(
        EC.title_is("Dashboard")
    )
courseID = int(courseUrl.split("/")[-1])

course = canvas.get_course(courseID)

courseDict = course.__dict__
d = courseDict["created_at"]
dt = datetime.fromisoformat(d[:-1]).astimezone(timezone.utc)
year = str(dt.year)
if int(dt.strftime("%m"))>=5 and int(dt.strftime("%m"))<=9:
    term = "Fall"
else:
    if int(dt.strftime("%m"))>=10 and int(dt.strftime("%m"))<=12:
        year = str(int(dt.year)+1)
    else:
        year = str(dt.year)
    term = "Spring"
cname = courseDict['name'] +" " + term +" " + year
cname = sanitize(cname)
parent_dir = os.getcwd()
path = os.path.join(parent_dir, cname)
if os.path.isdir(path):
    shutil.rmtree(path)
os.makedirs(path)
subfolders = ["Lecture Notes", "Course Syllabus", "Assessments and Sample Solutions",  "Attendance Record", "Complete Result", "Student Evaluation", "Instructor's Feedback"]
parent_dir = path
for folder in subfolders:
    os.makedirs(os.path.join(parent_dir,folder))
print("[-] made the folders")
    
f  = (course.get_files())
for i in f:
    if str(i)=="syllabus.pdf":
        i.download(path+"/Course Syllabus/" + str(i))
        print("[-] Syllabus downloaded")
        break
os.makedirs(path+"/Assessments and Sample Solutions/Model Assignments Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Model Quizzes Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Three Sample Graded Quizzes Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Three Sample Graded Assignments Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Quiz Copies")
os.makedirs(path+"/Assessments and Sample Solutions/Assignment Copies")



foldersCheck = [False, False, False]
folders = course.get_folders()
lectureFolder, solutionsFolder, assignFolder = None, None, None
folderid = 0
for m in range(len(list(folders))):
    if foldersCheck[0] and foldersCheck[1] and foldersCheck[2]:
        break
    if folders[m].__dict__['name']=="Slides":
        lectureFolder = folders[m]
        lfid = folders[m].__dict__["id"]
        foldersCheck[0] = True
    if folders[m].__dict__['name']=="Assignment Solutions":
        solutionsFolder =folders[m]
        sfid = folders[m].__dict__["id"]
        foldersCheck[1] = True
    if folders[m].__dict__['name']=="Assignments":
        solutionsFolder =folders[m]
        sfid = folders[m].__dict__["id"]
        foldersCheck[2] = True
if lectureFolder is not None:
    files_url = lectureFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    for f in filesdata:
        response = requests.get(f["url"], allow_redirects=True)
        fn = sanitize(f["filename"])
        open(path+"/Lecture notes/" + fn, 'wb').write(response.content)
    print("[-] Lecture Notes Downloaded")

if solutionsFolder is not None:
    files_url = solutionsFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    for f in filesdata:
        fn = sanitize(f["filename"])
        response = requests.get(f["url"], allow_redirects=True)
        open(path+"/Assessments and Sample Solutions/Model Assignments Solutions/" + fn, 'wb').write(response.content)
    print("[-] Solutions downloaded")

if assignFolder is not None:
    files_url = assignFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    for f in filesdata:
        fn = sanitize(f["filename"])
        response = requests.get(f["url"], allow_redirects=True)
        open(path+"/Assessments and Sample Solutions/Assignment Copies/" + fn, 'wb').write(response.content)
    print("[-] Assignment Files downloaded")

# Get Read only copy of all quizzes
quizzespath = path+"/Assessments and Sample Solutions/Quiz Copies"
quizzes = course.get_quizzes()
for q in quizzes:
    url = (q.__dict__)["html_url"]
    url+="/read_only"
    try:
        driver.get(url)
        driver.execute_script("document.getElementById('questions').classList.remove('brief');")
        time.sleep(2)
        fn = sanitize(str((q.__dict__)["title"]))
        driver.execute_script("window.print();")
        rename_last_downloaded_file(dummypath, quizzespath+'/', fn +'.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        continue

print("[-] Quizzes Preview done")



# # Get model solution for all quizzes
quizzesmodelpath = path + "/Assessments and Sample Solutions/Model Quizzes Solutions"   
for q in quizzes:
    try:
        driver.get(q.__dict__["html_url"]+'/edit#questions_tab')
        try:
            driver.execute_script("""document.getElementById('questions').classList.remove('brief');sp = document.getElementsByClassName('correct_answer');for(var i = 0; i < sp.length; i++){sp[i].style.color = 'Green'; sp[i].style.border = 'solid #00FF00'};document.getElementById("flash_message_holder").remove();""")
        except:
            pass
        time.sleep(2)  
        driver.execute_script("window.print();")
        fn = sanitize(str((q.__dict__)["title"]))
        time.sleep(1)
        rename_last_downloaded_file(dummypath, quizzesmodelpath+'/', fn +'-solution.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        continue
print("[-] Quizzes Model Solution is done")

# # Get 3 sample graded student submissions of each quiz
quizsubmissionspath = path + "/Assessments and Sample Solutions/Three Sample Graded Quizzes Solutions"
for q in quizzes:
    r = requests.get("https://hulms.instructure.com/api/v1/courses/" + str(courseID) + "/quizzes/"+ str(q.__dict__["id"]) + "/questions", headers=headers)
    questions = r.json()
    attachments = False
    for ques in questions:
        if ques["question_type"]=="file_upload_question":
            attachments = True
            break
    fn = str((q.__dict__)["title"])
    #  Fetching file uploads    
    if attachments:
        try:
            if "speed_grader_url" in q.__dict__.keys():
                if q.__dict__["speed_grader_url"] is not None:             
                    qassignIDindex = q.__dict__["speed_grader_url"][::-1].index("=")
                    qassignID = int(q.__dict__["speed_grader_url"][len(q.__dict__["speed_grader_url"])-qassignIDindex:])
                    a = (course.get_assignment(qassignID))
                    r =requests.get("https://hulms.instructure.com/api/v1/courses/" + str(courseID) + "/assignments/"+str(qassignID)+"/submissions?include[]=submission_history", headers=headers)
                    submissions = r.json()
                    s = sorted([i for i in submissions if i['score']!=None], key=lambda d: d['score'])
                    if s==[]:
                        continue
                    lowestsub = s[0]
                    highestsub = s[-1]
                    Sum = 0
                    count = 0
                    for i in s:
                        if i["score"]!=None:
                            Sum+=i["score"]
                            count+=1
                    average = Sum/count
                    averagesub = min(s, key=lambda x:abs(x["score"]-average))
                    if len(s)>2:
                        if averagesub==lowestsub and averagesub!=highestsub:
                            averagesub = s[1]
                        elif averagesub!=lowestsub and averagesub==highestsub:
                            averagesub = s[-2]
                        flag = False
                    currentquizsubmissionspath = quizsubmissionspath + "/" + fn
                    os.makedirs(currentquizsubmissionspath)
                    time.sleep(1.5)
                    subs = [lowestsub, highestsub, averagesub]
                    subsname = ["min", "max", "avg"]
                    subsnameattach = ["min-attachment", "max-attachment", "avg-attachment"]
                    for count in range(3):
                        submissionData = subs[count]["submission_history"][-1]["submission_data"]
                        attachedFiles = []
                        for k in submissionData:
                            if "attachment_ids" in k.keys():
                                attachedFiles.extend(k["attachment_ids"])
                        it = 1
                        for f in attachedFiles:
                            filee= canvas.get_file(f)
                            Index = str(filee)[::-1].index(".")
                            extname = str(filee)[len(str(filee))-Index:]
                            filee.download(currentquizsubmissionspath + "/" + fn + "-" +subsnameattach[count]+"-" + str(it) + "." + extname)
                            it+=1
                        try:
                            url = "https://hulms.instructure.com/courses/" + str(courseID) + "/gradebook/speed_grader?assignment_id=" + str(subs[count]["assignment_id"]) + "&student_id=" + str(subs[count]["user_id"])
                            driver.get(url)
                            time.sleep(2.5)  
                            driver.execute_script("window.print();")
                            time.sleep(0.5)
                            rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', fn + subsname[count]+'.pdf')
                        except Exception as why:
                            sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                            continue
        except Exception as why:
            sys.stderr.write('Error: {}\n'.format(why))
            continue
    else:
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
                averagesub = s[1]
            elif averagesub!=lowestsub and averagesub==highestsub:
                averagesub = s[-2]
            flag = False
        currentquizsubmissionspath = quizsubmissionspath + "/" + fn
        os.makedirs(currentquizsubmissionspath)
        time.sleep(1.5)
        try:
            driver.get(lowestsub.__dict__["html_url"])
            time.sleep(0.5)  
            driver.execute_script("window.print();")
            time.sleep(0.5)
            rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', fn +'-min.pdf')
            
            driver.get(highestsub.__dict__["html_url"])
            time.sleep(0.5)  
            driver.execute_script("window.print();")
            time.sleep(0.5)
            rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', fn +'-max.pdf')
            driver.get(averagesub.__dict__["html_url"])
            time.sleep(0.5)  
            driver.execute_script("window.print();")
            time.sleep(0.5)
            rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/',fn +'-avg.pdf')
        except Exception as why:
            sys.stderr.write('Chromedriver Error: {}\n'.format(why))
            continue
print("[-] Quizzes 3 Graded Assessments are done")

# Get read only copy for an assignments
assignpath = path+"/Assessments and Sample Solutions/Assignment Copies"
assigns = course.get_assignments()  

for i in assigns:
    if i.__dict__["is_quiz_assignment"]==False and "online_quiz" not in i.__dict__["submission_types"] and "external_tool" not in i.__dict__["submission_types"]:
        url = i.__dict__["html_url"]
        t = sanitize(str(i.__dict__["name"]))
        t+='.pdf'
        try:
            driver.get(url)
            time.sleep(1)  
            driver.execute_script("window.print();")
            time.sleep(1)
            rename_last_downloaded_file(dummypath, assignpath+'/', t)
        except Exception as why:
            sys.stderr.write('Chromedriver Error: {}\n'.format(why))
            continue       
print("[-] Assignments Preview Copies Done")        

# # Get 3 submissions for each assignments
assignsubmissionspath = path + "/Assessments and Sample Solutions/Three Sample Graded Assignments Solutions"
for a in assigns:
    # print(a.__dict__)
    if ((not a.__dict__['is_quiz_assignment'])) and ("none" not in a.__dict__['submission_types']) and "online_quiz" not in a.__dict__["submission_types"] and "external_tool" not in a.__dict__["submission_types"]:
        submissions = a.get_submissions()
        s = [] 
        for x in submissions:
            if x.score!=None and x.__dict__['submission_type']!=None:
                s.append(x)
        if len(s)==0: continue
        s.sort(key=lambda x: x.score)
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
                averagesub = s[1]
            elif averagesub!=lowestsub and averagesub==highestsub:
                averagesub = s[-2]
        subs = [lowestsub, highestsub, averagesub]
        subsname = ["min", "max", "avg"]
        aname = sanitize(str((a.__dict__)["name"]))
        currentassignsubmissionspath = assignsubmissionspath + "/" + aname
        try:
            if not os.path.exists(currentassignsubmissionspath):
                os.makedirs(currentassignsubmissionspath)
                time.sleep(1.5)
        except Exception as why:
                sys.stderr.write('Path creation: {}\n'.format(why))
                continue
        for count in range(3):
            if subs[count].__dict__["submission_type"]=="online_text_entry":
                try:
                    urlstr = subs[count].__dict__["preview_url"][:subs[count].__dict__["preview_url"].find("?preview")]
                    driver.get(urlstr)
                    time.sleep(1)
                    driver.execute_script("s = document.querySelectorAll('.submission-details-comments .comments');for (var i=0;i<s.length;i++)s[i].style.overflow = 'visible';")
                    time.sleep(1)  
                    driver.execute_script("window.print();")
                    time.sleep(1)
                    rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+'.pdf')

                    if "rubric" in a.__dict__.keys():
                        driver.get(urlstr)
                        time.sleep(1)
                        driver.execute_script("s = document.getElementById('rubric_holder');s.style.overflow = 'visible';")
                        time.sleep(1)  
                        driver.execute_script("window.print();")
                        time.sleep(1)
                        rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+' - rubric.pdf')

                except Exception as why:
                    sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                    continue
            elif subs[count].__dict__["submission_type"]=="discussion_topic":
                try:
                    driver.get(subs[count].__dict__["preview_url"])
                    time.sleep(1)  
                    driver.execute_script("window.print();")
                    time.sleep(1)
                    rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+'.pdf')
                except Exception as why:
                    sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                    continue
            elif subs[count].__dict__["submission_type"]=="online_upload":
                attachments = subs[count].__dict__["attachments"]
                c = 1
                for j in attachments:
                    try:
                        url = j["url"]
                        r = requests.get(url, allow_redirects=True)
                        Index = j["filename"][::-1].index(".")
                        extname = j["filename"][len(j["filename"])-Index:]
                        if "preview_url" not in j.keys() or j["preview_url"] is None:
                            open(currentassignsubmissionspath+"/"+aname + "-" + subsname[count] +" " + str(c) + "."+extname, 'wb').write(r.content)
                        elif "preview_url" in j.keys():
                            if j["preview_url"] is not None:
                                r =requests.get(url=API_URL + j["preview_url"], allow_redirects=False, headers=headers)
                                i1 = r.text.find("http")
                                i2 = r.text.find("redirected")
                                url = r.text[i1:i2-2]
                                i1 = url.find("view?")
                                url = url[:i1]
                                url+="annotated.pdf"
                                r = requests.post(url, allow_redirects=True, headers=headers)
                                r = requests.get(url+"/is_ready", allow_redirects=True, headers=headers)
                                r = requests.get(url, allow_redirects=True, headers=headers)

                                open(currentassignsubmissionspath+"/"+aname + "-" + subsname[count] +" " + str(c) + ' -annotated.pdf', 'wb').write(r.content)

                        c+=1
                    except Exception as why:
                        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                        continue

                c = 0
                try:
                    urlstr = subs[count].__dict__["preview_url"][:subs[count].__dict__["preview_url"].find("?preview")]
                    driver.get(urlstr)
                    time.sleep(1)  
                    driver.execute_script("s = document.querySelectorAll('.submission-details-comments .comments');for (var i=0;i<s.length;i++)s[i].style.overflow = 'visible';")
                    time.sleep(1)  
                    driver.execute_script("window.print();")
                    time.sleep(1)
                    rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+'.pdf')

                    if "rubric" in a.__dict__.keys():
                        driver.get(urlstr)
                        time.sleep(1)
                        driver.execute_script("r = document.getElementsByClassName('icon-rubric')[0];r.click();")
                        time.sleep(1)
                        driver.execute_script("s = document.getElementById('rubric_holder');s.style.overflow = 'visible';")
                        time.sleep(1)  
                        driver.execute_script("window.print();")
                        time.sleep(1)
                        rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+' - rubric.pdf')

                except Exception as why:
                    sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                    continue
            elif subs[count].__dict__["submission_type"]=="online_url":
                try:
                    open(currentassignsubmissionspath+"/"+aname+ "-" + subsname[count] +".txt", 'w').write(subs[count].__dict__["url"])
                except Exception as why:
                    sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                    continue
            else:
                continue
print("[-] Assignment graded assessments are done")                


discussionspath = path+"/Discussions"
os.mkdir(discussionspath)
discussions  = course.get_discussion_topics()
for i in discussions:
    try:
        url = (i.__dict__)["html_url"]
        driver.get(url)
        time.sleep(1)   
        driver.execute_script("window.print();")
        time.sleep(1)
        title =  sanitize(str((i.__dict__)["title"]))
        rename_last_downloaded_file(dummypath, discussionspath+'/', title+'.pdf')
    except Exception as why:
        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
        continue
print("Discussions Created")

driver.close()
driver.quit()
