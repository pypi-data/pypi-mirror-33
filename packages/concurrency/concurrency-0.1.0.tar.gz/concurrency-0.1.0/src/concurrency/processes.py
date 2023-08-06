import logging
import time
from multiprocessing import Pipe
try:
	from multiprocessing.reduction import reduce_connection, \
		rebuild_pipe_connection
except ImportError:
	from multiprocessing.reduction import reduce_connection, \
		rebuild_connection as rebuild_pipe_connection


def try_join_then_kill(process, timeout_until_kill, final_join_timeout=None):
	assert timeout_until_kill is not None
	process.join(timeout=timeout_until_kill)
	if process.is_alive():
		logging.warn('Killing {} since it could not be joined after {} seconds.'
					 .format(process, timeout_until_kill))
		process.terminate()
		process.join(timeout=final_join_timeout)


def PriorityPipe(duplex=True):
	rxp_normal, txp_normal = Pipe(duplex)
	rxp_urgent, txp_urgent = Pipe(duplex)
	return PriorityConnection(rxp_normal, rxp_urgent), \
		   PriorityConnection(txp_normal, txp_urgent)


class PriorityConnection:
	""" Same interface as multiprocessing.Connection except timeout option
	for each recv method and urgent option for each send method. """
	
	def __init__(self, normal, urgent):
		self.normal = normal
		self.urgent = urgent
	
	def __iter__(self):
		yield self.urgent
		yield self.normal
	
	def _wait(self, timeout=0):
		# return multiprocessing.connection.wait([i for i in self], timeout)
		start = time.time()
		while True:
			for conn in self:
				if conn.poll():
					return [conn]
			if timeout is not None and timeout < time.time() - start:
				break
	
	def _get(self, urgent):
		return self.urgent if urgent else self.normal
	
	def send(self, msg, urgent=False):
		self._get(urgent).send(msg)
	
	def recv(self, timeout=None):
		msg = self._wait(timeout)
		return msg[0].recv() if msg else None
	
	def fileno(self):
		return [conn.fileno() for conn in self]
	
	def close(self):
		for conn in self:
			conn.close()
	
	def poll(self, timeout=0):
		return self.urgent.poll(timeout / 2) or self.normal.poll(timeout / 2)
	
	def send_bytes(self, buffer, offset=-1, size=-1, urgent=False):
		self._get(urgent).send_bytes(buffer, offset, size)
	
	def recv_bytes(self, maxlength=-1, timeout=None):
		return self._wait(timeout)[0].recv_bytes(maxlength)
	
	def recv_bytes_into(self, buffer, offset=-1, timeout=None):
		return self._wait(timeout)[0].recv_bytes_into(buffer, offset)
	
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
	
	def reduce(self):
		self.urgent = reduce_connection(self.urgent)
		self.normal = reduce_connection(self.normal)
	
	def rebuild(self):
		self.urgent = rebuild_pipe_connection(*self.urgent[1])
		self.normal = rebuild_pipe_connection(*self.normal[1])
