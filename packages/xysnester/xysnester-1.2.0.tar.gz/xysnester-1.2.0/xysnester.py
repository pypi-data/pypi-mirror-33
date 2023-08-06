"""This is the standard way to include a multiple-line comment in your code.
"""
def print_lol(the_list,indent=False,length=0):
    """This is a function to print a list which includes another list"""
    for item in the_list:
        if  isinstance(item,list):
            print_lol(item,indent,length+1)
        else:
            if(indent):
                for t in range(length):
                    print("\t",end='')
            print(item)
