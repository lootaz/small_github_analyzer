import urllib.request
import urllib.error
import urllib.parse
import json
import re
import datetime
import logging as log
from consts import *


class GetResponse:
    def __init__(self, success, info=None, content=None):
        self.success = success
        self.info = info
        self.content = content


def get_rate_limits(proxy=None):
    url = GITHUB_API_CORE + GITHUB_RATE_LIMITS
    get_response = get(url, proxy=proxy)

    limit_remaining = 0
    if get_response.success:
        limit_remaining = get_response.info.get('X-RateLimit-Remaining', 0)

    log.info("Remaining limits for '{proxy}' is '{amount}'".format(proxy=proxy, amount=limit_remaining))
    return int(limit_remaining)


def get_next_proxy():
    limit_remaining = get_rate_limits()
    if limit_remaining > 0:
        return None

    if len(PROXY_LIMITS_LIST) > 0:
        for proxy in PROXY_LIMITS_LIST.keys():
            limit_remaining = get_rate_limits(proxy)
            PROXY_LIMITS_LIST[proxy] = limit_remaining
            if limit_remaining > 0:
                return proxy

    return None


def get_next_link(link_header):
    next_link = None
    if not link_header is None:
        links_str = link_header.split(',')
        for link_str in links_str:
            if 'next' in link_str:
                next_link = re.search(LINK_PATTERN, link_str).group(1)
                break
    return next_link


def get(url, proxy=None):
    content = []
    info = {}
    try:
        log.info("Request '{url}' (proxy '{proxy}')".format(url=url, proxy=proxy))

        request = urllib.request.Request(url)
        opener = urllib.request.build_opener()
        if proxy is not None:
            proxies = {
                "http": proxy,
                "https": proxy
            }
            opener.add_handler(urllib.request.ProxyHandler(proxies))
        else:
            if len(OAUTH_TOKEN) > 0:
                request.add_header("Authorization", "token " + OAUTH_TOKEN)

        with opener.open(request) as response:
            info = response.info()
            content = json.load(response)
            log.info("Received '%s' entities" % (len(content)))
    except Exception as ex:
        log.error(ex)
        return GetResponse(False)

    return GetResponse(True, info, content)


def filter_by_end_date(entities, end_date):
    result = []
    for entity in entities:
        created_at = datetime.datetime.strptime(entity['created_at'], DATE_FORMAT_TEMPLATE)
        if created_at < end_date:
            result.append(entity)
        else:
            break
    return result


def get_all(url, params=None, end_date=None):
    result_data = []
    if isinstance(params, dict):
        url += "?%s" % urllib.parse.urlencode(params)

    next_link = url
    while not next_link is None:
        proxy = get_next_proxy()

        get_response = get(next_link, proxy=proxy)
        if not get_response.success:
            PROXY_LIMITS_LIST.pop(proxy, None)
            log.error("Wrong proxy '%s' excluded from list" % proxy)
            continue

        info = get_response.info
        content = get_response.content

        if end_date is not None:
            filtered_content = filter_by_end_date(content, end_date)
            result_data += filtered_content
            if len(content) != len(filtered_content):
                break
        else:
            result_data += content
        next_link = get_next_link(info.get('Link', None))

    return result_data
