# --*-- coding：utf-8 --*--
'''

1.自己实现一个排序算法，不能使用python内置的sorted和sort，具体哪种排序算法不限；函数接口：mysort(data)
2.实现测试用例；
3.实现wordcount，自己找一篇英文文章或者句子，统计每个单词出现次数，并使用1中的排序算法输出排序后的结果； 
可选部分：
【 对于有一定基础的同学，可以考虑扩展接口如下
           mysort(data,key=somefunc,reveresed=True|False）
  支持自定义比较函数，比如按照sin(x)或者abs(x)结果排序这样；
'''


#字符统计
def wordcount(str):
    str_list = str.replace('\n', '').replace(',','').replace('.','').lower().split(' ')
    count_dict = {}
    for str in str_list:
        if str in count_dict.keys():
            count_dict[str] = count_dict[str] + 1
        else:
            count_dict[str] = 1
    return count_dict

#字典排序data为可迭代对象
def mysort(data):
    data = list(data.items())
    for i in range(len(data))[::-1]:
        for j in range(i):
            if data[j][1] > data[j+1][1]:
                data[j] ,data[j + 1]=data[j+1] ,data[j]
    return data

#仿造sorted函数的sort函数
def mysort(data,key=None,reversed=True):
    if(not hasattr(data,'__iter__')):
        raise TypeError('%s is not iterable',data)
    data = list(data)
    for i in range(len(data))[::-1]:
        for j in range(i):
            if ((key == None and data[j] > data[j+1]) or (key != None and key(data[j]) > key(data[j+1]))):
                data[j] ,data[j + 1]=data[j+1] ,data[j]
    return data if reversed else data[::-1]

#字典过滤的key值
def fn(x):
    return x[1]

if __name__ == '__main__':
    a={'H':1,'Ba':2,'c':4,'d':3}
    b=['ss','Ds','As','ab','fs']
    c='''WASHINGTON, May 11, (Xinhua) -- Chinese scientists demonstrated the first two-dimensional quantum
         walks of single photons in real spatial space, which may provide a powerful platform to boost analog quantum computing.
         They reported in a paper published on Friday in the journal Science Advances a three-dimensional photonic chip with a scale up to 49-multiply-49 nodes,
         by using a technique called femtosecond direct writing. Jin Xianmin, a quantum communication researcher with Shanghai Jiaotong University, who led the study, told Xinhua,
         it is the largest-scaled chip reported so far that allows for the realization of this two-dimensional quantum walk in real spatial space, and potential exploration for many new quantum computing tasks'''
    d=wordcount(c)
    print(d)
    print(a)
    print(sorted(b,key=str.lower))
    print(mysort(b,key=str.lower))
    print(mysort(d.items(),fn))
    
