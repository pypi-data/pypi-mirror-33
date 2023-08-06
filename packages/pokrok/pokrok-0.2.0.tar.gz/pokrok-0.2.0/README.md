PyPI offers at least 30 different progress meter packages. Which one should you use? Why choose? With pokrok, you can access a number of popular packages using a single consistent interface. With this approach, you can:

1. Allow your users to configure their favorite package.
2. Switch from one progress meter implementation to another without having to rewrite any code.
3. Use any supported package optimally, for the most common use cases, without having to read the manual.

# Types of progress meters

Generally, a progress meter is a visual representation of the progress of a task. The two most common types of progress meters are:

* Progress bar - shows progress of a task of known size, advancing steadily from 0 to 100% complete.
* Spinner - shows that there is progress, but with no indication of how much of the task is remaining (because the size of the task is unknown).

In addition to the progress indicator, each type of progress meter may be accompanied by other information such as elapsed time and estimated time remaining. We call the different aspects of the progress bar display 'widgets.'

Pokrok provides a simple API for displaying progress bars and spinners. The actual work is done by any one of many available progress bar packges in python. For each package, a sensible default display is provided. In addition, high-level configuration options are provided for limited customization of the bar/spinner display without having to know the details of the underlying progress bar/spinner implementation. Finally, access to the fine-grained configuration of the underlying package is provided for those that want it.

# Installation

Pokrok requires python 3.4+.

```bash
pip install pokrok
```

This will install pokrok, but for pokrok to be useful it also needs at least one supported progress bar package to be installed. Some examples are:

* tqdm
* halo

# Examples

```python
import pokrok as pk
import random

# Configure pokrok with a list of your preferred progress bars, in order. Set
# exclusive=True to prevent pokrok from using any other packages but the ones
# you specify.
pk.set_plugins(['tqdm', 'halo'], exclusive=True)

# Show progress while iterating 100 times
numbers = [random.random() for i in pk.progress_range(100)]

# Show progress while iterating over lines in a file
for line in pk.progress_file('foo.txt', 'rt'):
    print(line)

# Show progress while iterating over an arbitrary iterable. Since the
# `progress_iter` function doesn't know the number of items over which
# it is iterating, it must be told explicitly using the 'size' argument.
def generate_random(n):
    for i in range(n):
        yield random.random()

for num in pk.progress_iter(generate_random(100), size=100):
    print(num)

# Get a progress context manager bar you can control manually.
with pk.progress_meter(size=100) as bar:
    for i in range(1000):
        # Only update progress every 10 cycles
        if i % 10 == 0:
            bar.increment()
        print(i)

# Or take full control.
bar = pk.progress_meter(size=100)
bar.start()
for i in range(1000):
    # Only update progress every 10 cycles
    if i % 10 == 0:
        bar.increment()
    print(i)
bar.finish()
```

# Configuration

If you'd just like to use the default implementations provided by whatever plugin is selected, you don't need to do anything. However, if you want to take some control over the progress bar/spinner display, you have two options.

## High-level configuration

Pokrok defines a set of widgets that are commonly provided by progress meter packages. Widgets are combined into "styles." A style is simply a listing of the desired widgets (left-to-right). Separate widget lists can be provided for sized (i.e. progress bar) versus unsized (i.e. spinner) progress meters. There is a global default style, and any number of named styles can be created. When a style is used to create a progress meter, the underlying progress meter library will do its best to provide the desired display; any widgets it cannot provide are ignored silently.

```python
# Global configuration
from pokrok import set_styles, progress_meter, Style, Widget as w
set_styles(
    default=Style(sized=[w.BAR, w.ETA], unsized=[w.SPINNER, w.ELAPSED]),
    kitchen_sink=Style([w.SPINNER, w.BAR, w.ELAPSED, w.ETA])
)

# Use a pre-defined configuration
bar = progress_meter(size=100, style='kitchen_sink')

# Per-progress meter configuration
bar = progress_meter(size=100, style=Style([w.ETA, w.ELAPSED, w.BAR]))
```

## Fine-grained configuration

**NOTE: the fine-grained configuration support described below is still being implemented.**

You can also specify configuration options for each of the progress meter packages you want to support. All configuration options can be set via a JSON configuration file, '.pokrok'. Pokrok looks for this file by default in the following places (in order):

1. ~/pokrok.json
2. ./pokrok.json

By default, the first file discovered is loaded and used for configuration. You can override or supplement this behavior using the `configure()` function. Configuration options for each package can be specified in a dict via a keyword argument to `configure()`. If a file and keyword arguments are given together, the options in the file override the keyword arguments (i.e. the keyword arguments are treated as defaults for options that are not specified in the file). To override this behavior, call the `configure()` function twice - first with the file, then with the keyword arguments.


```python
import pokrok as pk

# Execute the default configuration behavior (this happens by default when the
# first progress meter is requested, so while you can call the configure()
# function explicitly, you don't have to unless you intend to override any options.
pk.configure()

# Load the configuration from an alternate file path, and override options for the
# tqdm and halo libraries.
pk.configure(filename='~/pokrok.json')
pk.configure(
    tqdm=dict(ncols=100, unit='sec'),
    halo=dict(spinner='dots', color='blue')
)
```

# Plugins

Plugins are created by implementing the pokrok API. The easiest way to do this is to extend the base classes in pokrok.plugins. For example, here is the implementation of the built-in `tqdm` module:

```python
from pokrok.plugins import (
    DefaultProgressMeterFactory, BaseProgressMeter, Status)
from pokrok.styles import Style, Widget


class TqdmProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        style_superset = Style([
            Widget.BAR, Widget.ETA, Widget.ELAPSED, Widget.SPINNER
        ])
        super().__init__('tqdm', TqdmProgressMeter, style_superset)

    def iterate(
            self, iterable, size=None, widgets=None, desc=None, start=None,
            **kwargs):
        if self._load_module():
            return self._module.tqdm(
                iterable, total=size, desc=desc, initial=start or 0, **kwargs)
        else:
            return iterable


class TqdmProgressMeter(BaseProgressMeter):
    def __init__(self, mod, size, style, desc, start, **kwargs):
        super().__init__(size)
        self.tqdm = mod.tqdm(
            total=size, desc=desc, initial=start or 0, **kwargs)

    def finish(self):
        super().finish()
        self.tqdm.close()

    def increment(self, n=1):
        self._check_status(Status.STARTED)
        self.tqdm.update(n)
```

To make the plugin visible to pokrok, add an entry point in your setup.py. For example, here is how the built-in TQDM plugin is configured:

```python
entry_points="""
    [pokrok]
    tqdm=pokrok.plugins.tqdm:TqdmProgressMeterFactory
"""
```

# TODO

* Add manual and automatic error handling (with callback to the plugin).
* Implement file-based configuration.
* Add support for additional packages:
    * progressbar2
* Add multi-progress bar support (e.g. for multithreading/multiprocessing)
    * https://pypi.python.org/pypi/progrock/0.3.1
