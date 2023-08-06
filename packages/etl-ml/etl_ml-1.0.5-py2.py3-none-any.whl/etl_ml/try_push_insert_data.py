from etl_ml.etl.push_insert_hive import PUSH_INSERT_DATA
import  time
from  etl_ml.etl.etl_dt_origin import ETL_DT_Origin
from etl_ml.etl.etl_ts import ETL_TS
from etl_ml.etl.etl_label import ETL_Label
# pi = PUSH_INSERT_DATA(6)
# pi.exec_script_by_ssh()
# pi.exec_script_by_tunnel(zip_file=False)
# 1: 'sec_insert_label',
# 2: 'sec_insert_gd',
# 3: 'sec_insert_yl',
# 4: 'sec_insert_dt',
# 5: 'sec_insert_dt_origin',
# 6: 'sec_insert_th',
# 7: 'sec_insert_ts'
class Try_Push_ETL:
  def __init__(self):
    self.true_conf_file='/Users/geo/Documents/etl_ml/etl_ml/conf/etl.conf'

  def push_label_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert label data")
    pid = PUSH_INSERT_DATA(1,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def  push_gd_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert gd data")
    pid = PUSH_INSERT_DATA(2,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_yl_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert yl data")
    pid = PUSH_INSERT_DATA(3,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_dt_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert dt data")
    pid=PUSH_INSERT_DATA(4,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_dt_origin_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert dt origin data")
    pid = PUSH_INSERT_DATA(5,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_th_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert th data")
    pid = PUSH_INSERT_DATA(6,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_ts_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert ts data")
    pid = PUSH_INSERT_DATA(7,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)


  def push_normal_insert(self,num,param=None,push_file=True,zip_file=False,send_email=False):
    print("insert  data")
    pid = PUSH_INSERT_DATA(int(num),conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)


  def  elt_dt_orgin(self,pc_local_path='/Users/geo/Documents/gudan/'):
    et = ETL_DT_Origin(e_m_config_file='conf/etl.conf')
    et.save_export_file()
    et.dt_origin_send_azkaban_exec_pipeline(ssh_conf_file='conf/etl.conf')

    et.download_dt_origin_from_azkaban(pc_local_path,ssh_conf_file='conf/etl.conf')

  def clear_test_score_xlsx(self):
    es=ETL_TS(e_m_config_file='conf/etl.conf')
    es.reconstruct_df_export_file()

  def clear_label_insert(self):
    etl = ETL_Label(config_file='conf/etl.conf')
    df = etl.re_construct_df_by_raw_header_loc_char_dict()
    etl.save_export_files(df, is_export_excel=True, csv_header=False)
    print(df.head())
    etl.put_etlfile_ftp()
    #etl.exec_ftp_get_mv_insert_command()

if __name__ == '__main__':
    print("****将要上传已经清洗后的数据并插入hive数据库，请确认配置文件 和函数参数 配置正确*****")
    try_push=Try_Push_ETL()
    time.sleep(1)
   # try_push.elt_dt_orgin()
    #try_push.clear_test_score_xlsx()
    try_push.clear_label_insert()
    #try_push.push_normal_insert(7,push_file=True,zip_file=False,send_email=False)

