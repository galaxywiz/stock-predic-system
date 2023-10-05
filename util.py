#----------------------------------------------------------#
# 유틸 함수들

def calcRate(origin, now):
    return (now - origin) / origin
    
def checkRange(start, now, end):
    return min(end, max(now, start))
    
def isRange(start, now, end):
    if now == checkRange(start, now, end):
        return True
    return False

#----------------------------------------------------------#
# 싱글톤
class SingletonInstane:
  __instance = None

  @classmethod
  def __getInstance(cls):
    return cls.__instance

  @classmethod
  def instance(cls, *args, **kargs):
    cls.__instance = cls(*args, **kargs)
    cls.instance = cls.__getInstance
    return cls.__instance