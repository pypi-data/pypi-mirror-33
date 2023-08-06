try:
    import inflect
    use_inflect=True
except ImportError:
    use_inflect=False

if use_inflect:
    inflect_engine=inflect.engine()
def singular_noun(word):
    if use_inflect:
        try:
            return inflect_engine.singular_noun(word)
        except:
            pass
    return word
def singular_verb(word):
    if use_inflect:
        try:
            return inflect_engine.singular_verb(word)
        except:
            pass
    return word

def singularise(word):
    x=singular_noun(word) # Placeholder for if/when I find a package for this
    if type(x).__name__=='str':
        return x
    else:
        return word