import json
import requests

def xingzuos():
    '''获取所有的星座'''
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_xingzuo.php'
    data = {}
    data['op'] = 'xingzuos'
    r = requests.post(url,data)
    res = r.json()
    if res['result']:
        return res['result']
    else:
        return -1


def _get_xingzuo_fortune(name='',today=False,tomorrow=False,week=False,month=False,year=False):
    if name == '':
        return -1
    if len(name) == 2:
        name += '座'
    xingzuo_dict = {
        '白羊座':1,
        '金牛座':2,
        '双子座':3,
        '巨蟹座':4,
        '狮子座':5,
        '处女座':6,
        '天秤座':7,
        '天蝎座':8,
        '射手座':9,
        '摩羯座':10,
        '水瓶座':11,
        '双鱼座':12
    }
    if name not in xingzuo_dict:
        return -1
    data = {}
    data['op'] = 'xingzuo_fortune'
    data['astroid'] = xingzuo_dict[name]
    url='https://www.yuanfudao.com/tutor-ybc-course-api/jisu_xingzuo.php'
    r = requests.post(url,data)
    print(r)
    res = r.json()
    print(res)
    res = res['result']
    print(res)
    if today:
        res_today = res['today']
        if 'summary' in res_today:
            del res_today['summary']
        if 'money' in res_today:
            del res_today['money']
        if 'career' in res_today:
            del res_today['career']
        if 'love' in res_today:
            del res_today['love']
        if 'health' in res_today:
            del res_today['health']
        return res_today
    elif tomorrow:
        res_tomorrow = res['tomorrow']
        if 'summary' in res_tomorrow:
            del res_tomorrow['summary']
        if 'money' in res_tomorrow:
            del res_tomorrow['money']
        if 'career' in res_tomorrow:
            del res_tomorrow['career']
        if 'love' in res_tomorrow:
            del res_tomorrow['love']
        if 'health' in res_tomorrow:
            del res_tomorrow['health']
        return res_tomorrow
    elif week:
        return res['week']
    elif month:
        return res['month']
    elif year:
        return res['year']
    else:
        return res

'''
{'date': '2017-12-29', 'presummary': '很渴望感情，喜欢去追求外地的异性朋友，已婚者，非常关爱对方，财运容易暗中很好。', 'star': '狮子座', 'color': '红色', 'number': '5'}
'''
def today_fortune(name=''):
    res = _get_xingzuo_fortune(name,today=True)

    return res


'''
{'date': '2017-12-30', 'presummary': '今天的双子会特别有慧根，对宗教玄学方面的东西会比较敏感。同时，也是比较忙碌的一天，工作运也很不错。', 'star': '摩羯座', 'color': '橙色', 'number': '1'}
'''
def tomorrow_fortune(name=''):
    res = _get_xingzuo_fortune(name,tomorrow=True)
    return res


'''
{'date': '2017-12-24~12-30', 'money': '财运一般。会有一些社会应酬。', 'career': '非常努力的工作，只为了能有更好的内部提升的机会。', 'love': '有伴的，想结婚了。但是在结婚的问题，容易跟恋人意见不合。', 'health': '注意身材，容易发胖&nbsp;。', 'job': '求职的关键是所求工作可以证明自己的能力，让恋人对你印像改观。'}
'''
def week_fortune(name=''):
    res = _get_xingzuo_fortune(name,week=True)
    return res


'''
{'date': '2017-12', 'summary': '感情运佳。伴侣关系发展良好，喜欢陪伴对方、和对方聊天，责任感增强。合作关系也有长足的进步。工作运上升，做事更有效率，与同事、下属关系良好。水星逆行期间，思考表达会受到影响，电子数据注意备份，出行注意交通安全。', 'money': '正财运不错，随工作成绩的提升而增加。', 'career': '合作关系对你的工作有助力，做事更注重结果，之前处理不好的问题得到解决，但是沟通要多加注意，受水星逆行影响，可能会出现信息延迟的现象，避免说话太多随意。', 'love': '有伴的人，感情发展不错，注意沟通上的误会。单身的人，有机会在聚会活动中认识到喜欢的人或者是经由长辈介绍认识。', 'health': '双子女们需要注意妇科问题，避免工作过度劳累。'}
'''

def month_fortune(name=''):
    res = _get_xingzuo_fortune(name,month=True)
    return res




def year_fortune(name=''):
    res = _get_xingzuo_fortune(name,year=True)
    return res


def fortune_info(name=''):
    res = _get_xingzuo_fortune(name)
    return res

if __name__ == '__main__':
    print(xingzuos())
    print("*"*10)
    print(fortune_info('双子座'))
