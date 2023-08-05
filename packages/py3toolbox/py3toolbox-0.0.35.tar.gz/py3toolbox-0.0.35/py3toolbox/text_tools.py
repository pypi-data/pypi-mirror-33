import os
import re
 
def re_search (re_pattern , text) :
  m = re.search(re_pattern, text)
  if m :  return m.groups
  return None

  
if __name__ == "__main__":
  pass  