# encoding:utf-8
from etl_ml.etl.etl_master import  E_M
import smtplib
from  configparser import  ConfigParser as cp
import os.path
from email.mime.text import  MIMEText
from email.mime.multipart import  MIMEMultipart
from email.mime.base import  MIMEBase
from email.encoders import encode_base64
from email.mime.application import MIMEApplication
import mimetypes
import  email.mime.multipart
import  email.mime.text
import logging


logger = logging.getLogger(
    name=__name__,
)
class EMail_Client(E_M):
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger(__name__)
  """
  邮件客户端
  """
  def __init__(self,send=None,title=None,body=None,conf_file='../conf/etl.conf',conf_sec="sec_email"):
    """
    初始化邮箱客户端，默认从配置文件里读取发送邮箱的 host port email pwd,并创建邮箱客户端连接
    """
    self.config_parser=cp()
    self.config_parser.read(conf_file,encoding='utf-8-sig')
    cps=self.config_parser
    self.conf_sec = conf_sec
    self.From=cps.get(conf_sec,"From")
    self.Host=cps.get(conf_sec,"Host")
    self.Port=cps.get(conf_sec,"Port")
    self.pwd=cps.get(conf_sec,"Pwd")
    self.To=cps.get(conf_sec,"To")
    self.Subject=cps.get(conf_sec,"Subject")
    self.Body=cps.get(conf_sec,"Body")
    self.Send_File_Name=None
    smtplib.SMTP()
    self.smtp_obj = smtplib.SMTP_SSL()
    self.smtp_obj.connect(host=self.Host, port=self.Port)
    result =self.smtp_obj.login(user=self.From, password=self.pwd)
    logger.info(msg=result)
    if str(result).endswith("successful')"):
      logger.info(msg="登录成功")


  def config_sec_value(self,key):
    """
    读取 配置文件 配置片段 的键所对应的值
    :param key: 配置文件 配置片段 的键
    :return:
    """
    field=self.config_parser.get(self.conf_sec,key)
    return field

  def send_normal_email(self,text=None,single_receiver=False):
    """
    发送 普通邮件 不带 附件,收件人可以单人 也可以多人
    :param text: 邮件正文内容
    :param single_receiver 是否为单用户 ，默认为真,多用户则以逗号分隔
    :return:
    """
    if text==None:
      text=self.config_parser.get(self.conf_sec,"Body")
    if single_receiver==False:
      to_mail_list=list(mail for mail in str(self.To).split(','))
    else:
      to_mail_list=str(self.To)
    message_content = '\n'.join(['From:%s' % self.From, 'To:%s' %self.To, 'Subject:%s' % self.Subject, '', text ])
    try:
      self.smtp_obj.sendmail(from_addr=self.From, to_addrs=to_mail_list, msg=str(message_content).encode('utf-8'))
      logger.info(msg="邮件发送成功")
      logger.info(msg="发送内容： %s"%message_content)
    except Exception as  ex:
      logger.error(msg="邮件发送失败failed %s" % ex)
      raise


  def  send_email_with_single_file(self,file_name=None,text=None,title=None,single_receiver=False):
      """
       发送带附件内容的邮件
       :param file_name: 文件名称 带文件全路径 相对路径 绝对路径都可以
       :param text: 邮件正文
       :param title: 邮件标题
       :param single_receiver: 是否为单用户 ，默认为假 ,多用户则以英文逗号分隔
       :return:
      """
      # 构造MIMEMultipart对象做为根容器
      main_msg = MIMEMultipart()
      if file_name==None:
        file_name=self.config_parser.get(self.conf_sec,'file_name')
        ## 设置附件头
      basename = os.path.basename(file_name)
      logger.info(msg="附件头 ： %s" % basename)
      if text==None:
        text=self.config_parser.get(self.conf_sec,"Body")
      attion="\n\n\n\n假如 使用foxmail客户端 附件名 显示为 未命名文件 ，请不要担心,这是foxmail客户端的bug，\n 只是文件名被篡改，重命名 原来的文件名即可，记得要填写后缀名,或者使用其他邮箱客户端正常打开"
      # 构造MIMEText对象做为邮件显示内容并附加到根容器
      text_msg = MIMEText("Hi Dear ：\n %s  \n 附件名为：%s \n %s"%(text,basename,attion))
      main_msg.attach(text_msg)
      if title ==None:
        main_msg['Subject'] = self.config_parser.get(self.conf_sec, "Subject")
      else:
        main_msg['Subject'] =title
      # 构造MIMEBase对象做为文件附件内容并附加到根容器
      to_mail_list_str = str(self.To)
      main_msg['To']=to_mail_list_str
      if single_receiver==False:
        to_mails_list=[mail for mail in to_mail_list_str.split(',')]
      else:
        to_mails_list=to_mail_list_str
      contype = 'application/octet-stream'
      maintype, subtype = contype.split('/', 1)
      logger.info(msg="传输附件 耗时较长 请耐心等待.....")
      ## 读入文件内容并格式化

      data = open(file_name, 'rb')
      file_msg = MIMEBase(maintype, subtype)
      file_msg.set_payload(data.read())
      data.close()
      encode_base64(file_msg)

      file_msg.add_header('Content-Disposition',
        'attachment', filename=('gbk', '', basename))
      main_msg.attach(file_msg)
      fullText = main_msg.as_string()

      # 用smtp发送邮件
      logger.info(msg=self.To)
      try:
        result=self.smtp_obj.sendmail(self.From, to_mails_list, fullText)
        logger.info(msg="恭喜你 %s 成功发送邮件给 %s 完毕"%(result,to_mail_list_str))
      finally:

        self.smtp_obj.quit()


  def  send_email_with_multi_file(self,file_name_list=None,text=None,title=None,single_receiver=False):
      """
      发送带多份附件内容的邮件
      :param file_name_list: 文件名称列表，带文件全路径 相对路径 绝对路径都可以，多份文件以英文逗号分隔
      :param text: 邮件正文
      :param title: 邮件标题
      :param single_receiver: 是否为单用户 ，默认为假 ,多用户则以英文逗号分隔
      :return:
      """
      # 构造MIMEMultipart对象做为根容器
      main_msg = MIMEMultipart()
      if file_name_list==None:
        file_name_list=self.config_parser.get(self.conf_sec,'file_name')
        ## 设置附件头
      upload_file_list=list(file for file in  str(file_name_list).split(','))
      flie_str=','.join(upload_file_list)
      if text==None:
        text=self.config_parser.get(self.conf_sec,"Body")
      attion="\n\n\n\n假如 使用foxmail客户端 附件名 显示为 未命名文件 ，请不要担心,这是foxmail客户端的bug，\n 只是文件名被篡改，重命名 原来的文件名即可，记得要填写后缀名,或者使用其他邮箱客户端正常打开"
      # 构造MIMEText对象做为邮件显示内容并附加到根容器
      text_msg = MIMEText("Hi Dear ：\n %s  \n 附件名为：%s \n %s"%(text,flie_str,attion))
      main_msg.attach(text_msg)
      if title ==None:
        main_msg['Subject'] = self.config_parser.get(self.conf_sec, "Subject")
      else:
        main_msg['Subject'] =title
      # 构造MIMEBase对象做为文件附件内容并附加到根容器
      to_mail_list_str = str(self.To)
      main_msg['To']=to_mail_list_str
      if single_receiver==False:
        to_mails_list=[mail for mail in to_mail_list_str.split(',')]
      else:
        to_mails_list=to_mail_list_str

      contype = 'application/octet-stream'
      maintype, subtype = contype.split('/', 1)
      logger.info(msg="传输附件 耗时较长 请耐心等待.....")
      ## 读入文件内容并格式化
      for  fi in upload_file_list:
        basename = os.path.basename(fi)
        logger.info(msg="附件头 ： %s" % basename)
        data = open(fi, 'rb')
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        data.close()
        encode_base64(file_msg)
        file_msg.add_header('Content-Disposition',
          'attachment', filename=('gbk', '', basename))
        main_msg.attach(file_msg)
      fullText = main_msg.as_string()

      # 用smtp发送邮件
      print(self.To)
      try:
        res=self.smtp_obj.sendmail(self.From, to_mails_list, fullText)
        logger.info(msg="恭喜你 成功发送邮件给 %s 完毕"%(to_mail_list_str))
      finally:

        self.smtp_obj.quit()

if __name__ == '__main__':
    em=EMail_Client()
    text='geo 发送多个人 带附件的邮件 东风快递'
    file_name="../data/AA80p2_DT_20180603_result_加工前数据.xlsx,../data/tmp_finance_model_data_source_xhh_0622_AA80p2.txt"
    file_nsame = "../data/AA80p2_DT_20180603_result_加工前数据.xlsx"
    #em.send_email_with_multi_file(file_name,text,"测试多份附件 渑池")
    em.send_email_with_single_file(file_nsame,text,title="测试单份附件 ok")
    #em.send_normal_email("有多个收件人",False)