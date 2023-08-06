import yaml
import os


# def history recording function
def history(word, deepth, history, trans, wordgroup, example, obj=None):
    # add path
    rootpath = os.path.abspath('..')

    # set a dict object to store arguments
    search_detail = [{
        'word': word,
        'deepth': deepth,
        'history': history,
        'translation': trans,
        'wordgroup': wordgroup,
        'example': example,
    }]
    # save to history.yml, utf-8 encoding
    if obj is None:
        obj = search_detail
    with open(rootpath + '\\dictionary\\data\\history.yml', 'a', encoding='utf-8') as file:
        yaml.dump(obj, file)
