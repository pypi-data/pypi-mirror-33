"""This is the standard way to include a multiple-line comment in your code.
"""
def print_lol(the_list,length=0):
    """This is a function to print a list which includes another list"""
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,length+1)
        else:
            for t in range(length):
                print("\t",end='')
            print(item)
