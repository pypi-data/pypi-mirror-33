"""这是nester.py模块，提供了一个函数用来遍历列表"""
def print_lol(the_list, level):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for blanks in range(level):
                print("\t", end='')
            print(each_item)
