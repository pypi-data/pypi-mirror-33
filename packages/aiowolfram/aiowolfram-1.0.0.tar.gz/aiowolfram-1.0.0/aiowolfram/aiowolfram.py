import aiohttp
import json

class WolframValues:
	'''an object representing a set of values from a wolfram assumption

	Attributes
	----------

	raw_json: [:class:`dict`]
		the raw json that mage this object

	name: [:class:`str`]
		the name of this value object

	desc: [:class:`str`]
		the decription of this value

	input: [:class:`str`]
		the input of this value

	'''
	def __init__(self, content):
		self.raw_json = content
		for key, val in content.items():
			setattr(self, key, val)

class WolframAssumption:
	'''an object representing an assumption from wolfram

	Attributes
	---------

	raw_json: [:class:`dict`]
		the raw json that made this object

	type: [:class:`str`]
		the type of assumption this object contains

	template: [:class:`str`]
		a template to be formatted by the values contained

	count: [:class:`int`]
		the amount of values contained

	values: list[:class:`WolframValues`]
		a list of this assumptions values

	'''
	def __init__(self, assumption):
		self.raw_json = assumption
		for key, val in assumption.items():
			setattr(self, key, val)
		self.values = []
		for value in assumption['values']:
			self.values.append(WolframValues(value))

class WolframImage:
	'''an object representing an image from wolfram

	Attributes
	---------

	raw_json: [:class:`dict`]
		the raw json that made this object

	src: [:class:`str`]
		a link to the image source

	title: [:class:`str`]
		this images title

	alt: [:class:`str`]
		the alternative title

	width: [:class:`int`]
		this images width

	height: [:class:`int`]
		the height of this image

	'''
	def __init__(self, image):
		self.raw_json = image
		for key, val in image.items():
			setattr(self, key, val)

class WolframSubPod:
	'''a subpod from a wolfram pod

	Attributes
	----------

	raw_json: [:class:`dict`]
		this subpods raw json

	title: [:class:`str`]
		the title of this subpod

	plaintext: [:class:`str`]
		the text this pod contains

	image: [:class:`WolframImage`]
		the image this subpod contains

	'''
	def __init__(self, subpod):
		self.raw_json = subpod
		self.title = subpod['title']
		self.text = subpod['plaintext']
		self.image = WolframImage(subpod['img'])

class WolframPod:
	'''a pod from a wolfram result

	Attributes
	--------

	raw_json: [:class:`dict`]
		the raw json pod

	title: [:class:`str`]
		the title of the pod

	scanner: [:class:`str`]
		the scanner type

	id: [:class:`str`]
		the response type

	position: [:class:`int`]
		the position of this pod in the list of pods

	error: [:class:`bool`]
		did this pod error

	numsubpods: [:class:`int`]
		the amount of subpods this pod has

	subpods: list[:class:`WolframSubPod`]
		a list of this pods subpods

	'''
	def __init__(self, pod):
		self.raw_json = pod
		for key, val in pod.items():
			setattr(self, key, val)
		self.subpods = []
		for subpod in pod['subpods']:
			self.subpods.append(WolframSubPod(subpod))

class WolframResp:
	'''an object representation of the response recived from wolfram aplhas api

	Attributes
	----------

	raw_json: [:class:`dict`]
		the raw json response taken from wolfram

	success: [:class:`bool`]
		whether the query was successful or not

	error: [:class:`bool`]
		if the result failed

	numpods: [:class:`int`]
		the amount of subpods this object has

	datatypes: [:class:`str`]
		the datatypes this object contains

	timedout: [:class:`str`]
		if the result timed out

	timedoutpods: [:class:`str`]
		the amount of pods that timed out

	timing: [:class:`float`]
		how long the request took

	parsetiming: [:class:`float`]
		how long the query took to parse serverside

	parsetimedout: [:class:`bool`]
		if the parsing timed out

	recalculate: [:class:`str`]
		TODO

	id: [:class:`str`]
		the id of this query

	host: [:class:`str`]
		the server that procccessed this query

	server: [:class:`str`]
		the server number that proccessed this query

	related: [:class:`str`]
		a related url

	version: [:class:`str`]
		the current api version for the servers

	pods: list[:class:`WolframPod`]
		a list of all the pods this request returned

	'''
	def __init__(self, content):
		queryresult = content['queryresult']
		self.raw_json = content
		for key, val in queryresult.items():
			if key == 'assumptions':
				self.assumptions = WolframAssumption(val)
			setattr(self, key, val)

		self.pods = []
		for pod in queryresult['pods']:
			self.pods.append(WolframPod(pod))

class Wolfram:
	'''The class for accessing wolfram alphas api

	Attributes
	----------
	key: [:class:`str`]
		the wolfram aplha api key
	'''
	def __init__(self, key):
		self.key = key

	async def query(self, question):
		'''Query the wolfram alpha api for a question

		Parameters
		--------
		question: [:class:`str`]
			the question to ask wolfram alpha

		Raises
		--------
		LookupError
			raised when the query returns no results

		'''
		url = 'http://api.wolframalpha.com/v2/query?input={}&appid={}&output=json'.format(
			question,
			self.key
		)

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				j = json.loads(await resp.text())

				if j['queryresult']['error']:
					raise LookupError('the search had no results')

				return WolframResp(j)