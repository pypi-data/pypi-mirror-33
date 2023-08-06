
"""The Nester.py module provides users with the capability of handling multi-dimensional lists in an easier and more 
   efficient manner."""

def print_lol(the_list):
    """ A list given as an argument has its contents printed out even if it is a multidimensional list through a recursive
        function. """

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
