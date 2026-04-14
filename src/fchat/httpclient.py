import aiohttp
import re


class HTTPClient():
    
    @staticmethod
    async def get_cookies(url:str, endpoint:str) -> aiohttp.CookieJar:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as s:
            async with s.get(url + endpoint) as response:
                cookies = s.cookie_jar.filter_cookies(url)                    
                return cookies
    
    # todo: type dict
    @staticmethod
    async def get(endpoint:str, headers:dict=None, cookies=None):
        headers = headers or {}
        cookies = cookies or {}
        
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            async with session.get(endpoint) as response:
                assert response.status == 200
                return await response.text()
            
    @staticmethod
    async def get_csrf_token(endpoint:str) -> str:
        html = await HTTPClient.get(endpoint)
        return HTTPClient.__get_regex(html)
    
    @staticmethod
    def __get_regex(text:str, pattern:str='name="csrf-token" content="(.+)"') -> str:
        return re.search(pattern, text).group(1).strip()
    
    # todo: type dict
    @staticmethod
    async def post(endpoint:str, data:dict=None, headers:dict=None, json:bool=True) -> dict | str:
        data = data or {}
        headers = headers or {}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(endpoint, data=data) as response:
                assert response.status == 200
                if json: 
                    return await response.json()
                else:
                    return await response.text()

    # todo: type dict
    @staticmethod
    async def get_login_cookie(endpoint:str, data:dict=None, headers:dict=None) -> aiohttp.CookieJar:
        data = data or {}
        headers = headers or {}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(endpoint, data=data) as response:
                assert response.status == 200
                return response.cookies
