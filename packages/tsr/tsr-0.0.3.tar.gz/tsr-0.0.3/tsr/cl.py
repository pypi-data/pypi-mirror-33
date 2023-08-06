import os, re, subprocess, curses, six, requests
import curses.textpad
import pandas as pd
from math import ceil
from html import unescape
from kitchen.text.display import textual_width_chop
import json # for json.load
# and for json.dump
import matplotlib as plt
from shlex import split as shlex_split

try:
    import nltk # for word_tokenize, pos_tag, PorterStemmer
    use_nltk = True
except ImportError:
    use_nltk = False
from collections import Counter
from time import sleep as time_sleep

from .modules import os_info # for writeif, mkdir, memory_usage, path
from .modules.colours import cl_to_assign
from .modules import general # for make_n_char_long, standardise_datetime, standardise_datetime_str, standardise_date
from .modules import regex, soups
from .modules.forumload import load_forum_database
from .modules.grammar import singularise

class Key:
    ESCAPE = 27
    RETURN = 10
    SPACE = 32


class Port_Source(requests.adapters.HTTPAdapter):
    # Credit: Martijn Pieters https://stackoverflow.com/questions/47202790/python-requests-how-to-specify-port-for-outgoing-traffic
    def __init__(self, port, *args, **kwargs):
        self._source_port = port
        super(Port_Source, self).__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, source_address=('', self._source_port))


def mainbody(screen):  # Over 1000 lines...
    def load_dict_users():
        users = {}
        username_colour_dict = {}  # temporary colour scheme for users without flairs/colours, for easier reading
        username_to_id = json.load(open(os.path.join(os_info.path.settings, 'username_to_id.json')))  # Merge into users.json?
        users = json.load(open(os.path.join(os_info.path.settings, 'users.json')))
        for entry in users:
            if not 'colour' in users[entry]:
                users[entry]['colour'] = 'end'
            if users[entry]['colour'] is None:
                users[entry]['colour'] = 'end'
            username = users[entry]['name']
            if type(username) == 'str':
                username = [username]
            users[entry]['name'] = ls_rm_dupl(username)  # tmp
        return users

    def share_dictionaries():
        soups.settings = settings  # Important to know settings['readonly'] value

    def list_forum_ids(forums):
        string = ''
        for category in forums:
            string += category + '\n'
            for forum in forums[category]:
                string += '  '.join(
                    ['', '', general.make_n_char_long(forums[category][forum]['id'], 4), forums[category][forum]['title']])
                string += '\n            ' + forums[category][forum]['desc']
                string += '\n'
        return string

    def list_commands(commands):
        string = ''
        for entry in commands:
            string += '\n\n' + entry
            string += '\n  ' + commands[entry]['desc'][0]
            print_usages = True
            try:
                string += '\n  ' + commands[entry]['common']['usage']
                print_usages = False
            except:
                pass
            for subentry in commands[entry]['commands']:
                string += '\n  ' + commands[entry]['commands'][subentry]['alts'][0]
                if print_usages:
                    string += '\n    ' + commands[entry]['commands'][subentry]['usage']
        return string

    def session_new():
        session = requests.Session()
        session.headers.update({'User-Agent': settings['user_agent']})
        i = 0
        while i < len(settings['port_sources']):
            try:
                session.mount('https://', Port_Source(settings['port_sources'][i]))
                break
            except:  # Port already in use
                pass
        return session

    def login(securitytoken, **kwargs):
        session = session_new()
        if securitytoken == '':  # Peek-a-boo! Here's some cookies for you!
            session.get('https://www.thestudentroom.co.uk/signin.php')
        credentials = json.load(open(os.path.join(os_info.path.settings, 'credentials.json')))
        if len(credentials) == 0:
            username = prompt_input('Username:    ')
            password = prompt_input('Password:    ')
            userid = prompt_input('User  ID:    ')
            account_credentials = {
                'vb_login_username': username,
                'vb_login_password': password,
                'userid': userid
            }
            credentials.append(account_credentials)
            with open(os.path.join(os_info.path.settings, 'credentials.json'), 'w') as f:
                json.dump(credentials, f)
        elif len(credentials) == 1:
            account_credentials = credentials[0]
        elif len(credentials) > 1:
            if 'username' in kwargs:
                account_username = kwargs['username']
            else:
                account_username = ''
            account_usernames = [x['vb_login_username'] for x in credentials]
            while account_username not in account_usernames:
                account_username = prompt_input('Accounts=' + str(account_usernames))
            account_credentials = [x for x in credentials if x['vb_login_username'] == account_username][0]
        data = dict(
            account_credentials)  # Create an element-wise copy of the dict (rather than one that refers back to the original dict)
        data['do'] = 'login'
        data['securitytoken'] = 'guest'
        data['utcoffset'] = '0'
        data['cookieuser'] = '1'
        url = 'https://www.thestudentroom.co.uk/login.php?do=login'
        request = session.post(url, data)
        securitytoken = soups.get_security_token_from_text(request.text)
        time_sleep(2)
        return session, account_credentials

    def main_init():
        os_info.mkdir(os_info.path.images)

        settings = json.load(open(os.path.join(os_info.path.settings, 'settings.json')))
        commands = json.load(open(os.path.join(os_info.path.settings, 'commands.json')))
        words_colour_dict = json.load(open(os.path.join(os_info.path.settings, 'colours_words.json')))
        domain_colour_dict = json.load(open(os.path.join(os_info.path.settings, 'colours_domains.json')))
        status_message = ''
        if settings['matplotlib']['headless_backend']:
            plt.use('Agg')
            status_message += 'Using Agg backend for matplotlib'

        forums = json.load(open(os.path.join(os_info.path.settings, 'forums.json')))
        if forums == {}:
            import tsr.modules.generate_forums
            tsr.modules.generate_forums.main()

        users = load_dict_users()

        j_meta = {
            'forum_id': 0,
            'number': 0,
            'sorting': ''
        }
        browsing = {
            'logged_in': False,
            'browsing': True,
            'forum_id': 0,
            'sorting': '',
            'thread_id': 0,
            'page_n': 1,
            'cursor': {
                'thread_id': 0,
                'post_id': 0,
                'user': {
                    'name': '',
                    'id': 0,
                },
            },
        }
        securitytoken = ''

        return forums, settings, commands, users, words_colour_dict, domain_colour_dict, j_meta, browsing, securitytoken, status_message

    def strip_textpad(text):
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Attempt to intelligently strip excess whitespace from the output of a
        curses textpad.
        """

        if text is None:
            return text

        # Trivial case where the textbox is only one line long.
        if '\n' not in text:
            return text.rstrip()

        # Allow one space at the end of the line. If there is more than one
        # space, assume that a newline operation was intended by the user
        stack, current_line = [], ''
        for line in text.split('\n'):
            if line.endswith('  ') or not line:
                stack.append(current_line + line.rstrip())
                current_line = ''
            else:
                current_line += line
        stack.append(current_line)

        # Prune empty lines at the bottom of the textbox.
        for item in stack[::-1]:
            if not item:
                stack.pop()
            else:
                break

        out = '\n'.join(stack)
        return out

    def add_line(window, text, row=None, col=None, attr=None):
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Unicode aware version of curses's built-in addnstr method.

        Safely draws a line of text on the window starting at position
        (row, col). Checks the boundaries of the window and cuts off the text
        if it exceeds the length of the window.
        """

        # The following arg combos must be supported to conform with addnstr
        # (window, text)
        # (window, text, attr)
        # (window, text, row, col)
        # (window, text, row, col, attr)
        cursor_row, cursor_col = window.getyx()
        row = row if row is not None else cursor_row
        col = col if col is not None else cursor_col

        n_cols = w - col - 1
        if n_cols <= 0:
            # Trying to draw outside of the screen bounds
            return

        try:
            text = clean(text, n_cols)
            params = [] if attr is None else [attr]
            window.addstr(row, col, text, *params)
        except (curses.error, ValueError, TypeError) as e:
            # Curses handling of strings with invalid null bytes (b'\00')
            #   python 2: TypeError: "int,int,str"
            #   python 3: ValueError: "embedded null byte"
            _logger.warning('add_line raised an exception')
            _logger.exception(str(e))

    def mainpad_addstr(row, column, content, attr):
        if -1 < row:  # <h-3:
            attr = str2colour[attr]
            mainpad.addstr(row, column, str(content)[:w], attr)

    def sort_by_post_attr(thread_ls, sorting='datetime', reverse=False):
        if len(thread_ls) == 0:
            return thread_ls
        sort_by_user_attr = False
        if sorting[:4] == 'user':
            sorting = sorting[4:]
            sort_by_user_attr = True
        if 'posts' in thread_ls[0]:
            object_to_read_attr_from = sort_by_post_attr(thread_ls[0]['posts'])[
                0]  # Get oldest post - necessary because user may cache the first page after the last
        else:
            object_to_read_attr_from = thread_ls[0]
        if 'datetime' in object_to_read_attr_from:
            sorted_keys_n = 2
            sorted_lastkey_1 = 'datetime'
            sorted_lastkey_2 = 'id'  # In case we have datetimes without times
        else:
            open_pager('Error:\n\n' + str(object_to_read_attr_from))

        # Sanitise thread_ls to remove incomplete threads (eg if scraper is running in background)
        thread_ls = [t for t in thread_ls if 'datetime' in t]

        if sort_by_user_attr:
            if sorted_keys_n == 1:
                thread_ls = sorted(thread_ls, key=lambda x: (x['user'][sorting], x[sorted_lastkey_1]), reverse=reverse)
            elif sorted_keys_n == 2:
                thread_ls = sorted(thread_ls,
                                   key=lambda x: (x['user'][sorting], x[sorted_lastkey_1], x[sorted_lastkey_2]),
                                   reverse=reverse)
        else:
            if sorted_keys_n == 1:
                thread_ls = sorted(thread_ls, key=lambda x: (x[sorting], x[sorted_lastkey_1]),
                                   reverse=reverse)  # Largest values at the top, where the cursor starts
            elif sorted_keys_n == 2:
                thread_ls = sorted(thread_ls, key=lambda x: (x[sorting], x[sorted_lastkey_1], x[sorted_lastkey_2]),
                                   reverse=reverse)
        return thread_ls

    def display_forum(thread_ls, **kwargs):
        mainpad.clear()
        mainpad.bkgd(' ', str2colour['mainpad_bg'])
        if 'sorting' in kwargs:
            sorting = kwargs['sorting']
        else:
            sorting = 'datetime'
        if 'scroll' in kwargs:
            scroll = kwargs['scroll']
        else:
            scroll = 0
        thread_ls = sort_by_post_attr(thread_ls, sorting, True)  # reverse=True
        current_line_y = -scroll  # mainpad_addstr() ignores lines if current_line_y < 0
        for t in thread_ls:
            try:
                datetime = t['datetime']
            except:
                datetime = t['posts'][0]['datetime']
            try:
                title = t['title']
            except:
                title = t['posts'][0]['title']
            try:
                nPosts = t['nPosts']
            except:
                try:
                    nPosts = len(t['posts'])
                except:
                    nPosts = t['nPosts_claimed']
            try:
                reps = t['reps']
            except:
                try:
                    reps = t['posts'][0]['reps']
                except:
                    reps = '?'
            try:
                username = t['user']['name']
            except:
                username = t['posts'][0]['user']['name']
            try:
                username_last = t['last_post_username']
            except:
                username_last = t['posts'][-1]['user']['name']
            datetime, nPosts, reps = str(datetime)[:10], str(nPosts), str(reps)
            mainpad.addstr(current_line_y, 0, str(current_line_y))
            mainpad.addstr(current_line_y, 4, title[:w - 60], str2colour['title'])
            mainpad.addstr(current_line_y, w - 58, datetime, curses.A_BOLD)
            mainpad.attron(str2colour['username'])
            mainpad.addstr(current_line_y, w - 46, username[:20])
            mainpad.addstr(current_line_y, w - 27, username_last[:20])
            mainpad.attroff(str2colour['username'])
            mainpad.addstr(current_line_y, w - 10, nPosts, str2colour['info'])
            mainpad.addstr(current_line_y, w - 4, reps, str2colour['reps'])
            current_line_y += 1
        if current_line_y > 0:
            post_start_lines = range(
                current_line_y)  # There is (currently) one thread entry per line, so use range, and we don't want to error out when
        else:
            post_start_lines = [0]
        return current_line_y, post_start_lines, thread_ls

    def display_posts(posts_ls, sorting='datetime'):
        mainpad.clear()
        current_line_y = 0
        post_start_lines = []
        posts_ls = sort_by_post_attr(posts_ls, sorting, True)  # reverse=True
        for post in posts_ls:
            post_start_lines.append(current_line_y)
            userid = post['user']['id']
            mainpad.addstr(current_line_y, 0, '-' * w, str2colour['faint'])  # Faint line to help viewing
            mainpad.addstr(current_line_y, 0, post['user']['name'], str2colour['username'])
            mainpad.addstr(current_line_y, 20, str(post['user']['id']), str2colour['userid'])
            try:
                mainpad.addstr(current_line_y, 30, str(post['user']['reps']), str2colour['reps'])
            except:  # User has hidden their reputation bar
                pass
            next_x = 33
            try:
                mainpad.addstr(current_line_y, 30, users[userid]['flair'], str2colour['userflair'])
                next_x = 30 + len(users[userid]['flair']) + 1
            except:
                pass
            mainpad.addstr(current_line_y, next_x, str(post['datetime']), str2colour['datetime'])
            if post['reps'] > 0:
                mainpad.addstr(current_line_y, w - 4, str(post['reps']), str2colour['reps'])

            for content in post['contents']:
                c = content['content']
                if content['type'] == 'spoiler':
                    c_normal_attr = '@@@spoiler~~~' + c.replace('\n', '\n~')
                elif content['type'] == 'quote':
                    c_normal_attr = '@@@quote~~~~~'
                    c = '>>' + content['user']['name'] + '    ' + str(content['post']['id']) + '\n>' + c.replace('\n',
                                                                                                                 '\n>')
                elif content['type'] == 'text':
                    c_normal_attr = '@@@default~~~'
                if len(c) > 1:
                    c = c.replace('@@@default~~~',
                                  c_normal_attr)  # In case we've defined locations of default colours before
                    c = c_normal_attr + c

                    usernames = set([re.escape(post['user']['name']) for post in
                                     posts_ls])  # re.escape means special characters dont affect our regex later
                    usernames_regex = '|'.join(usernames)
                    try:
                        c = re.sub(regex.url2, r'{0}\1{1}'.format('@@@url~~~~~~~', c_normal_attr), c,
                                   flags=re.MULTILINE)  # Colour urls
                        c = re.sub(regex.image, r'{0}\1{1}'.format('@@@image~~~~~', c_normal_attr), c,
                                   flags=re.MULTILINE)  # Colour images (inc. image filenames in urls) purple
                        c = re.sub(r'({0})'.format(usernames_regex), r'{0}\1{1}'.format('@@@username~~', c_normal_attr),
                                   c, flags=re.MULTILINE)  # Colour suspected usernames (in text)
                        c = regex.parse_custom_colours(c)
                    except:
                        pass

                    c_coloured = [[], []]
                    c_colours = []
                    c_split = c.split('@@@')
                    for i in range(len(c_split)):
                        cc = c_split[i]
                        attr = cc[:10].replace('~', '')
                        open('/tmp/usetwoleft', 'a').write('\n\n\nAttr: <' + attr + '>')
                        if attr == 'useTwoLeft':
                            open('/tmp/usetwoleft', 'a').write('\nAttr: <useTwoLeft> confirmed')
                            open('/tmp/usetwoleft', 'a').write('\nlist: ' + str(c_colours[1]))
                            if i > 1:
                                attr = c_colours[i - 2]
                                open('/tmp/usetwoleft', 'a').write('\nRepl: <' + str(attr) + '>')
                            else:
                                attr = str2colour['default']
                                open('/tmp/usetwoleft', 'a').write('\nRepl: <default> (bcos i<2)')
                        elif attr == '':
                            attr = curses.A_NORMAL
                            open('/tmp/usetwoleft', 'a').write('\nRepl: <A_NORMAL> (bcos blank)')
                        else:
                            attr = str2colour[attr]
                            open('/tmp/usetwoleft', 'a').write('\nSmoothly done')
                        c_coloured[0] += cc[10:]
                        c_colours.append(attr)
                        for i in range(len(cc) - 10):
                            c_coloured[1].append(attr)
                    current_line_x = 0
                    for i in range(len(c_coloured[0])):
                        char = c_coloured[0][i]
                        attr = c_coloured[1][i]
                        if i % w == 0:
                            current_line_y += 1
                            current_line_x = 0
                        mainpad.addstr(current_line_y, current_line_x, char, attr)
                        if char == '\n':
                            current_line_y += 1
                            current_line_x = 0
                        else:
                            current_line_x += 1
            current_line_y += 2
        return current_line_y, post_start_lines, posts_ls  # In case we want to append things to the mainpad

    def display_tuple_ls(ls):
        if type(ls) != type([]):
            raise ValueError('display_tuple_ls requires LIST argument')
        if len(ls) == 0:
            open_pager('display_tuple_ls: No results\n\n' + str(ls))
            return 0  # Not necessarily a bug if we get no results
        mainpad.clear()
        current_line_y = 0
        max_w_rows_ls = [max([len(str(tpl[i])) for tpl in ls]) for i in
                         range(len(ls[0]))]  # Maximum size of elements in each column
        # So we can easily say that offset of Nth element = max_length of (N-1)th element
        colours = [curses.color_pair(i) for i in range(len(max_w_rows_ls))]  # For alternating colours
        for tpl in ls:
            x_offset = 0
            for i in range(len(ls[0])):
                mainpad.addstr(current_line_y, x_offset, str(tpl[i]), colours[i])
                x_offset += max_w_rows_ls[i] + 1
            current_line_y += 1
        return current_line_y

    def get_attr(window, y, x):
        coord_value = window.inch(y, x)
        ch = coord_value & 255  # first 8 bits (2^8=256) are char
        attr_value = int((int(coord_value) - int(ch)) / 256)
        return attr_value

    def clean(string, n_cols=None):  # browse t 5316512    5316100
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Required reading!
            http://nedbatchelder.com/text/unipain.html

        Python 2 input string will be a unicode type (unicode code points).
        Curses will accept unicode if all of the points are in the ascii range.
        However, if any of the code points are not valid ascii curses will
        throw a UnicodeEncodeError: 'ascii' codec can't encode character,
        ordinal not in range(128). If we encode the unicode to a utf-8 byte
        string and pass that to curses, it will render correctly.

        Python 3 input string will be a string type (unicode code points).
        Curses will accept that in all cases. However, the n character count in
        addnstr will not be correct. If code points are passed to addnstr,
        curses will treat each code point as one character and will not account
        for wide characters. If utf-8 is passed in, addnstr will treat each
        'byte' as a single character.

        Reddit's api sometimes chokes and double-encodes some html characters
        Praw handles the initial decoding, but we need to do a second pass
        just to make sure. See https://github.com/michael-lazar/rtv/issues/96

        Example:
            &amp;amp; -> returned directly from reddit's api
            &amp;     -> returned after PRAW decodes the html characters
            &         -> returned after our second pass, this is the true value
        """

        if n_cols is not None and n_cols <= 0:
            return ''

        if isinstance(string, six.text_type):
            string = unescape(string)

        if False:  # self.config['ascii']:
            if isinstance(string, six.binary_type):
                string = string.decode('utf-8')
            string = string.encode('ascii', 'replace')
            return string[:n_cols] if n_cols else string
        else:
            if n_cols:
                string = textual_width_chop(string, n_cols)
            if isinstance(string, six.text_type):
                string = string.encode('utf-8')
            return string

    def curs_set(n):
        try:
            curses.curs_set(n)
        except:
            pass

    def text_input(window=False, allow_resize=False):
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Transform a window into a text box that will accept user input and loop
        until an escape sequence is entered.

        If the escape key (27) is pressed, cancel the textbox and return None.
        Otherwise, the textbox will wait until it is full (^j, or a new line is
        entered on the bottom line) or the BEL key (^g) is pressed.
        """
        if not window:
            window = curses.newwin(h - 3, w, 2, 0)
        window.clear()

        # Set cursor mode to 1 because 2 doesn't display on some terminals
        curs_set(1)

        # Keep insert_mode off to avoid the recursion error described here
        # http://bugs.python.org/issue13051
        textbox = curses.textpad.Textbox(window)
        textbox.stripspaces = 0

        def validate(ch):
            "Filters characters for special key sequences"
            if ch == Key.ESCAPE:
                raise exceptions.EscapeInterrupt()
            if (not allow_resize) and (ch == curses.KEY_RESIZE):
                raise exceptions.EscapeInterrupt()
            # Fix backspace for iterm
            if ch == curses.ascii.DEL:
                ch = curses.KEY_BACKSPACE
            return ch

        out = textbox.edit(validate=validate)
        if isinstance(out, six.binary_type):
            out = out.decode('utf-8')

        curs_set(0)
        return strip_textpad(out)

    def suspend():
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Suspend curses in order to open another subprocess in the terminal.
        """

        try:
            curses.endwin()
            yield
        finally:
            curses.doupdate()

    def open_pager(data, wrap=None):
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        View a long block of text using the system's default pager.

        The data string will be piped directly to the pager.
        """

        pager = os.getenv('PAGER') or 'less'
        command = shlex_split(pager)

        if wrap:
            data_lines = content.Content.wrap_text(data, wrap)
            data = '\n'.join(data_lines)

        try:
            curses.endwin()
            p = subprocess.Popen(command, stdin=subprocess.PIPE)
            try:
                p.communicate(data.encode('utf-8'))
            except KeyboardInterrupt:
                p.terminate()
            curses.doupdate()
        except OSError as e:
            screen.show_notification('Could not open pager %s' % pager)

    def prompt_input(prompt, key=False):
        '''
        The MIT License (MIT)

        Copyright (c) 2015 michael-lazar

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
        '''
        """
        Display a text prompt at the bottom of the screen.

        Params:
            prompt (string): Text prompt that will be displayed
            key (bool): If true, grab a single keystroke instead of a full
                        string. This can be faster than pressing enter for
                        single key prompts (e.g. y/n?)
        """
        v_offset, h_offset = screen.getbegyx()
        prompt = clean(prompt, w - 1)

        # Create a new window to draw the text at the bottom of the screen,
        # so we can erase it when we're done.
        s_row = v_offset + h - 1
        s_col = h_offset
        prompt_win = curses.newwin(1, len(prompt) + 1, s_row, s_col)
        prompt_win.bkgd(' ', str2colour['prompt'])
        add_line(prompt_win, prompt)
        prompt_win.refresh()

        # Create a separate window for text input
        s_col = h_offset + len(prompt)
        input_win = curses.newwin(1, w - len(prompt), s_row, s_col)
        input_win.bkgd(str(' '), str2colour['prompt'])
        input_win.refresh()

        if key:
            curs_set(1)
            ch = screen.getch()
            # We can't convert the character to unicode, because it may return
            # Invalid values for keys that don't map to unicode characters,
            # e.g. F1
            text = ch if ch != Key.ESCAPE else None
            curs_set(0)
        else:
            text = text_input(input_win)

        prompt_win.clear()
        input_win.clear()
        del prompt_win
        del input_win
        screen.touchwin()
        screen.refresh()

        return text

    def session_post(url, data, **kwargs):
        global browsing  # Global variables are bad. But pain to do otherwise.
        if 'logout' in kwargs:
            if kwargs['logout']:
                session = session_new()
        if not browsing['logged_in']:
            do_login = True
            if kwargs['login'] in kwargs:
                if not kwargs['login']:
                    do_login = False
            if do_login:
                session, account_credentials = login(securitytoken)
                browsing['logged_in'] = True
        securitytoken = soups.parse_page(page_type='register', session=session)
        session.post(url, data)
        return session

    def post_comment(session, **kwargs):
        if not browsing['logged_in']:
            session, account_credentials = login(securitytoken)
            browsing['logged_in'] = True
        if 'reply_to' in kwargs:
            post_id = kwargs['reply_to']
            post = [x for x in posts_list if x['id'] == post_id][0]
            username = post['user']['name']
            content = '\n'.join([x['content'] for x in post['contents'] if x['type'] == 'text'])  # Don't quote quotes
            prefill = '[QUOTE={};{}]{}[/QUOTE]\n'.format(username, str(post_id), content)
            open_pager(prefill)
        else:
            open_pager('''CTRL+G to post''')
        data = {
            'fromquickreply': '1',
            'securitytoken': securitytoken,
            'do': 'postreply',
            'p': 'who cares',
            'specifiedpost': '0',
            'parseurl': '1',
            'loggedinuser': str(account_credentials['userid']),
            'postroute': 'thread/bottom',
            'message': text_input(),
            'signature': '1',
            'sbutton': 'Submit Reply',
        }
        if 'thread_id' in kwargs:
            if securitytoken == 'guest':
                (_, data['securitytoken']) = soups.load_thread_page(kwargs['thread_id'], 1, session=session)
            url = 'https://www.thestudentroom.co.uk/newreply.php?do=postreply&t=' + str(
                kwargs['thread_id'])  # We are assuming we've run 'browse $THREAD' before this
            data['t'] = str(kwargs['thread_id'])

        session.post(url, data)
        return 'posted'

    screen.clear()
    screen.refresh()

    curses.start_color()
    curses.use_default_colors()

    (forums, settings, commands, users, words_colour_dict, domain_colour_dict, j_meta, browsing, securitytoken,
     status_message) = main_init()

    theme_to_bg = {
        'dark': curses.COLOR_BLACK,
        'paper': curses.COLOR_WHITE,
    }
    mainpad_bg = theme_to_bg[settings['theme']]
    if mainpad_bg == curses.COLOR_BLACK:
        mainpad_bg_opposite = curses.COLOR_WHITE
    elif mainpad_bg == curses.COLOR_WHITE:
        mainpad_bg_opposite = curses.COLOR_BLACK

    curses.init_pair(0, 0, mainpad_bg)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Title: white fg, black bg
    curses.init_pair(2, curses.COLOR_CYAN, mainpad_bg)
    curses.init_pair(3, curses.COLOR_GREEN, mainpad_bg)
    curses.init_pair(4, curses.COLOR_YELLOW, mainpad_bg)  # Warning
    curses.init_pair(5, curses.COLOR_RED, mainpad_bg)
    curses.init_pair(6, -1, curses.COLOR_MAGENTA)  # Command
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(8, curses.COLOR_MAGENTA, mainpad_bg)  # Command
    curses.init_pair(9, curses.COLOR_BLUE, mainpad_bg)  # Command
    curses.init_pair(10, mainpad_bg_opposite, mainpad_bg)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(12, curses.COLOR_RED, mainpad_bg)
    if mainpad_bg == curses.COLOR_BLACK:
        curses.init_pair(13, curses.COLOR_BLUE, mainpad_bg)
    elif mainpad_bg == curses.COLOR_WHITE:
        curses.init_pair(13, curses.COLOR_YELLOW, mainpad_bg)
    curses.init_pair(14, curses.COLOR_RED, mainpad_bg_opposite)
    curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(16, curses.COLOR_WHITE, mainpad_bg)
    curses.init_pair(17, curses.COLOR_BLACK, mainpad_bg)

    str2colour = {
        'default': curses.color_pair(0),
        'end': curses.color_pair(0),  # Old default

        'header': curses.color_pair(1),
        'title': curses.color_pair(4),
        'info': curses.color_pair(2),
        'success': curses.color_pair(3),
        'warning': curses.color_pair(4),
        'refuse': curses.color_pair(5),
        'error': curses.color_pair(5),
        'command': curses.color_pair(6),
        'url': curses.color_pair(2),
        'username': curses.color_pair(4),
        'userid': curses.color_pair(2),
        'userflair': curses.color_pair(1),
        '@username': curses.color_pair(1),  # Tag used to link users, similar to /u/Username
        'status': curses.color_pair(7),
        'prompt': curses.color_pair(7),
        'reps': curses.color_pair(3),
        'date': curses.color_pair(2),
        'datetime': curses.color_pair(2),
        'quote': curses.color_pair(8),
        'spoiler': curses.color_pair(9),
        'purple': curses.color_pair(8),
        'image': curses.color_pair(2),
        'mainpad_bg': curses.color_pair(10),
        'grep': curses.color_pair(12),
        'faint': curses.color_pair(13),
        'r_opposite': curses.color_pair(14),

        'white': curses.color_pair(16),
        'grey': curses.color_pair(17),
        'lgrey': curses.color_pair(17),
        'black': curses.color_pair(17),

        'purple': curses.color_pair(8),
        'lpurple': curses.color_pair(8),
        'dpurple': curses.color_pair(8),
        'red': curses.color_pair(5),
        'lred': curses.color_pair(5),
        'dred': curses.color_pair(5),
        'yellow': curses.color_pair(4),
        'lyellow': curses.color_pair(4),
        'dyellow': curses.color_pair(4),
        'orange': curses.color_pair(4),
        'brown': curses.color_pair(4),
        'green': curses.color_pair(3),
        'lgreen': curses.color_pair(3),
        'dgreen': curses.color_pair(3),
        'cyan': curses.color_pair(2),
        'lcyan': curses.color_pair(2),
        'dcyan': curses.color_pair(2),
        'blue': curses.color_pair(9),
        'lblue': curses.color_pair(9),
        'dblue': curses.color_pair(9),

        'white_on_black': curses.color_pair(11),
        'black_red': curses.color_pair(15),

        'bold': curses.A_BOLD,
        'underlined': curses.A_UNDERLINE,
        'blink': curses.A_BLINK,
        'dim': curses.A_DIM,
        'standout': curses.A_STANDOUT,
    }

    h, w = screen.getmaxyx()

    mainpad_size = 0
    while True:
        try:
            mainpad_size += 1
            mainpad = curses.newpad(mainpad_size * 1000,
                                    w)  # curses.newwin(h-3,w, 2,0) # #curses.newpad(mainpad_size*1000,w) # Main pad for displaying threads,posts,etc, easy scrolling
            del mainpad
        except:
            mainpad_size -= 1
            mainpad = curses.newpad(mainpad_size * 1000,
                                    w)  # curses.newwin(h-3,w, 2,0) #curses.newpad(mainpad_size*1000,w)
            break

    mainpad.scrollok(True)
    mainpad.bkgd(str(' '), str2colour['mainpad_bg'])
    username_to_id = {}
    j = {}
    command_last = ''

    current_line_y = 0

    key = 0
    cursor_x, cursor_y = 0, 0
    commandstr = ''
    command = ''
    command_last = ''
    commandstr_last = ''
    arguments_original = []
    last_object_displayed = ''
    scroll = 0
    mainpad_scroll = 0
    last_attr = 0
    height_of_current_displayed_obj = 2
    status_message = 'Loaded'
    commanded = False
    session = session_new()  # Pre-login, don't really need a session, but it helps us a) define our custom user agent, and b) makes the following script neater (no need to account for not having a session defined)
    persistant_bars = {
        'title': {
            'content': 'TITLE',
            'x': 0,
            'y': 0,
            'attr': [str2colour['header'], curses.A_BOLD],
        },
        'subtitle': {
            'content': 'SUBTITLE',
            'x': 0,
            'y': 1,
            'attr': [str2colour['header']],
        },
        'status': {
            'content': '{11} | last_object_displayed:{12} | Mainbar_h:{7}k | Last key:{3} | Last command:{4} | RAM:{2} | j_meta:{5} | token:{6}'.format(
                cursor_x, cursor_y, str(os_info.memory_usage()['rss']), key, commandstr_last, str(j_meta), securitytoken,
                str(mainpad_size), command_last, str(mainpad_scroll), str(h), str(status_message),
                last_object_displayed),
            'x': 0,
            'y': h - 1,
            'attr': [str2colour['status']],
        },
    }
    scroll_lines = [0]
    while key != ord('q'):
        # screen.clear()
        h, w = screen.getmaxyx()
        cursor_x_last, cursor_y_last = cursor_x, cursor_y
        if key == curses.KEY_DOWN:
            if cursor_y == scroll_lines[-1]:  # At the end of the page
                if (last_object_displayed == 'thread') & (browsing['browsing']):
                    commandstr = 'browse t ' + str(browsing['thread_id']) + ' ' + str(
                        browsing['page_n'] + 1)  # Load next page
                    commanded = True
            else:
                cursor_y_new = [row for row in scroll_lines if row > cursor_y] + [h]
                cursor_y_new = cursor_y_new[0]
                cursor_y_diff = cursor_y_new - cursor_y
                cursor_y = cursor_y_new
                if mainpad_scroll < height_of_current_displayed_obj:
                    mainpad_scroll += cursor_y_diff
        elif key == curses.KEY_UP:
            cursor_y_new = [0] + [row for row in scroll_lines if row < cursor_y]
            cursor_y_new = cursor_y_new[-1]
            cursor_y_diff = cursor_y_new - cursor_y
            cursor_y = cursor_y_new
            if cursor_y - mainpad_scroll < 1:
                mainpad_scroll += cursor_y_diff
        elif key == curses.KEY_RIGHT:
            if last_object_displayed == 'forum':
                if browsing['browsing']:
                    commandstr = 'browse ' + str(cursor_y)
                    commanded = True
                else:
                    commandstr = str(cursor_y)  # Index of highlighted thread
                    commanded = True
            else:
                cursor_x += 1
        elif key == curses.KEY_LEFT:
            if last_object_displayed != 'forum':
                commandstr = 'back'  # Index of highlighted thread
                commanded = True
            else:
                cursor_x -= 1
        elif key == ord(':'):
            command_prompt = 'Command :    '
            commandstr = prompt_input(command_prompt)
            commanded = True
        elif key == ord('r'):  # Reply
            if last_object_displayed == 'thread':
                status_message = post_comment(session, thread_id=browsing['thread_id'],
                                              reply_to=browsing['cursor']['post_id'])
            elif last_object_displayed == 'forum':  # So we want to reply to a thread, i.e. post a normal comment
                status_message = post_comment(session, thread_id=browsing['thread_id'])
        elif key == ord('R'):  # Award rep
            commandstr = 'rep ' + str(browsing['cursor']['post_id'])
            commanded = True

        if key in [curses.KEY_UP, curses.KEY_DOWN]:
            if last_object_displayed == 'thread':
                browsing['cursor']['post_id'] = posts_list[scroll_lines.index(cursor_y)]['id']
            elif last_object_displayed == 'forum':
                try:
                    browsing['cursor']['thread_id'] = thread_meta_list[scroll_lines.index(cursor_y)]['id']
                except:
                    if len(j) > 0:
                        browsing['cursor']['thread_id'] = j[min(scroll_lines.index(cursor_y), max(0, len(j) - 1))]['id']
                    else:
                        browsing['cursor']['thread_id'] = 0
                # Thread ID of the thread underneath the cursor
                # Actually would be better to define this alongside scroll_lines in a dictionary, on forum_load and thread_load

        commandstr_last = commandstr
        persistant_bars['status'][
            'content'] = '{11} | last_object_displayed:{12} | Mainbar_h:{7}k | Cursor:{3} | Last command:{4} | RAM:{2} | j_meta:{5} | token:{6}'.format(
            cursor_x, cursor_y, str(os_info.memory_usage()['rss']), str(browsing['cursor']), commandstr_last, str(j_meta),
            securitytoken, str(mainpad_size), command_last, str(mainpad_scroll), str(h), str(status_message),
            last_object_displayed)
        command_last = command
        arguments_last = arguments_original
        if commanded:
            arguments = shlex_split(commandstr)
            arguments_original = arguments
            command = arguments[0]
            arguments = arguments[1:]
            mainpad_scroll, cursor_y = 0, 0
            commanded = False
        else:
            command = ''
            arguments = []
            arguments_original = arguments = []
        cursor_x = min(max(0, cursor_x), w - 1)
        cursor_y = min(max(0, cursor_y), height_of_current_displayed_obj - 1)

        mainpad_scroll = min(max(0, mainpad_scroll), height_of_current_displayed_obj - 1)

        try:
            mainpad.chgat(cursor_y_last, cursor_x_last, 1, curses.color_pair(last_attr))  # Undo previous highlight
            last_attr = get_attr(mainpad, cursor_y, cursor_x)
            if mainpad_bg == curses.COLOR_BLACK:
                mainpad.chgat(cursor_y, cursor_x, 1, curses.A_REVERSE)  # Highlight 1 char at cursor location
            elif mainpad_bg == curses.COLOR_WHITE:
                mainpad.chgat(cursor_y, cursor_x, 1,
                              str2colour['white_on_black'])  # Highlight 1 char at cursor location
        except:  # We haven't drawn anything on the display, hence cannot change its colour
            pass

        for bar in persistant_bars:
            for attr in persistant_bars[bar]['attr']:
                screen.attron(attr)
            x = persistant_bars[bar]['x']
            y = persistant_bars[bar]['y']
            content = persistant_bars[bar]['content'][:w - 1]  # So it doesn't overflow
            while len(content) < w - 1:
                content += ' '
            screen.addstr(y, x, content)
            for attr in persistant_bars[bar]['attr']:
                screen.attroff(attr)

        mainpad.refresh(mainpad_scroll, 0, 2, 0, h - 1, w)
        screen.refresh()

        key = screen.getch()

        share_dictionaries()

        for entry in commands['threaddisplay']['commands']:
            if command in ['grep', 'egrep']:
                pass  # temporary
            elif command in commands['threaddisplay']['commands'][entry]['alts']:
                attr_value = arguments[0]
                arguments = arguments[1:]
                try:
                    number_to_print = int(arguments[1])
                    arguments = arguments[1:]
                except:
                    number_to_print = 50
                try:
                    sorting = arguments[0]
                except:
                    sorting = 'datetime'
                posts_list = []
                post_ids = []
                attr_is_user_attr = False
                for thread in j:
                    for post in thread['posts']:
                        if entry in post:
                            if post[entry] == attr_value:
                                posts_list.append(post)
                        elif (entry[:4] == 'user'):
                            attr = entry[4:]
                            attr_is_user_attr = True
                            if attr in post['user']:
                                if post['user'][attr] == attr_value:
                                    posts_list.append(post)
                try:
                    posts_list = sorted(posts_list, key=lambda x: x['user'][sorting], reverse=True)
                except:
                    posts_list = sorted(posts_list, key=lambda x: x[sorting], reverse=True)
                height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list)
        if command == 'total':
            current_line_y = 2
            if len(arguments) == 0:
                open_pager('''Rejected

                Requires an argument

                Attributes include
                    username userid date reps domain imghost

                eg
                    total username
                    total hour 50''')
            else:
                filter_attr = arguments[0]
                arguments = arguments[1:]
                attr_is_user_attr = False
                if filter_attr[:4] == 'user':
                    filter_attr = filter_attr[4:]
                    attr_is_user_attr = True
                try:
                    number_to_print = int(arguments[0])
                    arguments = arguments[1:]
                except:
                    number_to_print = 50
                try:
                    min_occurances = int(arguments[1])
                    arguments = arguments[1:]
                except:
                    min_occurances = 1
                try:
                    sort_by = arguments[0]
                except:
                    sort_by = 'count'

                attrs = Counter([])
                datetimes = []
                for thread in j:
                    attrs_to_append = []  # Clear it each time to avoid memory explosion in the case of words. Listing every word from every post from every thread is bad idea. Counter is probably more easy on RAM.
                    thread_new = {x: thread[x] for x in thread if x != 'posts'}
                    thread_new['posts'] = []
                    for post in thread['posts']:
                        if attr_is_user_attr:
                            if filter_attr in post['user']:
                                append_this = True
                                to_append = post['user'][filter_attr]
                        else:
                            if filter_attr in ['all', 'time', 'datetime', 'minute', 'hour', 'day', 'month', 'year']:
                                to_append = general.standardise_datetime_str(post['datetime'])
                                append_this = False
                                datetimes.append(to_append)
                            elif filter_attr in post:
                                to_append = post[filter_attr]
                                append_this = True
                            elif filter_attr in ['word', 'words']:
                                content = '\n'.join([x['content'] for x in post['contents'] if x['type'] != 'quote'])
                                to_append = regex.ls_words(
                                    content)  # WARNING: This can eat up a lot of memory, probably a bad idea to use on an entire forum consisting of 500 threads.
                                append_this = True
                            elif filter_attr in ['domain', 'domains']:
                                content = '\n'.join([x['content'] for x in post['contents'] if x['type'] != 'quote'])
                                to_append = regex.findall_domains(content)
                                append_this = True
                            elif filter_attr in ['imghost', 'imagehost', 'imghosts', 'imagehosts']:
                                content = '\n'.join([x['content'] for x in post['contents'] if x['type'] != 'quote'])
                                to_append = regex.findall_domains(content, only_image_hosts=True)
                                append_this = True
                        if append_this:
                            if type(to_append).__name__ in ['list']:
                                for child in to_append:
                                    attrs_to_append.append(child)
                            else:
                                attrs_to_append.append(to_append)
                    attrs = attrs + Counter(attrs_to_append)
                attrs = [(x, attrs[x]) for x in attrs if attrs[x] > min_occurances]
                if len(attrs) == 0:
                    status_message = 'No results'
                if filter_attr in ['all', 'time', 'date', 'minute', 'hour', 'day', 'month', 'year']:
                    df = pd.DataFrame()
                    df['datetime'] = pd.to_datetime(datetimes, format='%Y-%m-%d %H:%M:%S')
                    if filter_attr in ['all', 'date']:  # Has to come first, before df=df.groupby
                        df = df.groupby(df['datetime'].dt.normalize())
                        df.count().plot(figsize=(settings['matplotlib']['w'] / 100, settings['matplotlib']['h'] / 100))
                    else:
                        if filter_attr in ['all', 'time']:
                            df = df.groupby(df['datetime'].dt.time)
                        if filter_attr in ['all', 'minute']:
                            df = df.groupby(df['datetime'].dt.minute)
                        if filter_attr in ['all', 'hour']:
                            df = df.groupby(df['datetime'].dt.hour)
                        if filter_attr in ['all', 'day']:
                            df = df.groupby(df['datetime'].dt.weekday)
                        if filter_attr in ['all', 'month']:
                            df = df.groupby(df['datetime'].dt.month)
                        if filter_attr in ['all', 'year']:
                            df = df.groupby(df['datetime'].dt.year)
                        df.count().plot(kind='bar',
                                        figsize=(settings['matplotlib']['w'] / 100, settings['matplotlib']['h'] / 100))
                    if settings['matplotlib']['headless_backend']:
                        previous_plots = [x for x in os.listdir(os_info.path.main) if x.split('.')[-1] == 'png']
                        path_plot = os.path.join(os_info.path.images, filter_attr + '.png')
                        plt.pyplot.figure(
                            figsize=(settings['matplotlib_w'] / 100, settings['matplotlib_h'] / 100))
                        plt.pyplot.savefig(
                            path_plot)  # dpi of 1 doesnt work well with fonts etc, 100 is near standard dpi of 96
                        status_message = 'Saved as: ' + path_plot
                        plt.pyplot.close()
                    else:
                        plt.pyplot.figure(
                            figsize=(settings['matplotlib']['w'] / 100, settings['matplotlib']['h'] / 100))
                        plt.pyplot.show()
                        plt.pyplot.close()
                else:
                    attrs = sorted(attrs, key=lambda x: x[1], reverse=True)
                    attrs = attrs[:number_to_print]
                    height_of_current_displayed_obj = display_tuple_ls(attrs)
        elif command == 'help':
            if len(arguments) == 0:
                open_pager(list_forum_ids(forums) + '\n\n' + list_commands(
                    commands) + '\n\n' + 'If errors, check ~/.config/tsr/paths.json and $settingsPath/settings.json')
            elif len(arguments) == 1:
                try:
                    open_pager(commands[arguments[0]]['common']['help'])
                except:
                    open_pager(commands[arguments[0]]['desc'][-1])
            elif len(arguments) == 2:
                open_pager(commands[arguments[0]]['commands'][arguments[1]]['help'])
            open_pager('''
            List of commands:
            Loading       load
            Settings      setting flair colour dict
            Analytics     total byday
            Filters       filter grep egrep
            Browsing      browse url browser
            If logged in  post report rep
            Misc          back t
            ''')
        elif command == 'back':
            persistant_bars['subtitle']['content'] = ''
            last_object_displayed = 'forum'
            if browsing['browsing']:
                height_of_current_displayed_obj, scroll_lines, thread_meta_list = display_forum(thread_meta_list)
            else:  # So we can load more meta information when displaying the forum-like object
                try:
                    number_of_threads = int(arguments[0])
                    try:
                        sorting = arguments[1]
                    except:
                        sorting = 'datetime'
                except:
                    number_of_threads = 500
                    try:
                        sorting = arguments[0]
                    except:
                        sorting = 'datetime'
                height_of_current_displayed_obj, scroll_lines, j = display_forum(j, sorting=sorting)
        elif command == 'setting':
            if len(arguments) == 2:
                key = arguments[0]
                if key in settings:
                    value = arguments[1]
                    if value in ['false', 'False']:
                        value = False
                    elif value in ['true', 'True']:
                        value = True
                    else:
                        try:
                            value = int(value)
                        except:
                            try:
                                value = float(value)
                            except:
                                pass
                    settings[key] = value
            else:
                toprint = '''
                Error:  Requires two arguments

                Usage:  setting [variable] [value]

                Eg:
                    setting readonly true       (to avoid writing anything to disk - be it new settings, page caches, or logs)

                Variables are:'''
                for key in settings:
                    toprint += '\n                    {}'.format(str(key))
                open_pager(toprint)
        elif command in ['tag', 'flair', 'colour']:
            username = arguments[0]
            if command == 'colour':
                if arguments[1] not in colour:
                    toprint = '''
                    Error: Colour not available

                    Available colours are:'''
                    for key in colour:
                        toprint += '\n' + colour[key] + '   ' + key
                    open_pager(toprint)
            try:
                userid = str(username_to_id[username])
                username_is_name = True
                proceed = True
            except:
                username_is_name = False
                try:
                    userid = str(int(username))
                    proceed = True
                except:
                    userid = ''  # Prevent us from using the last value of userid, ie the wrong user
                    toprint = '''
                    Username not known. Try user_id instead.

                    Known usernames are:
                    ''' + str('\n'.join(username_to_id))
                    open_pager(toprint)
                    proceed = False
            if proceed:
                try:
                    if username_is_name:
                        try:
                            if username not in users[userid]['name']:
                                users[userid]['name'].append(username)
                        except:
                            users[userid]['name'] = [username]
                    users[userid][command] = arguments[1]
                except:
                    users[userid] = {'name': [username], command: arguments[1]}
        elif command == 'dict':
            command = arguments[0]
            arguments = arguments[1:]
            if command == 'save':
                if arguments[0] == 'all':
                    arguments = commands['dictionary']['commands']['save']['help']['dictionary']
                if 'settings' in arguments:
                    with open(os.path.join(os_info.path.settings, 'settings.json'), 'w') as f:
                        json.dump(settings, f)
                    status_message = 'Saved settings.json'
                if 'users' in arguments:
                    with open(os.path.join(os_info.path.settings, 'users.json'), 'w') as f:
                        json.dump(users, f)
                    status_message = 'Saved users.json'
                if 'domains' in arguments:
                    with open(os.path.join(os_info.path.settings, 'colours_domains.json'), 'w') as f:
                        json.dump(domain_colour_dict, f)
                    status_message = 'Saved colours_domains.json'
                if 'words' in arguments:
                    with open(os.path.join(os_info.path.settings, 'colours_words.json'), 'w') as f:
                        json.dump(words_colour_dict, f)
                    status_message = 'Saved colours_words.json'
                if 'commands' in arguments:
                    with open(os.path.join(os_info.path.settings, 'commands.json'), 'w') as f:
                        json.dump(commands, f)
                    status_message = 'Saved commands.json'
                if 'username_to_id' in arguments:
                    with open(os.path.join(os_info.path.settings, 'username_to_id.json'), 'w') as f:
                        json.dump(username_to_id, f)
                    status_message = 'Saved username_to_id.json'
                if 'j' in arguments:
                    with open(os.path.join(os_info.path.settings,
                                           '{0}_{1}_{2}.json'.format(str(j_meta['forum_id']), str(j_meta['number']),
                                                                     j_meta['sorting'])), 'w') as f:
                        json.dump(j, f)
                    status_message = 'Saved j to .json'
                if 'j_forum' in arguments:
                    with open(os.path.join(os_info.path.settings,
                                           '{0}_{1}_{2}.json'.format(str(j_meta['forum_id']), str(j_meta['number']),
                                                                     j_meta['sorting'])), 'w') as f:
                        json.dump(j_forum, f)
                    status_message = 'Saved j_forum to .json'
        elif command in ['url', 'browser'] + settings['browsers']:  # Open forum/thread in web browser
            if command == 'browser':
                command = settings['browsers'][0]  # Use default browser
            command_old = command
            command = arguments[0]
            argument = arguments[1]
            url = ''
            if command[:2] == 'f=':
                url = 'https://www.thestudentroom.co.uk/forumdisplay.php?' + command
            elif command[:2] in ['t=', 'p=']:
                url = 'https://www.thestudentroom.co.uk/showthread.php?' + command
            elif (command[:2] == 'u=') | (command == 'user'):
                try:
                    int(command[2:])
                    url = 'https://www.thestudentroom.co.uk/member.php?' + command
                except:
                    try:
                        url = 'https://www.thestudentroom.co.uk/member.php?' + str(int(argument))
                    except:
                        url = 'https://www.thestudentroom.co.uk/member.php?' + username_to_id[argument]
            elif general.is_number(command):
                thread_id = j[int(command)]['id']
                url = 'https://www.thestudentroom.co.uk/showthread.php?t=' + thread_id
            if command_old == 'url':
                status_message = (url)
            elif url != '':
                subprocess.call([command, url])
        elif command == 'browse':
            if len(arguments) == 0:
                open_pager('''
                Error: Requires at least one argument.

                Usage:
                    browse f [forumid] [page]?
                    browse t [threadid] [page]? [sorting]?
                    browse [threadNumber from forum-like object] [page]?

                Sorting methods include:  reps, date'

                Eg:
                    browse f 143                for page 1 of forum of id 143
                    browse t 12345678 3         for page 3 of thread of id 12345678
                    browse 73 1                 for page 1 of thread of index 143 (index=order in our forum object)

                Tip: Each thread page holds 20 posts
                If thread, also accepts page value of "all"''')
            else:
                sorting = 'datetime'
                if len(arguments) == 0:
                    add_line_('error', 'Requires more arguments')
                    browse_type = 'failed'
                else:
                    if general.is_number(arguments[0]):
                        browse_type = 'thread_list_index'
                        thread_list_index = int(arguments[0])
                        arguments = arguments[1:]
                        if len(arguments) == 0:
                            page_n = settings['default_thread_page']
                        else:
                            if arguments[0] in ['all', 'last']:
                                page_n = arguments[0]
                                arguments = arguments[1:]
                            else:
                                try:
                                    page_n = int(arguments[0])
                                    arguments = arguments[1:]
                                except:
                                    page_n = settings['default_thread_page']
                            try:
                                sorting = arguments[0]
                            except:
                                pass
                    elif len(arguments) == 1:
                        add_line_('error', 'Requires more arguments')
                        browse_type = 'failed'
                    else:
                        browsing['browsing'] = True
                        browse_type = arguments[0]
                        browse_id = int(arguments[1])
                        arguments = arguments[2:]
                        if len(arguments) == 0:
                            page_n = settings['default_thread_page']
                        else:
                            if arguments[0] in ['all', 'last']:
                                page_n = arguments[0]
                                arguments = arguments[1:]
                            elif len(arguments) == 1:
                                page_n = int(arguments[0])
                            else:
                                sorting = arguments[0]
                                page_n = int(arguments[1])
                if page_n == 'first':  # Because of settings['default_thread_page']
                    page_n = 1
                if browse_type == 'f':
                    forum_category = [key for key in forums if str(browse_id) in forums[key]][0]
                    persistant_bars['title']['content'] = '{}: {}'.format(forum_category,
                                                                          forums[forum_category][str(browse_id)][
                                                                              'title'])
                    persistant_bars['subtitle']['content'] = 'Page {}'.format(str(page_n))
                    last_object_displayed = 'forum'
                    browsing['forum_id'] = browse_id
                    (thread_meta_list, _, securitytoken) = soups.load_forumpage_threadmeta(browsing['forum_id'],
                                                                                           page_n)  # We shouldnt attempt to load all forum pages
                    height_of_current_displayed_obj, scroll_lines, thread_meta_list = display_forum(thread_meta_list,
                                                                                                    sorting=sorting)
                elif browse_type in ['t', 'thread_list_index']:
                    if browse_type == 't':
                        title = '?'
                        page_n = 1
                        thread_id = int(browse_id)
                    else:
                        thread_id = int(thread_meta_list[thread_list_index][
                                            'id'])  # Requires us to have run "browse f $FORUM_ID" before!
                        try:
                            title = thread_meta_list[thread_list_index]['title']
                        except:
                            title = thread_meta_list[thread_list_index]['posts'][0]['title']
                        if general.is_number(page_n):
                            page_n = min(page_n, ceil(thread_meta_list[thread_list_index]['nPosts_claimed'] / 20))
                        if page_n == 'last':
                            page_n = ceil(thread_meta_list[thread_list_index][
                                              'nPosts_claimed'] / 20)  # total number of pages in thread
                    persistant_bars['subtitle']['content'] = '{}: page {}'.format(title, str(page_n))
                    last_object_displayed = 'thread'
                    browsing['thread_id'] = thread_id
                    if page_n == 'all':
                        page_n = ceil(thread_meta_list[thread_list_index][
                                          'nPosts_claimed'] / 20)  # total number of pages in thread
                        if browsing['logged_in']:
                            (posts_list, securitytoken) = soups.load_thread(thread_id, page_n, session=session)
                        else:
                            (posts_list, securitytoken) = soups.load_thread(thread_id, page_n)
                    else:
                        if browsing['logged_in']:
                            (posts_list, securitytoken) = soups.load_thread_page(thread_id, page_n, session=session)
                        else:
                            (posts_list, securitytoken) = soups.load_thread_page(thread_id, page_n)
                    height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list, sorting)
                    username_to_id_new = {post['user']['name']: post['user']['id'] for post in posts_list}
                    username_to_id = dict(username_to_id, **username_to_id_new)  # Combine dicts
                    del username_to_id_new

                    browsing['thread_id'] = thread_id
                    del thread_id

                    if j_meta['forum_id'] != browsing['forum_id']:
                        j = []
                    j = [post for post in j if
                         post['title'] != posts_list[0]['title']]  # So we can replace it with the updated thread
                    j.append({
                        'datetime': posts_list[0]['datetime'],
                        'user': {
                            'name': posts_list[0]['user']['name'],
                            'id': posts_list[0]['user']['id']
                        },
                        'title': posts_list[0]['title'],
                        'nPosts': len(posts_list),
                        'nPosts_claimed': len(posts_list),
                        'posts': posts_list
                    })
            page_n = browsing['page_n']
        elif command == 'login':
            session, account_credentials = login(securitytoken)
        elif command == 'logout':
            logout_url = soups.get_logout_url_from_session(
                session)  # includes the logouthash and everything else required to log out
            session.get(logout_url)
        elif command == 'post':
            status_message = post_comment(session, thread_id=browsing['thread_id'])
        elif command == 'notifications':
            if not browsing['logged_in']:
                session, account_credentials = login(securitytoken)
                browsing['logged_in'] = True
            notifications_and_hrefs = soups.notifications_from_session(session)
            toprint = ''
            height_of_current_displayed_obj = display_tuple_ls(notifications_and_hrefs)
        elif command == 'report':  # Not working yet
            if len(arguments) < 2:
                open_pager('''
                Error:  Requires two arguments

                Descr:  Report a post that breaks site rules

                Usage:
                    report p [post_id]
                    report t [thread_id]')

                Eg:
                    report p 12345678   Report a REPLY with post_id 12345678
                    report t 23456789   Report a THREAD with thread_id of 23456789''')
            else:
                if not browsing['logged_in']:
                    session, account_credentials = login(securitytoken)
                    browsing['logged_in'] = True
                if securitytoken == 'guest':
                    (_, securitytoken) = soups.load_thread_page(browsing['thread_id'], 1, session=session,
                                                                data='report_categories')
                categories = {
                    'postinghelp': {
                        'threadmove': 'Thread in wrong forum',
                        'bump': 'Necroposting',
                        'swearing': 'Swear filter avoidance',
                        'foreignlang': 'Foreign language',
                        'txtspk': 'Textspeak',
                        'anon': 'Misuse of anonymous account'
                    },
                    'offensive': {
                        'hatred': 'Racial or religous hatespeech',
                        'discrimination': 'Discrimination',
                        'bullying': 'Bullying',
                        'harsh': 'Harsh language',
                        'insults': 'Insults',
                        'threats': 'Threats'
                    },
                    'nonconstructive': {
                        'nonconstructive': 'Not constructive'
                    },
                    'adspam': {
                        'advertising': 'Advertising',
                        'officialrep': 'Misuse of Official Rep account',
                        'spam': 'Spam'
                    },
                    'privacy': {
                        'privacy': 'Breach of privacy'
                    },
                    'graphic': {
                        'adult': 'Adult content',
                        'violence': 'Promoting violence'
                    },
                    'illegal': {
                        'copyright': 'Copyright infringement',
                        'drugs': 'Drug use',
                        'otherillegal': 'Other illegal activity'
                    },
                    'safety': {
                        'selfharm': 'Referencing self-harm',
                        'suicide': 'Suicide',
                    },
                    'offtopic': {
                        'offtopic': 'Off-topic comment'
                    },
                    'examdetails': {
                        'examdetails': 'Sharing exam/interview details'
                    }
                }
                data = {
                    'securitytoken': securitytoken,
                    'do': 'doadd',
                    'type': 'post',
                    'primaryid': arguments[0],
                    'message': arguments[1]
                }
                categories_strs = []
                toprint = ''
                for entry in categories:
                    for key in categories[entry]:
                        categories_strs.append(key)
                        toprint += general.make_n_char_long(key, 30) + categories[entry][key]
                open_pager(toprint)
                category = ''
                cancel_action = True
                while category not in categories_strs + ['cancel']:
                    category = input('Category:    ')
                    if category == 'cancel':
                        cancel_action = False
                        break
                if not cancel_action:
                    for entry in categories:
                        for key in categories[entry]:
                            if key == category:
                                if key == entry:
                                    data['category'] = [key]
                                else:
                                    data['category'] = [entry, key]
                    url = 'https://www.thestudentroom.co.uk/report.php'
                    session.post(url, data)
        elif command == 'rep':
            if len(arguments) == 0:
                open_pager('''
                Error:  Requires at least one argument

                Descr:  Award rep to a helpful post

                Usage:  rep [post_id]''')
            elif len(arguments) == 1:
                if not browsing['logged_in']:
                    session, account_credentials = login(securitytoken)
                    browsing['logged_in'] = True
                if securitytoken == 'guest':
                    (_, securitytoken) = soups.load_thread_page(browsing['thread_id'], 1, session=session)
                data = {
                    'securitytoken': securitytoken,
                    'do': 'helpfulanswer',
                    'using_ajax': '1',
                    'rank': '1',
                    'p': arguments[0]
                }
                url = 'https://www.thestudentroom.co.uk/helpfulanswers.php'
                session.post(url, data)
        elif command == 'register':  # Not implemented yet (requires CSS for human verification)
            if len(arguments) != 2:
                open_pager('''
                Error:  Requires at least two arguments

                Descr:  Register a new account

                Usage:  register [username] [password]''')
            elif len(arguments) == 2:
                data = {
                    'securitytoken': securitytoken,
                    'do': 'addmember',
                    'url': 'forum.php',
                    'gpu': '0',
                    'direct': '0',
                    'survey': '0',
                    'username': prompt_input('Username:    '),
                    'password': prompt_input('Password:    '),
                    'year': prompt_input('BIRTH: Year:    '),
                    'month': prompt_input('BIRTH: Month:    '),
                    'day': prompt_input('BIRTH: Day:    '),
                    'agree': '1',
                    'emailoptin': '1',  # 1 seems to mean 'opt out'.
                    'humanverify': {
                        'hash': '',
                        'input': ''
                    }
                }
                session = session_post('register.php', data, logout=True, login=False)
        elif command == 'account':  # Not working yet
            if arguments[0] == 'info':
                if len(arguments) == 0:
                    open_pager('''
                    Requires at least one argument

                    Rep: Award rep to a helpful post

                    Usage:
                        rep [post_id]
                    ''')
                elif len(arguments) == 1:
                    if not browsing['logged_in']:
                        session, account_credentials = login(securitytoken)
                        browsing['logged_in'] = True
                    list_of_flags, securitytoken = soups.get_list_of_flags_and_security_token(session)
                    data = {
                        'securitytoken': securitytoken,
                        'do': 'updateprofile'
                    }
                    data['showbirthday'] = input('Show birthday? 1=yes, 0=no:    ')
                    data['customtext'] = input('Custom user title:    ')
                    data['homepage'] = input('Your website/blog/etc homepage (if any):    ')
                    data['userfield'] = {}
                    data['userfield']['field1'] = input('About me:    ')
                    data['userfield']['field2'] = input('Location of residence:    ')
                    data['userfield']['field8'] = input('Sex (1:M, 2:F, 3:None):    ')
                    if data['userfield']['field8'] == '3':
                        data['userfield']['sexprivacy'] = '0'
                    else:
                        data['userfield']['sexprivacy'] = '1'
                    data['userfield']['field10'] = input('Location of study:    ')
                    data['userfield']['field11'] = input('Academic info:    ')
                    data['userfield']['field12'] = input('Name:    ')
                    data['userfield']['field16'] = input('Custom section:  Title:    ')
                    data['userfield']['field17'] = input('Custom section: Content:    ')
                    data['userfield']['field21'] = input('Sexual orientation:    ')
                    # Now to choose a flag, from too many options

                    open_pager('\n'.join(['  '.join(l) for l in list_of_flags]))  # Display scrolling list of flags
                    data['userfield']['field9'] = input('Flag ID:    ')

                    data['userfield']['field1_set'] = '1'
                    data['userfield']['field2_set'] = '1'
                    data['userfield']['field8_set'] = '1'
                    data['userfield']['field9_set'] = '1'
                    data['userfield']['field10_set'] = '1'
                    data['userfield']['field11_set'] = '1'
                    data['userfield']['field12_set'] = '1'
                    data['userfield']['field16_set'] = '1'
                    data['userfield']['field17_set'] = '1'
                    data['userfield']['field21_set'] = '1'

                    url = 'https://www.thestudentroom.co.uk/profile.php?do=updateprofile'
                    request = session.post(url, data)
                    os_info.writeif(os_info.path.log, request.text, settings['readonly'], append=True)
                    del request
        elif command in ['edit', 'delete']:
            if len(arguments) < 1:
                open_pager('''
                Requires at least one argument')

                edit [post_id] [new_content] [reason]?
                delete [post_id] [reason]?''')
            else:
                if not browsing['logged_in']:
                    session, account_credentials = login(securitytoken)
                    browsing['logged_in'] = True
                post_id = arguments[0]
                if command == 'edit':
                    message = arguments[1]
                    arguments = [arguments[0], arguments[1]]
                if len(arguments) > 2:
                    reason = arguments[2]
                else:
                    reason = ''
                securitytoken, posthash = soups.get_securitytoken_and_posthash_from_url(session,
                                                                                        'https://www.thestudentroom.co.uk/editpost.php?p={0}&do=editpost'.format(
                                                                                            post_id))
                if command == 'edit':
                    data = {
                        'securitytoken': securitytoken,
                        'do': 'updatepost',
                        'emailupdate': '0',
                        'parseurl': '1',
                        'reason': reason,
                        'p': post_id,
                        'posthash': posthash,
                        'message': message
                    }
                    url = 'https://www.thestudentroom.co.uk/editpost.php?do=updatepost'
                elif command == 'delete':
                    data = {
                        'securitytoken': securitytoken,
                        'do': 'deletepost',
                        'reason': reason,
                        'p': post_id,
                        'posthash': posthash,
                        'deletepost': 'delete'
                    }
                    url = 'https://www.thestudentroom.co.uk/editpost.php?do=deletepost'
                session.post(url, data)
        elif command == 'load':  # in commands['forumdisplay']['commands']['forum']['alts']: # Not elif, so that previous forum can be returned to easily
            if len(arguments) == 0:
                open_pager('''
                Error:  Requires at least one argument')

                Usage:  load [forum/f/user/u] [forumid/username] [options]?

                Eg:
                        load f 143')
                        load u MrUsername
                        load f 63 --force       (to reload even if it is already loaded)''')
            else:
                browsing[
                    'browsing'] = False  # So we can load more meta information when displaying the forum-like object
                command = arguments[0]
                arguments = arguments[1:]
                failed = True
                if command in ['f', 'forum']:
                    last_object_displayed = 'forum'
                    forum_type = 'forum'
                    try:
                        forum_id = str(int(arguments[0]))
                        failed = False
                    except:
                        list_forum_ids()
                elif command in ['u', 'user', 'username']:
                    last_object_displayed = 'forum'
                    forum_type = 'userid'
                    failed = False
                    try:
                        forum_id = str(username_to_id[arguments[0]])
                    except:
                        try:
                            forum_id = str(int(arguments[0]))
                        except:
                            open_pager('''
                    Error:  No userid found for username

                    Try loading the forum, or browsing a thread, in which the user was active, and then executing, to expand the list of userids''')
                            failed = True
                if not failed:
                    persistant_bars['title']['content'] = '{}:    {}'.format(command, arguments[0])
                    persistant_bars['subtitle']['content'] = 'Cache'
                    try:
                        number_of_threads = int(arguments[1])
                        try:
                            sorting = arguments[2]
                        except:
                            sorting = 'datetime'
                    except:
                        number_of_threads = 500
                        try:
                            sorting = arguments[1]
                        except:
                            sorting = 'datetime'
                    if (forum_id, number_of_threads, sorting) != (
                    j_meta['forum_id'], j_meta['number'], j_meta['sorting']):
                        if ('--force' in arguments) | (
                                (forum_id, number_of_threads) != (j_meta['forum_id'], j_meta['number'])):
                            (_, _, _, _, j_forum, username_to_id_new) = load_forum_database(forum_type, forum_id,
                                                                                            max_threads=number_of_threads,
                                                                                            sorting=sorting,
                                                                                            load_threads=True)
                            username_to_id = dict(username_to_id, **username_to_id_new)  # Combine dicts
                            del username_to_id_new
                            j_meta['forum_id'] = forum_id
                            j_meta['number'] = number_of_threads
                        j_meta['sorting'] = sorting
                    j = j_forum
                    height_of_current_displayed_obj, scroll_lines, j = display_forum(j, sorting=sorting)
        elif command == 'filter':
            if len(arguments) < 2:
                open_pager('''
                Error:  Requires at least two arguments')

                Descr:  Discard all posts in the forum which do not match the filter

                Usage:  filter [postAttribute/"user"+userattribute] [attributeValue]

                Eg:     filter user MrUsername''')
            else:
                filter_attr = arguments[0]
                attr_is_user_attr = False
                if filter_attr[:4] == 'user':
                    filter_attr = filter_attr[4:]
                    attr_is_user_attr = True
                filter_value = arguments[1]
                try:
                    sorting = arguments[2]
                except:
                    sorting = 'datetime'
                j = []
                for thread in j_forum:
                    thread_new = {x: thread[x] for x in thread if x != 'posts'}
                    thread_new['posts'] = []
                    for post in thread['posts']:
                        if attr_is_user_attr:
                            if filter_attr in post['user']:
                                if post['user'][filter_attr] == filter_value:
                                    thread_new['posts'].append(post)
                        else:
                            if filter_attr in post:
                                if post[filter_attr] == filter_value:
                                    thread_new['posts'].append(post)
                    if len(thread_new['posts']) > 0:
                        j.append(thread_new)
                height_of_current_displayed_obj, scroll_lines, j = display_forum(j, sorting=sorting)
        elif command == 't':
            if len(arguments) == 0:
                open_pager('''
                Error:  Requires at least one argument

                Usgae:  t [thread_id]''')
            else:
                thread_id = int(arguments[0])
                posts_list = [thread for thread in j if j[thread]['id'] == thread_id][0]
                height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(dummy, arguments)
        elif command in ['byday', 'bydate']:
            if len(arguments) == 0:
                open_pager('''
                Error:  Requires at least one argument

                Descr:  Display statistics about a certain post attribute.

                Usage:  byday [postAttribute]

                postAttributes include: word noun title user quote domain

                Eg:
                    byday username
                    byday word
                    byday noun''')
            else:
                words_to_ignore = regex.words_to_ignore + ['png', 'jpg', 'jpeg', 'gif', 'webm', 'mp4']
                try:
                    attr = arguments[0]
                    if attr[:4] == 'user':
                        attr_is_user_attr = True
                        attr = attr[4:]
                    else:
                        attr_is_user_attr = False
                except:
                    attr = 'word'
                dates = []
                for thread in j:
                    for post in thread['posts']:
                        dates.append(general.standardise_date(
                            post['datetime']))  # not sure why it has been failing on one forum and not the other
                dates = set(dates)  # rm duplicates
                dates = sorted(dates, reverse=True)  # Most recent first
                words_counters = {}
                words_counter_monthly = Counter([])
                toprint_monthly = []
                # toprint_tuple_ls=[]
                toprint = ''
                current_line_y = 0
                mainpad.clear()

                if attr in ['word', 'title', 'noun', 'user', 'quote',
                            'quoted']:  # Untagged usernames share the word dictionary with words.
                    colour_dict = dict(
                        words_colour_dict)  # Dont want changes to be saved in words_colour_dict, which might be saved to disk
                elif attr in ['domain']:
                    colour_dict = dict(domain_colour_dict)

                scroll_lines = [0]
                for i in range(len(dates)):
                    date = dates[i]
                    words_counter = Counter([])
                    current_line_y += 2
                    scroll_lines.append(current_line_y)
                    mainpad.addstr(current_line_y, 0, str(date)[:10], str2colour['date'])
                    current_line_x = 11
                    for thread in j:
                        for post in thread['posts']:
                            if date == general.standardise_date(post[
                                                            'datetime']):  # Do NOT use "is" instead of "==". Will only return first post for each date.
                                if attr_is_user_attr:
                                    words = [post['user'][attr]]
                                else:
                                    content = '\n'.join([x['content'] for x in post['contents'] if x[
                                        'type'] != 'quote'])  # We don't want to muddle the results by including quotes
                                    if attr == 'word':
                                        words = regex.ls_words(content)
                                    elif attr == 'noun':
                                        if use_nltk:
                                            content = ' '.join(re.split(regex.between_words, content))
                                            words_nltk_tokenised = nltk.word_tokenize(content)
                                            words_nltk_tagged = nltk.pos_tag(words_nltk_tokenised)

                                            words_nltk_tagged = [(w[0].lower(), w[1]) for w in words_nltk_tagged]

                                            nouns = [w[0] for w in words_nltk_tagged if w[1] == 'NN']
                                            verbs = [w[0] for w in words_nltk_tagged if w[1] in ['VBG', 'VB']]
                                            misc = [w[0] for w in words_nltk_tagged if w[1] == 'JJ']
                                            stemmer = nltk.PorterStemmer()
                                            nouns = [stemmer.stem(w) for w in nouns]
                                            verbs = [stemmer.stem(w) for w in verbs]
                                            misc = [stemmer.stem(w) for w in misc]
                                            words = nouns + verbs + misc
                                            words = [w for w in words if (len(w) > 2) & (w not in words_to_ignore)]
                                        else:
                                            open_pager(
                                                'Error:   nltk modules nltk.word_tokenize, nltk.pos_tag, nltk.PorterStemmer not installed')
                                            words = []
                                    elif attr == 'title':
                                        words = re.split(regex.between_words_title, post['thread']['title'])
                                        words = [w.lower() for w in words]
                                        words = [singularise(w) for w in words if
                                                 (len(w) > 2) & (w not in words_to_ignore)]
                                    elif attr == 'domain':
                                        words = regex.findall_domains(content)
                                    elif attr in ['quote', 'quotes']:
                                        words = [x['user'] for x in post['quotes']]
                                words_counter = words_counter + Counter(words)
                    words = []
                    words_countls = [(words_counter[x], x) for x in
                                     words_counter]  # list of tuples (username, #occurances)
                    results = sorted(words_countls, key=lambda x: x[0], reverse=True)[:10]
                    # result=' '.join(results)
                    n_colour = 0
                    for tpl in results:
                        word = tpl[1]
                        freq = tpl[0]
                        if word not in words_colour_dict:
                            if 'only-tagged' not in arguments:
                                colour_dict[word] = cl_to_assign[n_colour % len(cl_to_assign)]
                                n_colour += 1
                            else:
                                colour_dict[word] = 'default'
                        mainpad.addstr(current_line_y, current_line_x, word, str2colour[colour_dict[word]])
                        mainpad.addstr(current_line_y + 1, current_line_x, str(freq), str2colour[colour_dict[word]])
                        current_line_x += len(word) + 1
                    words_counter_monthly = words_counter_monthly + words_counter
                    words_counter = Counter([])

                    print_monthly_counter = False
                    if i + 1 == len(dates):
                        print_monthly_counter = True
                    elif date.month != dates[i + 1].month:
                        print_monthly_counter = True
                    if print_monthly_counter:
                        words_countls = [(words_counter_monthly[x], x) for x in
                                         words_counter_monthly]  # list of tuples (username, #occurances)
                        results = sorted(words_countls, key=lambda x: x[0], reverse=True)[:10]
                        n_colour = 0
                        toprint_monthly.append((str(date.year) + '-' + str(date.month), results))
                        words_counter_monthly = Counter([])
                for tupl in toprint_monthly:  # So we get monthly results after the daily results
                    current_line_y += 2
                    scroll_lines.append(current_line_y)
                    mainpad.addstr(current_line_y, 0, tupl[0], str2colour['date'])
                    current_line_x = 10
                    for tpl in tupl[1]:
                        word = tpl[1]
                        freq = tpl[0]
                        if word not in colour_dict:
                            if 'only-tagged' not in arguments:
                                colour_dict[word] = cl_to_assign[n_colour % len(cl_to_assign)]
                                n_colour += 1
                            else:
                                colour_dict[word] = 'default'
                        mainpad.addstr(current_line_y, current_line_x, word, str2colour[colour_dict[word]])
                        mainpad.addstr(current_line_y + 1, current_line_x, str(freq), str2colour[colour_dict[word]])
                        current_line_x += len(word) + 1
        elif command in ['grep', 'egrep']:
            if len(arguments) == 0:
                open_pager('''
                Error: Requires at least one argument.

                Usage: [grep/egrep] [pattern]

                eg: grep exam
                grep "biology exam"
                egrep "(aqa|AQA) [bB]iology"''')
            else:
                posts_list = []
                search_string = arguments[0]
                if command == 'egrep':
                    regexp = re.compile(search_string)
                for thread in j:
                    for post_old in thread['posts']:
                        post = dict(post_old)
                        print_post = False
                        for content_type in post['contents']:
                            post_content = content_type['content']
                            post_contents = post_content.split('\n')
                            for line in post_contents:
                                if len(line) > 0:
                                    if line[0] != '>':
                                        if command == 'grep':
                                            if search_string in line:
                                                print_post = True
                                                content_type['content'] = content_type['content'].replace(search_string,
                                                                                                          '@@@grep~~~~~~' + search_string + '@@@default~~~')
                                        if command == 'egrep':
                                            if regexp.search(line):
                                                print_post = True
                                                content_type['content'] = re.sub(r'({0})'.format(search_string),
                                                                                 r'{0}\1{1}'.format('@@@grep~~~~~~',
                                                                                                    '@@@default~~~'),
                                                                                 content_type['content'],
                                                                                 flags=re.MULTILINE)  # For this line, I must acknowledge Martijn Pieters for his helpful answer on StackOverflow.
                        if print_post:
                            posts_list.append(post)
                height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list)
        elif command == 'ifrep':  # eg "reps >10" to show all posts with rep > 10, "reps" to show all posts sorted by rep
            if len(arguments) < 2:
                open_pager('''
                Error:  Requires at least two arguments

                Usage:  ifrep [equivalence relation] [number]

                Eg:
                        ifrep > 30
                        ifrep = 10''')
            else:
                equivalence = arguments[0]
                n = int(arguments[1])
                posts_list = []
                for thread in j:
                    for post in thread['posts']:
                        print_post = False
                        if equivalence == '>':
                            if post['reps'] > n:
                                print_post = True
                        elif equivalence == '<':
                            if post['reps'] < n:
                                print_post = True
                        elif equivalence in ['=', '==']:
                            if post['reps'] == n:
                                print_post = True
                        if print_post:
                            posts_list.append(post)
                height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list)
        elif command == 'debug':
            if arguments[0] == 'path':
                open_pager('paths = ' + str(os_info.paths))  # The dictionary of paths that the path class is built from
            elif arguments[0] == 'dict':
                if arguments[1] == 'users':
                    open_pager(str(users))
        elif command == 'sort':  # Sort current displayed object by an attribute
            if len(arguments) == 1:
                sorting = arguments[0]
                if last_object_displayed == 'thread':
                    height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list, sorting)
                elif last_object_displayed == 'forum':
                    if browsing['browsing']:
                        height_of_current_displayed_obj, scroll_lines, thread_meta_list = display_forum(
                            thread_meta_list, sorting=sorting)
                    else:
                        height_of_current_displayed_obj, scroll_lines, j = display_forum(j, sorting=sorting)
            else:
                open_pager('''
                Error:  Requires one argument

                Usage:  sort [attribute]

                Attributes include:
                        username
                        userid
                        userreps
                        reps    (reps of post)
                        datetime''')
        else:
            if general.is_number(command):
                n = int(command)
                try:
                    sorting = arguments[0]
                except:
                    sorting = 'datetime'
                attr_is_user_attr = False
                if sorting[:4] == 'user':
                    attr_is_user_attr = True
                    sorting = sorting[4:]
                posts_list = j[n]['posts']
                if attr_is_user_attr:
                    posts_list = sorted(posts_list, key=lambda x: x['user'][sorting],
                                        reverse=True)  # Highest at the top
                else:
                    posts_list = sorted(posts_list, key=lambda x: x[sorting], reverse=True)
                height_of_current_displayed_obj, scroll_lines, posts_list = display_posts(posts_list)
                last_object_displayed = 'thread'
            else:
                pass


def main():
    curses.wrapper(mainbody)


if __name__ == "__main__":
    main()
