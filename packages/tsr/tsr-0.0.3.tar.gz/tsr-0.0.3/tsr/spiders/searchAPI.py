# -*- coding: utf-8 -*-
import json, io, re, os, sys, shutil, argparse, requests, time
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from ..modules.general import *
from ..modules.os_info import *
from ..modules import regex, forumload, soups

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
parser.add_argument('--forum-id', type=int)
parser.add_argument('--user-id', type=int)
parser.add_argument('--thread_type', type=str)
parser.add_argument('--page-first', type=int)
parser.add_argument('--page-last', type=int)
parser.add_argument('--overwrite-threads', dest='overwrite_threads', action='store_true')
parser.add_argument('--no-overwrite-threads', dest='overwrite_threads', action='store_false')
parser.add_argument('--overwrite-posts', dest='overwrite_posts', action='store_true')
parser.add_argument('--no-overwrite-posts', dest='overwrite_posts', action='store_false')
parser.add_argument('--delay', type=float)

mkdir(path.main)  # Superfluous, since mkdir() is recursive, but ignoring would look odd
mkdir(path.posts)
mkdir(path.threads)
mkdir(path.users)
mkdir(path.forums)
mkdir(path.settings)
touch(path.log)

settings = json.load(open(os.path.join(path.settings, 'settings.json')))


class Port_Source(requests.adapters.HTTPAdapter):
    # Credit: Martijn Pieters https://stackoverflow.com/questions/47202790/python-requests-how-to-specify-port-for-outgoing-traffic
    def __init__(self, port, *args, **kwargs):
        self._source_port = port
        super(Port_Source, self).__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, source_address=('', self._source_port))


def main_raw(**kwargs):
    try:
        threads = json.load(
            open(path.threads_json))  # json of all threads ever cached with json caching setting enabled
    except:
        threads = {}
    previously_cached_post_ids = []
    for t in threads:
        print(t)
        if 'posts' in t:
            for p in t['posts']:
                previously_cached_post_ids.append(p)

    def parse_threadpage(url):
        print('parse_threadpage({})'.format(url))
        soup = BeautifulSoup(session.get(url).text, 'html.parser')
        if '?t=' in url:
            thread_id = int(url.split('?t=')[-1].split('&')[0])
        else:
            thread_id = int(soup.find('link', {'rel': 'canonical'})['href'].split('?t=')[-1].split('&')[0])
        print(
            'soups.parse_threadpage({}, {}, {}, overwrite_posts={})'.format('soup', url, thread_type, overwrite_posts))
        open('/tmp/' + url.split('/')[-1] + '.0.html', 'w').write(str(soup))
        (post_list, _) = soups.parse_threadpage(soup, url, thread_type, overwrite_posts=overwrite_posts)
        del soup
        if len(post_list) == 20:
            page_last = page_current + 1  # tmp, lazy workaround
            print(len(post_list))
        else:
            page_last = 1
        return page_last

    def parse_threadpages(thread_type, thread_or_post_id):
        page_current = 1
        page_last = 1
        if thread_type == 'p':
            url = 'https://www.thestudentroom.co.uk/showthread.php?p={}'.format(thread_or_post_id)
            try:
                thread_id = soups.get_thread_id(BeautifulSoup(session.get(url).text, 'html.parser'))
            except:
                thread_id = None  # Thread probably removed
            time.sleep(delay)
        if thread_type == 't':
            thread_id = thread_or_post_id
        if thread_id:
            while page_current <= page_last:
                url = 'https://www.thestudentroom.co.uk/showthread.php?t={}&page={}'.format(thread_id, page_current)
                page_last = parse_threadpage(url)
                print(
                    'Parsed {} {} - Page {}/{}'.format(thread_type, str(thread_id), str(page_current), str(page_last)))
                page_current += 1
                time.sleep(delay)

    # Defaults/init states
    forum_id = False
    user_id = False
    thread_type = 't'
    page_first = 1
    page_last = 999999
    overwrite_threads = True
    overwrite_posts = False
    delay = 11.0

    if kwargs['forum_id'] != None:
        forum_id = kwargs['forum_id']
    elif kwargs['user_id'] != None:
        user_id = kwargs['user_id']
    if kwargs['thread_type'] != None:
        thread_type = kwargs['thread_type']
    if kwargs['page_first'] != None:
        page_first = int(kwargs['page_first'])
    if kwargs['page_last'] != None:
        page_last = int(kwargs['page_last'])
    if kwargs['overwrite_threads'] != None:
        overwrite_threads = kwargs['overwrite_threads']
    if kwargs['overwrite_posts'] != None:
        overwrite_posts = kwargs['overwrite_posts']
    if kwargs['delay'] != None:
        delay = int(kwargs['delay'])
    session = requests.Session()
    if 'port' in kwargs:
        if kwargs['port'] != None:
            session.mount('https://', Port_Source(kwargs['port']))
    d = {}
    thread_ids = []
    threads_cannot_load = []
    page_current = page_first
    if forum_id:
        id_value = forum_id
        filter_type = 'forumid'
    elif user_id:
        id_value = user_id
        filter_type = 'userid'
    else:
        raise Exception('Please specify either a forum-id or user-id')
    while page_current <= page_last:
        print('Requesting search page {}'.format(str(page_current)))
        if thread_type == 't':
            url = 'https://www.thestudentroom.co.uk/search.php?filter[type]=thread&filter[{}]={}&page={}'.format(
                str(filter_type), str(id_value), str(page_current))
        elif thread_type == 'p':
            url = 'https://www.thestudentroom.co.uk/search.php?filter[{}]={}&page={}'.format(str(filter_type),
                                                                                             str(id_value),
                                                                                             str(page_current))
        request = session.get(url)
        soup = BeautifulSoup(request.text, 'html.parser')
        thread_meta_list = soups.load_searchpage_threadmeta(soup, thread_type=thread_type)
        for thread in thread_meta_list:
            if thread_type == 't':
                thread_id = thread['id']
                if thread_id in threads:
                    nPosts_actual = len(threads[thread_id]['posts'])
                else:
                    nPosts_actual = -9  # Might have nPosts_claimed==0
                if nPosts_actual < thread['nPosts_claimed']:
                    print('Parsing t {}'.format(str(thread_id)))
                    parse_threadpages('t', thread_id)
            elif thread_type == 'p':
                post_id = thread['postid']
                if post_id in previously_cached_post_ids:
                    nPosts_actual = 999  # No way of knowing nPosts_claimed
                else:
                    nPosts_actual = -9  # Might have nPosts_claimed==0
                if nPosts_actual < thread['nPosts_claimed']:
                    print('Parsing thread which contains p {}'.format(str(post_id)))
                    parse_threadpages('p', post_id)
            time.sleep(delay)
        page_current += 1
        page_last = int(soup.find('a', {'class': 'pager-last'})['href'].split('&page=')[-1].split('&')[0])
        print('Last page {}'.format(str(page_last)))


def main():
    args = sys.argv[1:]
    main_raw(**vars(parser.parse_args(args)))  # So we can treat it as a dictionary


if __name__ == '__main__':
    main()
