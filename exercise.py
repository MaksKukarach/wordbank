# exercise.py
import random
import openai_api
from models import *

grammar_particles = {
    "english": ["is", "are", "the", "a", "an", "to", "do", "does", "has", "have"],
    "italian": ["è", "sono", "il", "la", "le", "i", "un", "una", "per", "fare", "ha", "ho"]
}

def process_sentence(sentence: str, source_lang: str, target_lang: str):
    """ Process a sentence to generate language learning exercises. """
    decap_sentence = sentence[0].lower() + sentence[1:]
    words = decap_sentence.strip(" .!?\"'").split()
    learnable_words = filter_learnable(words, source_lang.lower())
    
    # --- Word Matching Exercise ---
    # Create mapping of source word -> translated word using context-aware translation.
    translations = {
        word: openai_api.translate_word(word, source_lang, target_lang, sentence)
        for word in learnable_words
    }
    matching_target = list(translations.values())
    random.shuffle(matching_target)
    
    word_matching = {
        "type": "word_matching",
        "learnable_words": learnable_words,
        "translations": translations,
        "matching_target": matching_target
    }
    
    # --- Sentence Assembly Exercise --- Original -> Translated ---
    # Obtain the full translation of the sentence.
    translated_sentence = openai_api.translate_sentence(sentence, source_lang, target_lang)
    assembly_bricks = translated_sentence.split()
    assembly_shuffled = assembly_bricks.copy()
    random.shuffle(assembly_shuffled)
    
    sentence_assembly = {
        "type": "sentence_assembly",
        "original_sentence": sentence,
        "assembly_bricks": assembly_bricks,
        "assembly_shuffled": assembly_shuffled,
        "learnable_words": learnable_words,
    }
    
    # --- Reverse Assembly Exercise --- Translated -> Original ---
    # For reverse assembly, use the original sentence's words.
    reverse_bricks = sentence.split()  # original words in correct order
    reverse_shuffled = reverse_bricks.copy()
    random.shuffle(reverse_shuffled)
    
    reverse_assembly = {
        "type": "reverse_assembly",
        "translated_sentence": translated_sentence,
        "reverse_bricks": reverse_bricks,
        "reverse_shuffled": reverse_shuffled,
        "learnable_words": learnable_words,
    }
    
    # Combine sub-exercises into a list.
    exercises = [word_matching, sentence_assembly, reverse_assembly]
    
    return {
         "sentence": sentence,
         "source_lang": source_lang,
         "target_lang": target_lang,
         "exercises": exercises
    }

def filter_learnable(words, language):
    translatable_words = [word for word in words if word.lower() not in grammar_particles[language.lower()]]
    learnable_words = []
    for word in translatable_words:
        word_object = LearnedWord.query.filter_by(word=word).first()
        if not word_object or is_due(word_object):
            learnable_words.append(word)
    return learnable_words

def check_answer(exercise_type, user_answer, exercise_data):
    """
    Check the answer for a given sub-exercise.
    
    Parameters:
      - exercise_type: "word_matching", "sentence_assembly", or "reverse_assembly"
      - user_answer: the answer provided by the user
      - exercise_data: the sub-exercise data dictionary
    
    For word matching, we assume that if all pairs are matched, the answer is correct.
    """
    if exercise_type == "word_matching":
        return user_answer == True
    elif exercise_type == "sentence_assembly":
        correct_order = exercise_data.get("assembly_bricks", [])
        return user_answer == correct_order
    elif exercise_type == "reverse_assembly":
        correct_order = exercise_data.get("reverse_bricks", [])
        return user_answer == correct_order
    return False
