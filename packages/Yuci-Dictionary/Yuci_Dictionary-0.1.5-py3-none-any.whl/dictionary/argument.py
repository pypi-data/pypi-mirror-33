import argparse as ap


def get_argument():
    parser = ap.ArgumentParser(description='test')
    parser.add_argument('word', action='store', type=str, help='The word that you want to search.')
    parser.add_argument('-n', '--deepth', action='store', type=int, default=5, help='Number of examples, default 5.')
    parser.add_argument('--history', action='store', type=bool, default=True, help='Search word from history. True for enable, False for disable.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_argument()
