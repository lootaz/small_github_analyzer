GITHUB_API_CORE = "https://api.github.com"
GITHUB_RATE_LIMITS = "/rate_limit"
GITHUB_CONTRIBUTORS_TEMPLATE = "/repos/{owner}/{repo}/contributors"
GITHUB_PULL_REQUESTS_TEMPLATE = "/repos/{owner}/{repo}/pulls"
GITHUB_ISSUES_TEMPLATE = "/repos/{owner}/{repo}/issues"
OLD_PULL_REQUEST_DAYS = 30
OLD_ISSUE_DAYS = 14
LINK_PATTERN = '\<(.+?)\>'
DATE_FORMAT_TEMPLATE = "%Y-%m-%dT%H:%M:%SZ"

PROXY_LIMITS_LIST = {}

# Write your OAUTH_TOKEN here 
OAUTH_TOKEN=''

from proxy import *