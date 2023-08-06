# -*- coding: utf-8 -*-
#字符串相关函数
import random
import re
def fill_id(id,length):
    '''自动填充id到指定的长度'''
    idLength = len(str(id))
    if idLength>length:
        return str(id)
    else:
        return '0'*(length-idLength) + str(id)

def create_nonce_str(length=32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)


def replace_punctuation(content,replace_str=''):
    """
    去除标点符号
    :param content: 去除所有的标点符号
    :param replace_str : 替换字符串，默认为空
    """
    result = re.sub(ur"[^-_a-zA-Z0-9\u4e00-\u9fa5]+",replace_str,content)
    return result


if __name__ == '__main__':
    result=replace_punctuation(u'人生若只如初见，何事秋风悲画扇',' ')
    print(result)