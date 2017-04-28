import json
from urllib import urlencode

from scrapy import Spider, FormRequest, Request
from scrapy.conf import settings

from ..utils import load_members, save_members


class TfSpider(Spider):
    name = "tf"
    allowed_domains = ('thaifriendly.com',)
    start_urls = ('https://www.thaifriendly.com/',)

    members = {}

    def __init__(self, *args, **kwargs):
        super(TfSpider, self).__init__(*args, **kwargs)
        self.members = load_members()

    def parse(self, response):
        csrf = response.xpath('//form//input[@name="CSRFtoken"]/@value').extract_first()
        yield FormRequest(
            url=response.url,
            formdata={
                'username': settings['TF_USERNAME'],
                'password': settings['TF_PASSWORD'],
                'submit': 'Log in',
                'CSRFtoken': csrf
            },
            callback=self.browse
        )

    def browse(self, response):
        yield Request(
            url='{url}?{params}'.format(
                url=response.url,
                params=urlencode({
                    'c': 's',
                    'gender': 'f',
                    'agefrom': '0',
                    'ageto': str(settings['TF_AGE_TO']),
                    'weightfrom': '0',
                    'weightto': str(settings['TF_WEIGHT_TO']),
                    'heightfrom': '0',
                    'heightto': '0',
                    'country': 'TH',
                    'city': settings['TF_CITY'],
                    'area': '0',
                    'distance': str(settings['TF_DISTANCE']),
                    'education': 'ALL',
                    'ch': 'ALL',
                    'orderby': 'lastactive',
                    'online': 'off',
                    'agerange': 'agerangeoff',
                    'photo': 'off',
                    'page': 'undefined'
                })
            ),
            callback=self.parse_members,
            headers={
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

    def parse_members(self, response):
        """
        {
            'avatar': '/p/2015-06/Kittiya9/ava-726-e5bfe989a40ec7418c5e04923e4babfa-ava.jpg',
            'username': 'Kittiya9',
            'la': '7 hour ',
            'chatid': '0',
            'userid': '824235',
            'age': '30',
            'city': 'Phuket',
            'offline': 1
        }

        Profile: https://www.thaifriendly.com/{username}
        Avatar: https://www.thaifriendly.com/p/...
        """
        js = response.text.split('thumbs: ')[-1]
        js = js.split(' };')[0]
        columns = (
            'avatar', 'username', 'la', 'chatid', 'userid', 'age', 'city',
            'offline', 'onlinechat', 'newmember', 'birthday'
        )
        for key in columns:
            js = js.replace('{}:'.format(key), '"{}":'.format(key))
        rows = json.loads(js)
        rows = [{'username': row['username'], 'age': row['age'], 'city': row['city']} for row in rows]

        new_members = {}

        for row in rows:
            if row['username'] not in self.members:
                new_members[row['username']] = row

        self.members.update(new_members)

        save_members(self.members)

        yield new_members
