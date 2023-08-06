import argparse
import os
import sys
from issueline.IssueManager import IssueManager
from issueline.utils import get_current_author
from issueline.constants import STATUS_CLOSED, STATUS_OPEN


parser = argparse.ArgumentParser()
parser.add_argument('report', default=False)


def report_issue():
    if len(sys.argv) == 2:
        print('--kind, --title, --description')
        return

    parser.add_argument('--kind', type=str, help='Type of issue')
    parser.add_argument('--title', type=str, help='Title of issue')
    parser.add_argument('--description', type=str, help='Description of issue')

    args = parser.parse_args()

    manager = IssueManager(os.getcwd())

    issue = manager.report_issue(
        kind=args.kind if args.kind else 'note',
        title=args.title if args.title else 'no title',
        description=args.description if args.description else 'no description',
        author=get_current_author()
    )

    if issue:
        print('Your issue was created with the ID: ' + str(issue.id))
    else:
        print('Could not create issue')


def query_issue():
    if len(sys.argv) == 2:
        print('--id')
        return

    parser.add_argument('--id', type=str, help='ID of issue')

    args = parser.parse_args()

    manager = IssueManager(os.getcwd())

    issue = manager.query({'id': args.id if args.id else None}, True)

    print(issue.export() if issue else 'Could not find issue')


def close_issue():
    if len(sys.argv) == 2:
        print('--id')
        return

    parser.add_argument('--id', type=str, help='ID of issue')

    args = parser.parse_args()

    manager = IssueManager(os.getcwd())

    manager.update_issue(id=args.id, update={'status': STATUS_CLOSED})

    print(args.id + ' was closed')


def open_issue():
    if len(sys.argv) == 2:
        print('--id')
        return

    parser.add_argument('--id', type=str, help='ID of issue')

    args = parser.parse_args()

    manager = IssueManager(os.getcwd())

    manager.update_issue(id=args.id, update={'status': STATUS_OPEN})

    print(args.id + ' was opened')


def show_all_issues():
    manager = IssueManager(os.getcwd())

    for issue in manager.get_issues():
        print(
            '''kind={kind}
title={title}
description={description}
author={author}
id={id}
date={date}
status={status}\n'''.format(**issue.export())
        )


def run():
    command = None

    commands = [
        'report',
        'query',
        'all',
        'close',
        'open'
    ]

    if len(sys.argv) > 1:
        command = sys.argv[1]

    if command not in commands:
        print('Available commands are: ' + ', '.join(commands))

    if command == commands[0]:
        return report_issue()

    if command == commands[1]:
        return query_issue()

    if command == commands[2]:
        return show_all_issues()

    if command == commands[3]:
        return close_issue()

    if command == commands[4]:
        return open_issue()
