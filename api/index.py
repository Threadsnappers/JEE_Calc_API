from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import werkzeug

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
parser = werkzeug.datastructures.FileStorage

@app.route('/score', methods=['POST'])
@cross_origin()
def calculate_score():
    answer_key = request.files['file1']        
    response_sheet = request.files['file2']
    #Answer_Key
    soup = BeautifulSoup(answer_key.read(), "html.parser")
    table = soup.find("table", {"id": "ctl00_LoginContent_grAnswerKey"})
    key = {}
    bonus = []
    counter = 102
    question_2 = "_lbl_QuestionNo"
    answer_2 = "_lbl_RAnswer"
    status_2 = "lblstatus"
    ids = soup.find_all('span')
    question = []
    answer = []
    for val in ids:
        if val.get('id') != None:
            if question_2 in val.get('id'):
                question.append(val.text)
            if answer_2 in val.get('id'):
                answer.append(val.text)
            if status_2 in val.get('id'):
                bonus.append(question[-1])
                del question[-1] 
    print(len(question))
    for i in range(0,len(question)):
        key[question[i]] = answer[i]

    #Response_Sheet
    soup = BeautifulSoup(response_sheet.read(), "html.parser")
    tables = soup.find_all("table", {"class": "menu-tbl"})
    values = {}
    data = []
    for table in tables:
        sub = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) > 0:
                sub.extend([cell.text for cell in cells])
        data.append(sub)
    answers = []
    tables = soup.find_all("table",{"class": "questionRowTbl"})
    for table in tables:
        sub = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) > 0:
                sub.extend([cell.text for cell in cells])
        answers.append(sub)
    counter = 0
    for question in data:
        if 'MCQ' in question and ((('Answered' in question) or ('Marked For Review' in question)) and (not ('Not Attempted and Marked For Review' in question))):
            chosen = int(question[15])
            question_id = question[3]
            answer_id = question[3+chosen*2]
            values[question_id] = answer_id
        if 'SA' in question:
            answer = answers[counter]
            if ((('Answered' in question) or ('Marked For Review' in question)) and (not ('Not Attempted and Marked For Review' in question))):
                question_id = question[3]
                answer_id = answer[5]
                values[question_id] = answer_id
        counter += 1

    #Calculate Score
    correct = 0
    incorrect = 0
    incorr_q = []
    corr_q = []
    for elem in values:
        if(elem in bonus):
            continue
        if(key[elem] == values[elem]):
            corr_q.append(elem)
            correct += 1
        else:
            incorrect += 1
            incorr_q.append(elem)
    bonus = len(bonus)
    total = correct*4 - incorrect
    
    result = {'Correct': correct, 'Incorrect': incorrect, 'Total': total,
              'Incorrect_Questions': incorr_q, 'Bonus': bonus}

    return jsonify(result)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/about')
def about():
    return 'About'

if __name__ == '__main__':
    app.run(debug=True)
