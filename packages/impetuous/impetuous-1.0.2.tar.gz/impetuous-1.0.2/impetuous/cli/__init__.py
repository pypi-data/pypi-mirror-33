""" Impetuous and actions invoked from argument parser.
"""

import datetime
import logging
import re
import subprocess

import colorama as ca
import dateutil.parser

import impetuous.data
from impetuous.config import CONFIG_DIR, CONFIG_INI_PATH, write_config
from impetuous.interaction import Field
from impetuous.sheet import EntryNotFoundError, localtz, utcnow

logger = logging.getLogger(__name__)

entry_fields = [
    Field('entry', f) for f in impetuous.data.tables['entry'].c.keys()
]

submission_fields = [
    Field('submission', f) for f in impetuous.data.tables['submission'].c.keys()
]


def maybe_elide(string, max_length):
    r"""
    >>> maybe_elide('Hello world', 4)
    'H...'
    >>> maybe_elide('Hello world', 5)
    'H...d'
    >>> maybe_elide('Hello world', 9)
    'Hel...rld'
    >>> maybe_elide('Hello world', 10)
    'Hell...rld'
    >>> maybe_elide('Hello world', 11)
    'Hello world'
    >>> maybe_elide('Spam and eggs!', 9)
    'Spa...gs!'
    >>> maybe_elide('Spam and eggs!', 10)
    'Spam...gs!'
    >>> maybe_elide('We have phasers, I vote we blast \'em!   -- Bailey, "The Corbomite Maneuver", stardate 1514.2', 29)
    'We have phase...ardate 1514.2'

    """
    assert max_length > 3
    if len(string) > max_length:
        chunklen = (max_length - 3) // 2
        return "{}...{}".format(string[:chunklen + 1],
                                '' if chunklen == 0 else string[-chunklen:])
    else:
        return string


def one_line(string):
    r"""
    Sanitize for one-line printing?

    >>> sanitize('foo\nbar\tbaz')
    'foo bar baz'

    """
    return string.replace('\t', ' ').replace('\n', ' ')


def get_terminal_width():
    """
    Return the terminal width as an integer or None if we can't figure it out.
    """
    try:
        stty = subprocess.check_output(['stty', 'size'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(stty.strip().split(b' ')[1])
        except (ValueError, IndexError):
            pass
    try:
        tput = subprocess.check_output(['tput', 'cols'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(tput.strip())
        except ValueError:
            pass
    try:
        env = subprocess.check_output('echo -n $COLUMNS', shell=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(env)
        except ValueError:
            pass


def parse_friendly_datetime(value, default=utcnow().astimezone(localtz), **kwargs):
    """
    Only really seems to know what UTC and your local time zone is, everything
    else it'll ignore and we pretend like it's your local timezone ...

    >>> parse_friendly_datetime("1-1-2008 13:00:09")
    datetime.datetime(2008, 1, 1, 13, 0, 9, tzinfo=tzlocal())
    """
    if value == 'now':
        return default
    else:
        dt = dateutil.parser.parse(value, **kwargs)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=localtz)
        else:
            return dt


class WhenTime(object):

    class EntrySeek(object):

        class StartEdge:
            pass

        class EndEdge:
            pass

        def __init__(self, count, edge):
            self.count = count
            self.edge = edge

    def __init__(self, initial, seek=None, delta=None):
        assert initial.tzinfo is not None
        self.initial = initial
        self.seek = seek
        self.delta = delta

    def absolute_datetime(self, entries):
        """
        Return an absolute date and time, possibly relative to some given
        entries if this WhenType specifies a delta (such as relative to a entry's
        start/end time).
        """
        value = self.initial
        if self.seek is not None:
            steps = []
            for entry in entries:
                if self.seek.edge is self.seek.StartEdge:
                    time = entry.start
                else:
                    time = entry.end
                if time is None:
                    raise ValueError(_("Refusing seek past null time."))
                elif time < value:
                    steps.append(time)
                else:
                    break
            try:
                value = steps[-self.seek.count]
            except IndexError:
                raise EntryNotFoundError(_("No entry matching seek."))
        if self.delta is not None:
            value += self.delta
        return value


class WhenArgType(object):
    """
    It's important to use utcnow and the local timezone as attributes on this
    guy instead of just localtimenow because otherwise, time zones will fuck
    you in weird ways.

    Trust me. UTC is the only sane time zone. Use it as much as possible.
    """

    when_format_re = re.compile(
        # Fixed initial
        r'((\.|now)|(?:(\d{1,2}):(\d{1,2}):?(\d{1,2})?))?'
        # Seek
        r'(([[\]])(\d*))?'
        # Relative offset
        r'(([+-])(\d+h)?(\d+m)?(\d+s)?)?'
        r'$'
    )

    def __init__(self, utcnow=utcnow, localtz=localtz):
        self.utcnow = utcnow
        self.localtz = localtz

    def __repr__(self):
        """ For formatting nicely when displayed in an argument parsing message.
        """
        return 'WhenArgType'

    def __call__(self, text):
        """
        Returns a WhenTime which can be used to produce an absolute time given
        the context of a collection of entries.
        """
        if text == 'now':
            return WhenTime(self.utcnow())

        match = self.when_format_re.match(text)
        if match is not None:
            (initial, initial_dot, initial_hour, initial_minute, initial_second,
             seek, seek_edge, seek_count,
             delta, delta_sign, delta_hours, delta_minutes, delta_seconds
             ) = match.groups()

            # Set initial
            if initial is None or initial_dot:
                initial = self.utcnow()
            else:
                time = datetime.time(hour=int(initial_hour),
                                     minute=int(initial_minute),
                                     second=0 if initial_second is None else int(initial_second[0:]))
                now = self.utcnow()
                today = now.astimezone(self.localtz).date()
                initial = datetime.datetime.combine(today, time).replace(tzinfo=self.localtz)

            # Set seek
            if seek is not None:
                if seek_edge == '[':
                    seek_edge = WhenTime.EntrySeek.StartEdge
                else:
                    seek_edge = WhenTime.EntrySeek.EndEdge
                seek = WhenTime.EntrySeek(edge=seek_edge,
                                         count=int(seek_count) if seek_count else 1)

            # Finally make relative/delta time adjustment
            if delta is not None:
                delta = datetime.timedelta(
                    hours=0 if delta_hours is None else int(delta_hours[:-1]),
                    minutes=0 if delta_minutes is None else int(delta_minutes[:-1]),
                    seconds=0 if delta_seconds is None else int(delta_seconds[:-1])
                )
                if delta_sign == '-':
                    delta = -delta

            return WhenTime(initial=initial, seek=seek, delta=delta)
        else:
            raise ValueError(_("Bad format '{}'.").format(text[0:]))
