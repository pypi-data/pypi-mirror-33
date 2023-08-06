import  paramiko as  pm
import  os
from  configparser import ConfigParser
import logging

logger = logging.getLogger(
    name=__name__,
)
class SSH_Cli():
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)
  def __init__(self,host=None,user=None,pwd=None,server_path=None,server_file=None,local_path=None,port=22,conf_file="../conf/etl.conf",conf_sec="sec_server_file_up_down"):
    """
    ssh 客户端  默认初始化ssh 并创建ssh连接
    :param host:
    :param user:
    :param pwd:
    :param server_path:
    :param local_path:
    :param port:
    :param conf_file:
    :param conf_sec:
    """
    print("初始化 ssh_client")
    self.get_pty=True
    self.config_parser = ConfigParser()
    self.config_parser.read(conf_file,encoding='utf-8-sig')
    cps=self.config_parser
    self.conf_sec=conf_sec
    self.port=port
    self.host=host
    print("host %s "%host)
    if host==None:
      self.host =cps.get(self.conf_sec,'host')
      print("配置的host %s"%self.host)
    self.user=user
    if user==None:
      self.user = cps.get(self.conf_sec,'user')
    self.pwd=pwd
    if pwd==None:
      self.pwd =cps.get(self.conf_sec,'pwd')
    print("马上创建 ssh _client")
    self.ssh_client=pm.SSHClient()
    self.ssh_client.set_missing_host_key_policy(pm.AutoAddPolicy())
    self.ssh_client.connect(hostname=self.host,username=self.user,port=self.port,password=self.pwd)
    self.server_path=server_path
    if server_path==None:
      self.server_path =cps.get(self.conf_sec,'server_path')
    self.local_path=local_path
    if local_path==None:
      self.local_path=cps.get(self.conf_sec,'local_path')
    self.server_file=server_file
    if server_file==None:
      self.server_file = cps.get(self.conf_sec, 'server_file')
    self.local_user=cps.get(self.conf_sec,'local_user')
    self.local_host=cps.get(self.conf_sec,'local_host')
    self.local_pwd=cps.get(self.conf_sec,'local_pwd')

    self.transport=pm.Transport((self.host,self.port))
    self.transport.connect(username=self.user,password=self.pwd)

  def config_sec_value(self, key):
      """
      读取 配置文件 配置片段 的键所对应的值
      :param key: 配置文件 配置片段 的键
      :return:
      """
      field = self.config_parser.get(self.conf_sec, key)
      return field


  def  exec_single_cmd(self,cmd_str):
    """
    执行 单条服务器 shell 命令
    :param cmd_str: 命令字符串
    :return: 返回执行结果输出
    """
    stdin, stdout, stderr = self.ssh_client.exec_command(cmd_str)
    for  line in stdout:
      print(line.strip('\n'))

  def exec_server_shell_script(self,script_path,args):
    """
    执行 服务器 脚本 ，
    注意：要确认登录的用户是否有权限执行 ，另外文件是否是可执行文件
    :param script_path: 服务器端脚本 绝对路径
    :param args: 执行脚本的参数
    :return: 返回执行的结果输出
    """
    cmd_str="sh %s %s"%(script_path,args)
    stdin, stdout, stderr = self.ssh_client.exec_command(cmd_str)
    for line in stdout:
      print(line.strip('\n'))

  def  exec_batch_cmd(self,cmd_list):
    """
    执行 多条服务器 shell 命令列表
    :param cmd_list: shell 命令 字符串列表
    :return:返回执行结果输出
    """
    cmd_list_str=";".join(cmd_list)
    stdin, stdout, stderr =self.ssh_client.exec_command(cmd_list_str,get_pty=self.get_pty)
    for  line in stdout:
      print(line.strip('\n'))

  def  scp_download_file_from_server(self,local_path,server_path=None,server_file=None):
    """
    从服务器 下载文件到本地
    :param local_host: 本地 host 比如127.0.0.1 要确认本机电脑已经开启ssh服务，否则会失败
    :param local_user: 本地 电脑登录 用户
    :param local_pwd:  本地 电脑登录用户密码
    :param local_path:  要下载到本地的保存目录
    :param server_path:  要下载文件在服务器端的路径
    :param server_file:  要下载的服务器文件名
    :return: 执行结果输出
    """
    scp_str="sshpass -p  %s scp -r %s/%s %s@%s:%s "%(self.local_pwd,server_path,server_file,self.local_user,self.local_host,local_path)
    print(scp_str)
    # scp_str="sshpass -p geotmt scp -r /home/hiveuser/dt_orgin_edit_script/result/zyxj_0621_AA38p2/zyxj_0621_AA38p2_v1.0_20180622.zip geo@10.111.25.103:/Users/geo/Document/gudan/ "
    stdin, stdout, stderr = self.ssh_client.exec_command(scp_str, get_pty=self.get_pty)
    print("文件已经下载到你的电脑目录： %s/%s"%(local_path,server_file))
    for line in stdout:
      print(line.strip('\n'))

  def scp_upload_local_file_to_server(self,local_path,server_path=None,server_file=None):
    """
    从本地上传文件到服务器
    :param local_host: 本地 host 比如127.0.0.1 要确认本机电脑已经开启ssh服务，否则会失败
    :param local_user: 本地 电脑登录 用户
    :param local_pwd:  本地 电脑登录用户密码
    :param local_path:  要上传到本地的保存目录
    :param server_path:  要上传文件在服务器端的路径
    :param server_file:  要上传的服务器文件名
    :return: 执行结果输出
    """
    local_host=self.local_host
    local_user=self.local_user
    local_pwd=self.local_pwd
    scp_str = "sshpass -p  %s scp -r %s@%s:%s%s %s " % (
    local_pwd,  local_user, local_host, local_path, server_file,server_path)
    print(scp_str)
    #sshpass -p  'geotmt' scp -r 'geo'@'10.111.25.103':/Users/geo/Documents/etl_ml/etl_ml/data/tmp_finance_model_data_source_xhh_0622_AA80p2.txt /home/hiveuser/dt_orgin_edit_script/source/xhh_0626_AA80p2

    stdin, stdout, stderr = self.ssh_client.exec_command(scp_str, get_pty=self.get_pty)

    print("文件将要上传到到测试服务器 目录： %s/%s" % (server_path, server_file))
    for line in stdout:
      print(line.strip('\n'))
    print("如果出现 【Host key verification failed.】 ，请修改 ssh 配置信息")



if __name__ == '__main__':
  host = "cdhnode1"
  user = '***'
  pwd = '*****'

  ssh_cli=SSH_Cli(host=host,user=user,pwd=pwd)
  local_user=ssh_cli.config_sec_value('local_user')
  local_host=ssh_cli.config_sec_value('local_host')
  local_pwd=ssh_cli.config_sec_value('local_pwd')
  server_file =ssh_cli.config_sec_value('server_file')
  server_path = ssh_cli.config_sec_value('server_path')
  local_path = ssh_cli.config_sec_value('local_path')
  #server_path = '/home/hiveuser/dt_orgin_edit_script/result/zyxj_0621_AA38p2'
  #ssh_cli.scp_download_file_from_server(local_host,local_user,local_pwd,local_path,server_path,server_file)
  ssh_cli.scp_upload_local_file_to_server(local_path,server_path,server_file)







  # host = "127.0.0.1"
  # user = 'geo'
  # pwd = 'geotmt'
  # local_user='geo'
  # local_host='10.111.25.103'
  # local_pwd='geotmt'
  # server_file ='zyxj_0621_AA38p2_v1.0_20180622.zip'
  # server_path = '/home/hiveuser/'
  #server_path = '/home/hiveuser/dt_orgin_edit_script/result/zyxj_0621_AA38p2'
  #local_path = '/Users/geo/Document/gudan/'

# ssh_cli=pm.SSHClient()
# ssh_cli.set_missing_host_key_policy(pm.AutoAddPolicy())
# ssh_cli.connect(hostname=host,username=user,port=22,password=pwd)
#
# stdin, stdout, stderr =ssh_cli.exec_command("cd /home/hiveuser/dt_orgin_edit_script/shell/ ; sh ./pipeline.sh zyxj_0621_AA38p2",get_pty=True)


# except Exception as ex:

# scp_str="scp -r root@cdhnode1:/home/hiveuser/dt_orgin_edit_script/result/zyxj_0621_AA38p2/zyxj_0621_AA38p2_v1.0_20180622.zip  /Users/geo/Document/gudan/"
# os.system(scp_str)
#
# ftp=pm.SFTPClient.from_transport(self.transport)
# local_path="/home/hiveuser/dt_orgin_edit_script/result/zyxj_0621_AA38p2/zyxj_0621_AA38p2_v1.0_20180622.zip"
# server_path="geo@10.111.25.103:/Users/geo/Document/gudan/"
# ftp.put(server_path,local_path)
# local_host='10.111.25.103'
# #stdin.write('Password:\n')
# # stdin.write('geotmt\n')
# # stdin.flush()

