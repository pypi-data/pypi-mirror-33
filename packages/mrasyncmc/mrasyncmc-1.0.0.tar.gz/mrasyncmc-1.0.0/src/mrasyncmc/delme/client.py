
import asyncio
import socket
import os
from . import CMemcachedClient
from .server import Server

async def create_client( servers, pool_size=2, loop=None, connection_timeout=1 ):
  c = Client([("localhost",11211),("localhost",11212),("localhost",11213),("localhost",11214)], pool_size, loop, connection_timeout)
  num = await c.setup_connections()
  if num == 0:
    print("WARNING: Unable to connect to any memcached servers")
  return c
  
  
class Client(CMemcachedClient):
  def __init__(self, servers, pool_size, loop, connection_timeout):
    self.connection_timeout = connection_timeout

    if not isinstance(servers, list):
      raise ValueError("Memcached client takes a list of (host, port) servers")

    super().__init__(len(servers))

    self.servers = []
    for s in servers:
      self.servers.append( Server( s[0], s[1], pool_size, loop, connection_timeout ) ) 

  async def setup_connections(self):
    cnt = 0
    for s in self.servers:
      if not await s.pool.open_connections():
        s.failed = True
      else:
        cnt += 1
    return cnt
      
  async def close(self):
    for s in servers:
      await s.pool.close()

  async def _get(self, key, cas=0):

    server_index = self.get_server_index_and_validate(key)
    c = await self.servers[ server_index ].pool.get_connection()
    with c:
      if cas:  c.w.write(b'gets ' + key + b'\r\n')
      else:    c.w.write(b'get '  + key + b'\r\n')
  
      val = None
      cas_token = None
      #fut = c.r.readline()
      #line = await asyncio.wait_for(fut,timeout=1)
      line = await c.r.readline()
      while line != b'END\r\n':
        spl = line.split()
        if spl[0] == b'VALUE':  # exists
          #key = spl[1]
          #flags = int(spl[2])
          length = int(spl[3])
          cas_token = int(spl[4]) if cas else None
          val = (await c.r.readexactly(length+2))[:-2]
  
        elif spl[0] == b'CLIENT_ERROR' or spl[0] == b'SERVER_ERROR' or spl[0] == b'ERROR':  
          raise ValueError('Server returned an error: ' + line.decode("utf-8"))
        else:
          raise ValueError('Server responded with an unexpected response: ' + line.decode('utf-8'))
  
        line = await c.r.readline()

      return val, cas_token

  async def get(self, key, default=None):
    val, cas = await self._get( key )
    return val

  async def gets(self, key, default=None):
    val, cas = await self._get( key, cas=1 )
    return val

  async def multi_get(self, keys):

    batches = {}
    for k in keys:
      srv = self.get_server_index_and_validate(k)
      if not srv in batches:
        batches[srv] = [k]
      else:
        batches[srv].append(k)

    d = {}
    for srv in batches.keys():
      keys = batches[srv]
      c = await self.servers[ srv ].pool.get_connection()
      with c:
        c.w.write(b'get '  + b' '.join(keys) + b'\r\n')
  
        line = await c.r.readline()
        while line != b'END\r\n':
          spl = line.split()
          if spl[0] == b'VALUE':  # exists
            key = spl[1]
            #flags = int(spl[2])
            length = int(spl[3])
            d[key] = (await c.r.readexactly(length+2))[:-2]
            
          elif spl[0] == b'CLIENT_ERROR' or spl[0] == b'SERVER_ERROR' or spl[0] == b'ERROR':  
            raise ValueError('Server returned an error: ' + line.decode("utf-8"))
          else:
            raise ValueError('Server responded with an unexpected response: ' + line.decode('utf-8'))
    
          line = await c.r.readline()

    return d

  async def _get_response(self, conn):
    line = b''
    resp = bytearray()
    while not line.endswith(b'\r\n'):
      line = await conn.r.readline()
      resp.extend(line)
    return resp[:-2]

  async def _store(self, cmd, key, val, exp=0, flags=0, noreply=True):

    server_index = self.get_server_index_and_validate(key)
    #self.validate_key(key)
    if not isinstance(exp,int):
      raise ValueError("Expiration must be an int")
    c = await self.servers[ server_index ].pool.get_connection()
    with c:
      args = [str(a).encode('utf-8') for a in (flags, exp, len(val))]
      cmd = cmd + b' ' + b' '.join([key] + args)
      if noreply: cmd += b' noreply'
      cmd += b'\r\n' + val + b'\r\n'
  
      c.w.write(cmd)
      if noreply: return
      await c.w.drain()
  
      resp = await self._get_response(c)
      return resp == b'STORED'

  async def set(self, key, val, exp=0, flags=0, noreply=True):
    return await self._store(b"set", key, val, exp, flags, noreply)
  async def append(self, key, val, exp=0, flags=0,noreply=True):
    return await self._store(b"append", key, val, exp, flags, noreply)
  async def prepend(self, key, val, exp=0, flags=0,noreply=True):
    return await self._store(b"prepend", key, val, exp, flags, noreply)
  async def replace(self, key, val, exp=0, flags=0,noreply=True):
    return await self._store(b"replace", key, val, exp, flags, noreply)
  async def add(self, key, val, exp=0, flags=0,noreply=True):
    return await self._store(b"add", key, val, exp, flags, noreply)

  async def delete(self, key):
    s = self.get_server_index_and_validate(key)
    c = await self.servers[ s ].pool.get_connection()
    with c:
      c.w.write(b'delete ' + key + b'\r\n')
      await c.w.drain()
      resp = await self._get_response(c)
      return resp == b'DELETED'

  async def incr(self, key, increment=1):
    """Returns the incremented value or None if the key wasn't found"""
    s = self.get_server_index_and_validate(key)
    c = await self.servers[ s ].pool.get_connection()
    with c:
      c.w.write(b'incr ' + key + b' ' + str(increment).encode('utf-8') + b'\r\n')
      await c.w.drain()
      resp = await self._get_response(c)
  
      if resp.isdigit(): return int(resp)
      if resp == b"NOT_FOUND": return None
      else:
        raise ValueError("Bad response from server on increment: " + str(resp))

  async def decr(self, key, decrement=1):
    """Returns the decremented value or None if the key wasn't found"""
    s = self.get_server_index_and_validate(key)
    c = await self.servers[ s ].pool.get_connection()
    with c: 
      c.w.write(b'decr ' + key + b' ' + str(decrement).encode('utf-8') + b'\r\n')
      await c.w.drain()
      resp = await self._get_response(c)
  
      if resp.isdigit(): return int(resp)
      if resp == b"NOT_FOUND": return None
      else:
        raise ValueError("Bad response from server on decrement: " + resp)

  async def stats(self, srv, args=None):
    if args is None: args = b''
    c = await self.servers[ srv ].pool.get_connection()

    c.w.write(b''.join((b'stats ', args, b'\r\n')))

    ret = {}
    line = await c.r.readline()
    while line != b'END\r\n':
      spl = line.split()
      if spl[0] != b'STAT': raise ValueError("Bad response from server on stats cmd: " + line)
      ret[spl[1]] = None
      if len(spl) == 3: ret[spl[1]] = spl[2]
      if len(spl) >= 3: ret[spl[1]] = b' '.join(spl[2:])
      line = await c.r.readline()

    return ret



