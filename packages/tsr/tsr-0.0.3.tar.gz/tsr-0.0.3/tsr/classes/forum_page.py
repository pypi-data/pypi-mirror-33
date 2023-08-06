import forumload, soups

class ForumPage(**kwargs):
    def __init__(self, **kwargs):
        if 'browse' in kwargs:
            if kwargs['browse']:
                if ('url' in kwargs)&('forum_id' in kwargs):
                    url=kwargs['ur']
                else:
                    url='https://www.thestudentroom.co.uk/forumdisplay?f='+str(kwargs['forum_id'])
                if 'page_n' in kwargs:
                    page_n=kwargs['page_n']
                else:
                    page_n=1
                
                (self.threads, _, securitytoken)=load_forumpage_threadmeta(kwargs['forum_id'], page_n)
