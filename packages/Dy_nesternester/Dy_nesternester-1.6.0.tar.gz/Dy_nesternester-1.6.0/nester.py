"""This is the "nester.py" module and it provides one function called print_lol()
    which prints lists that may or may not include nested listts."""

def print_lol(listme,indent=False,level=0):
    """This function takes a positional argument called "listme",which is any
        pythonlist(of -possibly -nested lists).Each data item in the provided
        list is (recursively)printed to the screen on it's own line.A second a
        -rgument called indent is used to swith indentation on or off.A third
        argument called "level" is used toinsert tab-stopswhen a nested list
        is encountered."""
    for each_item in listme:
        if isinstance(each_item,list):
                print_lol(each_item,indent,level+1);
        else:
            if indent:
                for tab_stops in range(level):
                    print("\t",end='')
            print(each_item)
			
    print("我是原始文件的模块hh") 

