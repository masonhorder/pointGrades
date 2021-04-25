from __future__ import division
from requests import Session
from bs4 import BeautifulSoup as bs
import re
import sys
import os
from getpass import getpass



def lines():
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = float(columns)
    i = 0
    while i < columns:
        i += 1
        sys.stdout.write("-")

os.system("clear")

lines()
print("\nmason horder\n\n")
lines()

print("\n")
username = input("Username: ")
password = getpass("Password: ")

with Session() as s:
    site = s.get("https://calhigh.schoolloop.com/portal/login?etarget=login_form")
    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("input", {"name":"form_data_id"})["value"]
    login_data = {
        'login_name': username,
    	'password': password,
        'form_data_id': token,
        'event_override': 'login',
    }
    s.post("https://calhigh.schoolloop.com/portal/login?etarget=login_form", login_data)
    home_page = s.get("https://calhigh.schoolloop.com/portal/student_home")
    home_page_html = bs(home_page.text, "html.parser")


courses = home_page_html.findAll(class_="student_row")
for course in courses:
    # each course
    courseName = course.find(class_="course").a.string


    if courseName == "Biology: The Living Earth(t3)":
        # if bio

        linkSection = course.find(class_="pr_link")

        if linkSection != None:
            # if link exists
            link = linkSection.a.get("href")
            link.replace("amp;","&")
            progressReport = s.get("https://calhigh.schoolloop.com" + link)
            progressReportHtml = bs(progressReport.text, "html.parser")
            assignments = progressReportHtml.find(class_="general_body").findAll("tr")
            
            assesmentCount = 0
            assignmentCount = 0
            assesmentScore = 0
            assingmentScore = 0

            for assignment in assignments:
                # assignments!

                columns = assignment.findAll("td")
                index = 0
                score = []
                isAssessment = False
                
                for column in columns:
                    if index == 0:
                        if "Assessment" in str(column.div):
                            # print("Assessment")
                            isAssessment = True
                    if index == 3: 
                        scoreString = column.div.string
                        if scoreString == None:
                            scoreString = column.div.find(class_="red").string
                        temp = re.findall(r'\d+', scoreString)
                        score = list(map(int, temp))
                        # print(score[0])
                    index += 1
                if isAssessment == True:
                    assesmentCount += 1
                    assesmentScore += score[0]
                else:
                    assignmentCount += 1
                    assingmentScore += score[0]
    

            assignmentAverage = assingmentScore/assignmentCount
            assessmentAverage = assesmentScore/assesmentCount
            classPoints = (assessmentAverage * .6) + (assignmentAverage * .4)
            if classPoints < 1.5:
                letter = "F"
            elif classPoints < 2.5:
                letter = "C"
            elif classPoints < 3.5:
                letter = "B"
            else:
                letter = "A"

            print("\n\n")
            lines()
            print("\n\nAssignment Average: " + str(assignmentAverage))
            print("Assessment Average: " + str(assessmentAverage))
            print("Total Class Points: " + str(classPoints))
            print("Letter Grade: " + letter + "\n")
            lines()
            print("\n\n")
