# some markov model thing
# Trey Robinson
# August 22, 2019

import re
import random


PUNCTUATION = {'.', '!', '?', ''}


def _get_probabilities(d):
    items = list(d.keys())
    total_weight = sum([d[x] for x in items])
    return items, [d[x] / total_weight for x in items]


def _choose(items, probs):
    p = probs[0]
    x = random.random()
    i = 0
    while x > p:
        i += 1
        p += probs[i]
    return items[i]


def _clean(text):
    text = text.lower()
    text = re.sub(r'[\[\]()`~"*&^%$#@]', '', text)
    return text


def _read_until_char(fp, charset):
    current = None
    while current is not '':
        buf = ''
        current = fp.read(1)
        while current is not '':
            buf += current
            if current in charset:
                break
            current = fp.read(1)
        yield buf.strip()


def _print_dict(name, d):
    s = name + ": {\n"
    for key in d:
        s += "\t{0}: {1}\n".format(key, d[key])
    s += "}"
    print(s)


class BufferedText:
    def __init__(self):
        self._fp = None
        self._buffer = ""

    def set_filename(self, filename):
        self._fp = filename

    def read(self):
        if self._fp is None:
            yield ''
        with open(self._fp, 'r') as fp:
            for sentence in _read_until_char(fp, PUNCTUATION):
                sentence = re.sub(r'[\[\]()`~"*&^%$#@]', '', sentence)
                sentence = re.sub(r'\n', ' ', sentence)
                yield sentence.strip()
        yield ''


class MarkovModel:
    """Markov model, no punctuation because handling it is a pain in the ass"""
    def __init__(self):
        """
        Implemented using a "dictogram" structure, benefits are fast (O(1)) lookup of nodes
        Consider the phrase "One fish, two fish, red fish, blue fish"
        It would be stored as the following
        {
            '_start':   {'one': 1},
            'one':      {'fish': 1},
            'fish':     {'two': 1, 'red': 1, 'blue': 1, '_end': 1}
            'two':      {'fish': 1},
            'red':      {'fish': 1},
            'blue':     {'fish': 1},
        }
        """
        self._dictogram = {
            "_start": {},
            "_end": {}
        }

    def __repr__(self):
        s = ""
        for key in self._dictogram:
            s += "{}: {}\n".format(key, self._dictogram[key])
        return s

    def update_model(self, text):
        u = "_start"
        n = "_end"
        text = text.split(' ')
        for v in text:
            v = _clean(v)
            if v not in self._dictogram:
                self._dictogram[v] = {}
            if v not in self._dictogram[u]:
                self._dictogram[u][v] = 0
            self._dictogram[u][v] += 1
            u = v

        if u not in self._dictogram[n]:
            self._dictogram[u][n] = 0
        self._dictogram[u][n] += 1

    def update_model_from_file(self, filename):
        fd = BufferedText()
        fd.set_filename(filename)
        for line in fd.read():
            self.update_model(line)

    def _traverse(self):
        s = ''
        neighbours, weights = _get_probabilities(self._dictogram["_start"])
        current = _choose(neighbours, weights)
        while current != "_end" and current != '':
            # _print_dict(current, self._dictogram[current])
            s += ' {}'.format(current)
            neighbours, weights = _get_probabilities(self._dictogram[current])
            previous = current
            current = _choose(neighbours, weights)
            # print("Selecting \"{}\" from \"{}\"".format(current, previous))
        return s.strip()

    def output(self, n=1):
        s = ''
        for i in range(0, n):
            s += self._traverse() + ' '
        return s.strip()


if __name__ == "__main__":
    import os
    markov = MarkovModel()
    for filename in os.listdir("text"):
        markov.update_model_from_file("text\\{}".format(filename))
