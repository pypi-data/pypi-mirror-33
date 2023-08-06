from etl_ml.etl.etl_master import  E_M
import pandas as pd
import numpy as np
from datetime import datetime
import  logging
import  os
from etl_ml.utils.ssh_utils import SSH_Cli
logger = logging.getLogger(
    name=__name__,
)
class ETL_DT_Origin(E_M):
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)
  def __init__(self,e_m_config_file='../conf/etl.conf',sec_name='sec_dt_origin_edit',tmp_pre='tmp_finance_model_data_source_'):
    super().__init__(config_file=e_m_config_file)
    self.raw_col_names=['id', 'gid', 'realname','mobile', 'certid',  'card', 'apply_time',
                  '信贷平台注册详情(如有多条命中,以分号分隔)', '贷款申请详情', '贷款放款详情', '贷款驳回详情', '逾期平台详情',
                  '欠款详情']
    self.sheet_name=self.config_parser.get(sec_name,"sheet_name")
    self.dt_origin_file=self.config_parser.get(sec_name,"dt_origin_file")
    self.date_Filed=self.config_parser.get(sec_name,"date_Filed")
    self.phone_Filed=self.config_parser.get(sec_name,"phone_Filed")
    self.idcard_Filed=self.config_parser.get(sec_name,"idcard_Filed")
    self.client_nmbr=self.config_parser.get(sec_name,"client_nmbr")
    self.batch=self.config_parser.get(sec_name,"batch")
    self.cn_simple_name=self.config_parser.get(sec_name,"cn_simple_name")
    self.source_path =self.config_parser.get(sec_name,'source_path')
    self.result_path =self.config_parser.get(sec_name,'result_path')
    self.shell_path =self.config_parser.get(sec_name,'shell_path')
    self.exec_pipeline =self.config_parser.get(sec_name,'exec_pipeline')
    logging.info(msg="各项配置参数已经加载。。。")
    dt=datetime.now()
    self.date_mid=dt.strftime('_%m%d_')
    self.file_extension='.txt'
    self.export_txt_file=os.getcwd()+"/data/"+tmp_pre+self.cn_simple_name+self.date_mid+self.client_nmbr+self.batch+self.file_extension
    self.raw_data=pd.read_excel(self.dt_origin_file, sheet_name=self.sheet_name,
      dtype={self.idcard_Filed: np.str, self.date_Filed: np.str,self.phone_Filed:np.str})
    logging.info(msg="已经 加载文件 %s 到pandas 中... "%self.dt_origin_file)


  def load_dt_origin_excel_file(self):
    raw_data = pd.read_excel(self.dt_origin_file, sheetname=self.sheet_name,
      dtype={'certid': np.str, 'apply_time': np.str, 'mobile': np.str})
    return raw_data

  def re_construct_df(self):
    self.raw_data['id'] = self.raw_data.index
    try:
      self.raw_data['apply_time'] = pd.to_datetime(self.raw_data['apply_time'], format='%Y/%m/%d', errors='coerce')
      self.raw_data['apply_time'] = self.raw_data['apply_time'].apply(lambda x: x.strftime('%Y/%m/%d'))
    except Exception as ex:
      logging.error(msg="时间 列 含有异常值 请检验 %s"%ex)
      raise

    logging.info(msg="已经将原始文件做了相关的清洗和处理")

  def  save_export_file(self,encoding='utf-8'):
    self.re_construct_df()
    print(self.raw_data.columns)
    print("若提示某列名不在index 导致 keyError，可能excel 列名存在空格 剔除 即可")
    self.new_data = self.raw_data[self.raw_col_names]
    self.new_data.to_csv(self.export_txt_file, sep='\t', header=False, index=False, encoding=encoding)
    logging.info(msg="导出文件成功，文件路径 ： %s "%self.export_txt_file)

  def  dt_origin_send_azkaban_exec_pipeline(self,ssh_conf_file="../conf/etl.conf",source_path='/home/hiveuser/dt_orgin_edit_script/source/',exec_path='/home/hiveuser/dt_orgin_edit_script/shell/pipeline.sh',shell_path='/home/hiveuser/dt_orgin_edit_script/shell/'):
    print("上传文件并执行")
    ssh_cli=SSH_Cli(conf_file=ssh_conf_file)
    server_flie=str(self.export_txt_file).split("/")[-1]
    sub_dir = self.cn_simple_name + self.date_mid + self.client_nmbr + self.batch
    #self.hive_server_dir_path="/home/hiveuser/dt_orgin_edit_script/source/"+sub_dir
    self.hive_server_dir_path =source_path + sub_dir
    mkdir_cmd_str="mkdir -p %s"%self.hive_server_dir_path
    ssh_cli.exec_single_cmd(mkdir_cmd_str)
    base_dir_tmp_file=os.getcwd()[:-3]+"data/"+server_flie
    print(base_dir_tmp_file)
    #lp="/Users/geo/Documents/etl_ml/etl_ml/data/tmp_finance_model_data_source_xhh_0622_AA80p2.txt"
    ssh_cli.scp_upload_local_file_to_server(local_path=base_dir_tmp_file,server_path=self.hive_server_dir_path,server_file='')

   # ssh_cli.scp_upload_local_file_to_server(local_path=lp, server_path=self.hive_server_dir_path,server_file=server_flie)

    #script_path='/home/hiveuser/dt_orgin_edit_script/shell/pipeline.sh'
    shell_exec_cmd='sh %s %s '%(exec_path,sub_dir)
    print(shell_exec_cmd)
    #shell_dir='/home/hiveuser/dt_orgin_edit_script/shell/'
    cd_dir_cmd="cd %s"%shell_path
    exec_cmd_list=[cd_dir_cmd,shell_exec_cmd]
    ssh_cli.exec_batch_cmd(exec_cmd_list)

  def  download_dt_origin_from_azkaban(self,pc_local_path,ssh_conf_file="../conf/etl.conf",resource_path='/home/hiveuser/dt_orgin_edit_script/result/'):
    print("开始下载已经加工好的文件")
    sub_dir = self.cn_simple_name + self.date_mid + self.client_nmbr + self.batch
    #export_path='/home/hiveuser/dt_orgin_edit_script/result/%s'%sub_dir
    export_path =resource_path+sub_dir
    print("目标目录: %s"%export_path)
    ssh_cli = SSH_Cli(conf_file=ssh_conf_file)
    print("注意去 你的电脑 %s 下查收 %s 的zip 压缩文件"%(pc_local_path,sub_dir))
    ssh_cli.scp_download_file_from_server(local_path=pc_local_path,server_path=export_path,server_file='*.zip')



if __name__ == '__main__':
    et=ETL_DT_Origin()

    et.save_export_file()
    #et.dt_origin_send_azkaban_exec_pipeline()
    pc_local_path='/Users/geo/Documents/gudan'
    et.download_dt_origin_from_azkaban(pc_local_path)
    # sec='sec_dt_origin_editor'
    # final_col_list='final_columns_list'
    # final_col=et.config_parser.get(sec,final_col_list)
    # ls=list(final_col.strip(',').split(','))
    # for l in ls:
    #   print(l)
    #print(final_col)
