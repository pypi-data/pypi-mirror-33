import nltk
# import gensim
# import pandas
import string
from nltk.corpus import stopwords
from gensim.models.doc2vec import TaggedDocument
from gensim.corpora import Dictionary
"""
TODO
stemming - DONE
lemmatizing - DONE
pos filter
tfidf splitter
w2v theme relevence
w2v weightings
frequency filtering (found more than twice)

RESEARCH
kwargumenrts - ad hoc arguments for theme relevence

"""

class saniti:
	def __init__(self, text = [], pipeline = []):

		#setup

		self.processes = {"token": self.token,
						  "depunct": self.depunct,
						  "unempty": self.unempty,
						  "out_tag_doc": self.out_tag_doc,
						  "out_corp_dict": self.out_corp_dic,
						  "lemma": self.lemma,
						  "destop": self.destop,
						  "stem": self.stem}
		self.pipeline = pipeline
		self.original_text = text


		if text != []:
			self.text = self.process(text, self.pipeline)

	def process(self, text, pipeline):
		self.text = text

		for line in pipeline:
			text = self.processes[line](text)

		return text

	def destop(self, text):
		text = [[word for word in doc if word not in stopwords.words("english")] for doc in text]
		return text

	def token(self, text):
		text = [nltk.word_tokenize(x) for x in text]
		return text

	def depunct(self, text):

		punct = str.maketrans("", "", string.punctuation)
		text = [[s.translate(punct) for s in doc] for doc in text]
		return text

	def unempty(self, text):

		text = [[s for s in doc if s != ""] for doc in text]

		return text

	def lemma(self, text):

		lemmatzer = nltk.WordNetLemmatizer()
		text = [[lemmatzer.lemmatize(w) for w in doc] for doc in text]

		return text

	def stem(self, text):
		stemmer = nltk.stem.PorterStemmer()
		text = [[stemmer.stem(word) for word in doc] for doc in text]

		return text

	def out_corp_dic(self, text):

		dictionary = Dictionary(text)
		corpus = [dictionary.doc2bow(doc) for doc in text]

		return {"dictionary": dictionary, "corpus": corpus}

	def out_tag_doc(self, text, tags = []):

		if tags == []:
			if self.original_text != []:
				tags = self.original_text
			else :
				tags = [" ".join(doc) for doc in text]
		list2 = []
		for xt, xid in zip(text, tags):
			try:
				td = TaggedDocument(xt, [xid])
				list2.append(td)

			except:
				print(f"disambig {x}")

		return(list2)

if __name__ == "__main__":

	original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]

	text = saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"])

	print(text.text)

	sani1 = saniti()
	text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"])
	print(text)




