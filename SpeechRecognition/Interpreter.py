import nltk
import spacy
from spacy.symbols import *

nlp = spacy.load('en')


def parse_phrase_deprecated(phrase):
	tokens = nltk.word_tokenize(phrase)
	tagged = nltk.pos_tag(tokens)
	print 'Tokenized phrase: ', tagged
	print
	find_objects_deprecated(tagged)


def find_objects_deprecated(tagged):
	print 'Just for testing purposes...'
	print 'NN: ',
	for word in tagged:
		if word[1][:2] == 'NN':
			print word[0], ' ',
	print
	print


def text2int(textnum, numwords={}):
	if not numwords:
		units = [
			"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
			"nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
			"sixteen", "seventeen", "eighteen", "nineteen",
		]

		tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

		scales = ["hundred", "thousand", "million", "billion", "trillion"]

		numwords["and"] = (1, 0)
		for idx, word in enumerate(units):    numwords[word] = (1, idx)
		for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
		for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

	current = result = 0
	for word in textnum.split():
		if word not in numwords:
			raise Exception("Illegal word: " + word)

		scale, increment = numwords[word]
		current = current * scale + increment
		if scale > 100:
			result += current
			current = 0

	return result + current


def parse_phrase(phrase):
	doc = nlp(unicode(phrase, encoding="utf-8"))
	print doc
	objects = []
	verbs = []
	quantity = []
	unit = []
	for np in doc.noun_chunks:
		objects.append(np.root.text)
		verbs.append(np.root.head.text)
		print np.text, np.root.text, np.root.dep_, np.root.head.text
	for word in doc:
		if word.pos == NOUN and word.head.pos == VERB:
			if word.text not in objects:
				unit.append(word)
				quantity.append(list(word.lefts)[0])
	print 'verbs: ', verbs
	print 'objects: ', objects
	print 'quanitity: ', quantity
	print 'unit: ', unit
	for i in range(len(verbs)):
		take_action(verbs[i], objects[i], quantity[i], unit[i])


def take_action(verb, object, quantity, unit):
	print 'Calling ', verb, ' with arguments: ', object, ', ', text2int(quantity.text), unit


parse_phrase('Move the circle down fifty pixels.')
