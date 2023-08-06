from copy import deepcopy
import fanstore
import logging
from mpi4py import MPI
import numpy as np
import os
import queue
from stat import S_IFDIR, S_IFLNK, S_IFREG, S_ISDIR, S_ISREG
import threading
from time import time
import hashlib

buffersize=65536
#buffersize=32758

class Server(threading.Thread):
    def __init__(self, workerid, comm, mqueue, fs, misc, tree, logging):
        threading.Thread.__init__(self)
        self.id = workerid
        self.comm = comm
        self.rank = comm.Get_rank()
        self.mqueue = mqueue
        self.fs = fs
        self.misc = misc
        self.logging = logging
    
    def run(self):
        self.logging.debug("rank "+str(self.rank)+": entering server thread")
        while True:
            p = self.comm.recv(tag=111)
            self.logging.debug("rank "+str(self.rank)+": server received "+p["mtype"]+" "+p["op"]+" "+str(p["data"].keys())+" from "+str(p["orig"]))
            if p["mtype"] == "req":
                self.mqueue.put(p)
            else:
                self.logging.error("rank "+str(self.rank)+": server "+ p["mtype"]+" not supporoted")

class Worker(threading.Thread):
    def __init__(self, workerid, comm, mqueue, fs, misc, tree, logging):
        threading.Thread.__init__(self)
        self.id = workerid
        self.comm = comm
        self.rank =comm.Get_rank()
        self.mqueue = mqueue
        self.fs = fs
        self.misc = misc
        self.tree = tree
        self.logging = logging
        self.rdlock = threading.Lock()

    def run(self):
        self.logging.debug("rank "+str(self.rank)+": entering worker thread")
        while True:
            p = self.mqueue.get(True, None)
            self.process(p)

            #self.rdlock.acquire()
            #try:
            #    p = self.mqueue.get(True, None)
            #    self.process(p)
            #finally:
            #    self.rdlock.release()
    
    def process(self, p):
        if p["mtype"] == "req":
            self.logging.debug("rank "+str(self.rank)+": worker processing "+str(p["mtype"])+" "+p["op"]+" "+str(p["data"].keys())+" from "+str(p["orig"]))
            if p["op"] == "RELEASE":
                for k in p["data"].keys():
                    self.fs.meta[k] = p["data"][k]
            elif p["op"] == "READ":
                for k in p["data"].keys():
                    try:
                        datapath = os.path.join(self.fs.datapoint, k[1:])
                        fd = open(datapath, 'rb')
                        src = fd.read()
                        fd.close()
                        self.logging.debug(str(time())+" rank "+str(self.rank)+": handing READ "+str(p["data"].keys())+" with tag "+str(p["ret"]))
                        send_count = 0
                        tag = p["ret"]
                        while send_count < len(src):
                            buf = bytearray()
                            if send_count + buffersize > len(src):
                                buf = deepcopy(src[send_count:])
                            else:
                                buf = deepcopy(src[send_count: send_count+buffersize])
                            self.logging.debug("rank "+str(self.rank)+": handling READ "+k+" sending "+str(len(src))+" bytes from "+str(send_count)+" hash value: "+ str(int(hashlib.md5(buf).hexdigest()[:8], 16)))
                            s = time()
                            self.comm.Send(np.frombuffer(buf, dtype=np.uint8), dest=p["orig"], tag=tag)
                            #self.comm.send(buf, dest=p["orig"], tag=tag)
                            e = time() - s
                            self.logging.debug(str(time())+" rank "+str(self.rank)+": handling READ "+k+" "+str(len(buf))+" bytes in "+str(e)+" secs")
                            tag += 1
                            send_count += buffersize
                        self.logging.debug(str(time())+" rank "+str(self.rank)+": completing READ "+k+" with tag "+str(p["ret"]))
                    except Exception as e:
                        self.logging.error("rank "+str(self.rank)+": handling READ "+k+" error: "+str(e))
            elif p["op"] == "GETATTR":
                tempdict={}
                tag=None
                for k in p["data"].keys():
                    if k in self.fs.meta:
                        tempdict[k] = self.fs.meta[k]
                        tag = self.fs.meta[k]["key"]
                    else:
                        tempdict[k] = None
                        tag = self.misc.hash(k)
                rp = self.misc.packet("ack", p["dtype"], p["op"], tempdict, self.rank, 1)
                self.comm.send(rp, dest=p["orig"], tag=tag)
            elif p["op"] == "MKDIR":
                for k in p["data"].keys():
                    self.fs.meta[k] = p["data"][k]
                for dest in self.tree.getChild():
                    self.logging.debug("rank "+str(self.rank)+": send MKDIR to"+ str(dest))
                    packet = self.misc.packet(p["mtype"], p["dtype"], p["op"], p["data"], self.rank)
                    self.comm.send(packet, dest=dest, tag=111)
            elif p["op"] == "READDIR":
                if self.rank == 0:
                    '''
                    This is a readdir request from rank other than 0
                    '''
                    rdata = {}
                    for path in p["data"].keys():
                        rlist = self.fs.readdir_internal(path)
                        self.logging.debug("rank "+str(self.rank)+": READDIR return "+(str(rlist)))
                        rdata[path] = rlist
                    self.logging.debug("rank "+str(self.rank)+": READDIR return "+str(rdata))
                    rp = self.misc.packet("ack", p["dtype"], p["op"], rdata, self.rank)
                    self.comm.send(rp, dest=p["orig"], tag=self.misc.hash(path))
                else:
                    self.logging.debug("rank "+str(self.rank)+": READDIR entry")
                    tempdict = dict()
                    for k in p["data"].keys():
                        for m in self.fs.meta:
                            if k == os.path.dirname(m) and not S_ISDIR(self.fs.meta[m]['st_mode']):
                                tempdict[m] = None 
                    for dest in self.tree.getChild():
                        self.logging.debug("rank "+str(self.rank)+": send READDIR to"+ str(dest))
                        packet = self.misc.packet(p["mtype"], p["dtype"], p["op"], p["data"], self.rank)
                        self.comm.send(packet, dest=dest, tag=111)
                    self.logging.debug("rank "+str(self.rank)+": READDIR ready to gather")
                    buf=self.comm.gather(tempdict)
            else:
                self.logging.error("rank "+str(self.rank)+": "+p["op"]+" not supported")
        elif p["mtype"] == "ack":
            self.logging.debug("rank "+str(self.rank)+": worker processing"+str(p))



if __name__ == '__main__':
    logging.basicConfig(filename='/dev/shm/fanstore.log', \
        format='%(asctime)s %(levelname)-8s %(message)s', \
        level=logging.INFO, \
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('Started')

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    mqueue = queue.Queue()

    misc = Fanstore.Misc()

    server = Server("server", comm, mqueue)
    server.start()
    logging.debug("rank "+str(rank)+": server: started")
    worker = Worker("worker", comm, mqueue)
    worker.start()
    logging.debug("rank "+str(rank)+": worker: started")


    if rank == 0:
        time.sleep(3)
        logging.debug("rank 0 is about to send a packet")
        data = misc.packet("req", "meta", dict(), rank, -1)
        ret = comm.send(data, dest=1)
        print(ret)


