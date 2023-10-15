#!venv/bin/python3

import argparse
import html2text
import json
import os
import requests
import sys

from dotenv import load_dotenv
load_dotenv()


def chunks(l, n):
    # https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class MailgunAPI(object):

    def __init__(self, api_domain, api_key, my_domain):
        self.api_endpoint = 'https://{:s}/v3/{:s}/messages'.format(
            api_domain, my_domain)
        self.auth = ('api', api_key)

    def send(self, from_email, to, subject, text=None, html=None):
        data = {'from': from_email, 'to': to, 'subject': subject}
        if text:
            data['text'] = text
        if html:
            data['html'] = html
        return requests.post(
            self.api_endpoint,
            auth=self.auth,
            data=data)


class FeedbinAPI(object):

    class AuthException(Exception):
        pass

    class APIException(Exception):
        def __init__(self, message=None, status_code=None, errors=None, url=None, method=None):
            if errors and not message:
                message = json.dumps(errors)
            super(FeedbinAPI.APIException, self).__init__(message)
            self.status_code = status_code
            self.errors = errors or []
            self.url = url
            self.method = method

        @property
        def human_str(self):
            return 'Feedbin API Error: {msg:s}\n{method:s}: {url:s}\nHTTP Status: {status}\nError Detail:\n{detail}'.format(
                msg=self.__str__(),
                status=self.status_code or '[unknown]',
                detail=json.dumps(self.errors, sort_keys=True, indent=2),
                method='HTTP {}'.format(self.method or '[unknown method]'),
                url=self.url or '[URL unknown]'
            )

    API_BASE = 'https://api.feedbin.com/v2'

    def __init__(self, username, password):
        self.auth = (username, password)

    def _check_response(self, r):
        if r.status_code == 401:
            raise FeedbinAPI.AuthException()
        if r.status_code != 200:
            decoded = r.json()
            raise FeedbinAPI.APIException(
                message=decoded.get('message'),
                status_code=decoded.get('status'),
                errors=decoded.get('errors'),
                method=r.request.method,
                url=r.request.url,
            )

    def _get_all_pages(self, endpoint, params=None):
        if params is None:
            params = {}
        params['page'] = 1
        resp = self._get(endpoint, params)
        results = resp.json()
        next_url = resp.links.get('next')
        while next_url:
            resp = requests.get(next_url, auth=self.auth)
            self._check_response(resp)
            results.extend(resp.json())
            next_url = resp.links.get('next')
        return results

    def _get(self, endpoint, params=None):
        url = '{base:s}/{endpoint:s}.json'.format(base=FeedbinAPI.API_BASE, endpoint=endpoint)
        resp = requests.get(url, auth=self.auth, params=params)
        self._check_response(resp)
        return resp

    def _get_decoded(self, endpoint, params=None):
        return self._get(endpoint, params).json()

    def get_starred_entries(self):
        entry_ids_chunks = list(chunks(self._get_decoded('starred_entries'), 100))
        entries = []
        for entry_ids in entry_ids_chunks:
            entries.extend(self._get_all_pages('entries', params={
                'ids': ','.join([str(id) for id in entry_ids]).strip(',')
            }))
        return entries

    def get_feed(self, feed_id):
        return self._get_decoded('feeds/{}'.format(feed_id))

    def check_auth(self):
        r = self._get('authentication')

    def mark_read(self, entry_id):
        url = '{base:s}/{endpoint:s}.json'.format(base=FeedbinAPI.API_BASE, endpoint='unread_entries')
        resp = requests.delete(url, auth=self.auth, json={
            "unread_entries": [entry_id]
        })
        self._check_response(resp)

    def unstar(self, entry_id):
        url = '{base:s}/{endpoint:s}.json'.format(base=FeedbinAPI.API_BASE, endpoint='starred_entries')
        resp = requests.delete(url, auth=self.auth, json={
            "starred_entries": [entry_id]
        })
        self._check_response(resp)


def run(feedbin_api, mailgun_api, from_email, to, dry_run):
    if dry_run:
        print('Listing entries which would be unstarred/archived...')
        print('')
    entries = feedbin_api.get_starred_entries()
    count = 0
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.inline_links = False
    h.wrap_links = False
    h.unicode_snob = True
    h.body_width = 0
    h.use_automatic_links = True
    h.ignore_tables = True
    for entry in entries:
        feed = feedbin_api.get_feed(entry['feed_id'])
        feed_title = feed['title']
        title = entry['title'] or ''
        url = entry['url'] or ''
        summary = entry['summary'] or ''
        content = entry['content'] or ''
        print('{:s}: {:s} ( {:s} )'.format(feed_title, title, url))
        html_body = '<strong><a href="{:s}">{:s}</a></strong><br><br>'.format(url, title)
        text_body = url + '\r\n\r\n'
        if len(summary) > 0:
            html_body = html_body + summary + '<br><br>'
            text_body = text_body + h.handle(summary) + '\r\n'
        html_body = html_body + '<hr><br><br>' + content
        text_body = text_body + '---\r\n\r\n' + h.handle(content)
        mailgun_api.send(from_email, to,
                         '{:s}: {:s}'.format(feed_title, title),
                         html=html_body, text=text_body)
        if not dry_run:
            feedbin_api.unstar(entry['id'])
            feedbin_api.mark_read(entry['id'])
        count += 1
    print('')
    print('{:d} entries affected.'.format(count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send your starred Feedbin entries to an email address.')
    parser.add_argument('--dry-run', type=str2bool, default='true', help='True to send mail, but not unstar/archive anything in Feedbin. False to send mail, unstar and archive starred entries. Default: True.')
    parser.add_argument('--from', type=str, default=None, dest='from_email', help='Email to send from, eg. "User <mailgun@YOUR_DOMAIN_NAME>". Required.')
    parser.add_argument('--to', type=str, default=None, help='Address to send email to, eg. "things@example.com". Required.')
    args = parser.parse_args()

    if not args.from_email:
        eprint("Missing required argument --from.")
        sys.exit(1)
    if not args.to:
        eprint("Missing required argument --to.")
        sys.exit(1)

    feedbin_user = os.getenv('FEEDBIN_USERNAME')
    feedbin_pass = os.getenv('FEEDBIN_PASSWORD')
    # allow this program to use the same env file as
    # https://github.com/cdzombak/feedbin-auto-archiver :
    if not feedbin_user:
        feedbin_user = os.getenv('FEEDBIN_ARCHIVER_USERNAME')
    if not feedbin_pass:
        feedbin_pass = os.getenv('FEEDBIN_ARCHIVER_PASSWORD')
    if not feedbin_user or not feedbin_pass:
        eprint("Feedbin username & password must be set using environment variables.")
        eprint("Copy .env.sample to .env and fill it out to provide credentials.")
        sys.exit(1)
    feedbin_api = FeedbinAPI(feedbin_user, feedbin_pass)
    try:
        feedbin_api.check_auth()
    except FeedbinAPI.AuthException:
        eprint("Feedbin authentication failed.")
        eprint("Check your credentials and try again.")
        sys.exit(1)

    mailgun_api_domain = os.getenv('MAILGUN_API')
    mailgun_domain = os.getenv('MAILGUN_DOMAIN')
    mailgun_api_key = os.getenv('MAILGUN_API_KEY')
    if not mailgun_api_domain or not mailgun_domain or not mailgun_api_key:
        eprint("Mailgun configuration must be set using environment variables.")
        eprint("Copy .env.sample to .env and fill it out to provide credentials.")
        sys.exit(1)
    mailgun_api = MailgunAPI(mailgun_api_domain, mailgun_api_key, mailgun_domain)

    try:
        run(feedbin_api, mailgun_api, from_email=args.from_email, to=args.to, dry_run=args.dry_run)
        sys.exit(0)
    except FeedbinAPI.APIException as e:
        eprint(e.human_str)
        sys.exit(3)
