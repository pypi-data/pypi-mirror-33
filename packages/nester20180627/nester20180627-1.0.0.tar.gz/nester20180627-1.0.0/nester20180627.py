"""这是一个"nester20180627.py"的模块，提供一个名为print_lol()的函数，这个函数作用是打印列表，
其中有可能包含（也可能不包含）嵌套列表。"""
def print_lol(the_list):
    """这个函数取第一个位置参数，名为"the_list" ,这可以是任何Python列表（也可以包含嵌套列表的列表）。所指定
    的列表中每个数据项会（递归地）输出到屏幕上，各数据各占一行。"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
