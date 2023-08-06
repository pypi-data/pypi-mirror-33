# Petact

[![PyPI version](https://img.shields.io/pypi/v/petact.svg)](https://pypi.org/project/petact/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cc0574a2e4c64f60bece2a6b1caa2b0f)](https://www.codacy.com/app/MatthewScholefield/petact?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=MatthewScholefield/petact&amp;utm_campaign=Badge_Grade)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/matthewscholefield/petact.svg)](https://github.com/MatthewScholefield/petact/archive/master.zip)
[![License](https://img.shields.io/github/license/matthewscholefield/petact.svg)](https://github.com/MatthewScholefield/petact/blob/master/LICENSE)

*A package extraction tool for Python*

Petact is a library used for installing and updating compressed
tar files. When `install_package` is called, it downloads an md5 file
and compares it with the md5 of the locally downloaded tar. If they
are different, the old extracted files are deleted and the new tar
is downloaded and extracted to the same place.

## Usage

```python
from os.path import isdir
from petact import install_package, download, download_extract_tar, calc_md5


install_package(
    tar_url='http://mysite.com/binaries.tar.gz', folder='place/for/binaries',
    md5_url='http://mysite.com/binaries.tar.gz.md5', 
    on_download=lambda: print('Updating...'),
    on_complete=lambda: print('Update Complete.')
)


# Other utility functions
words = download('http://mysite.com/words.txt').split(b' ')
download('http://mysite.com/anotherfile.bin', 'anotherfile.bin')
md5_str = calc_md5('anotherfile.bin')
if not isdir('data'):
    download_extract_tar('http://mysite.com/data.tar.gz', 'data')
```

## Installation

```bash
pip3 install petact
```
