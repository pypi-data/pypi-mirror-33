from etl_ml.etl.etl_master import E_M

import  logging
logger = logging.getLogger(
    name=__name__,
)

class  Send_Ftps_hive_server(E_M):
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)

  def __init__(self,sec='sec_upload_batch_zip_file'):
    super().__init__()
    self.sec_upload_file=sec
    self.upload_batch_zip_file=self.config_parser.get(self.sec_upload_file, 'upload_batch_zip_file')
    self.hive_server_dir_path=self.config_parser.get(self.sec_upload_file, 'hive_server_dir_path')

    #发送文件到 ftp服务器 ，并 从ftp  下载到hive服务器
  def send_batch_zip_file_func(self):
    logging.info(msg='开始上传 到ftp服务器 %s'%self.upload_batch_zip_file)
    self.push_file_ftp(self.upload_batch_zip_file)
    self.export_txtfile_path =self.upload_batch_zip_file
    self.ftp_etl_file =self.upload_batch_zip_file
    logging.info(msg='开始 拉取到 hive  服务器目录 %s'%self.hive_server_dir_path)
    self.ftpget_file_server()


if __name__ == '__main__':
    sf=Send_Ftps_hive_server()
    sf.send_batch_zip_file_func()