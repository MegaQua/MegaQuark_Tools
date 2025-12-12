# === Sender ===
import socket

HOST = "127.0.0.1"
PORT = 5055
path = r"C:\Users\qiu\Desktop\test.py"  # 修改为你的脚本路径

s = socket.socket()
s.connect((HOST, PORT))
s.send(path.encode("utf-8"))
s.close()
