# exercise.py
import random
import openai_api
from models import LearnedWord, is_due

# Global dictionary for grammar particles per language.
GRAMMAR_PARTICLES = {
    "english": ["is", "are", "the", "a", "an", "to", "do", "does", "has", "have"],
    "italian": ["è", "sono", "il", "la", "le", "i", "un", "una", "per", "fare", "ha", "ho"],
    "russian": []  # Add as needed.
}

def filter_learnable(words, language: str):
    """Return words that are not grammar particles and either not in DB or due for review."""
    particles = GRAMMAR_PARTICLES.get(language.lower(), [])
    translatable = [word for word in words if word.lower() not in particles]
    learnable = []
    for word in translatable:
        word_obj = LearnedWord.query.filter_by(word=word).first()
        if not word_obj or is_due(word_obj):
            learnable.append(word)
    return learnable

def create_word_matching_exercise(sentence: str, learnable_words: list, source_lang: str, target_lang: str):
    """Generate a word matching exercise."""
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
    """Generate an exercise where the user assembles the translated sentence."""
    translated_sentence = openai_api.translate_sentence(sentence, source_lang, target_lang)
    assembly_bricks = translated_sentence.split()
    assembly_shuffled = assembly_bricks.copy()
    random.shuffle(assembly_shuffled)
    return {
        "type": "sentence_assembly",
        "original_sentence": sentence,
        "translated_sentence": translated_sentence,
        "assembly_bricks": assembly_bricks,
        "assembly_shuffled": assembly_shuffled,
        "learnable_words": learnable_words
    }

def create_reverse_assembly_exercise(sentence: str, translated_sentence: str, learnable_words: list):
    """Generate an exercise where the user assembles the original sentence from the translated one."""
    reverse_bricks = sentence.split()
    reverse_shuffled = reverse_bricks.copy()
    random.shuffle(reverse_shuffled)
    return {
        "type": "reverse_assembly",
        "translated_sentence": translated_sentence,
        "reverse_bricks": reverse_bricks,
        "reverse_shuffled": reverse_shuffled,
        "learnable_words": learnable_words
    }

def create_fill_in_blanks_exercise(sentence: str, source_lang: str, target_lang: str, learnable_words: list):
    """
    Generate a fill-in-the-blanks exercise.
    Randomly select one or two words from learnable_words (preserving the order of their appearance in the sentence)
    and replace their first occurrence in the sentence with "___".
    Returns the modified sentence and the list of correct answers (in order).
    """
    translated_sentence = openai_api.translate_sentence(sentence, source_lang, target_lang)
    if not learnable_words:
        selected = []
    else:
        # Choose randomly 1 or 2 words, but not more than available.
        k = random.choice([1, 2])
        k = min(len(learnable_words), k)
        selected = random.sample(learnable_words, k)
        # Sort the selected words based on their first appearance in the sentence
        selected.sort(key=lambda w: sentence.lower().find(w.lower()))
    
    fill_sentence = sentence
    blanks = []  # correct answers in order
    for word in selected:
        # Find first occurrence (case-insensitive)
        lower_sentence = fill_sentence.lower()
        lower_word = word.lower()
        index = lower_sentence.find(lower_word)
        if index != -1:
            # Replace only the first occurrence.
            fill_sentence = fill_sentence[:index] + "___" + fill_sentence[index+len(word):]
            blanks.append(word)
    return {
        "type": "fill_in_blanks",
        "original_sentence": sentence,
        "translated_sentence": translated_sentence,
        "fill_in_sentence": fill_sentence,
        "blanks": blanks,  # the correct words for the blanks in order
        "learnable_words": blanks
    }

def create_word_options_exercise(sentence: str, source_lang: str, target_lang: str, learnable_words: list):
    """
    Generate a word options exercise.
    Randomly select one learnable word, obtain its translation, and generate three distractor options.
    """
    if not learnable_words:
        candidate = sentence.split()[0]
    else:
        candidate = random.choice(learnable_words)
    correct_word = candidate
    similar_options = openai_api.get_similar_words(candidate, source_lang)
    if not similar_options or len(similar_options) < 3:
        similar_options = [candidate + suffix for suffix in ["1", "2", "3"]]
    distractors = similar_options[:3]
    options = distractors + [correct_word]
    random.shuffle(options)
    prompt_translation = openai_api.translate_word(candidate, source_lang, target_lang, sentence)
    return {
        "type": "word_options",
        "prompt_translation": prompt_translation,
        "correct_word": correct_word,
        "options": options,
        "learnable_words": [correct_word]
    }

def process_sentence(sentence: str, source_lang: str, target_lang: str):
    """
    Process a sentence to generate a suite of language learning exercises.
    Returns a dictionary with the original sentence, languages, and a list of sub-exercise objects.
    """
    decap_sentence = sentence[0].lower() + sentence[1:]
    words = decap_sentence.strip(" .!?\"'").split()
    learnable_words = filter_learnable(words, source_lang)
    
    word_matching = create_word_matching_exercise(sentence, learnable_words, source_lang, target_lang)
    sentence_assembly = create_sentence_assembly_exercise(sentence, source_lang, target_lang, learnable_words)
    reverse_assembly = create_reverse_assembly_exercise(sentence, sentence_assembly["translated_sentence"], learnable_words)
    fill_in_blanks = create_fill_in_blanks_exercise(sentence, source_lang, target_lang, learnable_words)
    word_options = create_word_options_exercise(sentence, source_lang, target_lang, learnable_words)
    
    exercises = [word_matching, sentence_assembly, word_options, reverse_assembly, fill_in_blanks]
    
    return {
         "sentence": sentence,
         "source_lang": source_lang,
         "target_lang": target_lang,
         "exercises": exercises
    }

def check_answer(exercise_type: str, user_answer, exercise_data: dict):
    if exercise_type == "word_matching":
        return user_answer is True
    elif exercise_type == "sentence_assembly":
        correct_order = exercise_data.get("assembly_bricks", [])
        return user_answer == correct_order
    elif exercise_type == "reverse_assembly":
        correct_order = exercise_data.get("reverse_bricks", [])
        return user_answer == correct_order
    elif exercise_type == "fill_in_blanks":
        correct = exercise_data.get("blanks", [])

        # Normalize both correct answers and user answers
        norm_correct = [w.strip().lower() for w in correct]
        norm_user = [w.strip().lower() for w in user_answer]

        # Debugging output
        print("Expected:", norm_correct)
        print("User Answer:", norm_user)

        return norm_user == norm_correct
    elif exercise_type == "word_options":
        correct = exercise_data.get("correct_word", "")
        return user_answer.strip().lower() == correct.strip().lower()
    return False

