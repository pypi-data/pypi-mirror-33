import aiohttp
from defusedxml.ElementTree import fromstring

class Rule34Image:
	'''Represents a post from rule34.xxx

	Attributes
	---------
	url: [:class:`str`]
		the url to the full file
	tags: list[:class:`str`]
		the images tags
	file_url= [:class:`str`]
		the url to the full file
		also aliased to url
	source [:class:`str`]
		a url to the source material (the artists tumblr/website)
	height [:class:`str`]
		the height of the full size image
	width [:class:`str`]
		the width of the image
	id [:class:`str`]
		the post id
		useful for reaquiring the image later on by passing it as pid to rule34get
	preview_url [:class:`str`]
		the url for the preview image
	preview_height [:class:`str`]
		the height of the preview image
	preview_width [:class:`str`]
		the width of the preview image
	sample_url [:class:`str`]
		the url to the sample image
	sample_height [:class:`str`]
		the height of the sample image
	sample_width [:class:`str`]
		the width of the example image
	md5 [:class:`str`]
		the images hash
	parent_id [:class:`str`]
		the id of the parent post, empty if theres no parent
	rating [:class:`str`]
		the rating of the post (usually "e" for explicit)
	change: [:class:`str`]
		the time the image was last edited
	created_at [:class:`str`]
		the time the image was last edited
	creator_id [:class:`str`]
		the id of the author
	score [:class:`int`]
		the images score
	status [:class:`str`]
		the status of the image
	has_children [:class:`bool`]
		does the post have children
	has_comments [:class:`bool`]
		does the post have comments
	has_notes [:class:`bool`]
		does the post have notes
	'''
	def __init__(self, **kwargs):
		#automatically set this objects attributes through the power of python!
		for key, val in kwargs.items():
			setattr(self, key, val)
		#make this a list for convenience sake
		self.tags = kwargs['tags'].split(' ')

		#alias url to file_url for convenience
		self.url = kwargs['file_url']

		#these are important enough to warrant the extra lines
		self.has_children = kwargs['has_children'] == "true"
		self.has_comments = kwargs['has_comments'] == "true"
		self.has_notes = kwargs['has_notes'] == "true"
		self.score = int(kwargs['score'])

async def rule34get(tags = None, limit: int = 50, pid: int = None) -> list:
	'''Fetch a certain amount of images asyncronously from rule34.xxx

	Parameters
	----------
	tags: Optional[:class:`str`,`list`]
		the tags to search for
		if passing a string the tags must be seperated by one whitespace each
	limit: Optional[:class:`int`]
		the amount of images to retrive from rule34
		must be between 1 and 100 as per API rules
	pid: Optional[:class:`int`]
		specify this to search for a post with a specific id
		instead of using tags to search

	Raises
	------------
	AttributeError:
		when both tags and pid are passed,
		neither tags or pid are passed or
		when limit is out of range of 1 and 100 as per api rules

	LookupError:
		when nothing is found from the search

	Yields
	-----------
	list [:class:`Rule34Image`]
		a list of image objects fetched from rule34.xxx
	'''
	if tags is None and pid is None:
		raise AttributeError('either tags or pid must be used')
	elif tags is not None and pid is not None:
		raise AttributeError('only tags or pid can be specified, not both')
	elif not 1 <= limit <= 100:
		raise AttributeError('The page limit must be between 1 and 100')

	if isinstance(tags, list):
		tags = ' '.join(tags)

	if pid is None:
		url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={tags}&limit={limit}'.format(
			tags = tags,
			limit = limit
		)
	else:
		url = 'https://rule34.xxx/index.php?page=dapi&s=post&q=index&id={}'.format(pid)


	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			root = fromstring(await resp.text())

			if not root and pid is None:
				raise LookupError('Nothing with tags <{}> found'.format(tags))

			elif not root:
				raise LookupError('No post with an id of <{}> found'.format(pid))

			for post in root:
				yield Rule34Image(**post.attrib)
