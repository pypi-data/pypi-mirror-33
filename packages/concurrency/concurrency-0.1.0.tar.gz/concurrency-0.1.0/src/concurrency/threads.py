import logging
import random
import threading
import time
from collections import deque
from Queue import Queue, Full, Empty
from threading import Thread, Event


def multiqueue_get(queues, timeout=None):
	"""Waits for all queues to have at least one value queued, blocking gets in
	any other thread. When all queues are ready, returns list of values gotten
	from each queue in same order the queues were passed in."""
	for q in queues:
		q.not_empty.acquire()
	try:
		if timeout is None:
			for q in queues:
				q.not_empty.wait()
		else:
			end = time.time() + timeout
			done = 0
			for q in queues:
				wait = max(0, end - time.time())
				q.not_empty.wait(wait)
				if q._qsize():
					done += 1
			if done < len(queues):
				raise Empty
		return [q._get() for q in queues]
	finally:
		for q in queues:
			q.not_empty.release()


def wait(start_threads=1):
	i = 0.25
	time.sleep(i)
	while threading.active_count() > start_threads:
		logging.getLogger().debug('Waiting on {} threads to close: {}'
								  .format(threading.active_count() - 1,
										  threading.enumerate()[1:]))
		i *= 2
		time.sleep(i)


def deprecated_loop(f):
	"""Proposed deprecation:
	Reason: Does not work with MultiLoop if the method being looped is an
		member of an object other than the MultiLoop that is managing the thread
		because it looks for self._shutdown (self is the object it is a member of)
	Replacement: Set loop argument in MultiLoop.add_thread to True
	"""
	def new(self, *args, **kwargs):
		full_name = '{} loop ({}.{}).'.format(threading.current_thread().name,
											  f.__module__, f.__name__)
		logging.getLogger(__name__).debug('Initializing {}.'.format(full_name))
		while True:
			f(self, *args, **kwargs)
			if self._shutdown:
				# self.shutdown()
				break
		logging.getLogger(__name__).debug('Terminating {}.'.format(full_name))
	new.__name__ = f.__name__
	return new


class Looper(Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None,
				 verbose=None, rate=1, randomness=0, callback=None,
				 error_callback=None, daemon=False, error_limit=1):
		Thread.__init__(self, group=group, name=name, verbose=verbose)
		self.daemon = daemon
		self.target = target
		self.rate = rate
		self.randomness = randomness
		self.args = args
		self.kwargs = kwargs
		self._kill = Event()
		self._kill.set()
		self._run = Event()
		self._run.set()
		self._loop_thread = None
		self.counter = 0
		self.callback = callback
		self.error_callback = error_callback
		self.error_limit = error_limit
		self.error_counter = 0
	
	@property
	def paused(self):
		return not self._run.is_set()
	
	def pause(self):
		self._run.clear()
	
	def resume(self):
		self._run.set()
	
	def shutdown(self):
		self._kill.set()
		self._run.set()
		self.join()
	
	def run(self):
		self._kill.clear()
		execution = 0
		while not self._kill.wait(max(self._delay() - execution, 0)):
			start = time.time()
			try:
				ret = self.target(*self.args, **self.kwargs)
				if callable(self.callback):
					self.callback(ret)
				self.counter += 1
			except Exception as e:
				self.error_counter += 1
				if callable(self.error_callback):
					self.error_callback(e)
				if self.error_counter >= self.error_limit:
					raise
			execution = start - time.time()
			self._run.wait()
	
	def _delay(self):
		period = 1.0 / self.rate
		radius = self.randomness * period
		return random.uniform(period - radius, period + radius)


class MultiLoop(object):
	""" For multithreading, not multiprocessing. """
	
	def __init__(self):
		self.__state_lock = threading.Lock()
		self.__open = False
		self._threads = {}
	
	def __iter__(self):
		for _, thread in self._threads.items():
			yield thread
	
	def __getitem__(self, item):
		return self._threads[item]
	
	def __len__(self):
		return len(self._threads)
	
	@property
	def is_open(self):
		return self.__open
	
	def add_thread(self, name, target, args=(), loop=False):
		if loop:
			target = self.loop(target)
		if name in self._threads:
			raise KeyError('Thread {} already exists.'.format(name))
		self._threads[name] = threading.Thread(target=target, name=name, args=args)
		self._threads[name].daemon = True
	
	def replace_thread(self, name, target, args=()):
		if name in self._threads:
			self._threads[name].join(3)
			if self._threads[name].is_alive():
				raise RuntimeError('Thread {} is still alive, cannot replace.'.format(name))
		self._threads[name] = threading.Thread(target=target, name=name, args=args)
		self._threads[name].daemon = True
	
	def start(self):
		self.__open = True
		for thread in self:
			thread.start()
	
	def cleanup(self):
		self.join()
		self._threads = {}
	
	def is_alive(self):
		return max([thread.is_alive() for thread in self])
	
	def join(self, timeout=None):
		end = None if timeout is None else time.time() + timeout
		threads = [thread for thread in self if thread.is_alive]
		while len(threads) > 0 and (time.time() < end or end is None):
			wait = (end - time.time()) / (
				len(threads)) if end is not None else 1
			for thread in threads:
				thread.join(wait)
			threads = [thread for thread in threads if thread.is_alive()]
	
	def _custom_shutdown(self, *args, **kwargs):
		pass
	
	def _pre_shutdown(self, *args, **kwargs):
		pass
	
	def shutdown(self, *args, **kwargs):
		if self.__open:
			with self.__state_lock:
				if self.__open:
					logging.getLogger(__name__).debug('Preparing to shutdown {}.'
													  .format(self.__class__.__name__))
					self._pre_shutdown(*args, **kwargs)
					logging.getLogger(__name__).debug('Shutting down {}.'
													  .format(self.__class__.__name__))
					self.__open = False
					self._custom_shutdown(*args, **kwargs)
	
	def loop(self, f):
		def new(*args, **kwargs):
			full_name = '{} loop ({}.{}).'.format(
				threading.current_thread().name,
				f.__module__, f.__name__)
			logging.getLogger(__name__).debug('Initializing {}.'.format(full_name))
			while self.is_open:
				f(*args, **kwargs)
			logging.getLogger(__name__).debug('Terminating {}.'.format(full_name))
		new.__name__ = f.__name__
		return new


class MessageQueue(Queue):
	""" Double ended queue for inserts, get() empties entire queue. """
	
	def __init__(self, *args, **kwargs):
		Queue.__init__(self, *args, **kwargs)
		self._lock = threading.Lock()

	def append(self, item, block=True, timeout=None):
		self._put(self.queue.append, item, block, timeout)
		
	put = append
	
	def appendleft(self, item, block=True, timeout=None):
		self._put(self.queue.appendleft, item, block, timeout)
	
	def _put(self, method, items, block, timeout):
		with self.not_full:
			if self.maxsize > 0:
				if not block:
					if self._qsize() >= self.maxsize:
						raise Full
				elif timeout is None:
					while self._qsize() >= self.maxsize:
						self.not_full.wait()
				elif timeout < 0:
					raise ValueError("'timeout' must be a non-negative number")
				else:
					endtime = time.time() + timeout
					while self._qsize() >= self.maxsize:
						remaining = endtime - time.time()
						if remaining <= 0.0:
							raise Full
						self.not_full.wait(remaining)
			with self._lock:
				method(items)
			self.unfinished_tasks += 1
			self.not_empty.notify()
	
	def get_all(self, block=True, timeout=None):
		with self.not_empty:
			if not block:
				if not self._qsize():
					raise Empty
			elif timeout is None:
				while not self._qsize():
					self.not_empty.wait()
			elif timeout < 0:
				raise ValueError("'timeout' must be a non-negative number")
			else:
				endtime = time.time() + timeout
				while not self._qsize():
					remaining = endtime - time.time()
					if remaining <= 0.0:
						raise Empty
					self.not_empty.wait(remaining)
			with self._lock:
				items = self.queue
				self.queue = deque()
			self.not_full.notify()
			return items
