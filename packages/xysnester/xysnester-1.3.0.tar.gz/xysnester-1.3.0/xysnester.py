"""This is the standard way to include a multiple-line comment in your code.
"""
"""V1.2.0
def print_lol(the_list,indent=False,length=0):
    """"""This is a function to print a list which includes another list""""""
    for item in the_list:
        if  isinstance(item,list):
            print_lol(item,indent,length+1)
        else:
            if(indent):
                for t in range(length):
                    print("\t",end='')
            print(item)
"""
#V1.3.0
import sys
def print_lol(the_list,indent=False,length=0,fn=sys.stdout):
    """This is a function to print a list which includes another list"""
    for item in the_list:
        if  isinstance(item,list):
            print_lol(item,indent,length+1,fn)
        else:
            if(indent):
                for t in range(length):
                    print("\t",end='',file=fn)
            print(item,file=fn)
