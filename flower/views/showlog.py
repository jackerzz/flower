import logging
import time
from tornado import web,gen,ioloop
import json
from ..views import BaseHandler
from ..utils.node import Node
from ..conf import confi
from tornado.concurrent import Future
logger = logging.getLogger(__name__)


class ShowlogView(BaseHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        app = self.application
        self.render("showlog.html", broker_url=app.capp.connection().as_uri(), )

class ProcessManagement(web.RequestHandler):

    def get(self):
        '''
        获取进程信息列表
        :return:
        '''
        response = self.getAllNodeProcessInfo()
        self.write(json.dumps(response))

    def post(self):
        param = self.request.body.decode('utf-8')
        prarm = json.loads(param)
        logger.info(prarm['action'])
        logger.info(prarm['name'])
        action = prarm['action']
        name = prarm['name']
        environment = prarm['environment']
        if action != "allRestart":
            self.manager(environment,name,action)

        elif action == "allRestart":
            self.allRestart(name)

    def manager(self,env,name,action):
        row = confi[env]
        nd = Node(row['name'], row['host'], row['port'], row['username'], row['password'])
        process, msg = True,"操作成功"
        if action == "start":
            process, msg =nd.start_process(name)

        elif action == "stop":
            process, msg = nd.stop_process(name)

        elif action == "restart":
            process, msg=nd.restart_process(name)

        if process:
            self.write(json.dumps({"进程":name,"环境":env,"操作类型":action,"状态":"ok","msg":msg}))
        else:
            self.write(json.dumps({"进程": name, "环境": env, "操作类型": action, "状态": "失败","msg":msg}))



    def allRestart(self,name):
        for env,row in confi.items():
            nd = Node(row['name'],row['host'],row['port'],row['username'],row['password'])
            nd.restart_process(name)

    def getAllNodeProcessInfo(self):
        '''
        此处可以优化为并发
        '''
        data = []

        for env,row in confi.items():
            nd = Node(row['name'],row['host'],row['port'],row['username'],row['password'])
            data.extend(nd.serialize_processes())

        response = {"status": 0, "msg": "ok", "data": {"count": len(data), "rows": data}}
        return response

class StreamingHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        future = Future()
        unique_name = self.get_argument('name')
        ioloop.IOLoop.current().add_timeout(time.time() + 1, self.do_some_stuff,unique_name)
        self.np = Node("environment--02", "192.168.95.120", '9001', 'user', '123')
        yield future

    def do_some_stuff(self,unique_name):
        if self.request.connection.stream.closed():
            logger.info("客户端关闭：%s" % (unique_name))
            return
        logger.info("回调：%s"%(unique_name))
        logs = self.np.get_process_logs(unique_name)
        for row in logs['stdout']:
            self.write(row+"\n")
        self.flush()
        ioloop.IOLoop.current().add_timeout(time.time() + 1, self.do_some_stuff, unique_name)


