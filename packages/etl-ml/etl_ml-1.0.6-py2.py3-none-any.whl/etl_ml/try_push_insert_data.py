from etl_ml.etl.push_insert_hive import PUSH_INSERT_DATA
import  time
from  etl_ml.etl.etl_dt_origin import ETL_DT_Origin
from etl_ml.etl.etl_ts import ETL_TS
from etl_ml.etl.etl_label import ETL_Label
from  etl_ml.etl.add_cli_code import Add_Cli_Code
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
    """
    推送已经清洗好的 样本数据 到公司 的 hive 机器 并 insert到hive 的fkdb 库 tab_client_label 表中
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:
    """
    print("insert label data")
    pid = PUSH_INSERT_DATA(1,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def  push_gd_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的gd数据到公司 的 hive 机器 并 insert到hive fkdb 的 tab_fk_gd_data表中
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段

    :return:
    """
    print("insert gd data")
    pid = PUSH_INSERT_DATA(2,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_yl_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的 yl数据到公司 的 hive 机器 并 insert到hive fkdb 的 tab_fk_yl_v2_3 表中
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:

    """
    print("insert yl data")
    pid = PUSH_INSERT_DATA(3,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_dt_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的 duotou 数据到公司 的 hive 机器 并 insert到hive 的  fkdb.tab_fk_dt_v1 表中
        :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:
    :param param:
    :param push_file:
    :param zip_file:
    :param send_email:
    :return:
    """
    print("insert dt data")
    pid=PUSH_INSERT_DATA(4,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_dt_origin_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的 dt_origin 数据到公司 的 hive 机器 并 insert到hive  fkdb的 tab_fk_dt_origin 表中
        :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:
    :param param:
    :param push_file:
    :param zip_file:
    :param send_email:
    :return:
    """
    print("insert dt origin data")
    pid = PUSH_INSERT_DATA(5,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_th_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的 th 数据到公司 的 hive 机器 并 insert到hive fkdb 的tab_fk_th_score  表中
        :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch  model_code
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:

    """
    print("insert th data")
    pid = PUSH_INSERT_DATA(6,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)

  def push_ts_insert(self,param=None,push_file=True,zip_file=False,send_email=False):
    """
    推送清洗好的 test_score 数据到公司 的 hive 机器 并 insert到hive 的 tab_fk_testscore_indx**** 表中
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch  model_code
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:
    :param param:
    :param push_file:
    :param zip_file:
    :param send_email:
    :return:
    """
    print("insert ts data")
    pid = PUSH_INSERT_DATA(7,conf_file=self.true_conf_file)
    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)


  def push_normal_single_file_ftps_insert(self,num,param=None,push_file=True,zip_file=False,send_email=False):
    """
     推送清洗好的 某一清洗好的数据到公司ftp 再到 的 hive 机器 并 insert到hive 的 *** 表中,
    :param num: 1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch  model_code
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:

    """
    print("insert  data")
    pid = PUSH_INSERT_DATA(int(num),conf_file=self.true_conf_file)

    pid.exec_script_by_tunnel(param,push_file,zip_file,send_email)


  def push_normal_single_file_scp_insert(self, num, param=None, push_file=True, zip_file=False, send_email=False):
    """
     推送清洗好的 某一清洗好的数据 scp到我们的 测试集群 hive 机器 并 insert到hive 的 *** 表中, 暂时还不能使用
    :param num: 1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :param param: 额外的 入库执行 配置参数，默认 会配置好client_nmbr batch  model_code
    :param push_file:  是否推送本地文件到hive 机器，如果文件已经存在于hive机器，可以不推送则为False
    :param zip_file:  传输的文件是否被压缩，如果被压缩了则为True
    :param send_email: 是否发送邮件，默认不发送，如果发送 请配置好 etl.conf [sec_email] 片段
    :return:

    """
    print("insert  data")
    pid = PUSH_INSERT_DATA(int(num), conf_file=self.true_conf_file)
    pid.exec_script_by_ssh(param, push_file, zip_file, send_email)


  def push_zip_file_ftps_runx_batch_insert(self,num):
    """
    执行把打包到一个zip 批量的同类数据文件  zip压缩包 ftp上传 到hive 服务器 并入库  暂时不支持th 批量，暂时还有点小问题
    :param num:  1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :return:
    """
    print("insert batch Data to hive ")
    pid = PUSH_INSERT_DATA(int(num), conf_file=self.true_conf_file)
    self.insert_script ='runx.sh'
    mv_txt_guidang='mv %s/AA*txt %s/guidang'%(pid.hive_server_dir_path,pid.hive_server_dir_path)
    pid.exec_ssh_command(cmd_str=mv_txt_guidang)
    pid.exec_script_by_tunnel(param=None, push_file=True, zip_file=True, send_email=False)


  def push_zip_file_scp_runx_batch_insert(self,num):
    """
    执行把打包到一个zip 批量的同类数据文件  zip压缩包 scp 上传 到我们 测试集群 hive 服务器 并入库  暂时不支持th 批量，暂时还不可以使用
    :param num:  1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :return:
    """
    print("insert batch Data to hive ")
    pid = PUSH_INSERT_DATA(int(num), conf_file=self.true_conf_file)
    self.insert_script ='runx.sh'
    mv_txt_guidang='mv %s/AA*txt %s/guidang'%(pid.hive_server_dir_path,pid.hive_server_dir_path)
    pid.exec_ssh_command(cmd_str=mv_txt_guidang)
    pid.exec_script_by_ssh(param=None, push_file=True, zip_file=True, send_email=False)


  def  elt_dt_orgin(self,pc_local_path='/Users/geo/Documents/gudan/',e_m_config_file='conf/etl.conf',ssh_conf_file='conf/etl.conf'):
    """
    dt_origin 多头原始指标加工 包括 甘工给的数据清洗 及上传到 dt加工服务器 并执行脚本 加工
    :param pc_local_path: 多头加工后结果 下载到本地 要保存到本地的目录
    :param e_m_config_file:  加工父类 的配置文件地址，默认不需要修改
    :param ssh_conf_file:  ssh 客户端 的配置文件地址，默认不需要修改
    :return:
    """
    et = ETL_DT_Origin(e_m_config_file=e_m_config_file)
    et.save_export_file()
    et.dt_origin_send_azkaban_exec_pipeline(ssh_conf_file=ssh_conf_file)

    #et.download_dt_origin_from_azkaban(pc_local_path,ssh_conf_file='conf/etl.conf')

  def clear_test_score_xlsx(self,e_m_config_file='conf/etl.conf'):
    """
    清洗原始的test_socre Excel文件为 可以入库的txt 文件
    :param e_m_config_file:加工父类 的配置文件地址，默认不需要修改
    :return:
    """
    es=ETL_TS(e_m_config_file=e_m_config_file)
    es.reconstruct_df_export_file()

  def clear_label_insert(self,config_file='conf/etl.conf',is_export_excel=True, csv_header=False):
    """
    清洗客户给的样本数据 并上传 到hive 服务器 并入库
    :param config_file:  label 的配置文件 ，默认不需要修改
    :param is_export_excel:  是否导出 excel ，默认为True 导出
    :param csv_header:  导出的 txt 文件是否带 header ，默认不带
    :return:
    """
    etl = ETL_Label(config_file=config_file)
    df = etl.re_construct_df_by_raw_header_loc_char_dict()
    etl.save_export_files(df, is_export_excel=is_export_excel, csv_header=csv_header)
    print(df.head())
    etl.put_etlfile_ftp()
    etl.exec_ftp_get_mv_insert_command()

  def only_ftp_upload_file(self,num):
    """
    只是 通过ftp 上传文件 到 hive 机器而已
    :param num:  参数绝对了要上传到 hive 的哪个 目标目录中 1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :return:
    """
    print("upload ftp   data")
    pid = PUSH_INSERT_DATA(int(num),conf_file=self.true_conf_file)
    pid.push_etl_data_use_ftps()

  def only_scp_upload_file(self,num):
    """
    只是 通过scp 上传文件 到 hive 机器而已
    :param num:  参数绝对了要上传到 hive 的哪个 目标目录中 1 ：label ；2 ：gd ; 3:yl ;4:duotou ; 5 :dt_origin ; 6:th ;7: test_Score
    :return:
    """
    print("upload scp   data")
    pid = PUSH_INSERT_DATA(int(num),conf_file=self.true_conf_file)
    pid.push_etl_data_use_scp()

  def add_new_customer_id(self,num,client_name=None,client_code=None):
    """
    新增客户编号
    :param client_name:  客户中文名
    :param client_code:  客户 code
    :return:
    """
    print("add new customer id  data")
    pid = PUSH_INSERT_DATA(int(num),conf_file=self.true_conf_file)
    if client_name!=None:
      pid.etl_insert_file=client_name
    if client_code !=None:
      pid.client_nmbr=client_code
    pid.batch=None
    pid.exec_script_by_tunnel(param=None,push_file=False,zip_file=False,send_email=False)

    add_code=Add_Cli_Code(client_name,client_code)
    add_code.exec_add_cli_code()

if __name__ == '__main__':
    print("****将要上传已经清洗后的数据并插入hive数据库，请确认配置文件 和函数参数 配置正确*****")
    try_push=Try_Push_ETL()
    time.sleep(1)
    try_push.elt_dt_orgin()
    #try_push.clear_test_score_xlsx()
    #try_push.clear_label_insert()
    #try_push.push_normal_insert(7,push_file=True,zip_file=False,send_email=False)

