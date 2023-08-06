# import json
# import os
#
# import zmq
# from tinydb import Storage
#
# import zproc
# from zproc.utils import Queue
# from zproc.utils import get_random_ipc
#
# ACQUIRE_FLAG = b'ACQ'
# RELEASE_FLAG = b'REL'
#
#
# def _get_ipc_path(filename):
#     return filename + '_router_ipc_path'
#
#
# def init_tinydb_storage(ctx: zproc.Context, filename):
#     _get_ipc_path(filename)
#     ctx.state.setdefault(qname, Queue())
#
#     queue = Queue()
#
#     @ctx.processify()
#     def manager_proc(state):
#         ipc_path = get_random_ipc()
#
#         ctx = zmq.Context()
#         sock = ctx.socket(zmq.ROUTER)
#         sock.connect(ipc_path)
#
#         current = None
#
#         while True:
#             ident, msg = sock.recv_multipart()
#
#             if msg == ACQUIRE_FLAG:
#                 if queue:
#                     for ident in queue.drain():
#                         sock.send_multipart([ident, b''])
#                 else:
#                     if current is None or ident == current:
#                         sock.send_multipart([ident, b''])
#                     else:
#                         queue.enqueue(ident)
#             elif msg == RELEASE_FLAG and (current is None or ident == current):
#                 current = None
#
#
# def get_tinydb_storage(state):
#     class ZeroTinyDBStorage(Storage):
#         def __init__(self, filename):
#             self.filename = filename
#             self.signature = _get_ipc_path(self.filename, os.getpid())
#             self.qname = _get_queue_name(self.filename)
#             print(self.signature, self.qname)
#
#         def _acquire(self):
#             state.atomic(lambda state, signature, qname: state[qname].enqueue(signature), self.signature, self.qname)
#             state.get_when_equal(self.signature, ACQUIRE_FLAG)
#
#         def _release(self):
#             state[self.signature] = RELEASE_FLAG
#
#         def read(self):
#             self._acquire()
#
#             try:
#                 with open(self.filename) as handle:
#                     data = json.load(handle)
#                     return data
#             except (json.JSONDecodeError, FileNotFoundError):
#                 return None
#             finally:
#                 self._release()
#
#         def write(self, data):
#             self._acquire()
#
#             try:
#                 with open(self.filename, 'w') as handle:
#                     return json.dump(data, handle)
#             finally:
#                 self._release()
#
#         def close(self):
#             pass
#
#     return ZeroTinyDBStorage
