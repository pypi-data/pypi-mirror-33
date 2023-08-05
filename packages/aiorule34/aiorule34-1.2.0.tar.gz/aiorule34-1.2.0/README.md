# aiorule34

## Installation

~~pip install aiorule34~~ once i manage to make twine work properly

## Usage
```
from aiorule34 import rule34get as r34get

async for post in r34get(['overwatch','mei_(overwatch)']):
	print(post.url)
```