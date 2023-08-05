# Saniti

**Sanitise lists of text documents quickly, easily and whilst maintaining your sanity**

The aim was to streamline processing lists of documents into the same outputs into simply specifying the list of texts and defining the sanitization pipeline.

### Usage:

**As a function-ish**

```
import saniti
original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]
text = saniti.saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"]) #sanitise the text while initalising the class
print(text.text)

{'dictionary': <gensim.corpora.dictionary.Dictionary object at 0x000002BA9F5FFEF0>, 'corpus': [[(0, 1), (1, 1), (2, 2)], [(0, 1), (1, 1), (2, 1)], []]}
```

**As a class**

```
import saniti
sani1 = saniti.saniti() # initialise the santising class
text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"]) # sanitise the text
print(text)

[TaggedDocument(words=['I', 'like', 'move', 'move'], tags=['I like move move']), TaggedDocument(words=['I', 'likeing', 'move'], tags=['I likeing move']), TaggedDocument(words=[], tags=[''])]
```

## Pipeline Components

* "token" - tokenise texts
* "depunct" - remove punctuation
* "unempty" - remove empty words within documents
* "lemma" - lemmatize text
* "destop" - remove stopwords
* "stem" - stem texts
* "out_tag_doc" - turns the texts into gensim tagged documents for Doc2Vec
* "out_corp_dict" - turns the texts into gensim corpus and dictionary