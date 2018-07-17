import pprint
import datetime
import urllib.parse
import logging
import argparse

from operator import itemgetter
from simple_requests import get_all
from consts import *


def filter_entities(entities, begin_date=None, end_date=None):
    if (begin_date is None) and (end_date is None):
        return entities

    result = []
    for entity in entities:
        created_at = datetime.datetime.strptime(entity['created_at'], DATE_FORMAT_TEMPLATE)
        if (begin_date is not None) and (created_at < begin_date):
            continue
        if (end_date is not None) and (created_at > end_date):
            break
        result.append(entity)
    return result


def get_open_pull_requests(owner, repo, begin_date=None, end_date=None, branch='master'):
    print("Get open pull requests...")
    url = GITHUB_API_CORE + GITHUB_PULL_REQUESTS_TEMPLATE.format(owner=owner,
                                                                 repo=repo)

    params = {'direction': 'asc', 'state': 'open', 'per_page': 100, "base": branch}
    open_pull_requests = get_all(url, params, end_date)

    filtered_open_pull_requests = filter_entities(open_pull_requests, begin_date, end_date)

    print("Open pull requests: %s" % (len(filtered_open_pull_requests)))
    return filtered_open_pull_requests


def get_closed_pull_requests(owner, repo, begin_date=None, end_date=None, branch='master'):
    print("Get closed pull requests...")
    url = GITHUB_API_CORE + GITHUB_PULL_REQUESTS_TEMPLATE.format(owner=owner,
                                                                 repo=repo)

    params = {'direction': 'asc', 'state': 'closed', 'per_page': 100, "base": branch}
    closed_pull_requests = get_all(url, params, end_date)

    filtered_closed_pull_requests = filter_entities(closed_pull_requests, begin_date, end_date)

    print("Closed pull requests: %s" % (len(filtered_closed_pull_requests)))
    return filtered_closed_pull_requests


def get_open_closed_pull_requests(owner, repo, begin_date=None, end_date=None, branch='master'):
    get_open_pull_requests(owner, repo, begin_date, end_date, branch)
    get_closed_pull_requests(owner, repo, begin_date, end_date, branch)


def get_old_pull_requests(owner, repo, begin_date=None, end_date=None, branch='master'):
    today = datetime.datetime.utcnow()

    old_pull_requests = 0
    if ((begin_date is None) and (end_date is None)) or \
            ((end_date is not None) and ((today - end_date).days < OLD_PULL_REQUEST_DAYS)) or \
            ((begin_date is not None) and (today - begin_date).days > OLD_PULL_REQUEST_DAYS):

        open_pull_requests = get_open_pull_requests(owner, repo, begin_date, end_date, branch='master')

        for open_pull_request in open_pull_requests:
            pr_created_at = datetime.datetime.strptime(open_pull_request['created_at'], DATE_FORMAT_TEMPLATE)
            if (today - pr_created_at).days >= OLD_PULL_REQUEST_DAYS:
                old_pull_requests += 1
    else:
        print("All open pull requests out of range [{begin_date}:{end_date}]".format(begin_date=begin_date,
                                                                                     end_date=end_date))

    print("Old open pull requests: {old}".format(old=old_pull_requests))
    return old_pull_requests


def get_contributors(owner, repo):
    print("Get contributors...")
    url = GITHUB_API_CORE + GITHUB_CONTRIBUTORS_TEMPLATE.format(owner=owner,
                                                                repo=repo)
    params = {'direction': 'asc', 'per_page': 100}
    contributors = get_all(url, params)
    print("Total contributors: %s" % (len(contributors)))
    result = []
    for contributor in contributors:
        result.append((contributor['login'], contributor['contributions']))

    result.sort(key=itemgetter(1), reverse=True)
    print("Top 30 contributors:")
    pprint.pprint(result[:30])


def get_open_issues(owner, repo, begin_date=None, end_date=None, branch='master'):
    print("Get open issues...")
    url = GITHUB_API_CORE + GITHUB_ISSUES_TEMPLATE.format(owner=owner,
                                                          repo=repo)
    params = {'direction': 'asc', 'state': 'open', 'per_page': 100, 'base': branch}
    open_issues = get_all(url, params, end_date)

    filtered_open_issues = filter_entities(open_issues, begin_date, end_date)

    print("Open issues: %s" % (len(filtered_open_issues)))
    return filtered_open_issues


def get_closed_issues(owner, repo, begin_date=None, end_date=None, branch='master'):
    print("Get closed issues...")
    url = GITHUB_API_CORE + GITHUB_ISSUES_TEMPLATE.format(owner=owner,
                                                          repo=repo)
    params = {'direction': 'asc', 'state': 'closed', 'per_page': 100, 'base': branch}
    closed_issues = get_all(url, params, end_date)

    filtered_closed_issues = filter_entities(closed_issues, begin_date, end_date)

    print("Closed issues: %s" % (len(filtered_closed_issues)))
    return filtered_closed_issues


def get_open_closed_issues(owner, repo, begin_date=None, end_date=None, branch='master'):
    get_open_issues(owner, repo, begin_date, end_date, branch)
    get_closed_issues(owner, repo, begin_date, end_date, branch)


def get_old_issues(owner, repo, begin_date=None, end_date=None, branch='master'):
    today = datetime.datetime.utcnow()

    old_issues = 0
    if ((begin_date is None) and (end_date is None)) or \
            ((end_date is not None) and ((today - end_date).days < OLD_ISSUE_DAYS)) or \
            ((begin_date is not None) and (today - begin_date).days > OLD_ISSUE_DAYS):

        open_issues = get_open_issues(owner, repo, begin_date, end_date, branch)
        for open_issue in open_issues:
            created_at = datetime.datetime.strptime(open_issue['created_at'], DATE_FORMAT_TEMPLATE)
            if (today - created_at).days >= OLD_PULL_REQUEST_DAYS:
                old_issues += 1
    else:
        print("All open issues out of range [{begin_date}:{end_date}]".format(begin_date=begin_date,
                                                                              end_date=end_date))

    print("Old open issues: {old}".format(old=old_issues))
    return old_issues


def validate_datetime(value):
    try:
        return datetime.datetime.strptime(value, DATE_FORMAT_TEMPLATE)
    except ValueError:
        msg = "Not a valid date: '%s'" % (value)
        raise argparse.ArgumentTypeError(msg)


def validate_url(value):
    splitted_url = urllib.parse.urlsplit(value)
    splitted_path = splitted_url.path.split('/')
    if len(splitted_path) != 3:
        msg = "Unknown url format: '%s'. Expected: https://github.com/<owner>/<repo>" % (value)
        raise argparse.ArgumentTypeError(msg)

    return splitted_path[1], splitted_path[2]


if __name__ == '__main__':
    logging.basicConfig(filename='sga.log', filemode='w', level=logging.INFO,
                        format="%(asctime)s[%(levelname)s]: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                        help="Analyzing url",
                        type=validate_url)
    parser.add_argument("--begin_date",
                        help="Analyzing begin date - format 'YYYY-MM-DDThh:mm:ssZ'",
                        type=validate_datetime)
    parser.add_argument("--end_date",
                        help="Analyzing end date - format 'YYYY-MM-DDThh:mm:ssZ'",
                        type=validate_datetime)
    parser.add_argument("--branch",
                        help="Analyzing branch (default 'master')",
                        type=str,
                        default='master')

    args = parser.parse_args()
    owner, repo = args.url
    begin_date = args.begin_date
    end_date = args.end_date
    branch = args.branch

    if (begin_date is not None) and (end_date is not None) and (begin_date > end_date):
        begin_date, end_date = end_date, begin_date

    print("Analize started for:")
    print("\towner: " + owner)
    print("\trepo: " + repo)
    print("\tbegin_date: " + str(begin_date))
    print("\tend_date: " + str(end_date))
    print("\tbranch: " + branch)

    get_contributors(owner, repo)
    get_open_closed_pull_requests(owner, repo, begin_date=begin_date, end_date=end_date, branch=branch)
    get_old_pull_requests(owner, repo, begin_date=begin_date, end_date=end_date, branch=branch)
    get_open_closed_issues(owner, repo, begin_date=begin_date, end_date=end_date, branch=branch)
    get_old_issues(owner, repo, begin_date=begin_date, end_date=end_date, branch=branch)
