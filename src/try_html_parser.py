#!/usr/bin/env python3
"""Test for https://spb.hh.ru/vacancy/76870825"""
from html.parser import HTMLParser
import urllib.request


class MyHTMLParser(HTMLParser):
    tags: int = 0  # 963
    wattrs: int = 0  # 884

    def handle_starttag(self, tag, attrs):
        print(f"Encountered a start tag: '{tag}' with {len(attrs)} attrs.")
        self.tags += 1
        if len(attrs):
            self.wattrs += 1


parser = MyHTMLParser()
# with open("jetland.ru.html", 'rt', encoding='utf-8') as in_file:
with urllib.request.urlopen('https://jetlend.ru/') as in_file:
    parser.feed(in_file.read().decode("utf-8"))
    print(parser.tags, parser.wattrs)
