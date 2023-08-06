#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import base64
import pickle
import os
import re

try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

import pyquery

from robobrowser import RoboBrowser
from robobrowser.compat import urlparse


class RoboBrowserQuery(RoboBrowser):
    simple_cookie = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('parser', 'lxml')
        self.send_referer = True
        super(RoboBrowserQuery, self).__init__(*args, **kwargs)

    @property
    def query(self):
        if not hasattr(self.state, 'pyquery'):
            self.state.pyquery = pyquery.PyQuery(
                self.get_decoded_content())

        return self.state.pyquery

    def set_cookie_at_next_request(self, cookie_text):
        """
        DEPRECATED
        set cookie text.
        recommend: from django.utils.encoding import smart_str
                   set_cookie_at_next_request(smart_str(cookie_text))
        """
        self.simple_cookie = SimpleCookie()
        self.simple_cookie.load(cookie_text)

    def set_cookie(self, cookie_dict):
        """
        DEPRECATED
        :param cookie_dict:
        """
        self.session.cookies.set(**cookie_dict)

    def cookie_as_dict(self):
        """
        DEPRECATED
        """
        if not self.simple_cookie:
            return None
        return {k: v.value for k, v in self.simple_cookie.items()}

    def get_cookies(self):
        """
        :return: http.cookiejar.Cookie list
        For serialize, example django cache
        """
        return list(iter(self.session.cookies))

    def get_serialized_cookies(self):
        b = pickle.dumps(self.get_cookies())
        return base64.b64encode(b).decode()

    def save_cookies_to_file(self, file_path):
        """
        Save pickled cookies to file
        """
        with open(file_path, 'wb') as fp:
            pickle.dump(self.get_cookies(), fp)

    def set_cookies(self, cookies):
        """
        From serialized, example django cache
        """
        for cookie in cookies:
            self.session.cookies.set_cookie(cookie)

    def set_serialized_cookies(self, text):
        b = base64.b64decode(text)
        cookies = pickle.loads(b)
        self.set_cookies(cookies)

    def load_cookies_from_file(self, file_path, fail_silently=True):
        """
        Load unpickled cookies to file
        """
        if not os.path.exists(file_path) and fail_silently:
            return
        with open(file_path, 'rb') as fp:
            cookies = pickle.load(fp)
            self.set_cookies(cookies)

    def get_cookies_as_dicts(self):
        """
        Get cookies for debug
        """
        return [c.__dict__ for c in iter(self.session.cookies)]

    def get_cookie_values_as_dicts(self):
        """
        Get cookies for eazy debug.
        """
        return [
            {
                "domain": c.domain,
                "name": c.name,
                "value": c.value,
            } for c in iter(self.session.cookies)
        ]

    def open(self, *args, **kwargs):
        if self.simple_cookie:
            kwargs.update({'cookies': self.cookie_as_dict()})
        super(RoboBrowserQuery, self).open(*args, **kwargs)

    def preview(self, suffix='.html'):
        """
        Preview latest response with GUI web browser
        """
        import tempfile
        import subprocess

        f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        f.write(self.state.response.content)
        f.close()

        # for mac.
        subprocess.Popen(['open', f.name])
        # Auto delete required?

    def get_decoded_content(self):
        """
        Get html content as str
        """
        he = self.header_encoding()
        if he:
            return self.response.content.decode(
                encoding=he, errors="ignore")
        else:
            return self.response.content.decode(errors="ignore")

    def take_snapshot(self, file_path):
        """
        take html snapshot to file
        """
        with open(file_path, "wb") as fp:
            fp.write(self.state.response.content)

    re_meta_refresh_content_url = re.compile(r'url=(.+)', re.I)

    re_http_equiv_refresh = re.compile("^refresh$", re.I)

    def meta_refresh(self):
        """
        Execute meta refresh.
        """
        meta_refresh = self.find(
            'meta', attrs={'http-equiv': self.re_http_equiv_refresh})
        if not meta_refresh:
            return

        content = meta_refresh['content']
        if not content:
            return

        match = self.re_meta_refresh_content_url.search(content)
        if not match:
            return

        self.open(match.group(1))

    def load_html(self, html, **kwargs):
        """
        Load html force. Overwrite on current state.
        """
        from robobrowser.browser import BeautifulSoup
        kwargs.setdefault('features', 'lxml')
        parsed = BeautifulSoup(html, **kwargs)
        self.state.parsed = parsed
        if hasattr(self.state, 'pyquery'):
            delattr(self.state, 'pyquery')

    def submit_form(self, form, submit=None, **kwargs):
        if self.url and self.send_referer:
            kwargs.setdefault('headers', {})
            kwargs['headers'].setdefault('Referer', self.url)

        super(RoboBrowserQuery, self).submit_form(
            form, submit=submit, **kwargs)

    def get_parsed_url(self):
        """
        Get parsed current url.
        """
        return urlparse.urlparse(self.url)

    def get_parsed_query(self, flatten=True, *kwargs):
        """
        Get parsed current url queries
        """
        parsed_url = self.get_parsed_url()
        qs = urlparse.parse_qs(parsed_url.query, *kwargs)
        if not flatten:
            return qs
        return {
            k: v if len(v) >= 2 else v[0]
            for k, v in qs.items()
        }

    def reparse(self, decode=True, encoding=None, errors='ignore'):
        """
        Retry parse content for beautifulsoup
        """
        from bs4 import BeautifulSoup
        if decode:
            if encoding:
                content = self.state.response.content.decode(
                    encoding, errors=errors)
            else:
                content = self.state.response.content.decode(
                    errors=errors)
        else:
            content = self.state.response.content
        self.state.parsed = BeautifulSoup(content, features=self.parser)

    def header_encoding(self):
        match = re.search(
            'charset=(.+)',
            self.response.headers.get('Content-Type', ''),
            re.IGNORECASE)
        if match:
            return match.group(1).lower()

    def find_elements_by_text_match(self, query, needle):
        """
        Search elements includes needle text.
        """
        elements = self.query(query)
        for i in range(elements.length):
            e = elements.eq(i)
            if needle in e.text():
                yield e
