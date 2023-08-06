import re
import argparse

# 所有设定错误的集合
errors = {
    '101': 'error:101: Word must be completely letters.',
    '201': 'error:201: New setting must be seperate by comma.'
}

# define new exception
class UnSupport(Exception):
    pass

class InputError(Exception):
    pass

# Input check


def Input_check(word, check):

    error_code = None

    # 判断错误类型
    if check == '101':
        if re.search(r'\d|\W', word) is not None:
            error_code = '101'
    elif check == '201':
        if re.search(r'[\sa-z]*,[\sa-z]*', word) is None:
            error_code = '201'

    # 打印错误信息
    if error_code is not None:
        raise InputError(errors[error_code])

if __name__ == '__main__':
    word = input(':')
    Input_check(word)
