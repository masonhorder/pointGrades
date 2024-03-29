from __future__ import division
from requests import Session
from bs4 import BeautifulSoup as bs
import re
import sys
import os
from getpass import getpass
from flask import Flask, request, render_template,jsonify

app = Flask(__name__)

def webScrape(username,password):
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
        s.post("https://calhigh.schoolloop.com/portal/toggleModule?d=x&module_name=grades")
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
                    gradesList = []

                    for assignment in assignments:
                        # assignments!

                        columns = assignment.findAll("td")
                        index = 0
                        score = []
                        isAssessment = False
                        assignmentName = ""
                        for column in columns:
                            if index == 0:
                                assignmentName = column.div.a.text
                                assignmentName.replace("u'", "")
                                assignmentName.replace("'", "")
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
                        gradesList.append([score[0],isAssessment,assignmentName])
                        if isAssessment == True:
                            assesmentCount += 1
                            assesmentScore += score[0]
                        else:
                            assignmentCount += 1
                            assingmentScore += score[0]
            

                    assignmentAverage = assingmentScore/assignmentCount
                    assessmentAverage = assesmentScore/assesmentCount
                    classPoints = (assessmentAverage * .6) + (assignmentAverage * .4)
                    print(gradesList)
                    if classPoints < 1.5:
                        letter = "F"
                    elif classPoints < 2.5:
                        letter = "C"
                    elif classPoints < 3.5:
                        letter = "B"
                    else:
                        letter = "A"

                    # print("\n\n")
                    # print("\n\nAssignment Average: " + str(assignmentAverage))
                    # print("Assessment Average: " + str(assessmentAverage))
                    # print("Total Class Points: " + str(classPoints))
                    # print("Letter Grade: " + letter + "\n")
                    # print("\n\n")
        s.post("https://calhigh.schoolloop.com/portal/toggleModule?d=x&module_name=grades")
    
    gradesString = ""

    for grade in gradesList:
        gradeType = "Assignment"
        if grade[1] == True:
            gradeType = "Assesment"
        gradesString += "<br>" + grade[2] + " " + gradeType + " " + str(grade[0])

    return "<p>" + username + ":<br><span class='letterGrade'>" + letter + "</span><br><span class='point'>" + str(classPoints) + "</span><br><br>Assignment Average: " + str(assignmentAverage) + "<br>Assessment Average: " + str(assessmentAverage) +"</p>" + gradesString



@app.route('/')

def home():
    return render_template('home.html')
    
@app.route('/join', methods=['GET','POST'])
def my_form_post():
    username = request.form['username']
    word = request.args.get('username')
    password = request.form['password']
    combine = webScrape(username,password)
    result = {
        "output": combine
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)