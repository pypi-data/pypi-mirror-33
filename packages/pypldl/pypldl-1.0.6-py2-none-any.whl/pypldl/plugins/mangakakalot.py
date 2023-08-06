import re
import os
import logging
from collections import OrderedDict
from .manga import _MangaTask

HANDLER_NAME = 'mangakakalot'
logger = logging.getLogger(HANDLER_NAME)


def normalize_title(title):
    """Normalize a manga title"""
    return title.lower().replace(' ', '_').replace('-', '_')


class MangakakalotTask(_MangaTask):
    """
    Download manga chapters on mangakakalot
    """

    handler_name = HANDLER_NAME
    base_url = "http://mangakakalot.com"
    uri_re = re.compile(r"^(?:http:)?//mangakakalot.com/(?P<type>manga|chapter)/(?P<title>[^/]+)(?:/(?P<chapter>[^/]+))?$")

    @classmethod
    def from_uri(cls, uri):
        m = cls.uri_re.match(uri)
        if m is None:
            return None
        if m.group('chapter'):
            chapters = [m.group('chapter')]
        else:
            chapters = None
        return cls(title=m.group('title'), chapters=chapters)

    @classmethod
    def build_manga_url(cls, title):
        return '{0}/manga/{1}'.format(cls.base_url, title)

    @classmethod
    def build_chapter_url(cls, title, chapter):
        return '{0}/chapter/{1}/{2}'.format(cls.base_url, title, chapter)

    @classmethod
    def get_manga_info(cls, dm, title):
        soup = dm.request_soup(cls.build_manga_url(normalize_title(title)))
        if soup.find(text=re.compile("Sorry, the page you have requested cannot be found.")):
            return False

        # get pretty title
        s = soup.find('meta', property='og:title')['content']
        pretty_title = s.split(' Manga Online')[0]
        # get path title
        s = soup.find('meta', property='og:url')['content']
        path_title = cls.uri_re.match(s).group('title')

        chapters = OrderedDict()
        for e in soup.find('div', class_='chapter-list').find_all('a')[::-1]:
            chapter_name = e.text.strip()
            path = cls.uri_re.match(e['href']).group('chapter')
            chapters[chapter_name] = path

        return {'title': pretty_title, 'path': path_title, 'chapters': chapters}


    def get_chapter_pages_paths(self, chapter):
        soup = self.request_soup(self.build_chapter_url(self.title, chapter))
        pages = []
        for e in soup.find('div', id='vungdoc').find_all('img', class_='img_content'):
            pages.append(e['src'])
        return pages

    def get_image_url(self, page):
        return page

