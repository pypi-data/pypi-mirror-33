import datetime, json
from .os_info import path
import os.path
from dateutil.relativedelta import relativedelta # Since datetime now refuses to work with months and years

users={}
username_colour_dict={} # temporary colour scheme for users without flairs/colours, for easier reading
username_to_id={}
users=json.load(open(os.path.join(path.settings, 'users.json')))
for entry in users:
    if 'colour' not in users[entry]:
        users[entry]['colour']='end'
settings=json.load(open(os.path.join(path.settings, 'settings.json')))



def level_domain(level, domain):
    if not is_int(level):
        raise ValueError('level_domain(level_number, domain_string)')
    neglevel=-int(level)
    return '.'.join(domain.split('.')[neglevel:])



def dictfind(original_dict, **kwargs):
    ''' eg
    >>>d={
        'foo':{
            'bar': 11,
            'bob': 'george',
        },
        'gimli':{
            'gandalf':{
                'frodo':5,
                'samwise':7,
            },
            'radagast':11,
        },
        'jones':{
            'gandalf':{
                'frodo':1,
                'samwise':2,
            },
            'radagast':3,
        },
    }
    >>>find(d, bar='>5')
    ['foo']
    >>>find(d, gandalf_frodo='>3')
    ['gimli']
    '''
    # NB foo='*bar*' will not work
    ListOnlyKeys=True
    if '_ListOnlyKeys' in kwargs:
        ListOnlyKeys=kwargs['_ListOnlyKeys']
    d=dict(original_dict) # Apparently dicts are automatically global
    for kw in kwargs:
        if kw[0]!='_':
            kw_value=kwargs[kw]
            kw_relation=None
            if kw_value[0] in ['*', '>', '<', '=']:
                kw_relation=kw_value[0]
                kw_value=kw_value[1:]
            kw_relation_end=None
            if kw_value[-1] in ['*']:
                kw_relation_end=kw_value[-1]
                kw_value=kw_value[:-1]
            new_d={}
            key0=None
            if '_' in kw:
                key0=kw.split('_')[0]
                key1=kw.split('_')[1]
                for key in d:
                    if key0 in d[key]:
                        '''for key in d[key0]:
                            if kw_relation=='*':
                                if key.startswith(kw_value):
                                    new_d[key]=d[key]
                            elif kw_relation_end=='*':
                                if key.endswith(kw_value):
                                    new_d[key]=d[key]'''
                        if key1 in d[key][key0]:
                            this_value=d[key][key0][key1]
                            if kw_relation=='>':
                                kw_value=int(kw_value)
                                if this_value>kw_value:
                                    new_d[key]=d[key]
                            elif kw_relation=='<':
                                kw_value=int(kw_value)
                                if this_value>kw_value:
                                    new_d[key]=d[key]
                            elif kw_relation=='=':
                                if this_value==kw_value:
                                    new_d[key]=d[key]
                '''Following elif segment is more efficient (since not check each loop), but worse code'''
            elif kw_relation_end=='*':
                kw_value=kw_value[:-1]
                for key in d:
                    if key.startswith(kw_value):
                        new_d[key]=d[key]
                    #if key.startswith(kw_value):
                    #    ls.append( key )
            elif kw_relation=='*':
                kw_value=kw_value
                for key in d:
                    if key.endswith(kw_value):
                        new_d[key]=d[key]
                        #ls.append( key )
            elif kw_relation=='>':
                kw_value=int(kw_value)
                for key in d:
                    if d[key][kw]>kw_value:
                        print('       {}>{}'.format(d[key][kw], kw_value), end='\r')
                        new_d[key]=d[key]
                        #ls.append( key )
            elif kw_relation=='<':
                kw_value=int(kw_value)
                for key in d:
                    if d[key][kw]<kw_value:
                        new_d[key]=d[key]
                        #ls.append( key )
            else:
                for key in d:
                    if d[key][kw]==kw_value:
                        new_d[key]=d[key]
            
            d=dict(new_d)
    if ListOnlyKeys:
        return [key for key in d]
    else:
        return d


def userid_colour(userid):
    if type(userid)!='str':
        userid=str(userid)
    try:
        return users[userid]['colour']
    except:
        raise Exception('userid {0} has no colour. users[{0}] = {1}'.format(userid, users[userid]))


def make_n_char_long(x, n, spacing=' '):
    y=str(x)
    while len(y)<n:
        y+=spacing
    if len(y)>n:
        y=y[:n]
    return y


def myjoin(*args):
    string=''
    for arg in args:
        string+='  '+str(arg)
    return string[2:]


def standardise_datetime(datestr):
    if isinstance(datestr, datetime.datetime):
        return datestr
    elif isinstance(datestr, datetime.date):
        return datetime.datetime.combine(datestr, datetime.time(0, 0)) # Sets to midnight
    try:
        return datetime.datetime.strptime(datestr, '%d-%m-%Y')
    except:
        try:
            return datetime.datetime.strptime(datestr, '%Y-%m-%d')
        except:
            datestr=datestr.strip().lower()
            if datestr=='yesterday':
                return datetime.datetime.now()-datetime.timedelta(days=1)
            elif 'ago' in datestr:
                date_ls=datestr.split(' ')
                #print(date_ls)
                try:
                    n=int(date_ls[0])
                    formatIs_n_obj_ago=True
                except:
                    formatIs_n_obj_ago=False
                if formatIs_n_obj_ago:
                    date_type=date_ls[1]
                    if date_type in ['second', 'seconds']:
                        return datetime.datetime.now()-datetime.timedelta(seconds=n)
                    elif date_type in ['minute', 'minutes']:
                        return datetime.datetime.now()-relativedelta(minutes=n)
                    elif date_type in ['hour', 'hours']:
                        return datetime.datetime.now()-relativedelta(hours=n)
                    elif date_type in ['day', 'days']:
                        return datetime.datetime.now()-datetime.timedelta(days=n)
                    elif date_type in ['week', 'weeks']:
                        return datetime.datetime.now()-datetime.timedelta(days=n*7)
                    elif date_type in ['month', 'months']:
                        return datetime.datetime.now()-relativedelta(months=n)
                    elif date_type in ['year', 'years']:
                        return datetime.datetime.now()-relativedelta(years=n)
                    elif date_type in ['decade', 'decades']:
                        return datetime.datetime.now()-relativedelta(years=n*10)
            else:
                for char in ['T', ' ', '_']:
                    if len(datestr)>18: # So probably includes seconds
                        try:
                            try:
                                datestr=datestr[:19] # Remove the trailing +00:00
                                return datetime.datetime.strptime(datestr, '%Y-%m-%d'+char+'%H:%M:%S')
                            except:
                                datestr=datestr[:19] # Remove the trailing +00:00
                                return datetime.datetime.strptime(datestr, '%d-%m-%Y'+char+'%H:%M:%S')
                        except:
                            pass
                    else:
                        try:
                            try:
                                return datetime.datetime.strptime(datestr, '%Y-%m-%d'+char+'%H:%M')
                            except:
                                return datetime.datetime.strptime(datestr, '%d-%m-%Y'+char+'%H:%M')
                        except:
                            pass
    raise Exception('Unknown datetime string: '+str(datestr))


def standardise_datetime_str(datestr):
    return str(standardise_datetime(datestr))


def standardise_date(string):
    return standardise_datetime(string).date()


def standardise_date_str(datestr):
    return str(standardise_date(datestr))


def standardise_time(timestr):
    return datetime.datetime.strptime(timestr, '%H:%M').time()


def is_number(x):
    try:
        dummy=float(x)
        return True
    except:
        return False

def is_int(x):
    try:
        dummy=int(x)
        return True
    except:
        return False

def ls_rm_dupl(ls): # Useful to have rather than list(set(, since it preserves order. Perhaps sorted(list(set( would be more performative, I will look into this eventually.
    l=[]
    for x in ls:
        if x not in l:
            l.append(x)
    return l


def ls_in_str(ls,string):
    for element in ls:
        try:
            if element in string:
                return True
        except:
            pass
    return False


def mystrip(text):
    while '  ' in text:
        text=text.replace('  ',' ')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    while ' \n' in text:
        text=text.replace(' \n','\n')
    while '\n ' in text:
        text=text.replace('\n ','\n')
    while '\n> > ' in text:
        text=text.replace('\n> > ','\n> ')
    while '>\n' in text:
        text=text.replace('>\n','')
    while '~\n' in text:
        text=text.replace('~\n','\n')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    while '\r\n' in text:
        text=text.replace('\r\n','\n')
    while '\n\r' in text:
        text=text.replace('\n\r','\n')
    while '\n\n' in text:
        text=text.replace('\n\n','\n')
    return text.strip()
