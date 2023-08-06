import inspect
from collections import namedtuple


def FlexMsg(name, arg_names):
	arg_names = 'source ' + arg_names if isinstance(arg_names, str) else ['source'] + arg_names
	Generic = namedtuple(name, arg_names)
	
	class Special(Generic):
		def __new__(cls, *args, **kwargs):
			source = kwargs.get('source', get_qualname(inspect.stack()[2][0]))
			return Generic.__new__(Generic, source, *args)
	
	return Special


class Message(object):
	# __metaclass__ = Immutable
	
	def __init__(self, typ=None, value=None, state=None, source=None):
		if isinstance(source, str):
			self.source = source
		elif source is None:
			self.source = get_qualname(inspect.stack()[2][0])
		else:
			self.source = source.__class__.__name__
		self.type = typ
		self.value = value
		self.state = state
	
	def __eq__(self, other):
		return self.type == other.type \
			   and self.value == other.value \
			   and self.state == other.state
	
	def matches(self, other):
		return self.type == other.type \
			   and self.state == other.state
	
	def __str__(self):
		value = self.value.NAME if hasattr(self.value, 'NAME') else self.value
		return 'IPC({}: {} [{} - {}])'.format(self.source, self.type, value, self.state)
	
	def __repr__(self):
		return str(self)
	
	def data_str(self):
		try:
			val = self.value.NAME
		except AttributeError:
			val = self.value
		return '{}, {}, {}'.format(self.type, val, self.state)


def get_qualname(frame):
	cls = None
	module = frame.f_globals.get('__name__', 'unknown_module')
	method = frame.f_code.co_name
	vars = frame.f_locals
	if 'self' in vars:
		cls = vars['self'].__class__.__name__
	elif 'cls' in vars:
		cls = vars['cls'].__name__
	if cls is None:
		return '{}.{}'.format(module, method)
	return '{}.{}.{}'.format(module, cls, method)
