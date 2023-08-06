#Author Zhang Ting
def hz_nest_print(list_obj):
    for item in list_obj:
        if isinstance(item,list):
            hz_nest_print(item)
        else :
            print(item)

