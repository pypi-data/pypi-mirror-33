import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
from html.parser import HTMLParser

USER_AGENT = 'Python-urllib/3.6 AutoReporter/0.1.7'

class ATError(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class TokenParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            if len(attrs) == 0:
                pass
            else:
                if ('name', 'token') in attrs and ('type', 'hidden') in attrs:
                    self.token = attrs[2][1]


class ContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.content = ''
        self.trigger = False
    
    def handle_starttag(self, tag, attrs):
        if tag != 'textarea':
            return
        if ('id', 'mdeditor') in attrs and ('name', 'content') in attrs:
            self.trigger = True
            return
    
    def handle_endtag(self, tag):
        if tag == 'textarea' and self.trigger:
            self.trigger = False

    def handle_data(self, data):
        if self.trigger:
            self.content = data


token_parser = TokenParser()
content_parser = ContentParser()


class ReportSender:
    def __init__(self, username, password):
        # general cookie jar
        cj = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(handler)
        self.opener = opener
        
        self.login(username, password)

    def parse_token(self, res):
        token_parser.feed(res)
        token_parser.close()
        return token_parser.token

    def parse_content(self, res):
        content_parser.feed(res)
        content_parser.close()
        return content_parser.content

    def login(self, username, password):
        url = 'https://at.twtstudio.com/login'
        print('Loggin into %s...' % url)

        try:
            token_res = self.opener.open(url)
            token = self.parse_token(token_res.read().decode('utf-8'))
            if not token:
                print('Failed to parse token from %s. Aborting' % url)
                raise ATError('token not found')
            data = {
                'token': token,
                'username': username,
                'password': password
            }
            post_data = urllib.parse.urlencode(data).encode('utf-8')
            login_req = urllib.request.Request(url, data=post_data, method='POST')
            login_req.add_header("User-Agent", USER_AGENT)
            self.opener.open(login_req)
        except Exception as e:
            raise ATError(str(e))

    def get_content(self):
        url = 'https://at.twtstudio.com/report/write'
        print('Fetching present weekly report...')
        try:
            request = urllib.request.Request(url)
            request.add_header("User-Agent", USER_AGENT)
            response = self.opener.open(request).read().decode('utf-8')
            write_token = self.parse_token(response)
        except Exception as e:
            raise ATError(str(e))
        
        if not write_token:
            print('Failed to parse token from %s. Aborting...' % url)
            raise ATError('token not found')
        old_content = self.parse_content(response)
        self.old_content = old_content
        self.write_token = write_token

    def write(self, content):
        url = 'https://at.twtstudio.com/report'
        print('Writing report with your commit messages...')

        data = {
            'token': self.write_token,
            'content': content
        }
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data=post_data, method='POST')
        request.add_header("User-Agent", USER_AGENT)

        try:
            self.opener.open(request)
        except Exception as e:
            raise ATError(str(e))
    