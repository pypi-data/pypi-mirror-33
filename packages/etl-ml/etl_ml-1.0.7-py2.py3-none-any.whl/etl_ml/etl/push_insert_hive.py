
from configparser import  ConfigParser as  cp
import logging

from etl_ml.etl.etl_master import E_M
from etl_ml.utils.ssh_utils import SSH_Cli
from etl_ml.utils.em_cli import  EMail_Client
import  datetime
import time
logger = logging.getLogger(
    name=__name__,
)

class PUSH_INSERT_DATA(E_M,SSH_Cli):
  """
  推送数据到hive 机器  并入库的hive 数据库
  """
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)

  def __init__(self,conf_sec=None,conf_file='../conf/etl.conf',em_ssh_config_file='conf/etl.conf'):
    super().__init__(config_file=em_ssh_config_file)
    print(conf_file)
    self.config_parser=cp()
    self.config_parser.read(conf_file,encoding='utf-8-sig')
    cps=self.config_parser
    def switchs(conf_sec):
      intkey =int(conf_sec)
      switch={
         0:'sec_insert_client_code',
         1:'sec_insert_label',
         2:'sec_insert_gd',
         3:'sec_insert_yl',
         4:'sec_insert_dt',
         5:'sec_insert_dt_origin',
         6: 'sec_insert_th',
         7:'sec_insert_ts'
      }
      vals=switch.get(intkey)
      return vals
    self.conf_sec=switchs(conf_sec)
    cs=self.conf_sec
    print("开始PUSH_INSERT_DATA 初始化配置")
    print("开始寻找 PUSH_INSERT_DATA的配置项，请确认 EM 的配置文件路径是否正确")
    self.etl_insert_file=cps.get(cs,'etl_insert_file')
    print("找到寻找PUSH_INSERT_DATA的配置项")
    self.client_nmbr=cps.get(cs,'client_nmbr')
    if int(conf_sec)!=0:
      self.batch=cps.get(cs,'batch')
    self.hive_server_dir_path=cps.get(cs,'hive_server_dir_path')
    self.insert_script=cps.get(cs,'insert_script')
    self.hive_host=cps.get(cs,'hive_host')
    self.conf_sec_num=conf_sec
    if  int(conf_sec)==6 or int(conf_sec)==7:
      self.model_code=cps.get(cs,'model_code')


  def push_etl_data_use_ftps(self):
    """
    使用ftp推送文件到 hive 机器，中间需要ftp服务器中转 适用于 有跳板机的hive
    :return:
    """
    logger.info(msg="使用ftp推送文件到 hive 机器")
    self.push_file_ftp(upload_etl_file=self.etl_insert_file)
    self.ftp_etl_file=self.etl_insert_file
    self.ftpget_file_server()
    logger.info(msg="推送文件到 hive 机器 成功")

  def send_email_team(self,params=None,to=None):
    em_cli=EMail_Client()
    if params==None:
      params=" "
    body="""
    风控组同事 ：
      大家好， %s 文件已经上传入库，
      分区：client_nmbr=%s
          batch=%s
      %s
      如有问题请与我联系
      祝好
      
    彭堂超
    
    """%(self.etl_insert_file,self.client_nmbr,self.batch,params)
    if to!=None:
      em_cli.To =to
    #em_cli.To='dmfk.list@geotmt.com'
    em_cli.send_normal_email(text=body,single_receiver=True)
    print("log")


  def exec_script_by_tunnel(self,params=None,push_file=True,zip_file=False,send_email=False):
    """
    #小问题 文件上传了，脚本执行命令 正确，但是数据却没有真正入库，除了样本以外都这种情况
    使用 ssh tunnel技术 执行shell  script ，适用于 有跳板机的hive
    :param params: 执行脚本所需要的必要参数 一般读取 etl.conf配置文件中的 client_nmbr  batch 等，额外参数 再在这里配置
    :param  push_file  是否推送文件 ，默认为True 意思是 入库脚本函数执行前，要入库的文件还没有上传到hive，如果为False,说明要入库的文件已经上传到hive了
    :param zip_file  是否为zip rar 压缩文件 ，默认为False 如果为真True  则需要解压，一般多头 多头原始指标 txt都比较大，需要压缩加快传输
    :return:
    """
    logger.info(msg="使用 ssh tunnel技术 执行shell  script")
    if push_file==True:
      self.push_etl_data_use_ftps()
    self.export_txtfile_path=self.etl_insert_file
    if zip_file==True:
      zip_file_loc=str(self.hive_server_dir_path)+"/"+str(self.etl_insert_file).split("/")[-1]
      unzip_cmd_str="unzip   %s -d %s"%(zip_file_loc,self.hive_server_dir_path)
      logger.info(msg="解压文件 %s"%unzip_cmd_str)
      self.exec_ssh_command(self.hive_host, unzip_cmd_str)
      self.export_txtfile_path =str(self.etl_insert_file).replace("zip","txt")
   # self.exec_ssh_command(self.hive_server_dir_path)
    if params == None:
      etl_file = str(self.etl_insert_file).split('/')[-1]
      if int(self.conf_sec_num) < 6:
        params = "\t" + self.client_nmbr + "\t" + self.batch
      else:
        params =  "\t" + self.client_nmbr + "\t" + self.batch + '\t' + self.model_code
    logger.info(params+"\t"+str(self.hive_server_dir_path)+"/"+str(self.insert_script))
    self.script_insert_hive( script_param_str=params,hive_server_dir_path=self.hive_server_dir_path , script_name=self.insert_script)
    if send_email==True:
      self.send_email_team()



  def push_etl_data_use_scp(self):
    """
    使用 scp 技术 推送 文件到hive机器 ，适用于 没有跳板机 本地机器可以直连 hive机器
    :return:  local_path,server_path=None,server_file=None
    """
    logger.info(msg="使用 scp 技术 推送 文件到hive机器")
    server_file=str(self.etl_insert_file).split("/")[-1]
    self.local_host='127.0.0.1'
    self.local_user='geo'
    self.local_pwd='geotmt'
    ssh_Cli=SSH_Cli()
    self.hive_server_dir_path = '/home/hiveuser/fk_data/label_data'
    ssh_Cli.scp_upload_local_file_to_server(local_path=self.etl_insert_file,server_path=self.hive_server_dir_path,server_file=server_file)

  def exec_script_by_ssh(self,params=None,push_file=True,zip_file=False,send_email=False):
    """
    使用 ssh 技术 执行 shell 脚本命令，适用于 没有跳板机，本地机器可以直连hive的机器
    :param params: 执行脚本所需要的必要参数
    :param  push_file  是否推送文件 ，默认为True 意思是 入库脚本函数执行前，要入库的文件还没有上传到hive，如果为False,说明要入库的文件已经上传到hive了
    :return:
    """

    logger.info(msg="")
    if push_file==True :
      self.push_etl_data_use_scp()
    insert_script_path=self.hive_server_dir_path+"/"+self.insert_script
    if zip_file==True:
      zip_file_loc=str(self.hive_server_dir_path)+"/"+str(self.etl_insert_file).split("/")[-1]
      unzip_cmd_str="unzip   %s -d %s"%(zip_file_loc,self.hive_server_dir_path)
      logger.info(msg="解压文件 %s"%unzip_cmd_str)
      self.exec_ssh_command(self.hive_host, unzip_cmd_str)
      self.export_txtfile_path =str(self.etl_insert_file).replace("zip","txt")
    if params==None:
      etl_file=str(self.etl_insert_file).split('/')[-1]
      if  int(self.conf_sec_num)<6:
        params=etl_file+"\t"+self.client_nmbr+"\t"+self.batch
      else:
        params = etl_file + "\t" + self.client_nmbr + "\t" + self.batch+'\t'+self.model_code

    self.exec_server_shell_script(script_path=insert_script_path,args=params)
    if send_email==True:
      self.send_email_team()


if __name__ == '__main__':
    print("推送清洗后的数据到hive 库")
    # pi=PUSH_INSERT_DATA(1)
    # pi.exec_script_by_tunnel(push_file=False,zip_file=False)
    #pi = PUSH_INSERT_DATA(6)
    #pi.exec_script_by_ssh()
    #pi.exec_script_by_tunnel(zip_file=False)

