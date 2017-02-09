print('Loading imports...')

import EntityTrainer as Et
from EntityTrainer import nlp

print('Imports loaded')
print

Et.train('custom_dict_files/Shapes.txt', 'SHAPE')
Et.train('custom_dict_files/Colors.txt', 'COLOR')


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
    # Layout of adjective is as follows
    # shape_one: [ [colors] [other] ]
    adjectives = []
    verbs = []
    quantity = []
    for ent in Et.match(doc):
        print(ent.label_, ent.text)
        if ent.label_ == u'QUANTITY':
            quantity.append(ent.text.lower())
        elif ent.label_ == u'SHAPE':
            objects.append(ent.text.lower())
        elif ent.label_ == u'COLOR':
            print ent.text.lower()
    for np in doc.noun_chunks:
        found_shape = False
        if np.root.tag_ == 'PRP':
            if len(objects) > 0:  # If the preposition is referring to a previous object...
                objects.append(''.join(objects[-1:]))
                adjectives.append(adjectives[-1:][0])
            else:
                print ('ERROR: Unable to find object of prepositional phrase.')
                return
        for word in np:
            if word.text.lower() in objects:
                found_shape = True
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
            verbs.append(np.root.head.text.lower())
    print 'verbs: ', verbs
    print 'objects: ', objects
    print 'descriptors: ', adjectives
    print 'quantity: ', quantity
    for i in range(len(verbs)):
        take_action(verbs[i], objects[i], adjectives[i], quantity[i])


def take_action(verb, obj, desc, quantity):
    print 'Calling ', verb, ' with arguments: ', desc, ' -> ', obj, ', ', text2int(''.join(quantity.split(" ")[:-1])), ''.join(quantity.split(" ")[-1:])


parse_phrase('Move the small blue circle down fifty pixels, then move it down by twenty pixels.')
