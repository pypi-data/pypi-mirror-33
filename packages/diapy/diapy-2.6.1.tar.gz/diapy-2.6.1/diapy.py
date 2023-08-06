import datetime
import hashlib
import base64
from cryptography.fernet import Fernet
import os
import pickle
import zlib
import pickletools
import re
from urllib import request
import json
import random
import getpass

__version__ = 'Release 2.6.1'


class Diary(object):
    # Class the instance which will be returned in get function.
    class DiarySpecific(object):
        def __init__(self, content, tags, mood, date, time, location, weather, temperature):
            self.content = content
            self.tags = tags
            self.mood = mood
            self.date = date
            self.time = time
            self.location = location
            self.weather = weather
            self.temperature = temperature

        def __str__(self):
            r = ''

            # Calculate date and weekday.
            date = datetime.datetime.strptime(self.date, '%Y%m%d')
            date = datetime.date(date.year, date.month, date.day)
            week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            r += 'Date: ' + str(date) + ' ' + week[datetime.date.weekday(date)] + '\n'
            r += 'Time: ' + self.time + '\n'
            r += 'Location: ' + str(self.location) + '\n'
            r += 'Weather: ' + self.weather + '\n'
            r += 'Temperature: ' + str(self.temperature) + ' Degree Celsius\n'
            r += 'Mood: ' + self.mood + '\n'
            r += 'Tags: ' + str(self.tags) + '\n'
            r += 'Content: ' + self.content
            return r

        __repr__ = __str__

    def __init__(self, path):
        self.path = path

        # Call several function to open file.
        self._input_pwd('Please input the main password: ')
        self._open_file()
        self.check()

    def __getitem__(self, item):
        return self.get(item)

    def _input_pwd(self, text):
        # Input password.
        pwd = getpass.getpass(text)

        # Process password to key.
        self._key = base64.urlsafe_b64encode(hashlib.sha256(pwd.encode('utf-8')).digest())

    def change_pwd(self):
        self.check()
        self._input_pwd('Please input the new password: ')
        self._status = 'Unsaved'

    def _crypt(self, mode, text):
        f = Fernet(self._key)
        if mode in ['Encrypt', 'e', 'E', 'encrypt']:
            return f.encrypt(text)
        if mode in ['Decrypt', 'd', 'D', 'decrypt']:
            return f.decrypt(text)

    def _open_file(self):
        # Extract data.
        if not os.path.exists(self.path):
            with open(self.path, 'wb'):
                pass
        with open(self.path, 'rb') as f:
            text = f.read()

        # Check if this is a new file.
        if text == b'':
            info = input('Diary info: ')
            self._content = {'info': info, 'date': str(datetime.date.today()),
                             'version': __version__, 'data': {}}
            self._status = 'Unsaved'
        else:
            text = self._crypt('d', base64.urlsafe_b64encode(text))
            self._content = pickle.loads(zlib.decompress(text))

            # Print information.
            print(f'diapy {__version__}')
            print('File:', self._content['info'], self._content['date'])

            self._status = 'Saved'

    def save(self):
        self.check()

        # Edit version.
        if self._content['version'] != __version__:
            self._content['version'] = __version__
        with open(self.path, 'wb') as f:
            # Dump, optimize, compress, encrypt, decode.
            f.write(base64.urlsafe_b64decode(self._crypt('e', zlib.compress(
                pickletools.optimize(pickle.dumps(self._content, 4))))))
        self._status = 'Saved'

    def close(self):
        # Check if saved.
        if self._status == 'Unsaved':
            print('Do you want to save the file before closing it?(y/n/c(cancel))')
            c = input()
            if c == 'y':
                self.save()
            elif c == 'c':
                return

        # Delete data.
        self._key = None
        self._content = None
        self._status = 'Closed'

    def check(self):
        if self._status == 'Closed':
            raise ValueError('File closed.')
        elif not hasattr(self, '_key') or not isinstance(self._key, bytes):
            raise ValueError('Key error.')
        elif not hasattr(self, '_content') or not isinstance(self._content, dict):
            raise ValueError('Context error.')
        else:
            # Version check.
            v = self._content.get('version')
            if not v:
                v = self._content['info']
                v = v[v.rfind(' ', 0, v.rfind(' ')) + 1:]
            if v != __version__:
                print(f'''Warning: File created by DMS v{v} may not be open properly on current version.
Please adjust the file manually.
If you update the file correctly, the version will auto change into current one while saving.
You can use the export_all() and import_all() to export/import data.''')
                self._status = 'Unsaved'
            return self._status

    def get(self, dates):
        self.check()

        if isinstance(dates, int):
            dates = str(dates)
        if isinstance(dates, str):
            if self._content['data'].get(dates) is None:
                return None
            d = self._content['data'][dates]
            return self.DiarySpecific(d['content'], d['tags'], d['mood'], dates, d['time'],
                                      d['location'], d['weather'], d['temperature'])
        else:
            # Get several dates in a list.
            r = []
            for date in dates:
                r.append(self.get(date))
            return r

    def ls(self, mode=None, value=None, specific=True):
        self.check()
        r = {}

        # Check the value.
        if isinstance(value, int):
            value = str(value).zfill(2)

        if mode == 'year':
            if value is None:
                for k in self._content['data']:
                    if k[:4] not in r:
                        r[k[:4]] = [k]
                    else:
                        r[k[:4]].append(k)
            else:
                for k in self._content['data']:
                    if k[:4] == value:
                        if k[4:6] not in r:
                            r[k[4:6]] = [k]
                        else:
                            r[k[4:6]].append(k)
        elif mode == 'month':
            if value is None:
                for k in self._content['data']:
                    if k[4:6] not in r:
                        r[k[4:6]] = [k]
                    else:
                        r[k[4:6]].append(k)
            else:
                for k in self._content['data']:
                    if k[6:] == value:
                        if k[6:] not in r:
                            r[k[6:]] = [k]
                        else:
                            r[k[6:]].append(k)
        elif mode == 'date':
            if value is None:
                for k in self._content['data']:
                    if k[6:] not in r:
                        r[k[6:]] = [k]
                    else:
                        r[k[6:]].append(k)
            else:
                for k in self._content['data']:
                    if k[6:] == value:
                        if k[6:] not in r:
                            r[k[6:]] = [k]
                        else:
                            r[k[6:]].append(k)
        elif mode == 'tags':
            if value is None:
                for k in self._content['data']:
                    for t in self._content['data'][k]['tags']:
                        if t not in r:
                            r[t] = [k]
                        else:
                            r[t].append(k)
            else:
                for k in self._content['data']:
                    for t in self._content['data'][k]['tags']:
                        if t == value:
                            if t not in r:
                                r[t] = [k]
                            else:
                                r[t].append(k)
        elif mode == 'mood' or mode == 'location' or mode == 'weather':
            if value is None:
                for k in self._content['data']:
                    if self._content['data'][k][mode] not in r:
                        r[self._content['data'][k][mode]] = [k]
                    else:
                        r[self._content['data'][k][mode]].append(k)
            else:
                for k in self._content['data']:
                    if self._content['data'][k][mode] == value:
                        if self._content['data'][k][mode] not in r:
                            r[self._content['data'][k][mode]] = [k]
                        else:
                            r[self._content['data'][k][mode]].append(k)
        else:
            return self._content['data'].keys()

        if not specific:
            for k in r:
                r[k] = len(r[k])

        return r

    def edit(self, date, key, value):
        self.check()
        if not isinstance(date, str):
            date = str(date)
            self._content['data'][date][key] = value
        self._status = 'Unsaved'

    def delete(self, date):
        self.check()
        if not isinstance(date, str):
            date = str(date)
        self._status = 'Unsaved'
        return self._content['data'].pop(date)

    def new(self, content, tags, mood, date=None, time=None, location=None, weather=None, temperature=None,):
        self.check()

        def get_time(mode):
            dateobj = datetime.datetime.now()
            if mode == 'date':
                return dateobj.strftime('%Y%m%d')
            elif mode == 'time':
                return dateobj.strftime('%H:%M')

        def url_get(url, timeout=None):
            with request.urlopen(url, timeout=timeout) as f:
                txt = f.read()
            return txt

        def get_location():
            # Accurate to city.
            txt = url_get('http://ip-api.com/json', timeout=15).decode('utf-8')
            d = json.loads(txt)
            return d['city']

        def get_weather():
            def process_weather_page(s):
                try:
                    s = re.search('<pre>.+</pre>', s, re.S).group().split('\n')[1:3]  # Find the useful 2 lines.
                    s[0] = re.sub('<span .+</span>', '', s[0]).strip()  # Process the sky condition.

                    # Find the temperature number(s).
                    find = re.compile(r'<span class="ef\d{1,3}">-?\d{1,3}</span>')
                    t = find.findall(s[1])

                    # Get average of the temperature.
                    for c in range(len(t)):
                        t[c] = int(re.sub('<.+?>', '', t[c]))
                    s[1] = sum(t) / len(t)

                    return s  # s[0] is sky condition, s[1] is the average temperature.
                except:
                    # If any error, return None.
                    return None

            if ' ' in location:
                loc = '~' + re.sub(' ', '+', location)
            else:
                loc = location

            txt = url_get('http://wttr.in/' + loc + '?0&Q&m', timeout=15).decode('utf-8')
            return process_weather_page(txt)

        if time is None:
            print('Auto fetching time...')
            time = get_time('time')
        elif re.match(r'\d{2}:\d{2}', time) is None:
            raise ValueError('Expected form of time: M:S, got: ' + time)

        r = dict()

        r['time'] = time

        if location is None:
            print('Auto fetching location...')
            location = get_location()

        r['location'] = location

        if weather is None and temperature is None:
            print('Auto fetching weather...')
            w = get_weather()
            r['weather'] = w[0]
            print('Auto fetching temperature...')
            r['temperature'] = w[1]
        elif weather is None:
            print('Auto fetching weather...')
            w = get_weather()
            r['weather'] = w[0]
            r['temperature'] = temperature
        elif temperature is None:
            print('Auto fetching temperature...')
            w = get_weather()
            r['weather'] = weather
            r['temperature'] = w[1]
        else:
            r['weather'] = weather
            r['temperature'] = temperature

        r['tags'] = tags
        r['content'] = content
        r['mood'] = mood

        if date is None:
            date = get_time('date')
            self._content['data'][date] = r
        else:
            if not isinstance(date, str):
                date = str(date)
            if re.match(r'\d{8}', date) is None:
                raise ValueError('Expected form of date: %Y%m%d, got: ' + date)
            self._content['data'][date] = r

        self._status = 'Unsaved'

        print(self.get(date))

    def recall(self):
        self.check()
        r = {}
        timedelta = datetime.timedelta
        t = datetime.datetime.today()
        t1 = t - timedelta(weeks=1)

        s = str(t1.year) + str(t1.month).zfill(2) + str(t1.day).zfill(2)
        r['a week ago'] = self.get(s)

        if t.month == 1:
            s = str(t.year - 1) + '12' + str(t.day).zfill(2)
        else:
            s = str(t.year) + str(t.month - 1).zfill(2) + str(t.day).zfill(2)
        if self.get(s):
            r['a month ago'] = self.get(s)

        min_year = int(sorted(list(self.ls('year').keys()), key=int)[0])
        for year in range(min_year, t.year):
            s = str(year) + str(t.month).zfill(2) + str(t.day).zfill(2)
            r[f'today in {str(year)}'] = self.get(s)

        # Pop None.
        keys = list(r.keys())
        for k in keys:
            if r[k] is None:
                r.pop(k)
        return r

    def export_all(self):
        self.check()
        r = self._content

        # Ask if export the key.
        print('Do you want to export the key?(y/n)')
        c = input()
        if c == 'y':
            r['key'] = self._key

        return r

    def import_all(self, content):
        self.check()

        # Confirm.
        print('This will over-write your current file. Do you want to continue?(y/n)')
        c = input()
        if c == 'y':
            if content.get('key'):
                # Ask if import the key.
                print('Do you want to import the key?(y/n)')
                c = input()
                if c == 'y':
                    self._key = content.pop('key')
                else:
                    content.pop('key')
            self._content = content
            self._status = 'Unsaved'

    def random(self):
        self.check()
        return self.get(random.choice(list(self._content['data'].keys())))
