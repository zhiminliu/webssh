#-*- encoding:utf-8 -*-  
#author: zhiminliu
  
import tornado.web  
import tornado.websocket  
import tornado.httpserver  
import tornado.ioloop  
import paramiko
import time
import socket
import sys
import threading
import Queue
import json

class MyThread(threading.Thread):  
    def __init__(self,id,chan):  
        threading.Thread.__init__(self)  
        self.chan=chan
    def run(self):  
        while not self.chan.chan.exit_status_ready():
            time.sleep(0.1)
            try:
                data = self.chan.chan.recv(1024) 
                data_json={"data":data}
                self.chan.write_message(json.dumps(data_json))
            except Exception,ex:
                print str(ex)
        self.chan.sshclient.close()
        return False

class BaseHandler(tornado.web.RequestHandler):  
    def get_current_user(self):  
        return self.get_secure_cookie("username") 

class LoginHandler(BaseHandler):  
    def get(self):  
        self.render('index.html')  
    def post(self):  
        ##获取参数
        args=self.request.arguments
        print args
        global host
        host=args["h"][0]
        global port
        port=args["p"][0]        
        global username
        username=args["u"][0]
        global passwd
        passwd=args["passwd"][0]
        global rows
        rows=args["rows"][0]
        global cols
        cols=args["cols"][0]
        try:
            sshclient=paramiko.SSHClient()
            sshclient.load_system_host_keys()
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(host,int(port),username,passwd)
            self.set_secure_cookie("username",username)
            print u"登录成功"
            respon_json={"status":True,"response":""}
        except Exception,ex:
            print u"登录失败"
            respon_json={"status":False,"response":str(ex)}
            #print str(ex)
        
        self.write(json.dumps(respon_json))
        
  
class WebSocketHandler(tornado.websocket.WebSocketHandler):  
    def check_origin(self, origin):  
        return True  
    def open(self):
        self.sshclient=paramiko.SSHClient()
        self.sshclient.load_system_host_keys()
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshclient.connect(host,int(port),username,passwd)
        self.chan=self.sshclient.invoke_shell(term='xterm',width=int(cols), height=int(rows))
        self.chan.settimeout(0)
        t1=MyThread(999,self)
        t1.setDaemon(True)
        t1.start() 
        
    def on_message(self, message):  
        try:
            self.chan.send(message)
        except Exception,ex:
            print str(ex)
        
    def on_close(self):  
        self.sshclient.close()
  
class Application(tornado.web.Application):  
    def __init__(self):  
        handlers = [  
            (r'/',LoginHandler),  
            (r'/ws', WebSocketHandler)  
        ]  
  
        settings = { "template_path": ".","static_path": "static","cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=","login_url":"/"}  
        tornado.web.Application.__init__(self, handlers, **settings)  
  
if __name__ == '__main__':  
    ws_app = Application()  
    server = tornado.httpserver.HTTPServer(ws_app)  
    server.listen(8011)  
    tornado.ioloop.IOLoop.instance().start()  
  
''''' 
python ws_app.py 
'''  

