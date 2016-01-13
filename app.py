import os
from flask import Flask, render_template, request
from similarity import *

from flask import jsonify

# refers to application_top
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

APP_DATA = os.path.join(APP_ROOT, 'static/data')

DEBUG = True

app = Flask(__name__)
app.debug = DEBUG

ALLOWED_EXTENSIONS = set(['txt'])

@app.route('/')
def index():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')
    return render_template('index.html', navbar=navbar, footer=footer)

@app.route('/contact')
def contact():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')
    return render_template('contact.html', navbar=navbar, footer=footer)

@app.route('/visualize')
def visualize():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')

    # open and read example file
    with open(os.path.join(APP_DATA, 'example.txt')) as f:
        conv = readFile(f)

    # get lexical similarity
    tbtToken = build_turnbyturntokens(conv);
    similarity = computetbtsimilarities(tbtToken, windowweights, idf)

    # get the index of max similarity
    max_value = max(similarity)
    max_index = similarity.index(max_value)

    # get the index of second max similarity
    second_max = sorted(similarity)[-2]
    second_max_index = similarity.index(second_max)

    # get the index of third max similarity
    third_max = sorted(similarity)[-3]
    third_max_index = similarity.index(third_max)

    data = normalizeData(similarity)
    tbtConversation = turnByTurn(conv)

    return render_template('visualize.html', data=data, tbt=tbtConversation, max=max_index, secondMax = second_max_index, thirdMax = third_max_index, navbar=navbar, footer=footer)

@app.route('/about')
def about():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')
    return render_template('about.html', navbar=navbar, footer=footer)

@app.route('/visualize/graph')
def graph():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')
    # data = [[1,10],[2,20],[3,50],[4,70]]
    return render_template('graph.html', navbar=navbar, footer=footer)

@app.route('/visualize/graph', methods=['POST'])
def graph_post():
    navbar = render_template('navbar.html')
    footer = render_template('footer.html')
    file = request.files['file-input']

    if file and allowed_file(file.filename):
        conversation = readFile(file)

        # get lexical similarity
        tbtToken = build_turnbyturntokens(conversation);
        similarity = computetbtsimilarities(tbtToken, windowweights, idf)

        # get the index of max similarity
        max_value = max(similarity)
        max_index = similarity.index(max_value)

        # get the index of second max similarity
        second_max = sorted(similarity)[-2]
        second_max_index = similarity.index(second_max)

        # format similarity array so that it can be read by dygraph. 
        # ex: [65,76,86] --> [[0, 65], [1, 76], [2,86]]
        data = normalizeData(similarity)

        tbtConversation = turnByTurn(conversation)

        return render_template('generated-graph.html', data=data, tbt=tbtConversation, max=max_index, secondMax = second_max_index, navbar=navbar, footer=footer)
    else:
        return "ERROR: File extension not acceptable"

def readFile(file):
    conversation = []
    for line in file.readlines():
        if line == '\n': continue
        line = line.rstrip('\n') #remove '/n' at the end 
        parts = line.split(': ')
        row = {'Sender': parts[0], 'Text': parts[1]}
        conversation.append(row)
    return conversation

def turnByTurn(conv):
    turnbyturnconv = []
    text = []
    for l,line in enumerate(conv):
        sender = line['Sender']
        text.append(line['Text'])
        if l+1 < len(conv):
            if conv[l+1]['Sender'] != sender:
                t = ' '.join(text)
                line
                turnbyturnconv.append(sender+": "+t)
                text = []
    t = ' '.join(text)
    turnbyturnconv.append(sender+": "+t)
    return turnbyturnconv

def normalizeData(siml):
    data = [[0,0]]
    for x in range(len(siml)):
        data.append([x+1, siml[x]])
    return data

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run()