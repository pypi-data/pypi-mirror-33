
"""The Nester.py module provides users with the capability of handling multi-dimensional lists in an easier and more 
   efficient manner."""

def print_lol(the_list,indent=False,level=0):
    """ A list given as an argument has its contents printed out even if it is a multidimensional list through a recursive
        function. The additional argument level is preset to 0 and is used to determine how many tab spaces to indent
        when printing, with the tab spaces representing the order of the list being printed."""

    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)


def printFile(data):
    ''' A given file in a directory will be passed on as an argument into this function which will then print each line
        of that file leaving it as is'''
    if isinstance(data,str):
        data = open(data)
    for each_line in data:
        print(each_line,end='')

def displaySetup():
    '''For a PyPi project, when ran inside its directory will display the configuration info of the file 'setup.py' 
       The function must be ran inside that current working directory or an exception will be thrown and handled telling
       the user to check the current working directory'''
    try:
        file = open('setup.py')
    except:
        print('Failed to open configuration file, check if current directory is PyPi project')
        return
    list = []
    for each_line in file:
        if not each_line.find(',') == -1:
            (info,space) = each_line.split(',',1)
            list.append(info)
            print(info)

    file.close()
    return list
