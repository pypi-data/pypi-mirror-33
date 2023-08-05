'''
demo_nester.py模块,提供:
    1.print_lol函数,作用:打印列表(可处理嵌套列表)    
'''
#1
'''
    参数:
                    the_list:要打印的列表(可包含嵌套列表)
                    indent(可选参数):用来控制缩进的开启或关闭,默认为False,即关闭缩进
                    level(可选参数):遇到嵌套列表时插入的制表符数
                    file_name(可选参数):用来控制是否将列表内容写入文件,默认为sys.stdout,即打印到屏幕

      实现:
                    所指定的列表中的每个数据项会(递归地)输出到屏幕上,各数据各占一行,
                    (可选)在indent开启情况下,遇到嵌套列表时会打印level(可选)数目的制表符,
                    (可选)在file_name存在的情况下,每个数据项会(递归)地存入filename指定的文件中
'''
import sys
def print_lol(the_list,indent=False,level=0,file_name=sys.stdout):   
    for each_item in the_list :
        if isinstance(each_item,list) :
            print_lol(each_item,indent,level+1,file_name)
        else:
            if indent :
                for Tab in range(level) :
                    print("\t",end="",file=file_name)
            print(each_item,file=file_name)
            


