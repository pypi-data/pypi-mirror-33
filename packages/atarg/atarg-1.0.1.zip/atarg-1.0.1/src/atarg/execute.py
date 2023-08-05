import subprocess
import sys
from typing import List


def run_test(
        test_input: str,
        correct_output: str,
        command: List[str]) -> (str, bool):
    """
    テストを実行する

    Parameters
    ----------
    test_input : str
        テストのインプット
    correct_output : str
        テストの期待する正解アウトプット
    command : List[str]
        実行するコマンド

    Returns
    ----------
    user_output : str
        実行したコマンドの出力結果
    result : bool
        実行したコマンドの正誤
    """
    exec_process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
    user_output = exec_process.communicate(test_input.encode())[0].decode()
    user_output = user_output.strip()
    return user_output, user_output == correct_output


def run_tests(
        test_inputs: List[str],
        correct_outputs: List[str],
        command: List[str]) -> bool:
    """
    複数のテストを実行する(実際に実行するのはrun_test)

    Parameters
    ----------
    test_inputs : List[str]
        複数のテストのインプット
    correct_outputs: List[str]
        テストの期待する複数のアウトプット
    command: List[str]
        実行するコマンド

    Returns
    ----------
    result
        複数のテストの実行結果(1つでも不正解だとFalse)
    """
    results = []
    for test_input, correct_output in zip(test_inputs, correct_outputs):
        user_output, result = run_test(test_input, correct_output, command)
        message(test_input, correct_output, user_output, result)
        results.append(result)
    return all(results)


def message(test_input, correct_output, user_output, result):
    """
    Parameters
    ----------
    test_input : str
        テストのインプット
    correct_output : str
        テストの期待する正解アウトプット
    user_output : str
        実行したコマンドの出力結果
    result : bool
        テストの実行結果
    """
    sys.stdout.write('Input       : {}\n'.format(repr(test_input)))
    sys.stdout.write('Your Answer : {}\n'.format(user_output))
    sys.stdout.write('Output      : {}\n'.format(correct_output))
    if result:
        sys.stdout.write('Congraturation!!\n')
    else:
        sys.stdout.write('Uhmmmmm...\n')
    sys.stdout.write('-' * 30 + '\n')
