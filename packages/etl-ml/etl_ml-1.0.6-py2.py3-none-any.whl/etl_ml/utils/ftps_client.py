from ftplib import FTP
from ftplib import FTP_TLS

class  Ftps_client:
  ##初始化的时候会把登录参数赋值初始化
  def __init__(self,host,user,pwd,port=21):
    """
    ftps登录客户端 初始化
    :param host: ftps 主机名
    :param user: ftps 登录用户名
    :param pwd:  ftps 登录密码
    :param port: ftps 登录端口
    """
    self.host=host
    self.port=port
    self.user=user
    self.pwd=pwd
    self.Ftp=None
    #self._old_makepasv=FTP_TLS.makepasv

## ftp 登录项  含有闭包项
  def login(self,debug=2,set_pasv=True):
    """
    ftp服务器登录
    :param debug:
    :param set_pasv:
    :return:
    """
    _old_makepasv = FTP_TLS.makepasv
    def _new_makepasv(self):
      host, port = _old_makepasv(self)
      host = self.sock.getpeername()[0]
      return host, port
    FTP_TLS.makepasv = _new_makepasv
    self.Ftp = FTP_TLS(self.host)
    self.Ftp.set_debuglevel(debug)
    self.Ftp.auth()
    self.Ftp.login(self.user,self.pwd)
    self.Ftp.makepasv()
    self.Ftp.sendcmd('pbsz 0')
    self.Ftp.set_pasv(set_pasv)
    self.Ftp.prot_p()
    print("您好 您已经登录 ftp： %s 服务器" % self.host)
    self.Ftp.getwelcome()
    return self.Ftp


  def ftplistDir(self,ftps,sever_path):
    """
    显示  目录下的 文件列表
    :param ftps:
    :param sever_path:  服务器端 要 查看的目录路径
    :return:
    """
    self.Ftp.cwd("/")#首先切换得到根目录下，否则会出现问题
    self.Ftp.cwd(sever_path)
    files = ftps.nlst()
    for f in files:
      print(f)


  def  ftpDownloadSeverFile(self,sever_path,sever_file,new_localfile,buffersize=1024):
   """
   下载服务器文件
   :param sever_path: ftp服务器 要下载的 文件所在的目录路径
   :param sever_file: ftp服务器 要下载的文件名
   :param new_localfile: 对从ftp下载的文件在本地重新命名
   :param buffersize: 文件传输的 buffer size 默认不需要修改
   :return:
   """
   self.Ftp.cwd("/")
   self.Ftp.cwd(sever_path)
   with open(new_localfile , 'wb')as download_file:
      self.Ftp.retrbinary('RETR %s' %sever_file , download_file.write, buffersize)


  def  ftpUploadLocalFile(self,local_filepath,sever_path,new_severfile,buffersize=1024):
    """
    上传文件到ftp服务器
     需要注意 上传文件的  new_severfile 只能是文件名，不能包含带目录 的 文件全路径
    :param local_filepath:  本地文件 路径 包含全路径集 文件名
    :param sever_path:  ftp服务器的要上传文件的 服务器路径
    :param new_severfile:  对上传到ftp 服务器 文件的重新命名 注意：
                         需要注意 上传文件的  new_severfile
    :param buffersize:  传输读取字节的buffer  size  默认不需要修改
    :return:
    """
    self.Ftp.cwd("/")
    self.Ftp.cwd(sever_path)
    with open(local_filepath,'rb') as  upload_file:
      self.Ftp.storbinary('STOR ' + new_severfile, upload_file, buffersize)




def test():
  host = 'ftps.baidu.com'
  port = '21'
  user = 'zh****'
  pwd = 'zz****m'
  cli=Ftps_client(host,user,pwd,port)
  fs= cli.login(2,True)
  #fs.makepasv()
  # files = []
  # files = fs.nlst()
  # for f in files:
  #   print(f)
  path='china'
  cli.ftplistDir(fs,path)

##测试使用 通过
if __name__ == '__main__':
  test()