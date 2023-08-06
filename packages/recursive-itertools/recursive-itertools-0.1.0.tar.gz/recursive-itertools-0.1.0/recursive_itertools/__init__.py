
def rfilter(obj, filter_func):
  if isinstance(obj, dict):
    return {k:rfilter(v, filter_func) for k,v in obj.iteritems() if filter_func(v)}
  elif isinstance(obj, list):
    return [rfilter(x, filter_func) for x in obj if filter_func(x)]
  else:
    return obj


