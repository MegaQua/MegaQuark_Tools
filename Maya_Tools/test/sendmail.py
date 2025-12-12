import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 发件人和收件人邮箱
sender_email = "kyuuitu@gmail.com"
receiver_email = "kyuuitu@gmail.com"
password = "xdlanwyjyjbmwgzn"  # 应用程序专用密码

# 创建邮件对象
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Python SMTP 邮件测试"

# 邮件正文内容
body = "这是通过Python发送的邮件测试内容。"
message.attach(MIMEText(body, "plain"))

# SMTP 服务器设置
smtp_server = "smtp.gmail.com"
smtp_port = 465  # SSL端口通常为465

# 发送邮件
try:
    # 使用SMTP_SSL而不是SMTP
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(sender_email, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
    print("邮件发送成功！")
except Exception as e:
    print(f"邮件发送失败: {e}")
