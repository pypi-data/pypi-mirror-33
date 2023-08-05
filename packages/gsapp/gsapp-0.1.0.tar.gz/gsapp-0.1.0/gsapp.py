#Arraycoding:utf-8
from __future__ import unicode_literals
from logging.handlers import RotatingFileHandler
import sys
import logging
import getopt
import tornado.ioloop
import tornado.web
import tornado.gen
import signal
import json
import pymsgq
import os
import fcntl

logging_level_name_map = dict(DEBUG=logging.DEBUG, INFO=logging.INFO, WARNNING=logging.WARN, ERROR=logging.ERROR, FATAL=logging.CRITICAL)

class AppCtx(object):
    logic = None
g_AppCtx = AppCtx()
RUN_BATCH_NUM = 20
RUN_BUSY_SLEEP = 0.002
RUN_IDLE_SLEEP = 0.005
#################################################

class SysVMsgq(object):
    mq_sender = None
    mq_recver = None
    def __init__(self, path, max_buff_sz):
        self.mq_recver = pymsgq.Msgq(path, max_msg_buff_sz=max_buff_sz, create=True, passive=True)
        self.mq_sender = pymsgq.Msgq(path, max_msg_buff_sz=max_buff_sz, create=True, passive=False)

    def send(self, dst, buff):
        return self.mq_sender.send(buff, dst)
        
    def recv(self, mtype=0, block=False):
        return self.mq_recver.recv(mtype, block and 0 or pymsgq.IPC_NOWAIT)



class AppLogic(object):
    name = None  
    config = None
    msg_encode = None
    msg_decode = None
    gsrpc = None
    web_routers = []
    stop = False
    inst = 0
    daemon = False
    pidfile = None
    def set_stop(self):
        self.stop = True

    def getopts(self):
        return '',[]

    def init(self):
        print('app logic init hook')

    def set_name(self, name):
        self.name = name
    
    def set_pidfile(self, pidfile):
        self.pidfile = pidfile

    def set_daemon(self):
        self.daemon=True
    
    def get_name(self):
        return self.name

    def set_inst(self, inst):
        self.inst = inst

    def on_cmdopt(self, name, val):
        return 0

    def set_config(self, conf):
        self.config = conf

    def get_config(self):
        return self.config

    def run(self):
        return False

    def set_gsrpc(self, rpc):
        self.gsrpc = rpc
        
    def get_gsrpc(self):
        return self.gsrpc


    def listen_url(self, path, handler):
        self.web_routers.append((path, handler))

    def get_all_urls(self):
        return self.web_routers



def dict2obj(do):
    class _obj(object):
        def __init__(self, do):
            self.__dict__ = do
    return _obj(do)

def signal_stop(sig, info):
    logging.info("signal:%d stoped", sig)
    global g_AppCtx
    g_AppCtx.logic.set_stop()
    tornado.ioloop.IOLoop.current().stop()


def _init_gsapp_logic(logic):
   # signal.signal(signal.SIGQUIT, signal_stop)
   # signal.signal(signal.SIGTERM, signal_stop)
    signal.signal(signal.SIGINT, signal_stop)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

    logfmt = '%(asctime)s.%(msecs)03d|%(process)d|%(filename)s:%(lineno)d|%(levelname)s|%(message)s'
    formatter = logging.Formatter(logfmt,datefmt='%Y-%m-%dT%H:%M:%S')
    log_file_handler = RotatingFileHandler(filename=logic.config.log['filename'], maxBytes=logic.config.log['max_size'], backupCount=logic.config.log['max_roll'])
    log_file_handler.setFormatter(formatter)    
    logging.basicConfig(level=logging_level_name_map[logic.config.log['level']])
    log = logging.getLogger()
    log.addHandler(log_file_handler)


@tornado.gen.coroutine
def gsapp_check_and_dispatch_msgq_loop(logic):
    run_proc_num = 0
    gsrpc = logic.get_gsrpc()
    mq = gsrpc.get_mq()
    while not logic.stop:
        mtype,mbuff = mq.recv()
        if mtype == 0:
            #no msg sleep while :2ms
            run_proc_num = 0
            yield tornado.gen.sleep(RUN_IDLE_SLEEP)
        else:
            run_proc_num = run_proc_num + 1
            ############################
            try:
                gsrpc.feed(mtype, mbuff)
            except Exception,e:
                logging.exception("feed msg error from:%d !", mtype)
                continue
            #every 
            if run_proc_num > RUN_BATCH_NUM:
                yield tornado.gen.sleep(RUN_BUSY_SLEEP) 

@tornado.gen.coroutine
def gsapp_run_loop(logic):
    run_proc_num = 0
    while not logic.stop:
        if not logic.run():
            run_proc_num = 0
            yield tornado.gen.sleep(RUN_IDLE_SLEEP)
        else:
            run_proc_num = run_proc_num + 1
            if run_proc_num >= RUN_BATCH_NUM:
                yield tornado.gen.sleep(RUN_BUSY_SLEEP)



class GSRpc(object):
    service = {}
    listener = {}
    future = {}
    callback = {}
    txnid = 0
    proto = None
    mq = None
    encode = None
    decode = None
    def __init__(self, proto, mq, encode, decode):
        self.proto = proto 
        self.mq = mq
        self.encode = encode
        self.decode = decode

    def get_proto(self, name):
        return __import__(name)

    def get_mq(self):
        return self.mq

    def listen(self, cmd, service):
        if cmd % 2 == 0:
            self.listener[cmd] = service
        else:
            self.service[cmd] = service
    
    def notify(self, toid, cmd, ret, res):
        timenow = int(time.time())
        msg = self.rpc_msg_type()
        msg.head.cmd = cmd
        msg.head.ret = ret
        msg.head.txnid = 0
        msg.head.flags = 0
        msg.head.dst_id = toid
        body_name = self.cmd_body_name(cmd)
        setattr(msg, body_name, {'res':res})
        self.send_msg(toid, msg)

    def feed(self, fromid, buff):
        msg = self.decode(buff)
        body_name = self.cmd_body_name(msg.head.cmd)
        if msg.head.cmd in self.service:
            #if need reply 
            need_reply = False
            if msg.head.flags&1 == 1:
                need_reply = True
            ret = -1
            body  = getattr(msg, body_name, {'req':None})
            try:
                ret,rsp = self.service[msg.head.cmd](getattr(body,'req',None))
            except Exception,e:
                logging.exception(e)
                ret =  -1
                rsp = None
            if need_reply:
                rspmsg = msg
                rspmsg.head.cmd = msg.head.cmd + 1
                rspmsg.head.ret = ret
                if rsp is not None:
                    setattr(rspmsg, self.cmd_body_name(msg.head.cmd), {'res' : rsp})
                self.send_msg(fromid, rspmsg) 
        elif msg.head.cmd % 2 == 0 :
            rsp_msg = None
            body  = getattr(msg, body_name, {'res':None})
            res = getattr(body, 'res', None)
            if msg.head.txnid > 0:
                if msg.head.txnid in self.callback:
                    self.callback[msg.head.txnid](fromid, msg.head.ret, res)
                    del self.callback[msg.head.txnid]
            if  msg.head.cmd in self.listener:
                self.listener[msg.head.cmd](fromid, msg.head.ret, res)


    def send_msg(self, toid, msg):
        return self.mq.send(toid, self.encode(msg))

    def cmd_body_name(self, cmd):
        return self.proto.SSMsgCmd.Name(cmd).lower()[7:-4]

    def push(self, toid, cmd, req):
        timenow = int(time.time())
        msg = self.rpc_msg_type()
        msg.head.cmd = cmd
        msg.head.txnid = 0 
        msg.head.flags = 2
        msg.head.req_time = timenow
        msg.head.req_expired_time = timenow+10 
        msg.head.dst_id = toid
        body_name = self.cmd_body_name(cmd)
        setattr(msg, body_name, {'req':req})
        return self.send_msg(toid, msg)

    def call(self, toid, cmd, req, cb):
        timenow = int(time.time())
        self.txnid = self.txnid + 1
        msg = self.rpc_msg_type()
        msg.head.cmd = cmd
        msg.head.txnid = self.txnid
        msg.head.flags = 1
        msg.head.req_time = timenow
        msg.head.req_expired_time = timenow+10 
        msg.head.dst_id = toid
        body_name = self.cmd_body_name(cmd)
        setattr(msg, body_name, {'req':req})
        ret = self.send_msg(toid, msg)
        if ret == 0:
            self.callback[self.txnid] = cb
        else:
            raise Exception("send mq error")
        return ret


def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'): 
    try:   
        pid = os.fork()   
        if pid > 0:  
            sys.exit(0)   #父进程退出  
    except OSError, e:   
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )  
        sys.exit(1)  
  
    os.chdir("/")   
    os.umask(0)  
    os.setsid() 
  
    try:   
        pid = os.fork()   
        if pid > 0:  
            sys.exit(0)   #第二个父进程退出  
    except OSError, e:   
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )  
        sys.exit(1)  
  
    for f in sys.stdout, sys.stderr: f.flush() 
    si = open(stdin, 'r')  
    so = open(stdout, 'a+')  
    se = open(stderr, 'a+', 0)  
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())  
    os.dup2(se.fileno(), sys.stderr.fileno())


class AppRunner(object):
    def __init__(self, AppLogicImpl):
        self.logic = AppLogicImpl()
        global g_AppCtx
        g_AppCtx.logic = self.logic
        
    def usage(self):
        print('Usage:%s --config=<python config path> [options]' % sys.argv[0])
        sys.exit(-1)

    def start(self):
        shorts,longs = self.logic.getopts()
        try:
            options,args = getopt.getopt(sys.argv[1:],"hC:D"+shorts,["help","config=","name=","inst=","daemon","pidfile="]+longs)
        except getopt.GetoptError as err:
            print(str(err))
            self.usage()
        ######################################
        config_path = None
        for name,val in options:
            if name in ('-h','--help'):
                self.usage()
            elif name in ('-C','--config'):
                config_path = val
            elif name in ('--name',):
                self.logic.set_name(val)
            elif name in ('--inst',):
                self.logic.set_inst(int(val))
            elif name in ('-D','--daemon',):
                self.logic.set_daemon()
            elif name in ('--pidfile'):
                self.logic.set_pidfile(val)
            else:
                ret = self.logic.on_cmdopt(name, val)
                if ret < 0:
                    print('ERROR:%d options:(%s,%s)' % (ret,name,val))
                    sys.exit(-1)
                elif ret > 0:
                    sys.exit(0)
                else:
                    continue
        if self.logic.daemon:
            daemonize()

        if self.logic.pidfile:
             file = open(self.logic.pidfile, "w+")
             try:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
             except Exception,e:
                logging.error("instance is running already !")
                sys.exit(-1)
             file.write(str(os.getpid()))
        if config_path is None:
            self.usage()

        config = dict2obj(json.loads(open(config_path).read()))
        #####################################
        self.logic.set_config(config)
        _init_gsapp_logic(self.logic)
        ######################################################
        tornado.ioloop.IOLoop.current().call_later(0.5, gsapp_run_loop, self.logic)
        ######################################################
        if config.listen.find("smq://") != -1: 
            smk = config.listen[6:]
            codec_decode = json.loads
            codec_encode = json.dumps
            if getattr(config, 'pb_path', None) is not None:
                sys.path.append(config.pb_path)
                pb_module = __import__('ss_pb2')
                def protobuf_codec_decode(buff):
                    msg = pb_module.SSMsg()
                    msg.ParseFromString(buff)
                    return msg
                def protobuf_codec_encode(msg):
                    return msg.SerializeToString()
                codec_decode = protobuf_codec_decode
                codec_encode = protobuf_codec_encode
            ###################################################################
            mq = SysVMsgq(smk, config.msg_max_size)          
            self.logic.set_gsrpc(GSRpc(pb_module, mq, codec_encode, codec_decode))
            tornado.ioloop.IOLoop.current().call_later(0.5, gsapp_check_and_dispatch_msgq_loop, self.logic)
        else:
            #http
            port = int(config.listen.split(':')[-1])
            routers=self.logic.get_all_urls()
            app=tornado.web.Application(routers)
            server = HTTPServer(app, xheaders=True)
            server.listen(port)
        ############################################
        self.logic.init()
        tornado.ioloop.IOLoop.current().start()




if __name__ == '__main__':
    sys.path.append('../proto')
    import ss_pb2 as ss
    def async_proxy_heart_beat(req):
        logging.debug("on heart beat req:%s", str(req))
        return 0, None 

    class DemoLogic(AppLogic):
        def init(self):
            self.gsrpc.listen(ss.SS_CMD_ASYNC_PROXY_HEART_BEAT_REQ, async_proxy_heart_beat)

    AppRunner(DemoLogic).start()

