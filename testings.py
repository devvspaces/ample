abominations = ['\'','\"']

# Convenience functions
def replace_syntax(text):
    new_text = ''
    print(text)
    if text:
        for i in text:
            if i in abominations:
                new_text+='-'
            else:
                new_text+=i
    return new_text

print(replace_syntax('Urpi\''))