# openai_api.py
import openai

# Ensure you set your OPENAI_API_KEY in your environment
client = openai.OpenAI()


def generate_sentence(language="English", length="from 3 to 5", difficulty="easy or medium", grammar="",  new_words=None, topic=""):
    prompt = f"Write a sentence in {language}. There must be {length} words."
    if topic != "":
        prompt += f" The theme of the sentence is: {topic}."
    if grammar != "":
        prompt += f" Use only the grammar {grammar}."
    if new_words:
        prompt += f" Incorporate these words (in any order): {new_words}. You can change their form (tense, plural, etc.)."
    prompt += f" Difficulty of the sentence: {difficulty}."
    prompt += " Write the sentence only."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful language learning assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=1,
            max_tokens=500,
        )
        sentence = response.choices[0].message.content.strip()
        return sentence
    except Exception as e:
        return f"Error generating sentence: {str(e)}"


def translate_word(word, source_lang, target_lang, context):
    prompt = (
        f"Translate the word '{word}' from {source_lang} to {target_lang}."
        + f" The translation must fit the context: '{context}'"
        + "Return the translated word only in its base form."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a translation agent.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=30,
        )
        translated = response.choices[0].message.content.strip()
        return translated
    except Exception as e:
        return f"{e}: {word}_translated_with_context"

def translate_sentence(sentence, source_lang, target_lang):
    prompt = (
        f"Translate the following sentence from {source_lang} to {target_lang}:"
        + f" '{sentence}'"
        + "Try to follow the order of the words in the original sentence."
        + "Return the translated sentence only."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a translation agent.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=100,
        )
        translated = response.choices[0].message.content.strip()
        return translated
    except Exception as e:
        return f"{e}: {sentence}_translated"

def get_similar_words(word, language):
    prompt = (f"Write three different words orthographically (but not semantically) similar to '{word}' in {language}."
              + "If you can't come up with a word, create a fake one that sounds like a real word could."
              + "Return the words in lowercase separated by commas.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a language expert.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=100,
        )
        similar_words = response.choices[0].message.content.strip().split("\n")
        similar_words = similar_words[0].split(", ")
        return similar_words
    except Exception as e:
        return [f"{e}: similar_word_{i}" for i in range(3)]