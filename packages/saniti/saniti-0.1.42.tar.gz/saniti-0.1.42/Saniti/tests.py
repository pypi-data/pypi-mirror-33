import saniti

original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]

# text = saniti(original_text, ["token", "destop", "depunct", "unempty", "posfilter"])


sani1 = saniti.saniti()

text = sani1.process(original_text, ["token", "destop", "depunct", "unempty", "lemma", "out_tag_doc"])
print(text)
# print("worked")