from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from bs4 import BeautifulSoup
import werkzeug

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument('file1', type=werkzeug.datastructures.FileStorage, location='files')
parser.add_argument('file2', type=werkzeug.datastructures.FileStorage, location='files')

class FilesToArray(Resource):
    def post(self):
        args = parser.parse_args()
        answer_key = args['file1']        
        response_sheet = args['file2']

        #Answer_Key
        soup = BeautifulSoup(answer_key.read(), "html.parser")
        table = soup.find("table", {"id": "ctl00_LoginContent_grAnswerKey"})
        data = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) > 0:
                data.append([cell.text for cell in cells])
        key = {}
        for arr in data:
            key[arr[2].strip('\n')] = arr[3].strip('\n')

        
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
            if 'MCQ' in question and 'Answered' in question:
                chosen = int(question[15])
                question_id = question[3]
                answer_id = question[3+chosen*2]
                values[question_id] = answer_id
            if 'SA' in question:
                answer = answers[counter]
                if 'Answered' in question:
                    question_id = question[3]
                    answer_id = answer[5]
                    values[question_id] = answer_id
            counter += 1
        
        #Calculate Score
        correct = 0
        incorrect = 0
        incorr_q = []
        for elem in values:
            if(key[elem] == values[elem]):
                correct += 1
            else:
                incorrect += 1
                incorr_q.append(elem)
        total = correct*4 - incorrect

        result = {'Correct': correct, 'Incorrect': incorrect, 'Total': total,
                  'Incorrect_Questions': incorr_q}

        return jsonify(result)

api.add_resource(FilesToArray, '/score')

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'