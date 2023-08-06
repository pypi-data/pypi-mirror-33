# legos.apod

[![Travis](https://img.shields.io/travis/drewpearce/legos.apod.svg)]() [![PyPI](https://img.shields.io/pypi/pyversions/legos.apod.svg)]() [![PyPI](https://img.shields.io/pypi/v/legos.apod.svg)]()

[![PyPI](https://img.shields.io/pypi/wheel/legos.apod.svg)]() [![PyPI](https://img.shields.io/pypi/l/legos.apod.svg)]() [![PyPI](https://img.shields.io/pypi/status/legos.apod.svg)]()

Fetch xkcd comics right from chat using this xkcd lego.

## Usage

- `!apod` returns the latest photo
- `!apod r` or `!apod random` will return a random photo
- `!apod [yyyy-mm-dd]` will return the photo of corresponding date

### API Key
The NASA api has pretty strict limits. These can be mitigated by getting an [api key](https://api.nasa.gov/index.html#apply-for-an-api-key). You can add the key by directly inserting it in the code (look in the `__init__` function,) or by creating a config.ini file in the same directory that you run Legobot from. It should look like this:
```ini
[apod]
api_key=your-nasa-api-key
```

## Installation
cd into the current directory
`pip3 install .`

This is a Lego designed for use with [Legobot](https://github.com/Legobot/Legobot), so you'll get Legobot along with this. To deploy it, import the package and add it to the active legos like so:

```python
# This is the legobot stuff
from Legobot import Lego
# This is your lego
from legos.apod import APOD

# Legobot stuff here
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add your lego
baseplate_proxy.add_child(APOD)
```

## Tweaking

While you can use this one as-is, you could also add a localized version to your Legobot deployment by grabbing [apod.py](legos/apod.py) and deploying it as a local module. [Example of a Legobot instance with local modules](https://github.com/voxpupuli/thevoxfox/)

## Contributing

As always, pull requests are welcome.
