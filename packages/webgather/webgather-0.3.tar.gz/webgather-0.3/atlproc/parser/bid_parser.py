# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2016-06-29 10:22:20
# @Last Modified by:   mithril
# @Last Modified time: 2016-07-28 15:57:55


import re
from datetime import datetime, timedelta
import dateparser

time_pt = ur'\d{1,2}(时|:)?\d{1,2}(分)?'

date_pt = ur'\d{4}(年|-|/|\.)\d{1,2}(月|-|/|\.)\d{1,2}(日|\s)'

datetime_pt = ur'\d{4}(年|-|/|\.)\d{1,2}(月|-|/|\.)\d{1,2}(日|\s)?(\d{1,2}(时|:)?\d{1,2}(分)?)?'

datetime_board_pt = ur'(\d{4}(年|-|/|\.))?\d{1,2}(月|-|/|\.)\d{1,2}(日|\s)?(\d{1,2}(时|:)?\d{1,2}(分)?)?'

datetime_extract_pt = ur'(?P<date>(?P<year>\d{4})(年|-|/|\.)(?P<month>\d{1,2})(月|-|/|\.)(?P<day>\d{1,2})(日|\s)?)(?P<time>(?P<hour>\d{1,2})(时|:)?(?P<minute>\d{1,2})(分)?)?'

datetime_board_extract_pt = ur'((?P<date>(?P<year>\d{4})(年|-|/|\.))?(?P<month>\d{1,2})(月|-|/|\.)(?P<day>\d{1,2})(日|\s)?)(?P<time>(?P<hour>\d{1,2})(时|:)?(?P<minute>\d{1,2})(分)?)?'


mdHM_pt = ur'\d{1,2}(月|-|/|\.)\d{1,2}(日|\s)?(\d{1,2}(时|:)?\d{1,2}(分)?)?'

buy_date_pt = ur'(?P<start_date>%s)[^至]{0,20}?至(?P<end_date>%s)' % (datetime_pt, datetime_pt)


# http://www.guodian.org/zbs_614822.html
# 2016年7月14至7月20日17:00时止。
buy_date_pt_2 = ur'(?P<start_date>%s)[^至]{0,20}?至(?P<end_date>%s)' % (datetime_pt, mdHM_pt)


# 不能不匹配年， 会出现下面的问题
# 3.5 2016年6月30日
# 4.1 7月19日
# buy_date_board_pt = ur'(?P<start_date>%s)[^至]{0,20}?至(?P<end_date>%s)' %
# (datetime_board_pt, datetime_board_pt)

buy_date_pt_3 = ur'(售卖|购买|发售|文件获取|文件的获取)\D{0,30}(?P<date>%s)' % datetime_pt

# 购买截止时间

limit_date_pt = ur'(截止|截标)\D{0,40}(?P<date>%s)' % datetime_pt

open_date_pt = ur'开标\D{0,40}(?P<date>%s)' % datetime_pt

publish_date_pt = ur'(发布时间|发布日期|公告时间|公告日期)\D{0,20}(?P<date>%s)' % datetime_pt


# BidInfo = namedtuple('BidInfo', ['name', 'buy_start_date', 'buy_end_date', 'limit_date', 'open_date'])


def cast_int(s, default=0):
    try:
        return int(s)
    except:
        return default


def fmt_datetime(d):
    return d.strftime('%Y-%m-%d %H:%M') if d else None


def parse_date(d, default=None):
    if not d:
        return

    dt = None

    try:
        dt = dateparser.parse(d)
    except Exception as e:
        print u'dateparser.parse %s error' % d

    if not dt:
        try:
            m = re.search(datetime_extract_pt, d)
            date = m.group('date')
            time = m.group('time')

            year = cast_int(m.group('year'))
            month = cast_int(m.group('month'))
            day = cast_int(m.group('day'))
            hour = cast_int(m.group('hour'))
            minute = cast_int(m.group('minute'))

            if hour == 24:
                hour = 0

            if date:
                dt = datetime(year, month, day, hour, minute)

        except Exception as e:
            print u'parse date:%s error' % d

    if not dt and default == 'original':
        dt = d

    return dt


def check_max_interval(start_date, end_date, max_days=30):
    delta = end_date - start_date
    if delta.days < 0 or delta.days > max_days:
        return False

    return True


def validate_buy_date(start_date, end_date):
    if start_date and end_date:
        return check_max_interval(start_date, end_date)
    elif start_date or end_date:
        # alow just one value
        return True
    else:
        return False


def get_buy_date(text):
    start_date = None
    end_date = None
    matchs = []
    for m in re.finditer(buy_date_pt, text):
        start_date = parse_date(m.group('start_date'))
        end_date = parse_date(m.group('end_date'))

        if validate_buy_date(start_date, end_date):
            matchs.append([start_date, end_date])

    for m in re.finditer(buy_date_pt_2, text):
        start_date = parse_date(m.group('start_date'))

        em = re.search(datetime_board_extract_pt, m.group('end_date'))
        if em and em.group('year') is None:
            try:
                year = cast_int(em.group('year'), start_date.year)
                month = cast_int(em.group('month'))
                day = cast_int(em.group('day'))
                hour = cast_int(em.group('hour'))
                minute = cast_int(em.group('minute'))
                end_date = datetime(year, month, day, hour, minute)
            except Exception as e:
                print u'board_extract buy_end_date fail: %s' % m.group('end_date')

        if validate_buy_date(start_date, end_date):
            matchs.append([start_date, end_date])

    if len(matchs) == 0:
        m2 = re.search(buy_date_pt_3, text)
        if m2:
            start_date = parse_date(m2.group('date'))
    elif len(matchs) == 1:
        start_date, end_date = matchs[0]
    else:
        now_year = datetime.now().year
        left_matchs = filter(lambda x: x[0].year == now_year, matchs)
        start_date, end_date = left_matchs[-1] if left_matchs else matchs[-1]

    return start_date, end_date


def get_limit_date(text):
    m = re.search(limit_date_pt, text)
    if m:
        return parse_date(m.group('date'))

    return None


def get_open_date(pt, text):
    m = re.search(open_date_pt, text)
    if m:
        return parse_date(m.group('date'))

    return None


def parse_date_by_pt(pt, text, default='original'):
    m = re.search(pt, text)
    if m:
        return parse_date(m.group('date'), default)

    return None


replacements = {
    u'\s': '',
    u'\xa0': '',
    u'\u3000': '',
    u'：': ':'
}

def build_replace_pattern(replacements):
    substrs = sorted(replacements, key=len, reverse=True)
    return re.compile('|'.join(map(re.escape, substrs)))

rep_pt = build_replace_pattern(replacements)


def clean_text(text):
    ''' need  ensure test is utf-8 here '''
    return rep_pt.sub(lambda match: replacements[match.group(0)], text)

# def clean_text(text):
#     s = re.sub(u'\s', '', text).replace(u'\xa0', '').replace(u'\u3000', '')
#     return s


def parse_bidinfo(text):
    s = clean_text(text)
    buy_start_date, buy_end_date = get_buy_date(s)
    limit_date = parse_date_by_pt(limit_date_pt, s)
    open_date = parse_date_by_pt(open_date_pt, s)
    publish_date = parse_date_by_pt(publish_date_pt, s)

    # clean_text would convert 2016-8-4 9:30 to 2016-8-49:30
    # so use original text to have a try
    if buy_start_date and not isinstance(buy_start_date, datetime):
        buy_start_date, _ = get_buy_date(text)
    if buy_end_date and not isinstance(buy_end_date, datetime):
        _, buy_end_date = get_buy_date(text)

    if limit_date and not isinstance(limit_date, datetime):
        limit_date = parse_date_by_pt(limit_date_pt, text)
    if open_date and not isinstance(open_date, datetime):
        open_date = parse_date_by_pt(open_date_pt, text)
    if publish_date and not isinstance(publish_date, datetime):
        publish_date = None

    return {
        'buy_start_date': fmt_datetime(buy_start_date),
        'buy_end_date': fmt_datetime(buy_end_date),
        'limit_date': fmt_datetime(limit_date),
        'open_date': fmt_datetime(open_date),
        'publish_date': fmt_datetime(publish_date),
    }


# class Bid(object):
#     def __init__(self, name, content, buy_start_date=None, buy_end_date=None, limit_date=None, open_date=None):
#         self.name = name
#         self.content = content
#         self.buy_start_date = buy_start_date
#         self.buy_end_date = buy_end_date
#         self.limit_date = limit_date
#         self.open_date = open_date

#     @classmethod
#     def fromhtml(cls, s):
#         s = clean_text(s)
#         buy_start_date, buy_end_date = get_buy_date(s)
#         limit_date = get_limit_date(s)
#         open_date = get_open_date(s)


if __name__ == '__main__':
    # with open('test_clean.txt') as f:
    #     s = f.read()

    # s = s.decode('utf-8')

    s = u'2016年06月30日09时30分'

    # m = re.search(buy_date_pt, s)
    # print m.group('date')

    print parse_date(s)

    for k, v in locals().items():
        if not k.startswith('__'):
            print k, v
