import argparse

from atarg import parse_html
from atarg import execute


def parse_arguments():
    CONTESTS = ['ABC', 'ARC', 'AGC']
    TASKS = ['A', 'B', 'C', 'D']
    parser = argparse.ArgumentParser(
            prog='atarg',
            description='Testing tool before submit for atcoder',
            epilog='end',
            add_help=True,
            )
    parser.add_argument('contest', choices=CONTESTS, help='Contest name')
    parser.add_argument('number', type=int, help='Contest number')
    parser.add_argument('task', choices=TASKS, help='Task name')
    parser.add_argument(
            'command',
            help='Commands to solve',
            nargs='*')
    return parser.parse_args()


def main():
    args = parse_arguments()
    task = parse_html.translate_task(args.contest, args.number, args.task)
    url = parse_html.compose_url(args.contest, args.number, task)
    inputs_and_outputs = parse_html\
        .fetch_inputs_and_outputs(url, args.contest, args.number)
    inputs = inputs_and_outputs[::2]
    outputs = inputs_and_outputs[1::2]
    execute.run_tests(inputs, outputs, args.command)


if __name__ == '__main__':
    main()
