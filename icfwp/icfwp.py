import os

from flask import Flask, render_template

#import config
from markov.model import TransitionTable

PUNCTUATION = [
    '.', ',', '!', '?', ":", "/"
]

TERMINAL_PUNCTUATION = [
    '.', '!', '?'
]

STRIPPABLE_PUNCTUATION = [
    '"', '(', ')', '<', '>', ":"
]

app = Flask(__name__)
app.config.from_pyfile('config.py')
if 'ICFWP_CONFIG' in os.environ:
    app.config.from_envvar('ICFWP_CONFIG')


def prettify_result(segments):
    result = []
    previous = ''
    next_cap = True
    sentences = 0
    words = 0


    for item in segments:
        if item in PUNCTUATION and previous:
            result[-1] = "%s%s" % (previous, item)
            if item in TERMINAL_PUNCTUATION:
                next_cap = True
                sentences += 1
                if(sentences >= app.config["MAX_SENTENCES"] or
                   words >= app.config["SUGGESTED_WORDS"]):
                    break
        else:
            words += 1
            if words > app.config["MAX_WORDS"]:
                break
            if next_cap or item == "i":
                item = item.capitalize()
                next_cap = False
            result.append(item)
            previous = item

    if not result:
        # The best part about this is that nobody will be able to tell that
        # it's not actually a writing prompt.
        return "I dunno"

    # End it sensibly
    if '.' not in result[-1]:
        result[-1] = "%s." % result[-1]
    return " ".join(result)


def random_prompt(transition_table):
    return prettify_result(list(transition_table))


@app.route("/")
def root():
    markov_filename = app.config['MARKOV_STORAGE']
    tt = TransitionTable.from_filename(markov_filename)
    return render_template("index.html", prompt=random_prompt(tt))

@app.route("/about", defaults={'number': 3})
@app.route('/about/<int:number>')
def about(number):
    if number > 10:
        number = 10
    elif number < 1:
        number = 3

    markov_filename = app.config['MARKOV_STORAGE']
    tt = TransitionTable.from_filename(markov_filename)
    prompts = [random_prompt(tt) for unused in xrange(number)]
    return render_template("about.html", prompts=prompts)
