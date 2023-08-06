from .colours import cl
from .os_info import path
import os.path
import json # for json.load
from . import general # for myjoin, standardise_date/datetime, ls_rm_dupl

def load_forum_database(forumtype, f_or_u_id, **kwargs):
    toprint = ''
    load_threads = False
    sorting = 'id'
    maximum_threads = 100000
    if kwargs:
        if 'load_threads' in kwargs:
            if kwargs['load_threads']:
                load_threads = True
        if 'sorting' in kwargs:
            sorting = kwargs['sorting']
        if 'max_threads' in kwargs:
            maximum_threads = kwargs['max_threads']
    ls_success = []
    ls_warning = []
    ls_error = []
    ls_failure = []
    ls_threads = []  # All threads that can load
    usernames_to_id = {}

    if os.path.isfile(path.threads_json):
        threads = json.load(open(path.threads_json))  # json of all threads ever cached with json caching setting enabled
    else:
        threads = {}

    if forumtype == 'forum':
        threads_ls_path = os.path.join(path.forums, f_or_u_id, 'threads.txt')
        if os.path.isfile(threads_ls_path):
            fthreads_ls = [int(n) for n in open(threads_ls_path).read().split('\n') if
                           n != '']  # We want integers, because 55 < 500 (but '55' > '500')
        else:
            return [], [], [], [], [], {}
    elif forumtype == 'userid':
        posts_ls = json.load(open(path.users_json))[str(f_or_u_id)]['posts']
        fthreads_ls = []
        for postid in posts_ls:
            post_path = os.path.join(path.posts, str(postid) + '.json')
            if os.path.isfile(post_path):
                fthreads_ls.append(int(json.load(open(post_path))['thread']['id']))
    else:
        raise ValueError('Only valid forumtypes are "userid" and "forum"')

    fthreads_ls = sorted(list(set(fthreads_ls)), reverse=True)
    fthreads_ls = [str(n) for n in fthreads_ls]

    if sorting == 'rid':
        fthreads_ls = fthreads_ls[::-1]  # But by default, we want the newest threads first

    i, failures, errors, warnings, successes = 0, 0, 0, 0, 0
    while (successes + warnings + errors < maximum_threads) & (i < len(fthreads_ls)):
        threadid = fthreads_ls[i]
        try:
            list_of_posts = []
            if threadid in threads:
                thread_dict = threads[threadid]
                list_of_postids = thread_dict['posts']
                for postid in list_of_postids:
                    post = json.load(open(os.path.join(path.posts, str(postid) + '.json')))
                    post['datetime'] = general.standardise_datetime(post['datetime'])
                    list_of_posts.append(post)
                thread_dict['posts'] = list_of_posts  # Rather than list of post IDs
            else:  # We'll see if we have it in loose form
                tposts = open(os.path.join(path.threads, threadid, 'posts.txt')).read()
                for postid in general.ls_rm_dupl(tposts.rstrip().split('\n')):
                    post = json.load(open(os.path.join(path.posts, postid + '.json')))
                    post['datetime'] = general.standardise_datetime(post['datetime'])
                    list_of_posts.append(post)
                thread_dict_file = open(os.path.join(path.threads, threadid, 'meta.json'))
                thread_dict = json.load(thread_dict_file)
                thread_dict['posts'] = list_of_posts
                if load_threads:
                    for p in list_of_posts:
                        usernames_to_id[p['user']['name']] = p['user']['id']
                thread_dict['id'] = threadid
            thread_dict['nPosts'] = len(list_of_posts)
            if 'nPosts_claimed' in thread_dict:
                if thread_dict['nPosts'] == thread_dict['nPosts_claimed']:
                    successes += 1
                    ls_success.append(int(threadid))
                    if load_threads:
                        ls_threads.append(thread_dict)
                    toprint += general.myjoin(cl.green, threadid, '', successes, cl.yellow, warnings, cl.brown, errors, cl.red,
                                      failures, cl.end, '\r')  # Replaces last line of output
                else:
                    errors += 1
                    ls_error.append(int(threadid))
                    if load_threads:
                        ls_threads.append(thread_dict)
                    toprint += general.myjoin(cl.brown, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors,
                                      cl.red, failures, cl.red, 'nPosts:', thread_dict['nPosts'], 'nPosts_claimed:',
                                      thread_dict['nPosts_claimed'], cl.end)
            else:
                if len(thread_dict['posts']) == 0:
                    failures += 1
                    ls_failure.append(int(threadid))
                    toprint += general.myjoin(cl.red, 'Cannot load any posts', cl.end)
                else:
                    warnings += 1
                    ls_warning.append(int(threadid))
                    if load_threads:
                        ls_threads.append(thread_dict)
                    toprint += general.myjoin(cl.yellow, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors,
                                      cl.red, failures, cl.yellow, 'No nPosts_claimed', cl.end)
        except KeyError:  # due to no posts attached to thread_dict, i.e. we haven't cached the thread except from the forum page
            try:
                failures += 1
                ls_failure.append(int(threadid))
                toprint += general.myjoin(cl.red, threadid, cl.green, successes, cl.yellow, warnings, cl.brown, errors, cl.red,
                                  failures, cl.end)
            except:  # Probably blank
                pass
        i += 1
    return ls_success, ls_warning, ls_error, ls_failure, ls_threads, usernames_to_id
