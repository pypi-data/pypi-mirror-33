# Saniti

**Sanitise lists of text documents quickly, easily and whilst maintaining your sanity**

The aim was to streamline processing lists of documents into the same outputs into simply specifying the list of texts and defining the sanitization pipeline.

### Usage:

**As a function-ish**


>original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]

>text = saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"]) #sanitise the text while initalising the class

>print(text.text)


**As a class**


>sani1 = saniti() # initialise the santising class

>text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"]) # sanitise the text

>print(text)


## Pipeline Components

* "token" - tokenise texts
* "depunct" - remove punctuation
* "unempty" - remove empty words within documents
* "lemma" - lemmatize text
* "destop" - remove stopwords
* "stem" - stem texts
* "out_tag_doc" - turns the texts into gensim tagged documents for Doc2Vec
* "out_corp_dict" - turns the texts into gensim corpus and dictionary