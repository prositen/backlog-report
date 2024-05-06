import aiohttp
from urllib.parse import urlparse

from app.core.config import Config


class Shortcut(object):

    def __init__(self):
        config = Config.get_config()
        self.api_url = config.shortcut_url.rstrip('/')
        self.token = config.shortcut_token
        self.headers = {'Shortcut-Token': f'{self.token}'}

    async def get_url(self, path, query_parameters=None):
        path = path.lstrip('/')
        full_url = f'{self.api_url}/{path}'

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(full_url, params=query_parameters) as resp:
                result = await resp.json()
                return result

    @staticmethod
    def _get_next_page_token(url):
        for kv in (url or '').split('&'):
            if kv.startswith('next='):
                return kv.split('=')[1]
        return None

    async def get_stories(self, state, limit=25):
        path = '/search/stories'
        query_parameters = {'query': f'state:"{state}" -is:archived',
                            'page_size': 25}
        stories = []
        result = await self.get_url(path, query_parameters)
        stories.extend(result['data'])
        if limit < 0:
            limit = result['total']
        while ((len(stories) < limit) and
               (next_token := self._get_next_page_token(result.get('next')))):
            query_parameters['next'] = next_token
            result = await self.get_url(path=path, query_parameters=query_parameters)
            stories.extend(result['data'])
        return stories

    async def get_labels(self):
        path = '/labels'
        query_parameters = {'slim': 'true'}
        return await self.get_url(path, query_parameters)

    async def get_fields(self):
        path = '/custom-fields'
        return await self.get_url(path)
