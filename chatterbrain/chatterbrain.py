import json
import string
import re
import random

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords


class Token:
    def __init__(self):
        self.weight = 0
        self.related_words = []

    @staticmethod
    def serialize(obj):
        if isinstance(obj, Token):
            return obj.__dict__


class ChatterBrain:
    def __init__(self, phrase_step=1):
        self.memory = {}

        if phrase_step < 0:
            self.phrase_step = 1
        else:
            self.phrase_step = phrase_step

    def load(self, infile):
        memory_json = json.load(infile)

        for phrase in memory_json:
            obj = memory_json[phrase]
            token = Token()
            token.weight = obj['weight']
            token.related_words = obj['related_words']
            self.memory[phrase] = token

    def save(self, outfile):
        outfile.write(json.dumps(self.memory, default=Token.serialize))

    def learn(self, strinput):
        sents = sent_tokenize(strinput.lower())

        for sent in sents:
            words = word_tokenize(
                re.sub('[' + string.punctuation + ']', '', sent))

            if len(words) <= self.phrase_step:
                continue

            for i in range(0, len(words)):
                phrase = ' '.join(words[i:i + self.phrase_step:1])
                related_word = None

                if i + self.phrase_step < len(words):
                    related_word = words[i + self.phrase_step]
                else:
                    break

                token = None

                if phrase in self.memory:
                    token = self.memory[phrase]
                    token.weight += 1
                else:
                    token = Token()

                token.related_words.append(related_word)
                self.memory[phrase] = token

    def get_response(self, strinput):
        if len(self.memory) < 1:
            return None

        phrases_of_interest = self.get_phrases_of_interest(strinput.lower())

        start_phrase = random.choice(list(phrases_of_interest)) if len(
            phrases_of_interest) > 0 else random.choice(list(self.memory))
        current_phrase = start_phrase
        current_token = self.memory[current_phrase]
        response = current_phrase
        used_phrases = [current_phrase]
        while len(current_token.related_words) > 0:
            next_word = random.choice(current_token.related_words)
            response += ' ' + next_word
            full_phrase = word_tokenize(current_phrase)
            full_phrase.append(next_word)
            next_phrase = ' '.join(
                full_phrase[len(full_phrase) - self.phrase_step::])

            if next_phrase not in self.memory or next_phrase in used_phrases:
                break

            current_phrase = next_phrase
            current_token = self.memory[current_phrase]
            used_phrases.append(current_phrase)
        return response

    def get_phrases_of_interest(self, strinput):
        phrases = []
        sents = sent_tokenize(strinput)

        for sent in sents:
            words = [word for word in word_tokenize(
                re.sub('[' + string.punctuation + ']', '', sent)) if word.lower() not in stopwords.words('english')]

            for word in words:
                for phrase in self.memory:
                    token = self.memory[phrase]
                    if word in token.related_words and phrase not in phrases:
                        phrases.append(phrase)

        return phrases
