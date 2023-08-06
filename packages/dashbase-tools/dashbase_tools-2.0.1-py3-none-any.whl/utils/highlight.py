from colorama import init
from termcolor import colored

init()


def highlight_str(s, indices_list):
    if not s or not indices_list:
        return s
    temps = None
    i = 0
    for indices in indices_list:
        start = indices.get("offset")
        length = indices.get("length")
        if start == None or length == None:
            return s
        if length > 0:
            temps = temps + s[i:start] if temps else s[i:start]
            end = start + length
            part = s[start:end]
            temps += colored(part, 'green', 'on_red')
            i = end
    if i < len(s):
        temps += s[i:]
    return temps
