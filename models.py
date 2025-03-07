# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone

db = SQLAlchemy()

# Each level is a number of minutes until the next review:
# 10 min -> 1 hour -> 24 hours -> 2 days -> 4 days -> 7 days -> 14 days -> 30 days
MASTERY_LEVELS = [10, 60, 1440, 2880, 5760, 10080, 20160, 43200]

class LearnedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow)
    mastery_level = db.Column(db.Integer, default=0)

def add_word(word):
    # If word not in database, add the word to the database with mastery level 0 and current timestamp.
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
            # If the mastery level is already at the highest level, it will stay at max level.
            existing.mastery_level = min(existing.mastery_level + 1, len(MASTERY_LEVELS) - 1)
        else:
            existing.mastery_level = max(existing.mastery_level - 1, 0)
        existing.last_practiced = datetime.now(timezone.utc)
    else:
        add_word(input_word)
    db.session.commit()

def get_due_words():
    return LearnedWord.query.filter(LearnedWord.last_practiced < datetime.now(timezone.utc) - timedelta(minutes=MASTERY_LEVELS[0])).all()

def is_due(word):
    return word.last_practiced < datetime.now(timezone.utc) - timedelta(minutes=MASTERY_LEVELS[word.mastery_level])