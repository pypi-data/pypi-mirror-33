# -*- coding: utf-8 -*-
import shutil, requests, time
from bs4 import BeautifulSoup
import json # for json.load
import os.path

from . import general, os_info, regex, scrapers

os_info.mkdir(os_info.path.main)  # Superfluous, since os_info.mkdir() is recursive, but ignoring would look odd
os_info.mkdir(os_info.path.posts)
os_info.mkdir(os_info.path.threads)
os_info.mkdir(os_info.path.users)
os_info.mkdir(os_info.path.forums)
os_info.mkdir(os_info.path.settings)
os_info.touch(os_info.path.log)

settings = json.load(open(os.path.join(os_info.path.settings, 'settings.json')))

post_list = []  # We want to load just the first page of a thread, then display the results, then load the other pages in the background, continually appending them to this list as we refresh tsr_on_cl.py (probably so that every time we return to the main prompt, we get the latest page). Hence we probably want to do threading, and it is neater to do it here rather than mess the main thing up.
# Actually, having said that, it makes more sense to do it in tsr_on_cl.py. This is because we will probably want to utilise threading in other tasks.

'''
Security tokens etc
'''


def requests_get(url, session=None, **kwargs):
    if not session:
        session=requests.Session()
    i=0
    while True:
        i+=1
        try:
            return session.get(url, **kwargs)
        except Exception as e:
            print('E: Attempt {} failed to get {}'.format(i, url))
            print(e)
            time.sleep(1)


def get_security_token_from_url(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    return scrapers.get_security_token(soup)


def get_securitytoken_and_posthash_from_url(session, url):
    soup = BeautifulSoup(session.get(url).text, 'html.parser')
    securitytoken = scrapers.get_security_token(soup)
    posthash = scrapers.get_post_hash(soup)
    return securitytoken, posthash


def get_security_token_from_text(text):
    return scrapers.get_security_token(BeautifulSoup(text, 'html.parser'))


def get_post_hash_from_text(text):
    return scrapers.get_post_hash(BeautifulSoup(text, 'html.parser'))


def get_logout_url_from_session(session):
    return scrapers.get_logout_url(BeautifulSoup(session.get('https://www.thestudentroom.co.uk').text, 'html.parser'))


def get_list_of_flags_and_security_token(session):
    soup = BeautifulSoup(session.get('https://www.thestudentroom.co.uk/profile.php?do=editprofile').text, 'html.parser')
    list_of_flags = [tag.text for tag in soup.find('select', {'id': 'csel_field9'}).find_all('option')]
    list_of_flags[0] = 'None'
    securitytoken = scrapers.get_security_token(soup)
    return list_of_flags, securitytoken


'''
Threads
'''


def load_thread(thread_id, page_max, **kwargs):
    page_current = 1
    post_list = []
    while page_current < 1 + page_max:
        (post_list_new, securitytoken) = load_thread_page(thread_id, page_max, **kwargs)
        post_list += post_list_new
        post_list_new = []
        page_current += 1
    return post_list, securitytoken


def load_thread_page(thread_id, page_n, **kwargs):
    url = 'https://www.thestudentroom.co.uk/showthread.php?t={0}&page={1}'.format(str(thread_id), str(page_n))
    if 'session' in kwargs:
        request = kwargs['session'].get(url)
    else:
        request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    post_list, securitytoken = parse_threadpage(soup, url, 't', overwrite_posts=False)
    return post_list, securitytoken


def parse_page(**kwargs):
    if 'page_n' in kwargs:
        page_n = kwargs['page_n']
    else:
        page_n = 1

    if 'thread_id' in kwargs:
        url = 'https://www.thestudentroom.co.uk/showthread.php?t={0}&page={1}'.format(str(kwargs['thread_id']), str(page_n))
    elif 'forum_id' in kwargs:
        url = 'https://www.thestudentroom.co.uk/forumdisplay.php?f={0}&page={1}'.format(str(kwargs['forum_id']), str(page_n))
    elif 'page_type' in kwargs:
        if kwargs['page_type'] == 'register':
            url = 'https://www.thestudentroom.co.uk/register.php'
    elif 'url' in kwargs:
        url = kwargs['url']

    if 'session' in kwargs:
        request = kwargs['session'].get(url)
    else:
        request = requests.get(url)

    soup = BeautifulSoup(request.text, 'html.parser')

    if 'showthread.php' in url:
        if 't=' in url:
            return parse_threadpage(soup, url, 't')
        else:
            return parse_threadpage(soup, url, 'p')
    elif 'forumdisplay.php' in url:
        if 'forum_id' in kwargs:
            forum_id = kwargs['forum_id']
        else:
            forum_id = url.split('f=')[-1].split('?')[0]
        return load_forumpage_threadmeta(forum_id, page_n, **kwargs)
    elif 'editpost.php' in url:
        return scrapers.get_security_token(soup), scrapers.get_post_hash(soup)
    else:
        return scrapers.get_security_token(soup)


def get_thread_id(soup):
    thread_id = soup.find('a', {'class': 'twitter-share-button'})['data-url']
    thread_id = int(thread_id.split('t=')[-1].split('&')[0])
    return thread_id


def parse_threadpage(soup_main, url, thread_type, **kwargs):
    open('/tmp/' + url.split('/')[-1] + '.1.html', 'w').write(str(soup_main))
    if 'overwrite_posts' in kwargs:
        overwrite_posts = kwargs['overwrite_posts']
    else:
        overwrite_posts = False
    if settings['cache']['users'] == 'json':
        try:
            users = json.load(open(os_info.path.users_json))
        except:  # First time used
            users = {}
    if settings['cache']['threads'] == 'json':
        try:
            threads = json.load(open(os_info.path.threads_json))
        except:
            threads = {}
    post_list = []
    forum = {
        'name': [x.find('a').text for x in soup_main.find_all('span', {'class': 'navbar'})][-1],
        'id': [x.find('a')['href'] for x in soup_main.find_all('span', {'class': 'navbar'})][-1].split('?f=')[-1],
    }
    # url=soup_main.find('link', {'rel':'canonical'})['href']
    if '?t=' in url:
        thread_id = int(url.split('?t=')[-1].split('&page=')[0].split('&')[0])
    elif '?p=' in url:
        thread_id = soup_main.find('a', {'class': 'twitter-share-button'})['data-url']
        thread_id = int(thread_id.split('t=')[-1].split('&')[0])
    os_info.mkdir(os.path.join(os_info.path.forums, str(forum['id'])))
    outfile_path = os.path.join(os_info.path.forums, str(forum['id']), 'threads.txt')
    os_info.touch(outfile_path)
    os_info.writeif(outfile_path, str(thread_id) + '\n', not ((settings['cache']['on']) & (not settings['readonly'])),
            append=True)

    securitytoken = scrapers.get_security_token(soup_main)
    posts = soup_main.find_all('li', {'class': 'post'})
    for p in posts:
        try:  # There are different formats for dates
            date_reverse = p.find('span', {'class': 'datestamp'}).text  # 13-01-2018
            date_reverses = date_reverse.split('-')
            date_str = ''
            for x in date_reverses:
                date_str += '-' + x
            date_str = date_str[1:]

            time = p.find('span', {'class': 'timestamp'}).text  # 18:26

            datetime_str = date_str + 'T' + time
        except:
            datetime_str = p.find('time', {'class': 'standard'})['datetime']  # 2018-01-13T15:45:30+00:00

        userdata = p.find('div', {'class': 'username'}).find('a')
        user_id = int(userdata['href'].split('?u=')[-1])
        user_name = userdata.text.strip()
        user_avatar = p.find('div', {'class': 'avatar'}).find('img')['src']
        download_user_avatar = False
        if ('/genericavatar/' not in user_avatar) & (settings['cache']['avatars']):
            download_user_avatar = True
        user_avatar_url = 'https:' + user_avatar
        user_avatar = user_avatar.split('/')[-1]

        try:
            gender = p.find('div', {'class': 'sex'}).find('div')['title']
        except:
            gender = ''
        try:
            user_rank = p.find('li', {'class': 'rank'}).text.strip()
        except:
            user_rank = ''

        try:
            user_reps_data = p.find('span', {'class': 'rep'})['title']
            user_reps = int(user_reps_data.split(' +')[-1])
        except:
            user_reps = -1  # Some users hide their reps

        try:
            post_reps = int(p.find('span', {'class': 'score '}).text)
        except AttributeError:
            try:
                post_reps = int(p.find('span', {'class': 'score'}).text)
            except AttributeError:
                post_reps = 0  # Some old/locked/etc threads do not have reps at all

        # post_number=int(p.find('li', {'class':'post-number'}).text.strip()) # NOT post_id
        post_id = int(p.find('a', {'class': 'postanchor'})['id'].split('post')[-1])

        post_title = ''
        post_title_tag = p.find('div', {'class': 'post-title'})
        if post_title_tag:
            post_title = post_title_tag.text.strip()
        else:  # probably because is thread starter
            post_title_tag = p.find('span', {'class': 'titleline'})
            if post_title_tag:
                post_title = post_title_tag.find('a').text
            else:
                try:
                    post_title = p.find('title').text
                except:
                    pass
        if post_title == '':
            post_title = [x.find('span', {'class': 'text'}).text for x in soup_main.find_all('h1')][
                0]  # Why not use this from the start? Well, it seems that TSR does allow replies to have different titles to the original post title (the thread title). Not only are replies distinguished by "Re: " at the start, but it might also tell us if and when the thread title was changed.

        preview = '?'

        post_content_data = p.find('div', {'class': 'post-content'})
        scrapers.replace_images_with_hrefs(post_content_data)  # FIRST, to replace images in quotes and spoilers
        scrapers.full_urls(post_content_data)

        spoilers_tags = post_content_data.find_all('div', {'class': 'bb-spoiler'})
        spoilers_ls = []
        for q in spoilers_tags:
            qd = {}
            qd['type'] = 'spoiler'
            qd['content'] = general.mystrip(q.find('div', {'class': "spoiler-content"}).text)
            q.find(('span', {'class': "pre-spoiler"})).decompose()
            q.replaceWith(
                '@~@~@SPOILER@~@~@')  # Remove from soup so it doesn't add to the content.text we will do later on
            spoilers_ls.append(qd)

        quotes_tags = post_content_data.find_all('div', {'class': 'quote_block_container'})
        quotes_ls = []
        for q in quotes_tags:
            qd = {}
            qd['type'] = 'quote'
            qorigin = q.find('span', {'class': "origin"})
            qpostid_tag = None  # default value
            if qorigin != None:
                qd['user'] = {'name': qorigin.find(
                    'strong').text}  # todo: match ID to name (or maybe do this when browsing by matching post IDs)
                qpostid_tag = qorigin.find('a')
                qorigin.decompose()  # So the text portion - (Original post by USERNAME) - isn't included in the content
            else:
                qd['user'] = {'name': '?'}
            if qpostid_tag != None:  # Might be none if this isn't quoting a user, but eg an article
                try:
                    qpostid = int(qpostid_tag['href'].split('#post')[-1])
                except:
                    qpostid = -1
            else:
                qpostid = -1
            qd['post'] = {
                'id': qpostid,
            }
            qd['content'] = general.mystrip(q.find('div', {'class': "quote_block"}).text)
            q.replaceWith('@~@~@QUOTE@~@~@')
            quotes_ls.append(qd)

        videos_tags = post_content_data.find_all('iframe', {'title': lambda t: 'video' in t})
        videos_ls = []
        for q in videos_tags:
            qd = {}
            qd['type'] = 'video'
            qd['content'] = 'https:' + q['src'].split('?')[0]  # Remove the '?wmode=opaque' etc nonsense
            q.replaceWith(
                '@~@~@VIDEO@~@~@')  # Remove from soup so it doesn't add to the content.text we will do later on
            videos_ls.append(qd)

        anchors = post_content_data.find_all('a')  # FIRST, to replace images in quotes and spoilers
        for a in anchors:
            if a['href'] == 'http://www.thestudentroom.co.uk/app':
                a.decompose()
        for a in anchors:
            try:
                a.replaceWith(' ' + a['href'] + ' ')
            except:
                pass
        tags = scrapers.replace_tags(
            post_content_data)  # AFTER quotes, to only add tags in the current post (not quotes)

        content_split = general.mystrip(post_content_data.find('blockquote').text).split('@~@~@')
        content_dict_ls = []
        current_quote_n, current_spoiler_n, current_video_n = 0, 0, 0
        ls_of_domains = []
        for x in content_split:
            xd = {}
            plaintext = False  # default
            if x == 'QUOTE':
                xd = quotes_ls[current_quote_n]
                current_quote_n += 1
            elif x == 'SPOILER':
                xd = spoilers_ls[current_spoiler_n]
                current_spoiler_n += 1
            elif x == 'VIDEO':
                xd = videos_ls[current_video_n]
                current_video_n += 1
            else:
                xd['type'] = 'text'
                xd['content'] = x
                ls_of_domains = ls_of_domains + regex.findall_domains(x)
            content_dict_ls.append(xd)
        datetime = general.standardise_datetime(datetime_str)

        post_dict = {
            'id': post_id,
            'title': post_title,
            'preview': preview,
            'datetime': str(datetime),
            'reps': post_reps,
            'tags': tags,
            'domains': ls_of_domains,
            'user': {
                'id': user_id,
                'name': user_name,
                'reps': user_reps,
                'gender': gender,
                'rank': user_rank,
            },
            'thread': {
                'id': thread_id,
                'title': [x.find('span', {'class': 'text'}).text for x in soup_main.find_all('h1')][0],
            },
            'contents': content_dict_ls,
        }
        print(str(post_dict['id']), post_dict['contents'][0]['content'][:50])
        post_list.append(post_dict)
        thread_path = os.path.join(os_info.path.threads, str(thread_id))
        if thread_type == 'p':
            thread_meta_parent_path = os.path.join(os_info.path.threads, 'p' + str(post_id))
            if os.path.isdir(thread_meta_parent_path):
                if os.path.isdir(thread_path):
                    shutil.rmtree(thread_meta_parent_path)
                else:
                    shutil.move(thread_meta_parent_path, thread_path)

        if settings['cache']['on']:
            post_outfile = os.path.join(os_info.path.posts, str(post_id) + '.json')
            if (not os.path.isfile(post_outfile)) | (overwrite_posts):
                if settings['cache']['posts'] == 'loose':
                    os_info.touch(post_outfile)
                    with open(post_outfile, 'w') as fp:
                        json.dump(post_dict, fp)
                if settings['cache']['threads'] == 'loose':
                    os_info.mkdir(thread_path)
                    os_info.writeif(os.path.join(thread_path, 'posts.txt'), str(post_id) + '\n', settings['readonly'],
                            append=True)
                elif settings['cache']['threads'] == 'json':
                    no_previous_posts = False
                    thread_id = str(
                        thread_id)  # converting to string is important! Json happily converts integer keys to strings without raising warnings, so if thread_id is an integer, it will never find previous entries of the same thread
                    if thread_id in threads:
                        if 'posts' not in threads[thread_id]:
                            no_previous_posts = True
                    else:
                        threads[thread_id] = {}
                        no_previous_posts = True
                    if no_previous_posts:
                        for attr in post_dict:
                            threads[thread_id][attr] = post_dict[attr]
                            # We are making the assumption that the first post we encounter is the opening post. This is not always true, since we dont always look at the first page of a thread.
                        del threads[thread_id]['contents']
                        threads[thread_id]['posts'] = [post_id]
                        threads[thread_id]['id'] = int(thread_id)  # Overwrite post_id
                    else:
                        threads[thread_id]['posts'].append(post_id)
                    threads[thread_id]['title'] = \
                    [x.find('span', {'class': 'text'}).text for x in soup_main.find_all('h1')][0]
                if settings['cache']['users'] == 'loose':
                    user_path = os.path.join(os_info.path.users, str(user_id))
                    os_info.mkdir(user_path)
                    os_info.writeif(os.path.join(user_path, 'posts.txt'), str(post_id) + '\n', settings['readonly'],
                            append=True)
                    os_info.mkdir(os.path.join(user_path, 'avatars'))
                    try:
                        user_avatarlist = open(os.path.join(user_path, 'avatars', 'list.txt'), 'r').read().split('\n')
                    except:
                        os_info.touch(os.path.join(user_path, 'avatars', 'list.txt'))
                        user_avatarlist = [
                            'this is probably not a valid avatar name, although i may eventually be proven wrong.']
                    user_avatarlist = [x for x in user_avatarlist if x.strip()]  # Removes blank elements
                    if user_avatarlist[-1] != user_avatar:
                        os_info.writeif(os.path.join(user_path, 'avatars', 'list.txt'), str(user_avatar), settings['readonly'],
                                append=True)
                        if download_user_avatar:
                            os_info.download_file(user_avatar_url, os.path.join(user_path, 'avatars'))
                elif settings['cache']['users'] == 'json':
                    user_id_str = str(user_id)
                    if user_id_str in users:
                        users[user_id_str]['posts'].append(post_id)
                    else:
                        users[user_id_str] = {
                            'posts': [post_id],
                            'name': user_name,
                            'id': user_id,
                            'reps': user_reps,
                            'gender': gender,
                            'rank': user_rank,
                            'avatars': [user_avatar]
                        }
                        if user_avatar not in users[user_id_str]['avatars']:
                            users[user_id_str]['avatars'].append(user_avatar)
                            if download_user_avatar:
                                os_info.download_file(user_avatar_url, path.avatars)
    if settings['cache']['users'] == 'json':
        with open(os_info.path.users_json, 'r') as fp:
            users_old = json.load(
                fp)  # So each instance does not interfere with browser or other scrapers running in parallel
            for user in users_old:
                if user not in users:  # New user added by browsing
                    users[user] = users_old[user]
                else:
                    users[user]['posts'] = list(set(users_old[user]['posts'] + users[user]['posts']))
        with open(os_info.path.users_json, 'w') as fp:
            json.dump(users, fp, indent=2)
    if settings['cache']['threads'] == 'json':
        with open(os_info.path.threads_json, 'r') as fp:
            threads_old = json.load(
                fp)  # So each instance does not interfere with browser or other scrapers running in parallel
            for thread in threads_old:
                if thread not in threads:  # New thread added by browsing
                    threads[thread] = threads_old[thread]
                else:
                    if ('posts' in threads_old) & ('posts' in threads):
                        threads[thread]['posts'] = list(set(threads_old[thread]['posts'] + threads[thread]['posts']))
                    elif 'posts' in threads_old:
                        threads[thread]['posts'] = threads_old[thread]['posts']
        with open(os_info.path.threads_json, 'w') as fp:
            json.dump(threads, fp, indent=2)
    return post_list, securitytoken


'''
Forums
'''


def load_forumpage_threadmeta(forum_id, page_n, **kwargs):
    os_info.mkdir(os_info.path.main)  # Superfluous, since os_info.mkdir() is recursive, but ignoring would look odd
    os_info.mkdir(os_info.path.posts)
    os_info.mkdir(os_info.path.threads)
    os_info.mkdir(os_info.path.users)
    os_info.mkdir(os_info.path.forums)
    os_info.mkdir(os_info.path.settings)
    os_info.touch(os_info.path.log)  # Doesn't overwrite the log if it exists

    request = requests.get('https://www.thestudentroom.co.uk/forumdisplay.php?f={0}&page={1}'.format(str(forum_id), str(page_n)))
    soup = BeautifulSoup(request.text, 'html.parser')

    settings = json.load(open(os.path.join(os_info.path.settings, 'settings.json')))

    thread_meta_dict = {}
    thread_meta_list = []

    rows = soup.find_all('tr', {'class': 'thread'})
    securitytoken = scrapers.get_security_token(soup)
    for row in rows:
        thread_id = int(row.find('td', {'class': 'title'})['data-id'])
        title = row.find('span', {'class': 'titleline'}).find('a').text
        if title == '':  # Not sure why, sometimes blank
            title = row.find('td', {'class': 'title'})['title'].replace('\n',
                                                                        ' ')  # Despite what the name suggests, this is not the title, but rather, a glimpse of the opening post
        title_prefix = row.find('span', {'class': 'titleline'}).find('span', {'class': 'prefix'}).text.strip()
        if title_prefix not in ['Linked:', 'Moved:']:
            nPosts = int(row.find('span', {'class': 'replies'}).text.strip().replace(',', '').split(' ')[-1]) + 1
            author = row.find('td', {'class': 'title'}).find('span', {'class': 'byline'})
            try:  # requires javascript
                author_name = author.find('a', {'class': 'username'}).text.strip()
                author_id = int(author.find('a', {'class': 'username'})['href'].split('u=')[-1])
            except:
                author_name = author.text.strip()[2:].strip()
                author_id = -1
            try:  # requires javascript
                last_author_name = row.find('td', {'class': 'last-post'}).find('span', {'class': 'byline'}).find('a', {
                    'class': 'username'}).text.strip()
                last_author_id = int(row.find('td', {'class': 'last-post'}).find('span', {'class': 'byline'}).find('a',
                                                                                                                   {
                                                                                                                       'class': 'username'})[
                                         'href'].split('u=')[-1])
            except:
                last_author_name = row.find('td', {'class': 'last-post'}).find('span',
                                                                               {'class': 'byline'}).text.strip()[
                                   2:].strip()
                last_author_id = -1
            datetime = general.standardise_datetime(row.find('span', {'class': 'date_text'}).text)
            thread_meta_dict[thread_id] = {
                'title': title,
                'user': {
                    'name': author_name,
                    'id': author_id
                },
                'nPosts_claimed': nPosts,
                'datetime': str(datetime)
            }
            if settings['cache']['threads'] == 'loose':
                thread_meta_parent_path = os.path.join(os_info.path.threads, str(thread_id))
                os_info.mkdir(thread_meta_parent_path)
                thread_dump_filepath = os.path.join(thread_meta_parent_path, 'meta.json')
                if not os.path.isfile(thread_dump_filepath):  # Dont want to wear out the SSD/HDD
                    os_info.touch(thread_dump_filepath)
                    with open(thread_dump_filepath, 'w') as fp:
                        json.dump(thread_meta_dict[thread_id], fp, indent=1)
            thread_meta_dict[thread_id][
                'id'] = thread_id  # Dont want to waste space appending this to the file we write
            thread_meta_dict[thread_id]['last_post_username'] = last_author_name  # nor this, since it changes rapidly
            thread_meta_list.append(thread_meta_dict[thread_id])
    if 'sorting' in kwargs:
        thread_meta_list = sorted(thread_meta_list, key=lambda x: x[kwargs['sorting']])
    else:
        thread_meta_list = thread_meta_list[::-1]  # Reverse order, to put most recent posts at the bottom

    if settings['cache']['threads'] == 'json':
        try:
            thread_meta_dict_old = json.load(open(os_info.path.threads_json))
            for thread_id in thread_meta_dict:
                if str(thread_id) not in thread_meta_dict_old:
                    thread_meta_dict_old[str(thread_id)] = thread_meta_dict[thread_id]
        except:  # doesnt exist yet
            thread_meta_dict_old = thread_meta_dict
        with open(os_info.path.threads_json, 'w') as f:
            json.dump(thread_meta_dict_old, f, indent=2)
    return thread_meta_list, thread_meta_dict, securitytoken  # Give us the choice


'''
Search page
'''


def load_searchpage_threadmeta(soup, **kwargs):
    os_info.mkdir(os_info.path.main)  # Superfluous, since os_info.mkdir() is recursive, but ignoring would look odd
    os_info.mkdir(os_info.path.posts)
    os_info.mkdir(os_info.path.threads)
    os_info.mkdir(os_info.path.users)
    os_info.mkdir(os_info.path.forums)
    os_info.mkdir(os_info.path.settings)
    os_info.touch(os_info.path.log)  # Doesn't overwrite the log if it exists

    # Defaults
    thread_type = 't'

    if 'thread_type' in kwargs:
        thread_type = kwargs['thread_type']

    settings = json.load(open(os.path.join(os_info.path.settings, 'settings.json')))

    thread_meta_list = []

    rows = soup.find('table', {'id': 'search_results_posts'}).find_all('tr')
    rows = [t for t in rows if t.find('td', {'class': 'alt2'})]  # Removes the first three descriptive rows
    rows = [t for t in rows if t.find('td', {'class': 'alt2'}).find('a')]  # Check contains title
    for row in rows:
        x = row.find('td', {'class': 'alt2'})
        try:
            nReplies = int(row.find_all('td')[3].text.strip().split(' replies')[0])
        except:
            nReplies = -1

        dummy = [x for x in row.find_all('a') if x['href']]
        thread_or_post_id = \
        [x for x in dummy if 'showthread.php?' in x['href']][0]['href'].split('?' + thread_type + '=')[-1].split('&')[0]

        dummy = [x for x in row.find_all('a') if x['href']]
        author_tag = [x for x in dummy if 'member.php?u=' in x['href']][0]

        title = x.find('a').text
        nPosts = nReplies + 1
        author_name = author_tag.text
        author_id = int(author_tag['href'].split('u=')[-1])

        try:
            current_page_n_str = soup.find('li', {'class': 'current'}).text.strip()
        except:
            current_page_n_str = '1'
        print('\n', thread_type, current_page_n_str)

        thread_meta_dict = {
            'title': title,
            'user': {
                'name': author_name,
                'id': author_id
            },
            'nPosts_claimed': nPosts,
        }
        if thread_type == 't':
            thread_meta_dict['id'] = thread_or_post_id
        elif thread_type == 'p':
            thread_meta_dict[
                'postid'] = thread_or_post_id  # Making an entry for a single post just knowing its post id isn't worth it, plus often useful to be able to quickly translate thread ids to post ids
        if settings['cache']['threads'] == 'loose':
            thread_meta_parent_path = os.path.join(os_info.path.threads, str(thread_or_post_id))
            os_info.mkdir(thread_meta_parent_path)
            thread_dump_filepath = os.path.join(thread_meta_parent_path, 'meta.json')
            if not os.path.isfile(thread_dump_filepath):  # Dont want to wear out the SSD/HDD
                os_info.touch(thread_dump_filepath)
                with open(thread_dump_filepath, 'w') as f:
                    json.dump(thread_meta_dict, f)
        thread_meta_list.append(thread_meta_dict)
    if 'sorting' in kwargs:
        thread_meta_list = sorted(thread_meta_list, key=lambda x: x[kwargs['sorting']])
    else:
        thread_meta_list = thread_meta_list[::-1]  # Reverse order, to put most recent posts at the bottom

    if (thread_type == 't') & (settings['cache']['threads'] == 'json'):
        try:
            thread_meta_dict_old = json.load(open(os_info.path.threads_json))
            for thread_or_post_id in thread_meta_dict:
                if str(thread_or_post_id) not in thread_meta_dict_old:
                    thread_meta_dict_old[str(thread_or_post_id)] = thread_meta_dict
        except:  # doesnt exist yet
            thread_meta_dict_old = thread_meta_dict
        with open(os_info.path.threads_json, 'w') as f:
            json.dump(thread_meta_dict_old, f)
    return thread_meta_list


'''
Notifications
'''


def notifications_from_session(session):
    request = session.get('https://www.thestudentroom.co.uk/notifications.php')
    soup = BeautifulSoup(request.text, 'html.parser')
    notifications = soup.find('ol', {'class': 'notification-list'}).find_all('li', {'class': 'notification'})
    notifications_and_hrefs = [(n.find('a').text.strip().replace('\n', ' ').replace('\t', ' ').replace('        ',
                                                                                                       ' ').replace(
        '    ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' '), n.find('a')['href']) for n in
                               notifications]
    return notifications_and_hrefs
