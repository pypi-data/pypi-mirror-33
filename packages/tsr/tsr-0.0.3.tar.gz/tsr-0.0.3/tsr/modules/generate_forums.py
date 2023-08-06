from bs4 import BeautifulSoup
import requests, os.path
from . import os_info # for jdump, path


def main():
    forum_dict = {}

    forum_php = requests.get('https://www.thestudentroom.co.uk/forum.php')
    soup = BeautifulSoup(forum_php.text, 'html.parser')

    categories = soup.find_all('table', {'class': 'forum-category'})
    for category in categories:
        category_title = category.find('th', {'class': 'title'}).find('a').text.strip()
        forum_dict[category_title] = {}
        forums = category.find_all('tr', {'class': 'forum'})
        forums = [f for f in forums if f.find('div', {'class': 'description'})]
        for f in forums:
            title = f.find('a').text.strip()
            forum_id = int(f.find('td', {'class': 'info'})['id'][1:])
            nPosts_tag = f.find('td', {'class': 'count'})
            if nPosts_tag:
                nPosts = int(nPosts_tag.text.strip().replace(',', ''))
            else:
                nPosts = -1
            desc = f.find('div', {'class': 'description'}).text.strip()
            forum_dict[category_title][forum_id] = {
                'title': title,
                'id': forum_id,
                'nPosts': nPosts,
                'desc': desc,
            }
    os_info.jdump(forum_dict, os.path.join(os_info.path.settings, 'forums.json'))
