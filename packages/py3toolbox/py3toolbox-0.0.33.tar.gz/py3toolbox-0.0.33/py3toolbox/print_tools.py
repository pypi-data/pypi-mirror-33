import os


def cls():
  os.system('cls' if os.name=='nt' else 'clear')
  
def pause(txt=None) :
  press_keys_info = "Confirm and press \033[30;48;5;82m[Enter]\033[0m to continue ... or \033[7;49;5;91m[Ctrl-C]\033[0m to exit ...\n\n"
  if txt is None : txt = "\n\n---> " 
  pause_txt = txt + press_keys_info
  input(pause_txt)


def keep_print(text):
  print (text, sep=' ', end='', flush=True)    
  
def get_progress_bar(current, total, scale=50):
  percent = int(current/total*100+0.5)
  if percent <0   : percent = 0
  if percent >100 : percent = 100
  arrow_pos =  int(percent * scale /100 ) 
  if arrow_pos <=1 : 
    progress_bar = '>' * arrow_pos + '.' * (scale - arrow_pos)
  else:
    progress_bar = '=' * (arrow_pos -1) + '>' + '.' * (scale - arrow_pos)
  progress_bar = '    [{0}] {1:<5} {2:<12} \r'.format(progress_bar, str(percent) + '%',str(current) + '/' + str(total))
  return progress_bar

def format_str(fmt, *args) :
  return (fmt.format(*args))   

if __name__ == "__main__":
  #'{1} {0}'.format('one', 'two')  
  print(format_str('{1} {0}', 'One', 'Tow'))
  #print (get_progress_bar(10,23))
  pass  