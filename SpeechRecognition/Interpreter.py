from __future__ import print_function

print('Running Interpreter.py')
print()
print('Loading imports...')

import EntityTrainer as Et
from EntityTrainer import nlp

print('Imports loaded')
print()

Et.train('custom_dict_files/Shapes.txt', 'SHAPE')
Et.train('custom_dict_files/Colors.txt', 'COLOR')
Et.train('custom_dict_files/Directions.txt', 'DIRECTION')


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
    print("Decoding : ", doc)
    objects = []
    possible_objects = []
    # Layout of adjective is as follows
    # shape_one: [ [colors] [other] ]
    adjectives = []
    possible_adjectives = []
    verbs = []
    quantity = []
    possible_quantity = []
    direction = []
    possible_direction = []
    for ent in Et.match(doc):
        # print(ent.label_, ent.text)
        if ent.label_ == u'QUANTITY':
            quantity.append(ent.text.lower())
        elif ent.label_ == u'SHAPE':
            possible_objects.append(ent.text.lower())
        elif ent.label_ == u'DIRECTION':
            possible_direction.append(ent.text.lower())
    for np in doc.noun_chunks:
        appended_direction = False
        found_shape = False
        if np.root.tag_ == 'PRP':
            if len(objects) > 0:  # If the preposition is referring to a previous object...
                print("Preposition time! Objects thus far: ", objects)
                objects.append(''.join(objects[-1:]))
                adjectives.append(adjectives[-1:][0])
            else:
                print('ERROR: Unable to find object of prepositional phrase.')
                return
        for word in np:
            if word.text.lower() in possible_objects:
                found_shape = True
                objects.append(word.text.lower())
        if found_shape:
            temp_list = [[], []]
            for ent in Et.match(doc):
                if ent.label_ == u'COLOR' and ent.text in np.text:
                    temp_list[0].append(ent.text.lower())
            for word in np:
                if word.pos_ == 'ADJ':
                    temp_list[1].append(word.text.lower())
            adjectives.append(temp_list)
        if np.root.head.tag_ != 'IN':
            for child in np.root.head.children:
                if child.text.lower() in possible_direction:
                    direction.append(child.text.lower())
                    appended_direction = True
            verbs.append(np.root.head.text.lower())
            if not appended_direction:
                direction.append(u'')
    print('verbs: ', verbs)
    print('objects: ', objects)
    print('descriptors: ', adjectives)
    print('quantities: ', quantity)
    print('directions: ', direction)
    for i in range(len(verbs)):
        take_action(verbs[i], objects[i], adjectives[i], quantity[i], direction[i])


def take_action(verb, obj, desc, quantity, direction):
    print('Calling ', verb, ' with arguments: ', desc, ' -> ', obj, ', ', text2int(''.join(quantity.split(" ")[:-1])), ''.join(quantity.split(" ")[-1:]), ' ', direction)


parse_phrase('Move the big blue circle down fifty pixels, then move it up by twenty pixels. Enlarge the small yellow square by thirty pixels.')
