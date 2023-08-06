from bs4 import BeautifulSoup
import requests
import re
from .error_handler import *
from .history import history
from cmd import Cmd
import yaml
import os

# add path
rootpath = os.path.abspath('..')

# define dictionary process
class youdao_dict(object):
    # initiate basic settings
    def __init__(self, word, deepth=5):
        self.deepth = deepth
        self.word = word
        url = requests.get(
            'http://www.youdao.com/w/eng/{}/#keyfrom=dict2.index'.format(word))
        url.encoding = 'utf-8'
        html = url.text
        self.soup = BeautifulSoup(html, 'lxml')

    # capture webpage
    def website_capture(self):
        self.translation = self.soup.find(
            name='div', attrs={'class': 'trans-container'})
        self.wordgroup = self.soup.find_all(
            name='p', attrs={'class': 'wordGroup'})
        self.example = self.soup.find(
            name='div', attrs={'id': 'examplesToggle'})

    # analyze and display search result
    def display(self):
        count = 0
        wordgroup_list = []
        example_list = []

        print('=============\n' + self.word + '\n=============')

        # print all Chinese explanation
        self.translation = self.translation.ul.get_text()
        print('{}'.format(self.translation), end='\r')
        print('-----------------------------------------------')

        # print the first n wordgroups, n equals to self.deepth
        print('词组:')
        for i in self.wordgroup:
            wordgroup = i.a.get_text()
            meaning = re.sub(r'[a-zA-Z]*(\s)', '', i.get_text())
            wordgroup_list.append(('{0:25}'.format(wordgroup) + '|' + meaning))
            try:
                print(wordgroup_list[-1])
            except UnicodeEncodeError:
                pass
            count += 1
            if count >= self.deepth:
                count = 0
                break
        print('-----------------------------------------------')

        # print the first 3 example sentence
        print('例句:')
        example_div = self.example.ul.find_all(name='li')
        for i in example_div:
            example = re.sub(r'[0-9a-z]*.[0-9a-z]*.com|《[\u4e00-\u9fa5]*》', '', i.get_text())
            example = re.sub(r'\n', '', example, 3)
            example = example.replace('\n', '/', 1)
            example = re.sub(r'\n', '', example)
            example = re.split('/', example)
            example_list.append(('| ' + example[0] + '\n' + example[1]))
            print(example_list[-1])

        # return translations, wordgroups and example sencences
        return self.translation, wordgroup_list, example_list

# define CLI part
class Client(Cmd):
    """docstring for Cli"""
    prompt = 'yuci> '
    intro = '''
    ===============================\n
    ==Welcome to yuci-dictionary!==\n
    ==========version 0.1.5========\n'''

    # pre settings, loading configs from config.yml
    def __init__(self):
        Cmd.__init__(self)
        # get config from config.yml
        with open(rootpath + "\\dictionary\\data\\config.yml", 'r') as file:
            self.config = yaml.load(file)
            self.deepth = int(self.config['search_setting']['deepth'])
            self.history = bool(self.config['search_setting']['history'])

    # SETTING
    def do_setting(self, arg):
        # transform new changes from import.
        if arg != '':
            Input_check(arg, '201')
            arg = re.sub(r'([a-z]*)=|\s*', '', arg)
            changes = arg.split(',')
            deepth = changes[0]
            history = changes[1]

        # display previous setting
        settings_warning = '''
        Be careful with the settings below.
        If you don\'t know what are their usages,
        just keep it default.\n
        '''
        print('|settings|\n' + settings_warning)
        for i in self.config:
            print(i)
            for m in self.config[i]:
                print('  ' + m + ':' + self.config[i][m])

        if arg != '':
            if history is not True or deepth != 5:
                changes = {'search_setting': {'deepth': deepth, 'history': history}}
                print('PLEACE CONFIRM:\nNew changes: deepth:{0}, history:{1}\n'.format(deepth, history))
                confirm = input('ARE YOU SURE TO APPLY CHANGES?(Y/N):')
                if confirm == 'Y':
                    self.config = changes
                    with open(rootpath + "\\dictionary\\data\\config.yml", 'w') as file:
                        yaml.dump(self.config, file)
                    print('Restart the program to active the changes.')
                elif confirm == 'N':
                    pass

    def do_search(self, arg):
        # Check error in input
        Input_check(arg, '101')

        # web search & show result
        self.obj = youdao_dict(word=arg, deepth=self.deepth)
        self.obj.website_capture()
        translation, wordgroup, example = self.obj.display()

        # history recording
        if self.history is True:
            history(arg, self.deepth, self.history, translation, wordgroup, example)

    def do_version(self):
        print('yuci-dictionary version 0.1.4')

    def do_exit(self, arg):
        print('BYE!')
        return True

    # help files
    def help_search(self):
        print('Describtion: Search for a word\nKeyword: word\nKeyword_type: str\nUsage: search word')

    def help_s(self):
        print('Describtion: Shortcut for search')

    def help_setting(self):
        print('Describtion: Change setting\nKeyword: deepth, history\nkeyword_type: int, bool\nTip: The order must not be changed, every keyword must have a value.\nUsage: setting deepth,history')

    def help_exit(self):
        print('Describtion: Exit the program\nUsage: exit')

    def help_version(self):
        print('Describtion: Check program version\nUsage: version')

    # CLI setting
    def default(self, line):
        print('No command find.')

    def emptyline(self):
        pass

    def precmd(self, line):
        print('-----------------------------')
        return Cmd.precmd(self, line)

    # shortcut setting
    do_s = do_search

def main():
    Client().cmdloop()

if __name__ == '__main__':
    main()
