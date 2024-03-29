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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# ref: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters?noredirect=1&lq=1
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()


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

logging.getLogger("canvasapi").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("os").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


logging.basicConfig(filename='canvas-app.log', filemode='w', level = logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logging.info("Loading the config file")

configFile = open("config.json", "r")
conf = json.load(configFile)
exportEverything = False
if "*" in conf["files_to_download"]:
    exportEverything = True
API_URL = conf["API_URL"]
API_KEY = conf["API_KEY"]
LOGIN_URL = conf["LOGIN_URL"]
if API_KEY=="":
    API_KEY = input("Enter API Access token key:\n")
try:
    canvas = Canvas(API_URL, API_KEY)
except Exception as e:
    logging.error(e)
    exit()

headers ={"Authorization":"Bearer "+API_KEY}
courseUrl = input("Enter course URL:\n")
# courseUrl = "https://hulms.instructure.com/1923"
if conf["save_location"]=="":
    dummypath = os.path.join(os.getcwd(), "dummy")
else:
    dummypath = os.path.join(conf["save_location"], "dummy")
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
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
driver.get(LOGIN_URL)
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
if conf["save_location"] == "":
    parent_dir = os.getcwd()
else:
    parent_dir = conf["save_location"]
path = os.path.join(parent_dir, cname)
if os.path.isdir(path):
    shutil.rmtree(path)
os.makedirs(path)
logging.info("Base Folder created")
subfolders = ["Lecture Notes", "Syllabus and Other Downloaded Files", "Assessments and Sample Solutions",  "Attendance Record", "Complete Result", "Student Evaluation", "Instructor's Feedback"]
parent_dir = path
for folder in subfolders:
    os.makedirs(os.path.join(parent_dir,folder))
logging.info("Folders created")
print("[-] made the folders")
    
f  = (course.get_files())
toDownload = {i:False for i in conf["files_to_download"]}
for i in f:
    if str(i) in toDownload.keys() and toDownload[str(i)]==False:
        i.download(path+"/Syllabus and Other Downloaded Files/" + str(i))
        print("[-] " + str(i) + " downloaded")
        toDownload[str(i)] = True
    if all(value == True for value in toDownload.values()):
        break
os.makedirs(path+"/Assessments and Sample Solutions/Model Assignments Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Model Quizzes Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Three Sample Graded Quizzes Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Three Sample Graded Assignments Solutions")
os.makedirs(path+"/Assessments and Sample Solutions/Quiz Copies")
os.makedirs(path+"/Assessments and Sample Solutions/Assignment Copies")
os.makedirs(path+"/Assessments and Sample Solutions/Assignment Copies/Downloaded")
logging.info("Subfolders created")



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
        assignFolder =folders[m]
        afid = folders[m].__dict__["id"]
        foldersCheck[2] = True
if lectureFolder is not None:
    print("Downloading Lecture Notes")
    files_url = lectureFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    l = len(filesdata)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, f in enumerate(filesdata):        
        response = requests.get(f["url"], allow_redirects=True)
        fn = sanitize(f["filename"])
        open(path+"/Lecture Notes/" + fn, 'wb').write(response.content)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print("[-] Lecture Notes Downloaded")
    logging.info("Lecture Notes Downloaded")

if solutionsFolder is not None:
    print("Downloading Uploaded Solutions")
    files_url = solutionsFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    l = len(filesdata)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, f in enumerate(filesdata):
        fn = sanitize(f["filename"])
        response = requests.get(f["url"], allow_redirects=True)
        open(path+"/Assessments and Sample Solutions/Model Assignments Solutions/" + fn, 'wb').write(response.content)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print("[-] Solutions downloaded")
    logging.info("Solutions downloaded")

if assignFolder is not None:
    print("Downloading Uploaded Solutions")
    files_url = assignFolder.__dict__["files_url"]
    r =requests.get(files_url, headers=headers)
    filesdata = json.loads(r.text)
    l = len(filesdata)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, f in enumerate(filesdata):
        fn = sanitize(f["filename"])
        response = requests.get(f["url"], allow_redirects=True)
        open(path+"/Assessments and Sample Solutions/Assignment Copies/Downloaded/" + fn, 'wb').write(response.content)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print("[-] Assignment Files downloaded")
    logging.info("Solutions downloaded")

# # Get Read only copy of all quizzes
quizzespath = path+"/Assessments and Sample Solutions/Quiz Copies"
quizzes = course.get_quizzes()
l = len(list(quizzes))
if conf["download_quiz_copies"]:
    print("Downloading Quiz Copies")
    logging.info("Downloading Quiz Copies")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, q in enumerate(quizzes):
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if q.__dict__["published"]=="true" or q.__dict__["published"]==True:
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
                logging.error(why)
                continue

    print("[-] Quizzes Copies done")
    logging.info("Quizzes Copies done")



# # Get model solution for all quizzes
quizzesmodelpath = path + "/Assessments and Sample Solutions/Model Quizzes Solutions"   
if conf["download_model_quizzes"]:
    print("Downloading Quiz Canvas Solutions")
    logging.info("Downloading Quiz Canvas Solutions")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, q in enumerate(quizzes):
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
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
            logging.error(why)
            continue
    print("[-] Quizzes Model Solution is done")
    logging.info("Quizzes Model Solution is done")


# # Get 3 sample graded student submissions of each quiz
quizsubmissionspath = path + "/Assessments and Sample Solutions/Three Sample Graded Quizzes Solutions"
if conf["download_graded_quizzes"]:        
    print("Downloading Three Graded Quiz Solutions")
    logging.info("Downloading Three Graded Quiz Solutions")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i, q in enumerate(quizzes):
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        r = requests.get(API_URL+"/api/v1/courses/" + str(courseID) + "/quizzes/"+ str(q.__dict__["id"]) + "/questions", headers=headers)
        questions = r.json()
        attachments = False
        try:
            for ques in questions:
                if ques["question_type"]=="file_upload_question":
                    attachments = True
                    break
        except:
            pass
        fn = str((q.__dict__)["title"])
        #  Fetching file uploads    
        if attachments:
            try:
                if "speed_grader_url" in q.__dict__.keys():
                    if q.__dict__["speed_grader_url"] is not None:             
                        qassignIDindex = q.__dict__["speed_grader_url"][::-1].index("=")
                        qassignID = int(q.__dict__["speed_grader_url"][len(q.__dict__["speed_grader_url"])-qassignIDindex:])
                        a = (course.get_assignment(qassignID))
                        r =requests.get(API_URL+"/api/v1/courses/" + str(courseID) + "/assignments/"+str(qassignID)+"/submissions?include[]=submission_history", headers=headers)
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
                                url = API_URL+"/courses/" + str(courseID) + "/gradebook/speed_grader?assignment_id=" + str(subs[count]["assignment_id"]) + "&student_id=" + str(subs[count]["user_id"])
                                driver.get(url)
                                time.sleep(2.5)  
                                driver.execute_script("window.print();")
                                time.sleep(0.5)
                                rename_last_downloaded_file(dummypath, currentquizsubmissionspath+'/', fn + subsname[count]+'.pdf')
                            except Exception as why:
                                sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                                logging.error(why)
                                continue
            except Exception as why:
                sys.stderr.write('Error: {}\n'.format(why))
                logging.error(why)
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
                logging.error(why)
                continue
    print("[-] Quizzes 3 Graded Assessments are done")
    logging.info("[-] Quizzes 3 Graded Assessments are done")


# # Get read only copy for an assignments
assignpath = path+"/Assessments and Sample Solutions/Assignment Copies"
assigns = course.get_assignments()  
l = len(list(assigns))
if conf["download_assignment_copies"]:
    print("Downloading Assignment Copies")
    logging.info("Downloading Assignment Copies")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for it, i in enumerate(assigns):
        printProgressBar(it + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if i.__dict__["is_quiz_assignment"]==False and "online_quiz" not in i.__dict__["submission_types"]:
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
                logging.error(why)
                continue       
    print("[-] Assignments Preview Copies Done")
    logging.info("Assignments Preview Copies Done")


# # Get 3 submissions for each assignments
assignsubmissionspath = path + "/Assessments and Sample Solutions/Three Sample Graded Assignments Solutions"
if conf["download_graded_assignments"]:
    print("Downloading Assignment Submissions")
    logging.info("Downloading Assignment Submissions")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for it, a in enumerate(assigns):
        printProgressBar(it + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if (a.__dict__['is_quiz_assignment']==False) and "online_quiz" not in a.__dict__["submission_types"]:
            submissions = a.get_submissions()
            s = [] 
            for x in submissions:
                if x.__dict__["score"]!=None:
                    s.append(x)
            if len(s)==0: continue
            s.sort(key=lambda x: x.__dict__["score"])
            lowestsub = s[0]
            highestsub = s[-1]
            Sum = 0
            count = 0
            for i in s:
                if i.__dict__["score"]!=None:
                    Sum+=i.__dict__["score"]
                    count+=1
            average = Sum/count
            averagesub = min(s, key=lambda x:abs(x.__dict__["score"]-average))
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
                    logging.error(why)
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
                        logging.error(why)
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
                        logging.error(why)
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
                            logging.error(why)
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
                        logging.error(why)
                        continue
                elif subs[count].__dict__["submission_type"]=="online_url":
                    try:
                        open(currentassignsubmissionspath+"/"+aname+ "-" + subsname[count] +".txt", 'w').write(subs[count].__dict__["url"])
                    except Exception as why:
                        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                        logging.error(why)
                        continue
                else:
                    try:
                        urlstr = subs[count].__dict__["preview_url"][:subs[count].__dict__["preview_url"].find("?preview")]
                        driver.get(urlstr)
                        time.sleep(1)  
                        driver.execute_script("window.print();")
                        time.sleep(1)
                        rename_last_downloaded_file(dummypath, currentassignsubmissionspath +'/', aname+'-'+subsname[count]+'.pdf')
                    except Exception as why:
                        sys.stderr.write('Chromedriver Error: {}\n'.format(why))
                        logging.error(why)
                        continue
        
    print("[-] Assignment graded assessments are done")
    logging.info("Assignment graded assessments are done")                



if conf["download_discussions"]:
    discussionspath = path+"/Discussions"
    os.mkdir(discussionspath)
    discussions  = course.get_discussion_topics()
    l = len(list(discussions))
    print("Downloading Discussion Topics")
    logging.info("Downloading Discussion Topics")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for it, i in enumerate(discussions):
        printProgressBar(it + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
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
            logging.error(why)
            continue
    print("Discussions Created")
    logging.info("Discussions Created")


if exportEverything==True:
    url = API_URL+"/api/v1/courses/"+str(courseID)+"/content_exports?export_type=zip"
    r = requests.post(url, headers=headers)
    rtext = json.loads(r.text)
    exportId = rtext["id"]
    progressUrl = rtext["progress_url"]
    print("Exporting the entire course")
    printProgressBar(0, 100, prefix = 'Progress:', suffix = 'Complete', length = 50)
    completion = 0
    while completion<100:
        r = requests.get(progressUrl, headers=headers)
        rtext = json.loads(r.text)
        completion = rtext["completion"]
        printProgressBar(completion, 100, prefix = 'Progress:', suffix = 'Complete', length = 50)
        time.sleep(4)
    r = requests.get(API_URL+"/api/v1/courses/"+str(courseID)+"/content_exports/" + str(exportId), headers=headers)
    rtext = json.loads(r.text)
    filename = rtext["attachment"]["filename"]
    url = rtext["attachment"]["url"]
    r = requests.get(url, allow_redirects=True, headers=headers)
    filenamefinal = parent_dir + "/" + filename
    open(str(filenamefinal), 'wb').write(r.content)
logging.info("Course export completed and zip downloaded")
logging.info("Course Files download completed.")
print("[-] Course Export Zip Downloaded")
    

     

driver.close()
driver.quit()
