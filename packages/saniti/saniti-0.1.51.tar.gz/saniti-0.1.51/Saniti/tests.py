import saniti



original_text = ["I like to moves it, move its", "I likeing to move it!", "the of"]
text = saniti.saniti(original_text, ["token", "destop", "depunct", "unempty", "stem", "out_corp_dict"]) #sanitise the text while initalising the class
print(text.text)
