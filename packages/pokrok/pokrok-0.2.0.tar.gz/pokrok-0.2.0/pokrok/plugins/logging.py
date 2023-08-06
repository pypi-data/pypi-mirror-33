from datetime import datetime
from pokrok.plugins import DefaultProgressMeterFactory, BaseProgressMeter
from pokrok.styles import Style, Widget


STYLE_SUPERSET = Style(
    sized=[Widget.BAR, Widget.COUNTER, Widget.PERCENT, Widget.ELAPSED],
    unsized=[Widget.COUNTER, Widget.ELAPSED]
)


class LoggingProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        super().__init__('logging', LoggingProgressMeter, STYLE_SUPERSET)


class LoggingProgressMeter(BaseProgressMeter):
    """Progress meter that logs INFO messages at a specified interval.

    Args:
        interval: The reporting interval.
    """
    def __init__(
            self, mod, size, widgets, desc='', start=0, unit=None, multiplier=None,
            interval=1000, level='INFO', **kwargs
    ):
        super().__init__(size)
        self.logger = mod.getLogger()
        self.count = start or 0
        self.size = size
        self.interval = interval
        self.multiplier = multiplier
        self.start_time = None
        self._level = getattr(mod, level)
        self._scale = 1
        self._bar_size = 10
        self._bar_char = '*'

        # Warn the user if the level of the logger is above the level at which
        # log messages will be created
        if self._level < self.logger.level:
            self.logger.log(
                max(self.logger.level, mod.WARN),
                "Progress log messages will not be seen since the progress logging "
                "level %d is less that the logger's level %d",
                self._level, self.logger.level
            )

        default_widgets = STYLE_SUPERSET.get_widgets(size is not None)

        if widgets is None:
            widgets = default_widgets
        else:
            allowed = set(default_widgets)
            widgets = [w for w in widgets if w in allowed]

        self.key_fns = {}
        message = []

        if desc:
            message.append(desc)

        for w in widgets:
            if w == Widget.COUNTER:
                if size:
                    for suffix in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
                        if size < 1000:
                            break
                        size /= 1000
                        self._scale *= 1000
                    if suffix:
                        message.append('{count:.2f}/' + '{:.2f}'.format(size) + suffix)
                    else:
                        message.append('{count}/' + size)
                else:
                    message.append('{count}')
                if unit:
                    message.append(unit)
                self.key_fns['count'] = lambda: self.count / self._scale
            elif w == Widget.ELAPSED:
                message.append('{elapsed:.1f} seconds')
                self.key_fns['elapsed'] = (
                    lambda: datetime.now().timestamp() - self.start_time.timestamp())
            elif w == Widget.BAR:
                message.append('{bar}')
                bar_fmt = '[{{: <{}}}]'.format(self._bar_size)
                self.key_fns['bar'] = lambda: bar_fmt.format(
                    self._bar_char * round((self.count / self.size) * self._bar_size))
            elif w == Widget.PERCENT and size is not None:
                if Widget.COUNTER in widgets:
                    message.append('({percent:.0%})')
                else:
                    message.append('{percent:.0%}')
                self.key_fns['percent'] = lambda: self.count / self.size

        self.message = ' '.join(message)

    def start(self):
        super().start()
        self.start_time = datetime.now()

    def finish(self):
        super().finish()
        self.logger.log(self._level, "Read a total of %s records", self.count)

    def increment(self, n=1):
        cur_mod = self.count % self.interval
        if self.multiplier:
            n *= self.multiplier
        self.count += n
        if (self.count % self.interval) <= cur_mod:
            format_kwargs = dict((key, fn()) for key, fn in self.key_fns.items())
            self.logger.log(self._level, self.message.format(**format_kwargs))
