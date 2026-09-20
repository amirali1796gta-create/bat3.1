import time
from collections import defaultdict,deque
class RateLimiter:
 def __init__(self,limit=20,window=10): self.limit=limit; self.window=window; self.d=defaultdict(deque)
 def allow(self,uid):
  now=time.monotonic(); q=self.d[uid]
  while q and now-q[0]>self.window:q.popleft()
  if len(q)>=self.limit:return False
  q.append(now);return True
limiter=RateLimiter()
