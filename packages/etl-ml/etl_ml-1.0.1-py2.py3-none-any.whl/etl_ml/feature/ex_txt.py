import pandas as pd
import  numpy as np
import json
from  pandas.io.json import json_normalize

ganpath="logs/中原消金多头日志AA31P2_DT.xlsx"
sheet_name="外部日志详情"
etl_label_path='logs/AA38_p2_new_etl(1).xlsx'
# 手机号1  身份证  真实姓名  外部接口返回json
gandata=pd.read_excel(ganpath,sheet_name=sheet_name,header=0,encoding='utf-8',dtype={'手机号1':np.str})

# 'gid', 'realname', 'certid', 'mobile', 'card', 'apply_time', 'y_label',
#'apply_amount', 'apply_period', 'overdus_day', 'sense_code'

# etl_Data=pd.read_csv(etl_label_path,sep='\t',encoding='utf-8',header=None,dtype=np.str,names=['gid', 'realname', 'certid', 'mobile', 'card', 'apply_time', 'y_label',
# 'apply_amount', 'apply_period', 'overdus_day', 'sense_code'])

etl_Data=pd.read_excel(etl_label_path,sheet_name='Sheet1',header=0,encoding='utf-8',dtype={'mobile':np.str})
print(gandata.columns)
mergeda = pd.merge(gandata, etl_Data, how='inner', left_on='手机号1', right_on='mobile'
                                                                            '', suffixes=('_r', '_y'))
ex_merge=mergeda[['gid', 'realname',  'mobile', 'certid', 'apply_time','外部接口返回json/xml']]

ex_path='data_AA38p2.txt'
with open(ex_path,'w',encoding='utf-8') as f:
  ex_merge.apply(lambda row: f.write(str(row[0])+'\t'+str(row[1])+'\t'+str(row[2])+'\t'+str(row[3])+'\t'+str(row[4])+'\t'+str(row[5])+'\n'),axis=1)


# ex_merge=mergeda[['gid', 'realname', 'certid', 'mobile', 'card', 'apply_time','手机号1','外部接口返回json/xml']]
#
# ex_path='data_ex.txt'
# with open(ex_path,'w',encoding='utf-8') as f:
#   ex_merge.apply(lambda row: f.write(str(row[0])+'\t'+str(row[1])+'\t'+str(row[2])+'\t'+str(row[3])+'\t'+str(row[4])+'\t'+str(row[5])+'\t'+str(row[6])+'\t'+str(row[7])+'\n'),axis=1)
#




#
# path='/Users/geo/Downloads/小赢日志_加工前数据_to研发.xlsx'
#
# rawdata=pd.read_excel(path,header=0,encoding='utf-8',sheet_name='日志')
# dps='xiaoyss.txt'
#
# #rawdata.to_csv(dp,encoding='utf-8',index=False,sep='\t',header=True)
#
# nedata=rawdata[['gid', '真实姓名', '手机号1', '身份证', 'apply_time','外部接口返回json']]
# with open(dps,'w',encoding='utf-8') as f:
#   nedata.apply(lambda row: f.write(str(row[0])+'\t'+str(row[1])+'\t'+str(row[2])+'\t'+str(row[3])+'\t'+str(row[4])+'\t'+str(row[5])+'\n'),axis=1)
#
#
#
#mergeda.to_csv(dppp,encoding='utf-8',sep='\t',header=True,index=False)