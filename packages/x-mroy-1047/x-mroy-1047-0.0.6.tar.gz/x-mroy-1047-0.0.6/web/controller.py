
## this is write by qingluan
# just a inti handler
# and a tempalte offer to coder
import os
import re
import json
import time
import random
import tornado
import tornado.web
import functools
import asyncio
from base64 import b64encode
from tornado.websocket import WebSocketHandler
from qlib.data import dbobj
from qlib.log import L
from qlib.net import to
from seed.mrpackage.config import Host
from seed.mrpackage.services import Bitter
from .vultr import Controll, destroy_one, update_db, create_one
from concurrent.futures.thread import ThreadPoolExecutor


background_task_pocket =  ThreadPoolExecutor(max_workers=10)

def run_background(func, callback, *args, **kwds):
    def _callback(result):
        tloop = tornado.ioloop.IOLoop.instance()
        tloop.add_callback(lambda: callback(result.result()))
    future = background_task_pocket.submit(func, *args, **kwds)
    future.add_done_callback(_callback)


def back_request(url, callback,method='get', headers=None, data=None, proxy=None):
    if headers:
        T = functools.partial(to, headers=headers)
    if data:
        T = functools.partial(T, data=data)
    if method:
        T = functools.partial(T, method=method)
    if proxy:
        T = functools.partial(T, proxy=proxy)
    run_background(T, callback, url)


class GeoMap(dbobj):pass
class Reg(dbobj):pass
class Token(dbobj):pass
class Mark(dbobj):pass

class MyEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    tloop = tornado.ioloop.IOLoop.instance()
    def get_event_loop(self):
        """Get the event loop.

        This may be None or an instance of EventLoop.
        """
        # loop = super().get_event_loop()
        
        # Do something with loop ...
        return MyEventLoopPolicy.tloop



class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.db = self.settings['db']
        self.L = self.settings['L']
        self.shodan = lambda x: None
        if 'shodan' in self.settings:
            self.shodan = self.settings['shodan']
        self.get_ip = self.settings['geo']

    def get_current_user(self):
        return (self.get_cookie('user'),self.get_cookie('passwd'))
    def get_current_secure_user(self):
        return (self.get_cookie('user'),self.get_secure_cookie('passwd'))
    def set_current_seccure_user_cookie(self,user,passwd):
        self.set_cookie('user',user)
        self.set_secure_cookie("passwd",passwd)


    def json_arguments(self, key):
        return json.loads(self.request.body)[key]

class SocketHandler(WebSocketHandler):
    """ Web socket """
    clients = set()
    con = dict()

    @staticmethod
    def send_to_all(msg):
        for con in SocketHandler.clients:
            con.write_message(json.dumps(msg))

    @staticmethod
    def send_to_one(msg, id):
        SocketHandler.con[id(self)].write_message(msg)

    def json_reply(self, msg):
        self.write_message(json.dumps(msg))

    def open(self):
        SocketHandler.clients.add(self)
        SocketHandler.con[id(self)] = self

    def on_close(self):
        SocketHandler.clients.remove(self)

    def on_message(self, msg):
        SocketHandler.send_to_all(msg)





class IndexHandler(BaseHandler):

    def prepare(self):
        super(IndexHandler, self).prepare()
        self.template = "template/index.html"

    def get(self):
        user, passwd = self.get_current_secure_user()
        if not user or not passwd:
            self.redirect("/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.get_argument("some_argument")
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()
        self.write("hello world")
        self.finish()



class MapHandler(BaseHandler):

    def prepare(self):
        super(MapHandler, self).prepare()
        self.template = "template/map.html"

    def get(self):
        user, passwd = self.get_current_secure_user()
        if not user or not passwd:
            self.redirect("/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")
        
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/map")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.get_argument("some_argument")
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()
        self.write("hello world")
        self.finish()



class Get_ipHandler(BaseHandler):

    def prepare(self):
        super(Get_ipHandler, self).prepare()
        self.template = "template/get_ip.html"

    @tornado.web.asynchronous
    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        # self.L.ok('got')


        exmdata = []
        geo_ll = set()
        for d in self.db.query(Host):
            geojsonFeature = {
                "type": "Feature",
                "properties": {
                    "name": "Coors Field",
                    "amenity": "Baseball Stadium",
                    "popupContent": "This is where the Rockies play!"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-104.99404, 39.75621]
                }
            }


            desc = d.host
            ip = d.host
            data_m = {
                'label':'Unknow',
                'host': ip,
                'passwd': d.passwd,
                'createTime': d.getTime(),
                # 'loc':''
            }
            mark = self.db.query_one(Mark, host=ip)
            if mark:
                data_m['label'] = mark.label
            if ip == '0.0.0.0':continue
            geo = self.get_ip(d.host)
            geo_mark = '-'.join(geo)
            while geo_mark in geo_ll:
                geo = [str(float(geo[0]) + random.random()), str(float(geo[1]) + random.random())]
                geo_mark = '-'.join(geo)
            geo_ll.add(geo_mark)
            # data_m['loc'] = geo_mark
            geojsonFeature['properties']['name'] = desc
            geojsonFeature['geometry']['coordinates'] = geo
            geojsonFeature['properties']['msg'] = data_m
            # print(geojsonFeature['geometry']['coordinates'])
            exmdata.append(geojsonFeature)

        # print(exmdata)

        d = json.dumps(exmdata)
        self.write(d)
        self.finish()
        # return self.render(self.template, post_page="/get_ip")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow

        
        post_args = self.json_arguments("data")

        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()
        print("DDD ==>",post_args)
        for d in post_args:
            # geo = ','.join(d['geo'])
            geo = d['geo']
            print(d, geo)
            f = self.db.first('net', ip=d['ip'])
            if not f:
                self.db.insert("net", ['ip','geo','desc'], d['ip'], geo, d['desc'])

        self.write("ok")
        self.finish()



class TestHandler(BaseHandler):

    def prepare(self):
        super(TestHandler, self).prepare()
        self.template = "template/test.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/test")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.json_arguments("data")

        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()
        self.write("hello world")
        self.finish()




class Search_geoHandler(BaseHandler):

    def prepare(self):
        super(Search_geoHandler, self).prepare()
        self.template = "template/search_geo.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/search_geo")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.get_argument("name")
        print(">>",post_args)
        geo = self.db.query_one(GeoMap, name=post_args)
        if geo:
            self.write(geo.data)
        else:
            self.write(json.dumps({"features":[]}))
        self.finish()
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()



class GetStatusHandler(BaseHandler):

    def prepare(self):
        super(GetstatusHandler, self).prepare()
        self.template = "template/getstatus.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/getstatus")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        post_args = self.get_argument("ip")
        print(">>", post_args)
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']

        # redirect or reply some content
        # self.redirect()
        reg = self.db.query_one(Reg, host=post_args['ip'])
        if reg:
            b = Bitter(post_args['ip'])
            res = b.GetStatus()
        else:
            res = {"result":[]}
        self.write(json.dumps(res))
        self.finish()



class RemoteapiHandler(BaseHandler):

    def prepare(self):
        super(RemoteapiHandler, self).prepare()
        self.template = "template/remoteapi.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/remoteapi")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        
        post_args = self.json_arguments("req")
        if post_args['op'] == 'status':
            hosts = [i.host for i in self.db.query(Host)]
            reg_host = [i.host for i in self.db.query(Reg)]
            res = {
                "res":"ok",
                "log":" show information for all host in local db.",
                "data":[ {"host":host, "reg":True} if host in reg_host else {"host": host, "reg": False} for host in hosts]
            }
        elif post_args['op'] == 'reg':
            hosts = [i.host for i in self.db.query(Host)]
            regs = [i.host for i in self.db.query(Reg)]
            unreg = set(hosts) - set(regs)
            errs = {}
            for h in unreg:
                b = Bitter(h)
                try:
                    b.register()
                except Exception as e:
                    print(e)
                    errs[h] = str(e)
            res = {
                "res":"ok",
                "log":"res",
                "data":errs
            }
        elif post_args['op'] == 'clear':
            [self.db.delete(i) for i in self.db.query(Reg)]
            res = {
                'res':'ok',
                'log':'delete all',
                'data':[]
            }
        # redirect or reply some content
        # self.redirect()
        self.write(json.dumps(res))
        self.finish()



class AsyncremoteapiHandler(BaseHandler):
    
    def prepare(self):
        super(AsyncremoteapiHandler, self).prepare()
        self.template = "template/asyncremoteapi.html"

    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        user, passwd = self.get_current_secure_user()
        if not user or not passwd:
            self.redirect("/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")
        
        self.L.ok('got')
        return self.render(self.template, post_page="/asyncremoteapi")


    def back(self, data):
        if 'result' in data['msg']:
            data = json.dumps(data['msg']['result'])
        else:
            data = json.dumps(data['msg'])

        print(data)
        self.write(data)
        self.finish()
        # tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self.write_callback, data))

    def write_callback(self, output):
        self.write(output)
        self.finish()
    
    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow
        tloop = tornado.ioloop.IOLoop.current()
        token = self.db.query_one(Token)
        if token:
            token = token.token
        post_args = self.json_arguments("req")
        L(post_args, color='green')
        if post_args['op'] == 'status':
            h = post_args['ip']
            b = Bitter(h)
            
            b.async_rpc('Netstat', self.back, loop=tloop)

        elif post_args['op'] == 'check':
            h = post_args['ip']
            b = Bitter(h)
            b.async_send("", self.back, op='check', loop=tloop)

        elif post_args['op'] == 'regionlist':
            
            
            d = to("https://api.vultr.com/v1/regions/list", headers={"API-Key": token}).json()
            self.write(json.dumps(list(d.values())))
            self.finish()

        elif post_args['op'] == 'scriptlist':

            d = to("https://api.vultr.com/v1/startupscript/list", headers={"API-Key": token}).json()
            self.write(json.dumps(list(d.keys())))
            self.finish()

        elif post_args['op'] == 'mark':
            ip= post_args['ip']
            label = post_args['label']
            ol = self.db.query_one(Mark, host=ip)
            if ol:
                self.db.delete(ol)
            mark = Mark(host=ip, label=label)
            mark.save(self.db)

        elif post_args['op'] == 'destroy':
            h = post_args['ip']
            
            def after_get_servers(data):
                d = data.json()
                breakone = False
                for id in d:
                    if d[id]['main_ip'] == h:
                        destroy_one(token, id)
                        breakone = True
                        break
                
                Controll(token).do_update('')
                self.write(json.dumps({"id":"destroy"}))
                self.finish()
            back_request("https://api.vultr.com/v1/server/list", after_get_servers, headers={"API-Key": token})

        elif post_args['op'] == 'update':
            
            def after_get_servers(data):
                update_db(data)
                # Controll(api).do_update('')
                self.write(json.dumps({"update":"ok"}))
                self.finish()
            back_request("https://api.vultr.com/v1/server/list", after_get_servers, headers={"API-Key": token})

        elif post_args['op'] == 'settoken':
            api = post_args['token']
            t = Token(token=api)
            t.save(self.db)
            self.write(json.dumps({"msg":"ok"}))
            self.finish()

        elif post_args['op'] == 'create_server':
            # api = post_args['token']
            msg = post_args['msg']
            osn = post_args['os']
            label = post_args['label']
            print(post_args)
            osid = 270
            planid = 201
            if osn=='centos':
                osid = 167
            dcid = msg.split("DCID:").pop().strip()
            print(osid, dcid,planid)
            def after_get_scriptid(data):
                d = data.json()
                create_one(token,**{
                    "DCID":dcid,
                    "VPSPLANID": planid,
                    "OSID": osid,
                    "label": label,
                    "SCRIPTID":list(d.keys())[0]
                })
                self.write(json.dumps(d))
                self.finish()

            back_request("https://api.vultr.com/v1/startupscript/list", after_get_scriptid, 
                method='get',
                headers={"API-Key": token}, 
            )
        elif post_args['op'] == 'getpass':
            # h = post_args['ip']
            hh = self.db.query_one(Host, host=post_args['ip'])
            self.write(json.dumps({
                    'data':{
                        'passwd': hh.passwd,
                        'createTime': hh.getTime(),
                        'host': hh.host,
                    }
                }))
            self.finish()

        elif post_args['op'] == 'base':
            h = post_args['ip']
            b = Bitter(h)
            b.async_send("", self.back, op='base', loop=tloop)

        elif post_args['op'] == 'qr':
            h = post_args['ip']
            n = random.randint(1, 10)
            code = 'ss://' + b64encode('aes-256-cfb:thefoolish{n}@{host}:1300{n}'.format(host=h,n=n).encode('utf8')).decode('utf8')
            self.write(json.dumps({"data": code}))
            self.finish()

        elif post_args['op'] == 'map':
            if_tor = False
            if 'tor' in post_args:
                if_tor = True

            from_ip,to_port = post_args['ip'].split(":")
            target  = to_port + ":" + post_args['target']
            b = Bitter(from_ip)
            if not re.match(r'^(\d{1,3}.){3}(\d{1,3}):\d+$',target):
                self.write(json.dumps({
                    'res':'faild',
                    'log':'target is not incorrect!',
                    'data':[]

                    }))
                self.finish()
            b.async_rpc('PortMap', self.back, target,if_tor=if_tor, loop=tloop)
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()
        # self.write("hello world")
        # self.finish()

class LoginHandler(BaseHandler):
    def prepare(self):
        super(LoginHandler, self).prepare()
        self.template = "template/login.html"
    def get(self):
        return self.render(self.template, post_page="/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")
    
    @tornado.web.asynchronous
    def post(self):
        user = self.get_argument("user")
        passwd = self.get_argument("passwd")
        if user == "wj1dd" and passwd == "!@#!@#":
            self.set_current_seccure_user_cookie(user,passwd)
            self.redirect("/")
        else:
            self.write("Fu*k U !")
            self.finish()

class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")


class CreateHandler(BaseHandler):
    
    def prepare(self):
        super(CreateHandler, self).prepare()
        self.template = "template/create.html"

    def get(self):
        user, passwd = self.get_current_secure_user()
        if not user or not passwd:
            self.redirect("/whatthefuckcanyoubrut3memanwhatthefuckcanyoubrutememan")

        # L is log function , which include ok , info , err , fail, wrn
        self.L.ok('got')
        return self.render(self.template, post_page="/create")

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        post_args = self.get_argument("some_argument")
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write("hello world")
        self.finish()
    