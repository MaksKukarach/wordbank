# exercise.py
import random
import openai_api
from models import LearnedWord, is_due

# Global dictionary for grammar particles per language.
GRAMMAR_PARTICLES = {
    "english": ["is", "are", "the", "a", "an", "to", "do", "does", "has", "have"],
    "italian": ["è", "sono", "il", "la", "le", "i", "un", "una", "per", "fare", "ha", "ho"]
}

# === Helper Functions ===

def filter_learnable(words, language: str):
    """Filter out words that are considered grammar particles and are already learned."""
    particles = GRAMMAR_PARTICLES.get(language.lower(), [])
    translatable = [word for word in words if word.lower() not in particles]
    learnable = []
    for word in translatable:
        word_obj = LearnedWord.query.filter_by(word=word).first()
        if not word_obj or is_due(word_obj):
            learnable.append(word)
    return learnable

def create_word_matching_exercise(sentence: str, learnable_words: list, source_lang: str, target_lang: str):
    """Create a word matching exercise."""
    translations = {
        word: openai_api.translate_word(word, source_lang, target_lang, sentence)
        for word in learnable_words
    }
    matching_target = list(translations.values())
    random.shuffle(matching_target)
    return {
        "type": "word_matching",
        "learnable_words": learnable_words,
        "translations": translations,
        "matching_target": matching_target
    }

def create_sentence_assembly_exercise(sentence: str, source_lang: str, target_lang: str, learnable_words: list):
    """Create a sentence assembly exercise (original sentence -> translated sentence)."""
    translated_sentence = openai_api.translate_sentence(sentence, source_lang, target_lang)
    assembly_bricks = translated_sentence.split()
    assembly_shuffled = assembly_bricks.copy()
    random.shuffle(assembly_shuffled)
    return {
        "type": "sentence_assembly",
        "original_sentence": sentence,
        "assembly_bricks": assembly_bricks,
        "assembly_shuffled": assembly_shuffled,
        "learnable_words": learnable_words,
        "translated_sentence": translated_sentence
    }

def create_reverse_assembly_exercise(sentence: str, translated_sentence: str, learnable_words: list):
    """Create a reverse assembly exercise (translated sentence -> original sentence)."""
    reverse_bricks = sentence.split()  # original words in correct order
    reverse_shuffled = reverse_bricks.copy()
    random.shuffle(reverse_shuffled)
    return {
        "type": "reverse_assembly",
        "translated_sentence": translated_sentence,
        "reverse_bricks": reverse_bricks,
        "reverse_shuffled": reverse_shuffled,
        "learnable_words": learnable_words
    }

def create_fill_in_blanks_exercise(sentence: str, translated_sentence: str, learnable_words: list):
    """
    Create a fill-in-the-blanks exercise.
    The original sentence is modified by replacing each learnable word with a blank ("____").
    """
    fill_in_sentence = sentence
    for word in learnable_words:
        fill_in_sentence = fill_in_sentence.replace(word, "____")
    return {
        "type": "fill_in_blanks",
        "translated_sentence": translated_sentence,
        "fill_in_sentence": fill_in_sentence,
        "learnable_words": learnable_words
    }

# === Main Function ===

def process_sentence(sentence: str, source_lang: str, target_lang: str):
    """
    Process a sentence to generate a set of language learning exercises.
    This function returns a dictionary containing the original sentence, languages,
    and a list of sub-exercise objects.
    """
    # Make the sentence lowercase for initial processing.
    decap_sentence = sentence[0].lower() + sentence[1:]
    # Strip punctuation and split.
    words = decap_sentence.strip(" .!?\"'").split()
    learnable_words = filter_learnable(words, source_lang)
    
    # Create sub-exercises.
    word_matching = create_word_matching_exercise(sentence, learnable_words, source_lang, target_lang)
    sentence_assembly = create_sentence_assembly_exercise(sentence, source_lang, target_lang, learnable_words)
    reverse_assembly = create_reverse_assembly_exercise(sentence, sentence_assembly["translated_sentence"], learnable_words)
    fill_in_blanks = create_fill_in_blanks_exercise(sentence, sentence_assembly["translated_sentence"], learnable_words)
    
    # Combine all exercises.
    exercises = [word_matching, sentence_assembly, reverse_assembly, fill_in_blanks]
    
    return {
         "sentence": sentence,
         "source_lang": source_lang,
         "target_lang": target_lang,
         "exercises": exercises
    }

def check_answer(exercise_type: str, user_answer, exercise_data: dict):
    """
    Check the answer for a given sub-exercise.
    
    Parameters:
      - exercise_type: one of "word_matching", "sentence_assembly", "reverse_assembly", "fill_in_blanks"
      - user_answer: the answer provided by the user (its structure depends on the exercise type)
      - exercise_data: the sub-exercise data dictionary
    """
    if exercise_type == "word_matching":
        # For matching, assume the interactive matching ensures correctness.
        return user_answer is True
    elif exercise_type == "sentence_assembly":
        correct_order = exercise_data.get("assembly_bricks", [])
        return user_answer == correct_order
    elif exercise_type == "reverse_assembly":
        correct_order = exercise_data.get("reverse_bricks", [])
        return user_answer == correct_order
    elif exercise_type == "fill_in_blanks":
        correct_words = exercise_data.get("learnable_words", [])
        return user_answer == correct_words
    return False
