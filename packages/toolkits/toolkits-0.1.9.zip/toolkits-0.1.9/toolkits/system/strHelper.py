# -*- coding: utf-8 -*-
import pprint
import sys
from log4python.Log4python import log
reload(sys)
logger = log("MisUserActionEtl")
sys.setdefaultencoding('utf8')
import esm


def multi_search(search_list, search_string):
    index = esm.Index()
    for item in search_list:
        index.enter(item)
    index.fix()
    ret = index.query(search_string)
    return ret


if __name__ == '__main__':
    search_words = [u"宝马", u"马", u"奔驰", u"保时捷"]
    search_str = u"哎呀，今天在楼下看到了宝马，我老家倒是有养马的，以前的邻居有个奔驰，不对是保时捷，大爷的，都是马"
    pprint.pprint(multi_search(search_words, search_str))


