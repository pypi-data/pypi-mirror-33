import json
import requests


def meaning(keyword=''):
    if keyword == '':
        return -1
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_idiom.php'
    data = {}
    data['keyword'] = keyword
    data['op'] = 'meaning'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        return {
            '名称':res['name'],
            '读音':res['pronounce'],
            '解释':res['content'],
            '出自':res['comefrom'],
            '反义词':','.join(res['thesaurus']) if len(res['thesaurus'])>1 else ''.join(res['thesaurus']),
            '近义词':','.join(res['antonym']) if len(res['antonym'])>1 else ''.join(res['antonym']),
            '举例':res['example'].replace(' ','')
        }
    else:
        return -1

def meaning1(keyword=''):
    if keyword == '':
        return -1
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_idiom.php'
    data = {}
    data['keyword'] = keyword
    data['op'] = 'meaning'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        return {
            'name':res['name'],
            'duyin':res['pronounce'],
            'jieshi':res['content'],
            'chuzi':res['comefrom'],
            'fanyici':','.join(res['thesaurus']) if len(res['thesaurus'])>1 else ''.join(res['thesaurus']),
            'jinyici':','.join(res['antonym']) if len(res['antonym'])>1 else ''.join(res['antonym']),
            'lizi':res['example'].replace(' ','')
        }
    else:
        return 0

def search(keyword=''):
    if keyword == '':
        return -1
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_idiom.php'
    data = {}
    data['keyword'] = keyword
    data['op'] = 'search'
    r = requests.post(url, data=data)
    res = r.json()['result']
    if res:
        search_info = []
        for item in res:
            search_info.append(item['name'])
        return search_info
    else:
        return -1

def main():
    print(meaning('叶公好龙'))
    print(meaning1('叶公好龙'))
    print(search('一'))


if __name__ == '__main__':
    main()
