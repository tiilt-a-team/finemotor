print('Loading imports...')

import EntityTrainer as Et
from EntityTrainer import nlp

print('Imports loaded')
print

Et.train()


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
    print ("Decoding : ", doc)
    objects = []
    verbs = []
    quantity = []
    unit = []
    # Idea for adjective chaining...
    # First find shape
    # Look for instance of shape name in all NN's
    # Find adjectives within that
    for ent in Et.match(doc):
        print(ent.label_, ent.text)
        if ent.label_ == u'QUANTITY':
            quantity.append(ent.text.lower())
        elif ent.label_ == u'SHAPE':
            objects.append(ent.text.lower())
    for np in doc.noun_chunks:
        if np.root.tag_ == 'PRP':
            if len(objects) > 0:
                objects.append(''.join(objects[-1:]))
            else:
                print ('ERROR: Unable to find object of prepositional phrase.')
                return
        if np.root.head.tag_ != 'IN':
            verbs.append(np.root.head.text.lower())
    print 'verbs: ', verbs
    print 'objects: ', objects
    print 'quantity: ', quantity
    for i in range(len(verbs)):
        take_action(verbs[i], objects[i], quantity[i])


def take_action(verb, obj, quantity):
    print 'Calling ', verb, ' with arguments: ', obj, ', ', text2int(''.join(quantity.split(" ")[:-1])), ''.join(quantity.split(" ")[-1:])


parse_phrase('Move the circle down fifty pixels, then move it down by twenty pixels.')
