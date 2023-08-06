import asyncio
import logging

import attr

from impetuous.ext import API, SECRET, LudicrousConditions, Submission

logger = logging.getLogger(__name__)


@attr.s(frozen=True)
class Jira(API):

    IDENTIFIER = 'jira'
    pattern = attr.ib()
    server = attr.ib()
    basic_auth = attr.ib(metadata={SECRET: True},
                         convert=lambda value: tuple(value.split(':', 1)))

    def discover(self, impetuous, *entries):
        for entry in entries:
            for issuekey in self.discover_by_pattern(entry, self.pattern):
                yield entry, Submission(issuekey, {
                    'started': entry.start.strftime('%Y-%m-%dT%H:%M:%S.000%z'),
                    'timeSpentSeconds': entry.duration_in_minutes * 60,
                    'comment': entry.comment,
                })

    async def agent(self, impetuous):
        return JiraHttpAgent(self)


class JiraHttpAgent(object):

    def __init__(self, api):
        import aiohttp
        self.api = api
        self.sess = aiohttp.ClientSession(auth=aiohttp.BasicAuth(*api.basic_auth))
        self.close = self.sess.close

    async def submit(self, sub):
        import aiohttp
        where = self.api.server + '/rest/api/2/issue/{}/worklog'.format(sub.key)
        resp = await self.sess.post(where, json=sub.data, params={'notifyUsers': 'false'})
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise LudicrousConditions(e, "While submitting to {}: {}".format(resp.request_info.url, await resp.text()))
        else:
            return await resp.json()
