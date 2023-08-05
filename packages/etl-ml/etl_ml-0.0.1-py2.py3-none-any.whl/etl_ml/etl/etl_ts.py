from etl_ml.etl.etl_master import E_M
from etl_ml.etl.send_ftp_server import Send_Ftps_hive_server

import  pandas as pd
import  numpy as  np
import  logging
logger = logging.getLogger(
    name=__name__,
)

class ETL_TS(E_M):
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)

  def __init__(self,conf_sec='sec_test_score'):
    super().__init__()
    self.conf_sec = conf_sec
    self.etl_ts_file = self.config_parser.get(self.conf_sec, 'etl_ts_file')
    self.model_code=self.config_parser.get(self.conf_sec,'model_code')
    self.client_nmbr=self.config_parser.get(self.conf_sec,'client_nmbr')
    self.batch=self.config_parser.get(self.conf_sec,'batch')

    self.sheet_name=self.config_parser.get(self.conf_sec,'sheet_name')

    exp_fp='../data/'+self.client_nmbr+self.batch+'_'+self.model_code+'_etl.txt'
    self.export_ts_path=exp_fp
    self.hive_server_dir_path=self.config_parser.get(self.conf_sec,'hive_server_dir_path')
    self.raw_data=None

  def  reconstruct_df_export_file(self):
    self.raw_data = pd.read_excel(self.etl_ts_file, header=0, sheet_name=self.sheet_name, keep_default_na=False, dtype=np.str)
    self.raw_data.to_csv(self.export_ts_path, sep='\t', header=False, index=False, encoding='utf-8', na_rep='')
    logging.info(msg="文件清洗完成，生成文件 ：%s"%self.export_ts_path)
  def send_ts_ftp(self):
    logging.info(msg="准备上传ftp")
    #s_fu=Send_Ftps_hive_server()

    self.upload_batch_zip_file = self.export_ts_path
    logging.info(msg="清洗后的文件 : %s ,开始上传到 ftp 路径 : %s"%(self.upload_batch_zip_file,self.ftp_file_dir))

    self.push_file_ftp(self.upload_batch_zip_file)
    logging.info(msg="上传到ftp 成功 ,准备 ftpget 到 hive server")
    self.export_txtfile_path=self.upload_batch_zip_file
    #s_fu.hive_server_dir_path=self.hive_server_dir_path
    self.ftp_etl_file = self.upload_batch_zip_file
    self.ftpget_file_server()
    logging.info(msg="文件已经 到达 hive server %s, 请入库"%self.hive_server_dir_path)



  def ftpget_ts_server(self):
    print("log")


  def insert_ts_hive(self):
    print("log")

  def ts_reply_mail(self):
    print("log")

if __name__ == '__main__':
    es=ETL_TS()
    #es.reconstruct_df_export_file()
    es.send_ts_ftp()