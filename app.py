from flask import Flask, render_template, request, session, jsonify
from openai_api import generate_sentence
from exercise import process_sentence, check_answer
from models import db, update_word_mastery, get_due_words, get_all_words
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  # In production, use environment variables

# Configure the database (using SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wordbank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

def shuffle_filter(l):
    new_list = l.copy()
    random.shuffle(new_list)
    return new_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_exercise', methods=['POST'])
def start_exercise():
    level = request.form.get('level')
    grammar = request.form.get('grammar')
    length = request.form.get('length')
    new_words = request.form.get('new_words')
    direction = request.form.get('direction')
    topic = request.form.get('topic')

    if new_words == "":
        # Get up to 2 random due words from the database
        due_words = get_due_words()
        if len(due_words) >= 2:
            new_words = [word.word for word in due_words[:2]]
        else:
            new_words = [word.word for word in due_words]

    # Set languages
    langs = direction.lower().split("-")
    source_lang= langs[0]
    target_lang = langs[1]

    sentence = generate_sentence(level, grammar, length, new_words, source_lang, topic)
        
    exercise = process_sentence(sentence, source_lang, target_lang)
    session['exercise'] = exercise
    return render_template('exercise.html', exercise=exercise)

@app.route('/check_answer', methods=['POST'])
def check_user_answer():
    data = request.get_json()
    exercise_index = data.get('exercise_index')  # index of the sub-exercise
    exercise_type = data.get('exercise_type')      # type of the sub-exercise
    user_answer = data.get('user_answer', [])
    practiced_words = data.get('practiced_words', [])

    exercise = session.get('exercise')
    if not exercise:
        return jsonify({'result': 'error', 'message': 'Нет активного упражнения.'}), 400

    # Get the specific sub-exercise data
    try:
        sub_exercise = exercise["exercises"][exercise_index]
    except (KeyError, IndexError):
        return jsonify({'result': 'error', 'message': 'Неверные данные упражнения.'}), 400

    # Check the answer using our check_answer function.
    if check_answer(exercise_type, user_answer, sub_exercise):
        for word in practiced_words:
            update_word_mastery(word, increase=True)
        return jsonify({'result': 'correct'})
    else:
        return jsonify({'result': 'incorrect'})

@app.route('/wordbank')
def wordbank():
    words = get_all_words()
    return render_template('wordbank.html', words=words)

if __name__ == '__main__':
    app.run(debug=True)
