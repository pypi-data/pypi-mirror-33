class ProgressBar(object):
    def __init__(self, bar_max = 10):
        self.bar_symbol = '#'
        self.empty_symbol = ' '
        self.bar_max = bar_max
        self.rounding_precision = 0

        self.max_val = 100
        self.current_val = 0

        self.one_bar = self.max_val / self.bar_max

    def Update(self, current_val, printing=True):
        #if value has not changed, do nothing
        if current_val == self.current_val:
            return None
        self.current_val = current_val
        self.progress = (self.current_val / self.max_val) * 100
        #locks program to maximum percentage of 100 and minimum of 0
        if self.progress > 100:
            self.progress = 100
        elif self.progress < 0:
            self.progress = 0
        self.progress = round(self.progress, self.rounding_precision)
        self.progress_repr = str(self.progress).split('.')
        #change first zfill to 3 to pad int percentage
        if self.rounding_precision:
            self.progress_repr = self.progress_repr[0].zfill(0) + '.' + self.progress_repr[1].zfill(self.rounding_precision)
        else:
            self.progress_repr = self.progress_repr[0].zfill(0)
        if printing:
            self.Print()

    def Print(self, carriage_return = True):
        bar_n = int(self.progress / self.one_bar)
        bar_repr = self.bar_symbol * bar_n + (self.empty_symbol * (self.bar_max - bar_n))
        print('|{}|({}%)'.format(bar_repr, self.progress_repr) + '\r' if carriage_return else '', end='')


class TimeStorage(object):
    '''Seconds rounded to 4th decimal using Python's round method.
    values are int, except seconds and internal_seconds can be float.
    custom_input examples:
    23
    12:23
    1:12:23'''
    def __init__(self, seconds=0, minutes=0, hours=0, custom_input = ''):
        self.internal_seconds = seconds
        self.internal_seconds += minutes * 60
        self.internal_seconds += hours * 3600 #60 * 60
        if custom_input:
            self._custom_input(custom_input)

    def _minus_check(self, seconds):
        return seconds if self.internal_seconds > 0 else -seconds

    def _custom_input(self, inp):
        values = inp.split(':')
        try:
            self.internal_seconds += float(values[-1])
            self.internal_seconds += int(values[-2]) * 60
            self.internal_seconds += int(values[-3]) * 3600
        except IndexError:
            pass

    @property
    def hours(self):
        return self._minus_check(int(self.internal_seconds / 3600))

    @property
    def minutes(self):
        return self._minus_check(int((self.internal_seconds % 3600) / 60))

    @property
    def seconds(self):
        return self._minus_check(round(self.internal_seconds % 60,4))



    def __add__(self, other):
        return TimeStorage(self.internal_seconds + other.internal_seconds)

    def __sub__(self, other):
        return TimeStorage(self.internal_seconds - other.internal_seconds)

    def __gt__(self, other):
        return self.internal_seconds > other.internal_seconds
    def __lt__(self, other):
        return self.internal_seconds < other.internal_seconds
    def __ge__(self, other):
        return self.internal_seconds >= other.internal_seconds
    def __le__(self, other):
        return self.internal_seconds <= other.internal_seconds
    def __eq__(self, other):
        return self.internal_seconds == other.internal_seconds

    def __repr__(self):
        l = list(map(lambda x: str(abs(x)).zfill(2), (self.hours, self.minutes, self.seconds)))
        return ('-' if self.internal_seconds < 0 else '') + ':'.join(l)

import os
import copy
class File(object):
    '''Can't change folder parts yet except main folder.self
    You can change individual attributes to change absolute file path
    of the file'''
    def __init__(self, file_path):

        _abs_path = file_path
        tail, head = os.path.splitext(_abs_path)
        self.file_extension = head
        #file name without extension
        self.file_name_without_extension = os.path.split(tail)[1]
        tail, _ = os.path.split(_abs_path)
        self.folder_path = tail

    def Clone(self):
        return copy.copy(self)

    def set_folder_path(self, val, cloning=False):
        if cloning:
            clone = self.Clone()
            clone.folder_path = val
            return clone
        else:   
            self.folder_path = val
    @property
    def file_path(self):
        #absolute file path
        return os.path.join(self.folder_path, self.file_name_without_extension) + self.file_extension

    @property
    def file_name(self):
        #with extension
        return self.file_name_without_extension + self.file_extension

    def __repr__(self):
        return self.file_path

if __name__ == '__main__':
    '''
    import time
    p = ProgressBar()
    while True:
        time.sleep(0.2)
        p.Update(p.current_val + 1)
    '''
    '''    
    import time

    a = TimeStorage(2)
    b = TimeStorage(1)
    c = a - b
    d = TimeStorage(time.time())

    print(a,b,c)
    print(d)
    '''
    file = File('/home/rajatapaus/Desktop/yclip/scripts/config.txt')
    
    print(file.file_extension)
