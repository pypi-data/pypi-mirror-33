import json
import os
from issueline.constants import ISSUE_DIRECTORY
from issueline.Issue import Issue


class IssueManager(object):

    def __init__(self, directory):
        self.directory = directory

        if not os.path.isdir(ISSUE_DIRECTORY):
            os.makedirs(ISSUE_DIRECTORY)

    def get_data(self, name):
        contents = None

        data_path = os.path.join(self.directory, ISSUE_DIRECTORY, name)\
            + '.json'

        if os.path.isfile(data_path):
            with open(data_path) as _file:
                contents = _file.read()
            _file.close()

        return json.loads(contents) if contents else []

    def write_data(self, name, data):
        data_path = os.path.join(self.directory, ISSUE_DIRECTORY, name)\
            + '.json'

        with open(data_path, 'w+') as _file:
            _file.write(json.dumps(data, default=str))
        _file.close()

        return self.get_data(name)

    def get_issues(self):
        return [Issue(**issue) for issue in self.get_data('issues')]

    def query(self, query, single=False):
        issues = []

        for issue in self.get_issues():
            _issue = issue.export()

            for k, v in query.items():
                if k in _issue:
                    if _issue[k] == v:
                        if single:
                            return issue
                        else:
                            issues.append(issue)

        return issues

    def update_issue(self, id, update):
        data = self.get_data('issues')

        for i, issue in enumerate(data):
            if issue['id'] == id:
                for k, v in update.items():
                    issue[k] = v

                data[i] = issue

        return self.write_data('issues', data)

    def report_issue(self, kind, title, description, author):
        existing_data = self.get_data('issues')

        issue = Issue(
            kind=kind,
            title=title,
            description=description,
            author=author
        )

        if self.query({'id': issue.id}, True):
            return False

        existing_data.append(issue.export())

        self.write_data('issues', existing_data)

        return issue
