
from collections import defaultdict
from collections import Counter
import  math
import  numpy as np
import  pandas as pd

class Data_Stat:
  def __init__(self,datalist=[]):

    self.data_list=datalist
#求平均数
  def mean(self,datalist):
    size=len(datalist)
    sum=0
    for ele in datalist:
      sum+=int(ele)
    mean=sum/size
    return  mean

#求中位数
  def  median(self,datalist):
    size=len(datalist)
    newsort_list=sorted(datalist,key=lambda x:x,reverse=False)
    print(newsort_list)
    if size%2==1:
      medium_index=int((size+1)/2-1)
      medium=newsort_list[medium_index]
    else:
      medium_pre_index=size/2
      medium=(newsort_list[medium_pre_index]+newsort_list[medium_pre_index+1])/2
    return medium

#求分位数
  def  quantitle(self,datalist,percent):
    size=len(datalist)
    new_sort_list=sorted(datalist,key=lambda x:x,reverse=False)
    print(new_sort_list)
    percent_index=int(size*percent)-1
    print("index is %s"%percent_index)
    return new_sort_list[percent_index]




#求众数
  def mode(self,datalist):
    num_dict=Counter(datalist)
    print(num_dict)
    sort_dict=sorted(num_dict.items(),key=lambda x:x[1],reverse=False)
    print(sort_dict)
    print(sort_dict[-1][0])
    morenu=sort_dict[-1][0]
    return morenu

#求极差
  def  data_range(self,datalist):
    sort_list=sorted(datalist,key=lambda x:x,reverse=False)
    sub=float(sort_list[-1]-sort_list[0])
    return sub


  #求方差
  def  variance(self,datalist,bias=True):
    mean=self.mean(datalist)
    sum=0
    for ele in  datalist:
      #print("ele %f ,mean %f "%(ele,mean))
      sub=float(ele) - mean
      square=math.pow(sub,2)
      print("sub %f ,square %f "%(sub,square))
      sum+=square
    if bias:
      variance=sum/len(datalist)
    else :
      variance=sum/(len(datalist)-1)
    return variance

#求标准差
  def  standard_deviation(self,datalist):
    var=self.variance(datalist)
    std=math.sqrt(var)
    return std


  def do_mean(self,datalist):
    mean_num=self.mean(datalist)
    mean_list=list()
    for ele in datalist:
      mean_list.append(ele-mean_num)
    return mean_list

  def sum_square(self,datalist):
    sum=0
    for ele in datalist:
      sum+=math.pow(ele,2)
    return sum
  def  variance_tmp(self,datalist,bias=True):
    sum=self.sum_square(self.do_mean(datalist))
    if bias:
      variance = sum / len(datalist)
    else:
      variance=sum/(len(datalist)-1)
    return variance

  def describe(self,datalist):
    mean=self.mean(datalist)
    data_range=self.data_range(datalist)
    mode=self.mode(datalist)
    quantitle_pre=self.quantitle(datalist,0.25)
    quantitle_median=self.quantitle(datalist,0.5)
    quantitle_suf=self.quantitle(datalist,0.75)
    variance=self.variance_tmp(datalist)
    stdev=self.standard_deviation(datalist)
    print("""
    mean : %f ,
    data_range: %f ,
    mode: %s ,
    quantitle_0.25: %f ,
    quantitle_0.5: %f ,
    quantitle_0.75: %f  ,
    variance: %f ,
    stdev: %f ,
    
    """%(mean,data_range,mode,quantitle_pre,quantitle_median,quantitle_suf,variance,stdev))

#求协方差
  def  convariance(self,data_x,data_y,bias=False):
    size_x=len(data_x)
    size_y=len(data_y)
    if size_x==size_y:
      data_x_mean=self.do_mean(data_x)
      data_y_mean=self.do_mean(data_y)
      convar=np.dot(data_x_mean,data_y_mean)
      if bias==False:
        convariance=convar/(size_x-1)
      else:
        convariance = convar / size_x
    else:
      convariance=None
    return convariance
#求相关度
  def correlation(self,data_x,data_y):
    stdev_x=self.standard_deviation(data_x)
    stdev_y=self.standard_deviation(data_y)
    convariance=self.convariance(data_x,data_y)
    if stdev_x >0 and stdev_y >0:
      correlation=convariance/stdev_x/stdev_y
      return correlation
    else:
      return 0
  def normal_pdf(self,x,mu=0,sigma=1):
    sqrt_two_pi_sigma=math.sqrt(2*math.pi)*sigma
    fx=math.exp(-math.pow((x-mu),2)/2*math.pow(sigma,2))/sqrt_two_pi_sigma
    return fx




if __name__ == '__main__':
  datalist = [3, 6, 23, 6, 8, 2, 8, 9, 12, 5, 3, 7, 6]
  data_y=[4, 16, 3,8, 8, 9, -3, 5, 22, 15, 3, 11, 3]
  d_s=Data_Stat(datalist)
  # var_1=d_s.variance(d_s.data_list)
  # var_2=d_s.variance_tmp(d_s.data_list)
  # print("var1: %f, var2: %f"%(var_1,var_2))
  # d_s.describe(d_s.data_list)
  # print(d_s.convariance(datalist,data_y))
  # print(d_s.correlation(datalist,data_y))
  print(d_s.normal_pdf(0.0001))

