# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from time_utils import utc_now, ensure_utc

db = SQLAlchemy()

# Each level is a number of minutes until the next review:
# 5 min, 10 min, 15 min, 20 min, 30 min, 1 hour, 2 hours, 1 day, 2 days, 4 days, 1 week, 2 weeks, 1 month
MASTERY_LEVELS = [5, 10, 15, 20, 30, 60, 120, 1440, 2880, 5760, 10080, 20160, 43200]

def calculate_due_time(mastery_index=0):
    return utc_now() + timedelta(minutes=MASTERY_LEVELS[mastery_index])

class LearnedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    # Use a callable so that each new record gets a fresh value.
    due_time = db.Column(db.DateTime, default=calculate_due_time)
    mastery_level = db.Column(db.Integer, default=0)

def add_word(word):
    learned = LearnedWord.query.filter_by(word=word).first()
    if not learned:
        learned = LearnedWord(word=word)
        db.session.add(learned)
        db.session.commit()

def get_all_words():
    return LearnedWord.query.all()

def update_word_mastery(input_word, increase=True):
    if input_word is None:
        raise ValueError("Word cannot be None")
    existing = LearnedWord.query.filter_by(word=input_word).first()
    if existing:
        if increase:
            existing.mastery_level = min(existing.mastery_level + 1, len(MASTERY_LEVELS) - 1)
        else:
            existing.mastery_level = max(existing.mastery_level - 1, 0)
        # Update due_time using our utility functions.
        existing.due_time = calculate_due_time(existing.mastery_level)
    else:
        add_word(input_word)
    db.session.commit()

def get_due_words():
    return LearnedWord.query.filter(LearnedWord.due_time <= utc_now()).all()

def is_due(word: LearnedWord):
    return ensure_utc(word.due_time) <= utc_now()

def time_until_review(word: LearnedWord, formatted=True):
    # Ensure due_time is UTC aware.
    due = ensure_utc(word.due_time)
    diff = due - utc_now()
    if formatted:
        return str(diff).split(".")[0]  # Remove microseconds
    else:
        return diff
