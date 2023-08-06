from flask import Flask, jsonify, request as reqq
from urllib import request, parse
import socket, hashlib, re, time, threading
import urllib3


class micro_cell():
    '''
    远程请求调用封装类,用urllib处理请求发送和响应处理
    '''

    # 暂时启用轮询方式访问实例
    __instance_index = 0

    def __init__(self, e_app, service_name: str, interface: str, data=None, headers={},
                 origin_req_host=None, unverifiable=False,
                 method=None):

        self.__interface = interface
        self.__service_name = service_name.upper()
        self.__interface_app = e_app
        info = e_app.reg_info()
        if self.__service_name in info:
            # 获取服务对应的实例列表
            self.__instances = info[self.__service_name]
        else:
            # 服务不存在请求注册中心获得服务实例信息
            self.__interface_app.async_reg_info()
            # 再次检查服务信息
            if self.__service_name in e_app.reg_info():
                self.__instances = e_app.reg_info()[self.__service_name]
            else:
                raise Exception('服务不存在!!!')
        instance = self.__instances[self.__instance_index]
        # 检查服务注册信息(防止调用自身)
        if self.__interface_app.service_name() == self.__service_name:
            print('警告::使用有风险的远程调用单元(', self.__service_name, ',', self.__interface, ')')
            try:
                if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                        and \
                        instance['port'] is self.__interface_app.port():
                    # 检查请求路径
                    self.__instances.pop()
                instance = self.__instances[self.__instance_index]
            except Exception as e:
                print(e)
        url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
        self.__id = instance['id']
        self.__req_obj = request.Request(url=url, data=data, headers=headers,
                                         origin_req_host=origin_req_host, unverifiable=unverifiable,
                                         method=method)

    def __str__(self):
        return hashlib.sha1(
            (re.sub(':', '', self.__host) + str(self.__interface)).encode('utf8')).hexdigest()

    def __eq__(self, other):
        return str(other) == self.__str__()

    def request(self, data=None):
        '''
        发起远程请求
        :param data: 请求数据
        :return: 请求响应
        '''
        # 重写数据集(无数据集调用初始化数据集)
        _data = data if data else self.__req_obj.data
        instance = self.__instances[self.__instance_index]
        # 检查服务注册信息(防止调用自身)
        if self.__interface_app.service_name() == self.__service_name:
            print('警告::(有风险)使用远程调用单元调用自身服务(', self.__service_name, ',', self.__interface, ')')
            try:
                if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                        and \
                        instance['port'] is self.__interface_app.port():
                    # 检查请求路径
                    self.__instances.pop()
                else:
                    self.__instance_index = self.__instance_index + 1
                instance = self.__instances[self.__instance_index]
                url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
                setattr(self.__req_obj, 'full_url', url)
            except Exception as e:
                print(e)
        res = request.urlopen(self.__req_obj, data=bytes(parse.urlencode(_data), encoding="utf8") if _data else None)
        # 轮询方式访问实例
        self.__instance_index = (self.__instance_index + 1) if self.__instance_index < len(self.__instances) - 2 else 0
        self.__id = instance['id']
        url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
        setattr(self.__req_obj, 'full_url', url)
        # 处理结果集
        return eval(res.read().decode('utf8'))

    def pool_request(self, pool: urllib3.PoolManager, data: dict = None):
        """
        池化http请求方式发起远程调用
        :param pool: urllib3连接池实例
        :param data:请求参数
        :return:
        """
        # 轮询方式访问实例
        instance = self.__instances[self.__instance_index]
        # 检查服务注册信息(防止调用自身)
        if self.__interface_app.service_name() == self.__service_name:
            print('警告::(有风险)使用远程调用单元调用自身服务(', self.__service_name, ',', self.__interface, ')')
            try:
                if instance['host'] is socket.gethostbyname(socket.getfqdn(socket.gethostname())) \
                        and \
                        instance['port'] is self.__interface_app.port():
                    # 检查请求路径
                    self.__instances.pop()
                else:
                    self.__instance_index = self.__instance_index + 1
                instance = self.__instances[self.__instance_index]
            except Exception as e:
                print(e)
        url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
        res = pool.request(method=self.__req_obj.get_method(), url=url, fields=data)
        self.__id = instance['id']
        self.__instance_index = (self.__instance_index + 1) if self.__instance_index < len(self.__instances) - 2 else 0
        url = str('http://' + instance['host'] + ':' + instance['port'] + self.__interface)
        setattr(self.__req_obj, 'full_url', url)
        return eval(res.data.decode('utf8')) if res.status == 200 else {'event': res.status, 'msg': '服务调用异常'}


class micro_cell_list():
    '''
    服务调用集合类,自带urllib3连接池
    '''
    __family = {}

    def __init__(self, app, pool_size: int = 10, properties: dict = {}):
        '''
        初始化远程调用实例集群

        连接池默认连接数为10

        配置格式:{
            service_name<str> :[
                {
                    public_interface_prefix_1<str>:[
                            interface_prefix_1<str>,
                            interface_prefix_2<str>,
                            ...
                        ]
                },
                {
                    public_interface_prefix_2<str>:[
                            interface_prefix_1<str>,
                            interface_prefix_2<str>,
                            ...
                        ]
                },
                    ...
                ]
        }

        初始化后集群格式:
            {
                service_name<str>:
                    {
                        public_interface_prefix_1<str>:{
                                interface_prefix_1<str>:<micro_cell>,
                                interface_prefix_2<str>:<micro_cell>,
                                interface_prefix_3<str>:<micro_cell>,
                                ...
                        },
                        public_interface_prefix_1<str>:{
                                interface_prefix_1<str>:<micro_cell>,
                                interface_prefix_2<str>:<micro_cell>,
                                interface_prefix_3<str>:<micro_cell>,...
                        }
                    },...
            },...
        '''

        # 根据配置初始化集群
        if properties:
            # 存在集群配置
            for k, v in properties.items():
                services = {}
                for pub_v_item in v:
                    public_interfaces = {}
                    for k_item in pub_v_item:
                        if not str(k_item).startswith('/'):
                            raise Exception('配置路径格式有误,请以/开头(service_name:' + k + ',public_prefix:' + k_item + ')')
                        v_item = pub_v_item[k_item]
                        interface = {}
                        for item in v_item:
                            if not str(item).startswith('/'):
                                raise Exception(
                                    '配置路径格式有误,请以/开头(service_name:' + k + ',public_prefix:' + k_item + ',prefix:' + item + ')')
                            # 实例化远程调用实例
                            m_cell = micro_cell(app, str(k), str(k_item) + str(item))
                            interface[item] = m_cell
                        public_interfaces = interface
                    services[k_item] = public_interfaces
                self.__family[k.upper()] = services
        # 初始化连接池
        self.__req_pool = urllib3.PoolManager(pool_size)

    def request(self, service_name: str, interface: list, data: dict = None):
        """
        直接使用配置的服务调用单元集群发起请求
        使用多线程发起请求
        :param service_name: 服务名
        :param interface: 接口名,格式[公用接口,细化接口]
        :return:
        """
        try:
            _pub_interface_prefix = interface[0]
        except Exception:
            # 无法取值则默认为空
            _pub_interface_prefix = ''
        try:
            _interface_prefix = interface[1]
        except Exception:
            # 无法取值则默认为空
            _interface_prefix = ''
        args = (service_name.upper(), _pub_interface_prefix, _interface_prefix, self.__req_pool, data)
        target_obj = lambda x, y, z, pool, data=None: self.__family[x][y][z].pool_request(pool=pool, data=data)
        result = target_obj(*args)
        return result

    def get_cell_obj(self, service_name: str, interface: list):
        """
        获取对应服务调用单元实例<micro_cell>
        :param service_name: 服务名
        :param interface: 接口名,格式[公用接口,细化接口]
        :return:
        """
        _pub_prefix = interface[0] if interface[0] else ''
        _prefix = interface[1] if len(interface) > 1 and interface[1] else ''
        return self.__family[service_name][_pub_prefix][_prefix]


class e_app(Flask):
    '''

    服务器封装类(不支持dophon)


    请求的发送和封装使用urllib3处理
    简单的一个基于flask服务器的一个实例
    '''

    __host = '127.0.0.1'
    __port = 5000
    __reg_url = 'http://localhost:8361/reg/service/'
    __reg_update_url = None
    __reg_info = {}
    __reg_heart = False

    '''
    增强app内部定义连接池(默认10个连接数)
    '''
    req_pool = urllib3.PoolManager()

    def __init__(self, import_name, properties: dict, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False,
                 root_path=None):
        '''
        初始化服务器实例
        :param import_name:
        :param properties:
        :param static_url_path:
        :param static_folder:
        :param static_host:
        :param host_matching:
        :param subdomain_matching:
        :param template_folder:
        :param instance_path:
        :param instance_relative_config:
        :param root_path:
        '''
        # 启动微服务注册参数预处理流程
        if type(properties) is type(''):
            # 反射获取配置
            try:
                prop = __import__(properties)
                self.__prop = {
                    'host': getattr(prop, 'host', self.__host),
                    'port': getattr(prop, 'port', self.__port),
                    'service_name': getattr(prop, 'service_name').upper(),
                    'health_interface': getattr(prop, 'health_interface', '/heart'),
                    'prefer_own_ip': getattr(prop, 'prefer_own_ip', False)
                }
            except Exception as e:
                raise Exception('配置文件加载失败,请检查路径,错误信息:(' + str(e) + ')')
        elif isinstance(properties, type(())):
            raise Exception('暂不支持元组类型配置,请选择其他配置')
        elif isinstance(properties, type({})):
            if 'service_name' in properties.keys():
                self.__prop = {
                    'service_name': properties['service_name'].upper(),
                    'health_interface': properties[
                        'health_interface'] if 'health_interface' in properties.keys() else '/heart',
                    'host': properties['host'] if 'host' in properties.keys() else self.__host,
                    'port': properties['port'] if 'port' in properties.keys() and isinstance(properties['port'],
                                                                                             type(1)) else self.__port,
                    'prefer_own_ip': socket.gethostbyname(
                        socket.getfqdn(socket.gethostname())) if 'prefer_own_ip' in properties.keys() and isinstance(
                        properties['prefer_own_ip'], type(True)) else False
                }
            else:
                raise Exception('缺少必要参数(service_name)')
        # 初始化服务器
        Flask.__init__(self, import_name, static_url_path=static_url_path,
                       static_folder=static_folder, template_folder=template_folder,
                       instance_path=instance_path, instance_relative_config=instance_relative_config,
                       root_path=root_path)
        print('实例注册参数::', self.__prop)
        self.__reg_url = (properties['reg_url'] if 'reg_url' in properties.keys() else self.__reg_url) + self.__prop[
            'service_name']
        self.__reg_update_url = re.sub('/reg/service/.*', '/reg/update', self.__reg_url)
        self.regist_myself()

        self.add_url_rule('/heart/as/<service_name>', 'receive_heart', self.receive_heart, methods=['POST'])

    def regist_myself(self):
        """
        向注册中心注册自身服务
        :return:
        """
        while True:
            try:
                # 向注册中心发起注册
                res = self.req_pool.request(method='get', url=self.__reg_url, headers={
                    'prefer_ip': socket.gethostbyname(socket.getfqdn(socket.gethostname())) if self.__prop[
                        'prefer_own_ip'] else self.__host,
                    'service_port': self.__prop['port']
                })
                self.__reg_list_info = eval(res.data.decode('utf8'))
                break
            except Exception as e:
                print(Exception('微服务启动失败!!,错误原因::' + str(e)))
                print('30秒后重新注册')
                time.sleep(30)

    def service_name(self):
        return self.__prop['service_name']

    def port(self):
        return self.__prop['port']

    '''
    运行增强服务器
    '''

    def run(self, host=None, port=None, debug=None, **options):
        # 启动注册中心健康监测
        threading.Thread(target=self.check_reg_center).start()
        # 初始化注册服务实例(根据注册时返回的实例信息)
        Flask.run(self,
                  host=self.__prop['host'],
                  port=self.__prop['port'],
                  )

    '''
    更新微服务集群信息
    '''

    def update_reg_info(self, r):
        print('更新实例注册信息,', str(r), type(r))
        if not isinstance(r, type({})):
            for k in r.keys():
                v = r[k]
                r[k] = eval(v)
        self.__reg_info = r
        # 写入接收心跳标识
        if not self.__reg_heart:
            self.__reg_heart = True

    '''
    获取注册中心服务注册信息
    '''

    def reg_info(self):
        return self.__reg_info if self.__reg_info else self.__reg_list_info

    '''
    同步服务信息
    '''

    def async_reg_info(self):
        # 暂时使用重注册更新服务信息
        res = self.req_pool.request(method='get', url=self.__reg_update_url)
        result = eval(res.data.decode('utf8'))
        self.__reg_info = result
        return result

    def check_reg_center(self):
        if self.__reg_heart:
            # 存在接收心跳标识
            return
        else:
            # 定期检查注册中心
            while True:
                # 五分钟检查一次(默认)
                time.sleep(300)
                try:
                    res = self.req_pool.request(url=re.sub('/reg/service/.*', '/health', self.__reg_url), method='GET')
                    self.regist_myself()
                    print('注册中心存活' if res.status == 200 else '注册中心失活')
                except Exception as e:
                    print('注册中心失活', str(e))

    def receive_heart(self, service_name):
        '''
        接收注册中心心跳接口
        :return: 心跳接收信息
        '''
        # print('收到心跳!!!')
        if reqq.is_json:
            reg_info = reqq.json
        else:
            reg_info = reqq.form.to_dict()
        self.update_reg_info(reg_info)

        # 检查自身注册信息是否正确
        if self.__prop['service_name'] == service_name:
            return jsonify({'event': 200, 'msg': '收到心跳'})
        else:
            # 自身实例注册信息有误
            return jsonify({'event': 404, 'msg': '收到心跳'})

    '''
    微服务调用单元列表初始化(暂时弃用 )
    '''
    # def micro_request_init(self,service,interface=[]):
    #     m_c_l=micro_cell_list()
    #     # 查找服务是否存在
    #     for ser in service:
    #         for inter in interface:
    #             if ser not in self.__reg_info.keys():
    #                 # 不存在已注册服务中提示警告
    #                 print('<警告>服务',ser,'未找到注册实例,接口',inter,'有失效风险')
    #                 m_c_l.append(micro_cell(ser,inter))
    #             else:
    #                 for ser_int in self.__reg_list_info[self.__reg_list_info[ser]]:
    #                     print(ser_int)


class e_dophon():
    '''

    服务器封装类(支持dophon实例)


    请求的发送和封装使用urllib3处理
    简单的一个基于flask服务器的一个实例

    '''

    __reg_url = 'http://localhost:8361/reg/service/'
    __reg_update_url = None
    __reg_info = {}
    __reg_heart = False

    '''
    增强app内部定义连接池(默认10个连接数)
    '''
    req_pool = urllib3.PoolManager()

    def __init__(self):
        self.__dophon_instance = __import__('dophon.boot', fromlist=True)
        self.__dophon_app = getattr(self.__dophon_instance, 'app')
        # 启动微服务注册参数预处理流程
        try:
            properties = getattr(self.__dophon_instance, 'properties')
        except Exception as e:
            raise e

        if hasattr(properties, 'service_name'):
            self.__prop = {
                'service_name': properties.service_name.upper(),
                'health_interface': properties[
                    'health_interface'] if hasattr(properties, 'health_interface') else '/heart',
                'host': properties.host if hasattr(properties, 'host') else self.__host,
                'port': properties.port if hasattr(properties, 'port') and isinstance(properties.port,
                                                                                      type(1)) else self.__port,
                'prefer_own_ip': properties.prefer_ip_str
                if hasattr(properties,'prefer_ip_str') else
                socket.gethostbyname(socket.getfqdn(socket.gethostname()))
                if hasattr(properties,'prefer_own_ip') and isinstance(properties.prefer_own_ip, type(True)) else
                False
            }
        else:
            raise Exception('缺少必要参数(service_name)')

        print('实例注册参数::', self.__prop)
        self.__reg_url = (properties.reg_url if hasattr(properties, 'reg_url') else self.__reg_url) + self.__prop[
            'service_name']
        self.__reg_update_url = re.sub('/reg/service/.*', '/reg/update', self.__reg_url)
        self.regist_myself()

        self.__dophon_app.add_url_rule('/heart/as/<service_name>', 'receive_heart', self.receive_heart, methods=['POST'])

    def regist_myself(self):
        """
        向注册中心注册自身服务
        :return:
        """
        while True:
            try:
                # 向注册中心发起注册
                res = self.req_pool.request(method='get', url=self.__reg_url, headers={
                    'prefer_ip': self.__prop['prefer_own_ip']
                    if self.__prop['prefer_own_ip'] else self.__prop['host'],
                    'service_port': self.__prop['port']
                })
                self.__reg_list_info = eval(res.data.decode('utf8'))
                break
            except Exception as e:
                print(Exception('微服务启动失败!!,错误原因::' + str(e)))
                print('30秒后重新注册')
                time.sleep(30)

    def service_name(self):
        return self.__prop['service_name']

    def port(self):
        return self.__prop['port']

    '''
    运行增强服务器
    '''

    def run(self, host=None, port=None, debug=None, **options):
        # 启动注册中心健康监测
        threading.Thread(target=self.check_reg_center).start()
        # 初始化注册服务实例(根据注册时返回的实例信息)
        self.__dophon_instance.run_app()

    '''
    更新微服务集群信息
    '''

    def update_reg_info(self, r):
        print('更新实例注册信息,', str(r), type(r))
        if not isinstance(r, type({})):
            for k in r.keys():
                v = r[k]
                r[k] = eval(v)
        self.__reg_info = r
        # 写入接收心跳标识
        if not self.__reg_heart:
            self.__reg_heart = True

    '''
    获取注册中心服务注册信息
    '''

    def reg_info(self):
        return self.__reg_info if self.__reg_info else self.__reg_list_info

    '''
    同步服务信息
    '''

    def async_reg_info(self):
        # 暂时使用重注册更新服务信息
        res = self.req_pool.request(method='get', url=self.__reg_update_url)
        result = eval(res.data.decode('utf8'))
        self.__reg_info = result
        return result

    def check_reg_center(self):
        if self.__reg_heart:
            # 存在接收心跳标识
            return
        else:
            # 定期检查注册中心
            while True:
                # 五分钟检查一次(默认)
                time.sleep(300)
                try:
                    res = self.req_pool.request(url=re.sub('/reg/service/.*', '/health', self.__reg_url), method='GET')
                    self.regist_myself()
                    print('注册中心存活' if res.status == 200 else '注册中心失活')
                except Exception as e:
                    print('注册中心失活', str(e))

    def receive_heart(self, service_name):
        '''
        接收注册中心心跳接口
        :return: 心跳接收信息
        '''
        # print('收到心跳!!!')
        if reqq.is_json:
            reg_info = reqq.json
        else:
            reg_info = reqq.form.to_dict()
        self.update_reg_info(reg_info)

        # 检查自身注册信息是否正确
        if self.__prop['service_name'] == service_name:
            return jsonify({'event': 200, 'msg': '收到心跳'})
        else:
            # 自身实例注册信息有误
            return jsonify({'event': 404, 'msg': '收到心跳'})

    '''
    微服务调用单元列表初始化(暂时弃用 )
    '''
    # def micro_request_init(self,service,interface=[]):
    #     m_c_l=micro_cell_list()
    #     # 查找服务是否存在
    #     for ser in service:
    #         for inter in interface:
    #             if ser not in self.__reg_info.keys():
    #                 # 不存在已注册服务中提示警告
    #                 print('<警告>服务',ser,'未找到注册实例,接口',inter,'有失效风险')
    #                 m_c_l.append(micro_cell(ser,inter))
    #             else:
    #                 for ser_int in self.__reg_list_info[self.__reg_list_info[ser]]:
    #                     print(ser_int)


def enhance(import_name, properties: dict, static_url_path=None,
            static_folder='static', template_folder='templates',
            instance_path=None, instance_relative_config=False,
            root_path=None):
    '''
    获取增强服务器实例方法
    :param import_name: 实例代号,通常为__name__
    :param properties: 增强配置对象,类型为json
    :param static_path:
    :param static_url_path:
    :param static_folder:
    :param template_folder:
    :param instance_path:
    :param instance_relative_config:
    :param root_path:
    :return:增强服务器实例(可作为微服务)
    '''
    obj = e_app(import_name, properties, static_url_path=static_url_path,
                static_folder=static_folder, template_folder=template_folder,
                instance_path=instance_path, instance_relative_config=instance_relative_config,
                root_path=root_path)
    return obj

#
#
# '''
# 启动增强实例DEMO
# '''
# a = enhance(import_name=__name__, properties={'111': 'aaa', 'service_name': 'dxh-service','host':'0.0.0.0', 'port': 80,'reg_url':'http://127.0.0.1:8361/reg/service/'})
# b = enhance(import_name=__name__, properties={'111': 'aaa', 'service_name': 'dxh-service','host':'0.0.0.0', 'port': 81,'reg_url':'http://127.0.0.1:8361/reg/service/'})
# # a.micro_request_init(service=['DXH-TEST-ANOTHER','DXH-TEST'],interface=['/test','/test1'])
#
# m_c_list=micro_cell_list(a,properties={
#     'dxh-service':[
#         {
#             '/test':[
#                 '/test1'
#             ]
#         }
#     ]
# })
#
# @a.route('/')
# def enter():
#     result=m_c_list.request('dxh-service',['/test','/test1'])
#     print(result)
#     return jsonify(result)
#
# @b.route('/test/test1')
# def test():
#     return jsonify({'msg':'b服务被调用'})
#
# # resa = micro_cell(a, 'dxh-service', '/test')
#
# threading.Thread(target=a.run).start()
# threading.Thread(target=b.run).start()
#
