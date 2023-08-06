class __list_flextape(list): 
  def join(self, s):
    return s.join(self)

def slap(args):
  returnstr = ""
  list = __list_flextape(args)
  for arg in args:
    if type(arg) is list:
      returnstr += list.join(" ")
    else:
      returnstr += str(arg)
  return str(returnstr)

