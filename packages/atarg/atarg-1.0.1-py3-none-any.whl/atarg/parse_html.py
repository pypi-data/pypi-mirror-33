from typing import List

import requests
from bs4 import BeautifulSoup


def fetch_inputs_and_outputs(
        url: str,
        contest: str,
        contest_no: int) -> List[str]:
    """
    Atcoderの設問ページから入力と出力を取ってくる

    Parameters
    ----------
    url : str
        設問ページのURL
    contest : str
        コンテスト名. ABC, ARC or AGC
    contest_no : int
        コンテンストの番号

    Returns
    ----------
    inputs_and_output : List[str]
        インプットとアウトプットが交互に並んだリスト
    """
    def get_text(html):
        """
        HTMLタグ中からテキストを取り出す

        Parameters
        ----------
        html
            BeautifulSoupで定義されたResultSet

        Returns
        ----------
        lst
            取り出されたテキスト文字列のリスト
        """
        return list(map(lambda tag: tag.get_text().strip(), html))

    def split_half(lst):
        """
        リストの前半分を取り出す

        Parameters
        ----------
        lst
            半分に分けたいリスト

        Returns
        ----------
        lst_half
            引数で受け取ったリストの前半分
        """
        return lst[:int(len(lst)/2)]

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pre_list = soup.find_all('pre')
    if contest == 'ABC':
        if 1 <= contest_no <= 41:
            return get_text(pre_list[1:])
        else:
            return split_half(get_text(pre_list))[1:]
    elif contest == 'ARC':
        if 1 <= contest_no <= 57:
            return get_text(pre_list[1:])
        else:
            return split_half(get_text(pre_list))[1:]
    elif contest == 'AGC':
        return split_half(get_text(pre_list))[1:]


def translate_task(contest: str, contest_no: int, task: str) -> str:
    """
    Atcoderは第N回目コンテストのNの値によって、
    URLに含まれるタスク名がアルファベット(a, b, c, d)表される場合と
    数字(1, 2, 3, 4)で表される場合がある
    数字だった場合は、タスク名(A, B, C, D)をアルファベットの小文字に変換、
    アルファベットだった場合は小文字に変換する

    Parameters
    ----------
    contest : str
        コンテスト名. ABC, ARC or AGC
    contest_no : int
        コンテンストの番号
    task : str
        タスク名. A, B, C or D

    Returns
    ----------
    task
        タスク名(1, 2, 3, 4 または a, b, c, d)
    """
    translator = {'A': '1', 'B': '2', 'C': '3', 'D': '4'}
    if contest == 'ABC':
        if 1 <= contest_no <= 19:
            return translator[task]
        else:
            return task.lower()
    elif contest == 'ARC':
        if 1 <= contest_no <= 34:
            return translator[task]
        else:
            return task.lower()
    else:
        return task.lower()


def compose_url(contest: str, contest_no: int, task: str) -> str:
    """
    与えられたコンテスト名、コンテスト番号、タスク名から
    正しいURLを生成する

    Parameters
    ----------
    contest : str
        コンテスト名. ABC, ARC or AGC
    contest_no : int
        コンテンストの番号
    task : str
        タスク名. A, B, C or D

    Returns
    ----------
    url
        対応する問題のURL
    """
    host = 'https://beta.atcoder.jp/'
    return host + 'contests/' + contest.lower()\
                + '{:03d}'.format(contest_no)\
                + '/tasks/' + contest.lower()\
                + '{:03d}'.format(contest_no)\
                + '_' + task
