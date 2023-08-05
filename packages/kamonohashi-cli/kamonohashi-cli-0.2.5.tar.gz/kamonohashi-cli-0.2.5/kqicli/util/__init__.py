
import codecs


def cp65001(name):
    # for Windows encode
    # see https://qiita.com/fetaro/items/448407a6964d307e8840
    if name.lower() == 'cp65001':
        return codecs.lookup('utf-8')


codecs.register(cp65001)
