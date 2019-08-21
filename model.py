import random
import re


PUNCTUATION = {'.', '!', '?'}

def print_dict(dictionary):
    for key in dictionary.keys():
        s = "{0}: {1}\n".format(key, dictionary[key])
        print(s)


def choose(items, probs):
    p = probs[0]
    x = random.random()
    i = 0
    while x > p:
        i += 1
        p += probs[i]
    return items[i]


def get_probabilities(d):
    total_weight = sum([d[x] for x in d])
    return [d[key]/total_weight for key in d]


class BufferedText():
    def __init__(self, text=''):
        self._fp = None
        self._buffer = text

    def load_file(self, filename):
        self._fp = open(filename, 'r')

    def get_text(self, size=1024):
        # maintain the buffer
        while True:
            if self._fp is not None:
                self._buffer = self._fp.read(size)
                if not self._buffer: # failed to read
                    break
                # make sure that buffer ends at a whitespace
                while not str.isspace(self._buffer[-1]):
                    char = self._fp.read()
                    if not char:
                        break
                    self._buffer += char
            words = self._buffer.split()
            for word in words:
                yield re.sub(r'[\[\]\(\)~`"]', '', word)
            break
        yield ''


class LanguageModel:
    def __init__(self):
        self._words = {}

    def update_model(self, text):
        """
        This method is the main method in which the program will create it's language model.
        By reading in text, the program will create a word graph representing it's current vocabulary.
        Words are nodes, the probability of using a word directly after the current word are the edges.
        """
        v = None
        for u in text.get_text():
            if (u != ''):
                u = u.lower()
                # put word into graph if it doesn't already exist
                if u not in self._words:
                    self._words[u] = {}
                if v is not None:
                    # check for punctuation
                    # update edge if it already exists
                    if u in self._words[v]:
                        self._words[v][u] += 1
                    else:
                        # otherwise create edge in graph
                        self._words[v][u] = 1
                if u[-1] in PUNCTUATION:
                    v = None
                else:
                    v = u

    def create_chain(self):
        # pick a word at random
        # pick an edge from current word at random with weighted probability
        # traverse edge
        s = ''
        all_words = list(self._words)
        u = all_words[random.randint(0, len(all_words) - 1)]
        running = True
        while running:
            s += u + ' '
            neighbours = self._words[u]
            if self._words[u] == {}:
                running = False
            else:
                u = choose(list(neighbours), get_probabilities(neighbours))
        s = s.strip()
        print(s)

def load_all():
    import os
    languagemodel = LanguageModel()
    for f in os.listdir('text'):
            x = BufferedText()
            x.load_file('text\\{}'.format(f))
            languagemodel.update_model(x)
    return languagemodel

def load_one(filename):
    import os
    languagemodel = LanguageModel()
    x = BufferedText()
    x.load_file("text\\{}".format(filename))
    languagemodel.update_model(x)
    return languagemodel
