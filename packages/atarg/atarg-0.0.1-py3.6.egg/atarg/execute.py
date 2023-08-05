import subprocess
import sys


def run_test(test_input, correct_output, command):
    exec_process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
    user_output = exec_process.communicate(test_input.encode())[0].decode()
    user_output = user_output.strip()
    return user_output, user_output == correct_output


def run_tests(test_inputs, correct_outputs, command):
    results = []
    for test_input, correct_output in zip(test_inputs, correct_outputs):
        user_output, result = run_test(test_input, correct_output, command)
        message(test_input, correct_output, user_output, result)
        results.append(result)
    return all(results)


def message(test_input, correct_output, user_output, result):
    sys.stdout.write('Input       : {}\n'.format(repr(test_input)))
    sys.stdout.write('Your Answer : {}\n'.format(user_output))
    sys.stdout.write('Output      : {}\n'.format(correct_output))
    if result:
        sys.stdout.write('Congraturation!!\n')
    else:
        sys.stdout.write('Uhmmmmm...\n')
    sys.stdout.write('-' * 30 + '\n')
