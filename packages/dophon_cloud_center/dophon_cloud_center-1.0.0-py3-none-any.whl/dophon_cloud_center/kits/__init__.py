import hashlib
import schedule
from urllib import request, parse
import urllib3
import time
import json

_sech = schedule.Scheduler()

req_pool = urllib3.PoolManager()


class service_cell():
    __host = None
    __port = None
    __heart_interface = None
    __id = None

    def __init__(self, host, port, hear_url='/heart'):
        self.__host = host
        self.__port = port
        self.__heart_interface = hear_url
        self.__id = hashlib.sha1(
            (str(self.__host) + str(self.__port) + str(self.__heart_interface)).encode('utf8')).hexdigest()

    def __dict__(self):
        return {
            'id': self.__id,
            'host': self.__host,
            'port': self.__port,
            'heart_interface': self.__heart_interface
        }

    def __eq__(self, other):
        return self.__id == other['id']


class heart_sech():
    __sech = _sech
    __reg = {}

    def __init__(self, time):
        self.__sech.every(time).seconds.do(self.heart_beat)

    '''
    心跳一跳操作
    '''

    def heart_beat(self):
        try:
            # 获取每个服务
            for service_name in self.__reg:
                # 获取每个服务的实例列表
                services = self.__reg[service_name]
                # print(services)
                services_copy = services
                for instence in services:
                    # 获取每个具体实例
                    # print(instence)
                    ip_addr = str(instence['host']).split(':')[0]
                    url = 'http://' + ip_addr + ':' + instence['port'] + instence['heart_interface']+'/as/'+service_name
                    print('发送心跳:', url)
                    try:
                        res = req_pool.request(method='POST', url=url,
                                               body=bytes(json.dumps(self.__reg),encoding='utf8'),
                                               headers={
                                                   'Content-Type': 'application/json'
                                               })
                        res_result=eval(res.data.decode('utf8'))
                        if res_result['event'] == 404:
                            # 实例注册信息有误
                            services_copy.remove(instence)
                            self.__reg[service_name] = services_copy
                    except Exception as e:
                        # 连接失败打印错误信息
                        print(e, service_name, ip_addr, instence['port'], '连接失败,移除对应实例', )
                        services_copy.remove(instence)
                        self.__reg[service_name] = services_copy
                if 0 >= len(services):
                    self.__reg.pop(service_name)
                    if 0 >= len(self.__reg):
                        break;
        except Exception as e:
            print(e)
        # print(self.__reg)

    def update_reg(self, reg_info):
        self.__reg = reg_info

    def start_heart(self):
        while True:
            self.__sech.run_pending()
            time.sleep(15)


def get_heart(time=15):
    """
        :param time: 心跳检查时间,默认15秒,最低15秒(线程等待时间)
    """
    return heart_sech(time)
