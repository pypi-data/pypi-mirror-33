from typing import List

import requests
from bs4 import BeautifulSoup


def fetch_inputs_and_outputs(
        url: str,
        contest: str,
        contest_number: int) -> List[str]:
    def get_text(html):
        return list(map(lambda tag: tag.get_text().strip(), html))

    def split_half(lst):
        return lst[:int(len(lst)/2)]

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pre_list = soup.find_all('pre')
    if contest == 'ABC':
        if 1 <= contest_number <= 41:
            return get_text(pre_list[1:])
        else:
            return split_half(get_text(pre_list))[1:]
    elif contest == 'ARC':
        if 1 <= contest_number <= 57:
            return get_text(pre_list[1:])
        else:
            return split_half(get_text(pre_list))[1:]
    elif contest == 'AGC':
        return split_half(get_text(pre_list))[1:]


def translate_task(contest: str, contest_number: int, task: str) -> str:
    translator = {'A': '1', 'B': '2', 'C': '3', 'D': '4'}
    if contest == 'ABC':
        if 1 <= contest_number <= 19:
            return translator[task]
        else:
            return task.lower()
    elif contest == 'ARC':
        if 1 <= contest_number <= 34:
            return translator[task]
        else:
            return task.lower()
    else:
        return task.lower()


def compose_url(contest: str, contest_number: int, task: str) -> str:
    host = 'https://beta.atcoder.jp/'
    return host + 'contests/' + contest.lower()\
                + '{:03d}'.format(contest_number)\
                + '/tasks/' + contest.lower()\
                + '{:03d}'.format(contest_number)\
                + '_' + task
