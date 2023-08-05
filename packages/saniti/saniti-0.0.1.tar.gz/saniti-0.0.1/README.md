## Saniti

*Sanitise lists of text documents quickly, easily and whilst maintaining your sanity*

###Usage:

#### As a function-ish

'''
	original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]

	text = saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"])

	print(text.text)
'''

#### As a class
'''
	sani1 = saniti()
	text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"])
	print(text)
'''
