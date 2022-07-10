from urllib.parse import urlparse, urlunparse
import xmlrpc.client
from datetime import datetime

import functools
import xmlrpc.client


def xmlrpc_exceptions(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except xmlrpc.client.Fault as err:
            return False, err.faultString
        except xmlrpc.client.ProtocolError as err:
            return False, err.faultString
        except Exception as err:
            return False, str(err)

    return wrapped


class Process:
    """ Process Class """

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.name = self.dictionary["name"]
        self.description = self.dictionary["description"]
        self.start = self.dictionary["start"]
        self.stop = self.dictionary["stop"]
        self.now = self.dictionary["now"]
        self.state = self.dictionary["state"]
        self.statename = self.dictionary["statename"]
        self.spawnerr = self.dictionary["spawnerr"]
        self.exitstatus = self.dictionary["exitstatus"]
        self.stdout_logfile = self.dictionary["stdout_logfile"]
        self.stderr_logfile = self.dictionary["stderr_logfile"]
        self.pid = self.dictionary["pid"]

        self.start_hr = datetime.fromtimestamp(self.start).strftime(
            "%Y-%m-%d %H:%M:%S"
        )[11:]
        self.stop_hr = datetime.fromtimestamp(self.stop).strftime("%Y-%m-%d %H:%M:%S")[
                       11:
                       ]
        self.now_hr = datetime.fromtimestamp(self.now).strftime("%Y-%m-%d %H:%M:%S")[
                      11:
                      ]

        if self.state == 20:
            __uptime_string = self.description.split(",")[1].strip()
            self.uptime = __uptime_string.split(" ")[1].strip()
        else:
            self.uptime = 0

        self.dictionary.update(
            {
                "start_hr": self.start_hr,
                "stop_hr": self.stop_hr,
                "now_hr": self.now_hr,
                "uptime": self.uptime,
            }
        )

    @property
    def node(self):
        return self.dictionary["node"]

    @node.setter
    def node(self, name):
        self.dictionary["node"] = name

    @property
    def environment(self):
        return self.dictionary["environment"]

    @environment.setter
    def environment(self, name):
        self.dictionary["environment"] = name

    def serialize(self):
        return self.dictionary


class XmlRpc:
    @staticmethod
    def connection(host, port, username, password):
        if not (host.startswith("http://") or host.startswith("https://")):
            host = "http://" + host
        scheme, netloc, path, params, query, fragment = urlparse(host)
        path = path.rstrip("/")
        server = "{}:{}".format(netloc, port)
        if not (username == "" and password == ""):
            server = "{username}:{password}@{server}".format(
                username=username, password=password, server=server
            )

        uri = urlunparse((scheme, server, path + "/RPC2", params, query, fragment))

        # print(uri)
        return xmlrpc.client.ServerProxy(uri)


class Node:
    def __init__(self, name, host, port, username, password):
        self.name = name
        self.environment = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = XmlRpc.connection(
            self.host, self.port, self.username, self.password
        )

    @property
    def processes(self):
        try:
            return [
                Process(_p) for _p in self.connection.supervisor.getAllProcessInfo()
            ]
        except Exception as _:
            return []

    @property
    def is_connected(self):
        return self.__connect()

    def __connect(self):
        status, msg = self.get_system_list_methods_for_xmlrpc_server()
        if not status:
            print("Node: '{}', Error: '{}'".format(self.name, msg))
        return status

    @xmlrpc_exceptions
    def get_system_list_methods_for_xmlrpc_server(self):
        self.connection.system.listMethods()
        return True, "Okey, got system list methods"

    @xmlrpc_exceptions
    def get_process(self, unique_name):
        _p = self.connection.supervisor.getProcessInfo(unique_name)
        return Process(_p), ""

    def get_process_logs(self, unique_name):
        stdout_log_string = self.connection.supervisor.tailProcessStdoutLog(
            unique_name, 0, 1000
        )[0]
        stderr_log_string = self.connection.supervisor.tailProcessStderrLog(
            unique_name, 0, 1000
        )[0]
        logs = {
            "stdout": stdout_log_string.split("\n")[1:-1],
            "stderr": stderr_log_string.split("\n")[1:-1],
        }
        return logs

    @xmlrpc_exceptions
    def start_process(self, unique_name):
        if self.connection.supervisor.startProcess(unique_name):
            return True, ""
        else:
            return False, "cannot start process"

    @xmlrpc_exceptions
    def stop_process(self, unique_name):
        if self.connection.supervisor.stopProcess(unique_name):
            return True, ""
        else:
            return False, "cannot stop process"


    def restart_process(self, unique_name):
        process, msg = self.get_process(unique_name)
        if process is False:

            return process, msg

        elif process.state == 20:
            status, msg = self.stop_process(unique_name)
            if not status:
                return status, msg
        else:
            self.start_process(unique_name)
            return process, msg


    def serialize_general(self):
        return {
            "name": self.name,
            "environment": self.environment,
            # "host": self.host,
            # "port": self.port,
            # "username": self.username,
            # "password": self.password,
            "connected": self.is_connected,
        }

    def serialize_processes(self):
        response = []
        for p in self.processes:
            row = p.serialize()
            response.append(
                {
                    "environment": self.environment,
                    "name": row['name'],
                    "group": row['group'],
                    "start": row['start'],
                    "stop": row['stop'],
                    "now": row['now'],
                    "state": row['state'],
                    "statename": row['statename'],
                    "spawnerr": row['spawnerr'],
                    "exitstatus": row['exitstatus'],
                    "logfile": row['logfile'],
                    "stdout_logfile": row['stdout_logfile'],
                    "stderr_logfile": row['stderr_logfile'],
                    "pid": row['pid'],
                    "description": row['description'],
                    "start_hr": row['start_hr'],
                    "stop_hr": row['stop_hr'],
                    "now_hr": row['now_hr'],
                    "uptime": row['uptime']
                }
            )

        return response

    def serialize(self):
        return self.serialize_processes()

    def full_name(self):
        return "node:{}".format(self.name)


confi = {
    "environment--01": {
        "name": "environment--01",
        "username": "user",
        "password": "123",
        "host": "192.168.60.120",
        "port": "9001",
    },
    "environment--02": {
        "name": "environment--02",
        "username": "user",
        "password": "123",
        "host": "192.168.60.120",
        "port": "9001",
    },
    "environment--03": {
        "name": "environment--03",
        "username": "user",
        "password": "123",
        "host": "192.168.60.120",
        "port": "9001",
    },
}


def run():
    np = Node("environment--02", "192.168.95.120", '9001', 'user', '123')
    import json
    print(json.dumps(np.serialize()))
    # print(np.get_process_logs("celery-beat"))
    # print(np.restart_process("celery-beat"))
    # print(np.stop_process("celery-beat"))
    # print(np.stop_process("celery-master"))
    print(np.start_process("celery-master"))


#
# run()
