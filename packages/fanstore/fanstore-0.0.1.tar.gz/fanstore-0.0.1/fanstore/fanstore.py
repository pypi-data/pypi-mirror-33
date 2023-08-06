#!/usr/bin/env python3

from collections import defaultdict
from errno import ENOENT
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
from mpi4py import MPI
from stat import S_IFDIR, S_IFLNK, S_IFREG, S_ISDIR, S_ISREG
from sys import argv, exit
from time import time, sleep

import comm as com

import datetime
import hashlib
import logging
import numpy as np
import os
import pickle
import queue
import select
import shutil
import socket
import struct
import sys
import tarfile
import threading
import topology
import zlib

max_int = 2 ** (struct.Struct('i').size * 8 - 1) - 1
buffersize = 65536
#buffersize = 32758

if not hasattr(__builtins__, 'bytes'):
    bytes = str

class Fanstore(LoggingMixIn, Operations):
    def __init__(self, datapoint):
        '''
        Fanstore data is organized as following:
        self.meta stores persistent metadata
        self.data stores path persistent file data
        '''
        self.rdlock = threading.Lock()
        self.readlock = threading.Lock()
        self.meta = {}
        self.data = {}
        self.rmeta = {}
        self.rcache = defaultdict(bytes)
        self.wcache = defaultdict(bytes)
        self.readdircache = {}
        self.counttable = {}
        self.fd = 0
        self.datapoint = datapoint
        
        #initializing the root directory
        now = time()
        self.meta['/'] = dict(st_mode=(S_IFDIR | 0o755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2, location=[], key=None)

    '''
    below are POSIX interface
    '''
    def chmod(self, path, mode):
        global rank
        logging.debug("rank "+str(rank)+": CHMOD: "+path+", "+str(mode))
        if path in self.meta: 
            self.meta[path]['st_mode'] &= 0o770000 
            self.meta[path]['st_mode'] |= mode
        else:
            logging.error("rank "+str(rank)+": CHMOD: "+path+" does not exist")

    def chown(self, path, uid, gid):
        global rank
        logging.debug("rank "+str(rank)+": CHOWN: "+path+", "+str(uid)+", "+str(gid))

    def create(self, path, mode):
        global rank

        logging.debug("rank "+str(rank)+": CREATE: "+path+", "+str(mode)+" datapoint: "+self.datapoint)

        self.meta[path] =  dict(st_mode=(S_IFREG | mode), st_nlink=1,
                                     st_size=0, st_ctime=time(), st_mtime=time(), 
                                     st_atime=time(), location=rank, key=misc.hash(path))
        datapath=os.path.join(datapoint, path[1:])
        logging.debug("rank "+str(rank)+": CREATE: datapath "+datapath)
        dirpath=os.path.dirname(datapath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        self.data[path]=datapath
        self.wcache[path]=bytearray()
        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        global aqueue
        global misc
        global rank
        global size

        logging.debug("rank "+str(rank)+": GETATTR: "+path)
        if path in self.meta:
            logging.debug("rank "+str(rank)+": GETATTR: "+"metadata of "+path+" is self.meta ")
            return self.meta[path]
        elif path in self.rmeta:
            logging.debug("rank "+str(rank)+": GETATTR: "+"metadata of "+path+" is self.rmeta ")
            return self.rmeta[path]
        elif misc.findpeer(path) != rank:
            dest = misc.findpeer(path)
            logging.debug("rank "+str(rank)+": GETATTR: metadta of "+path+" is at "+str(dest))
            
            packet = misc.packet("req", "meta", "GETATTR", {path: None}, rank, 0)
            comm.send(packet, dest=dest, tag=111)
            rp = comm.recv(source=dest, tag=misc.hash(path))
            logging.debug("rank "+str(rank)+": GETATTR: recv ack of "+str(list(rp["data"].items()))+" while expecting "+path)

            try:
                if not rp["data"][path]:
                    logging.error("rank "+str(rank)+": GETATTR: "+path+" does not exist on "+str(dest)+". There is something wrong")
                    raise FuseOSError(ENOENT)
            except KeyError:
                logging.error("rank "+str(rank)+": GETATTR: recv ack of "+str(list(rp["data"].items()))+" while expecting "+path)

            #else:
            self.rmeta[path] = rp["data"][path]
            return self.rmeta[path]
        else:
            logging.error("rank "+str(rank)+": GETATTR: "+path+" does not exist")
            raise FuseOSError(ENOENT)

    def getxattr(self, path, name, position=0):
        global aqueue
        global misc
        global rank
        logging.debug("rank "+str(rank)+": GETXATTR: "+path+", "+name)
        #if empty return b''
        try:
            if path in self.meta:
                return self.meta[path][name]
            elif path in self.rmeta:
                return self.rmeta[path][name]
            elif misc.findpeer(path) != rank:
                dest = misc.findpeer(path)
                logging.debug("rank "+str(rank)+": GETXATTR: metadta of "+path+" is at "+str(dest))
                packet = misc.packet("req", "meta", "GETATTR", {path: None}, rank, 0)
                comm.send(packet, dest=dest, tag=111)
                rp = comm.recv(source=dest, tag=misc.hash(path))
                #self.meta[path] = rp["data"][path]
                #if not self.meta[path]
                if not rp["data"][path]:
                    logging.error("rank "+str(rank)+": GETXATTR: "+path+" does not exist")
                    return b''
                else:
                    #return self.meta[path][name]
                    attrs = rp["data"][path].get('attrs', {})
                    return attrs[name]

        except KeyError:
            logging.error("rank "+str(rank)+": GETXATTR: "+path+" "+name+" does not exist")
            return b''

    def listxattr(self, path):
        global rank
        logging.debug("rank "+str(rank)+": LISTXATTR "+path)
        if path in self.meta[path]:
            return self.meta[path].keys()
        elif path in self.rmeta[path]:
            return self.rmeta[path].keys()
        else:
            logging.error("rank "+str(rank)+": LISTXATTR: "+path+" does not exist")

    def open(self, path, flags):
        global rank
        self.readlock.acquire()
        try:
            if path in self.meta:
                self.counttable[path] = 1 if path not in self.counttable else self.counttable[path]+1
                logging.debug("rank "+str(rank)+": OPEN: "+path+", counttbale: "+str(self.counttable[path]))
        finally:
            self.readlock.release()
        logging.debug("rank "+str(rank)+": OPEN: "+path+", "+str(flags))
        self.fd += 1
        return self.fd
        
    def fetch(self, path, dest):
        global outqueue
        global rqueue
        global rank
        logging.debug(str(time())+" rank "+str(rank)+": FETCH: "+path+", from "+str(dest)+" hash value: "+str(self.meta[path]["key"])+" tag "+str(self.meta[path]["key"])) 
        
        packet = misc.packet("req", "data", "READ", {path: None}, rank, self.meta[path]["key"])
        s = time()
        comm.send(packet, dest=dest, tag=111)
        e = time() - s
        logging.debug(str(time())+" rank "+str(rank)+": FETCH: "+path+", from "+str(dest)+" message sent in "+ str(e)+ " secs")
        try:
            recv_count = 0
            tag=self.meta[path]["key"]
            while recv_count < self.meta[path]["st_size"]:
                bs = buffersize if recv_count+buffersize < self.meta[path]["st_size"] \
                     else self.meta[path]["st_size"]-recv_count
                rbuf = np.empty(bs, dtype=np.uint8)
                s = time()
                comm.Recv(rbuf, source=dest, tag=tag)
                buf = rbuf.tobytes()
                #req = comm.irecv(buffersize+10, source=dest, tag=tag)
                #buf = req.wait()
                #buf = comm.recv(source=dest, tag=tag)
                e = time() - s
                logging.debug(str(time())+" rank "+str(rank)+": FETCH: "+path+", from "+str(dest)+" received size: "+str(len(buf))+" in "+str(e)+" secs")
                self.rcache[path] += buf
                recv_count += len(buf)
                tag += 1
            logging.debug(str(time())+" rank "+str(rank)+": FETCH: "+path+", from "+str(dest)+" expecting "+ str(self.meta[path]["st_size"])+" bytes, actually received "+str(recv_count)+" bytes")
        except Exception as e:
            logging.error("rank "+str(rank)+": FETCH: "+path+", from "+str(dest)+" erorr "+ str(e))
            if path in self.rcache:
                logging.error(path+" is in rcache")
            else:
                logging.error(path+" is not in rcache, while it should")

    def read(self, path, size, offset, fh):
        global outqueue
        global rqueue
        global rank
        logging.debug("rank "+str(rank)+": READ: "+path+", "+str(size)+", "+str(offset))

        if path in self.rcache:
            return bytes(self.rcache[path][offset:offset + size])
        elif path in self.data:
            fd = open(self.data[path], 'rb')
            self.rcache[path] = fd.read()
            fd.close()
            return bytes(self.rcache[path][offset:offset + size])
        elif path in self.rmeta:
            logging.debug("rank "+str(rank)+": READ: "+path+" is at rmeta "+str(self.rmeta[path]["location"]))
            dest = self.rmeta[path]["location"]
            packet = misc.packet("req", "data", "READ", {path: None}, rank, self.rmeta[path]["key"])
            comm.send(packet, dest=dest, tag=111)
            rp = comm.recv(source=dest, tag=self.rmeta[path]["key"])
            self.rcache[path] = rp["data"][path]
            return bytes(self.rcache[path][offset:offset + size])
        elif path in self.meta:
            logging.debug("rank "+str(rank)+": READ: "+path+" is at self.meta tag:"+str(self.meta[path]["key"]))
            dest = self.meta[path]["location"]

            self.rdlock.acquire()
            try:
                if path not in self.rcache:
                    self.fetch(path, dest)
                    logging.debug("rank "+str(rank)+": READ: "+path+" fetch compeleted from "+str(dest))
                else:
                    logging.debug("rank "+str(rank)+": READ: "+path+" fetch compeleted from local rcacche")
            finally:
                self.rdlock.release()

            return bytes(self.rcache[path][offset:offset + size])
        else:
            logging.error("rank "+str(rank)+": READ: "+path+" does not exist")
        
    def readlink(self, path):
        pass

    def removexattr(self, path, name):
        pass

    def rename(self, old, new):
        pass

    def mkdir(self, path, mode):
        global rank
        global size
        global tree
        logging.debug("rank "+str(rank)+": MKDIR: "+path+", "+str(mode))

        parent = os.path.dirname(path)
        nlink = self.meta[parent]['st_nlink']
        self.meta[path] = dict(st_mode=(S_IFDIR | mode), st_nlink=nlink+1, st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time(), location=[], key=None)
        self.meta[parent]['st_nlink'] += 1

        for dest in tree.getChild():
            if dest != rank:
                logging.debug("rank "+str(rank)+": MKDIR: send packet to "+str(dest))
                packet = misc.packet("req", "meta", "MKDIR", {path: self.meta[path], parent: self.meta[parent]}, rank, 0)
                comm.send(packet, dest=dest, tag=111)
        return 0

    def mkdirs(self, paths, mode):
        global outqueue
        global rank
        global size
        global tree
        logging.debug("rank "+str(rank)+": MKDIRS: "+str(len(paths))+", "+str(mode))

        tempdict = {}
        for path in paths:
            parent = os.path.dirname(path)
            dl = [path]
            while parent != "/" and parent not in self.meta:
                dl.append(parent)
                parent = os.path.dirname(parent)
            for d in reversed(dl):     
                parent = os.path.dirname(d)
                nlink = self.meta[parent]['st_nlink']
                self.meta[d] = dict(st_mode=(S_IFDIR | mode), st_nlink=nlink+1, st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time(), location=[], key=None)
                self.meta[parent]['st_nlink'] += 1
                tempdict[d] = self.meta[d]

        for dest in tree.getChild():
            if dest != rank:
                logging.debug("rank "+str(rank)+": MKDIRS: send packet to "+str(dest))
                packet = misc.packet("req", "meta", "MKDIR", tempdict, rank, 0)
                comm.send(packet, dest=dest, tag=111)
        return 0

    def mkdirs_local(self, paths, mode):
        global rank
        global size
        global tree
        logging.debug("rank "+str(rank)+": MKDIRS_LOCAL: "+str(len(paths))+", "+str(mode))

        for path in paths:
            parent = os.path.dirname(path)
            dl = [path]
            while parent != "/" and parent not in self.meta:
                dl.append(parent)
                parent = os.path.dirname(parent)
            for d in reversed(dl):     
                parent = os.path.dirname(d)
                nlink = self.meta[parent]['st_nlink']
                self.meta[d] = dict(st_mode=(S_IFDIR | mode), st_nlink=nlink+1, st_size=0, st_ctime=time(), st_mtime=time(), st_atime=time(), location=[], key=None)
                self.meta[parent]['st_nlink'] += 1
        return 0

    def readdir_internal(self, path):
        global rank
        global tree
        logging.debug("rank "+str(rank)+": READDIR_INT: "+path)
        buf = []
        if path in self.readdircache:
            logging.debug("rank "+str(rank)+": READDIR_INT:"+ path +" in readdircache")
            return self.readdircache[path]
        if rank != 0:
            try:
                packet = misc.packet("req", "meta", "READDIR", {path: None}, rank, 0)
                logging.debug("rank "+str(rank)+": READDIR_INT:"+ path +" request sent to 0 ")
                comm.send(packet, dest=0, tag=111)
                rp = comm.recv(source=0, tag=misc.hash(path))
                logging.debug("rank "+str(rank)+": READDIR_INT:"+ path +" returned "+str(rp))
            except Error:
                logging.error("rank "+str(rank)+": READDIR_INT:"+ path +" Error")
            finally:
                self.readdircache[path] = rp["data"][path]
                return self.readdircache[path]
        else:
            '''
            Readdir can only be initiated by Rank 0, all other 
            nodes need to talk to 0 for this operation
            '''
            packet = misc.packet("req", "meta", "READDIR", {path: None}, rank, 0)
            tempdict = dict()
            for m in self.meta:
                if path == os.path.dirname(m) and not S_ISDIR(self.meta[m]['st_mode']):
                    tempdict[m] = None 
            for c in tree.getChild():
                logging.debug("rank "+str(rank)+": READDIR_INT: "+ path +" request sent to "+str(c))
                comm.send(packet, dest=c, tag=111)
            logging.debug("rank "+str(rank)+": READDIR_INT: "+ path +" ready to gather")
            buf=comm.gather(tempdict)
            logging.debug("rank "+str(rank)+": READDIR_INT: "+ path +" gathered: "+str(buf))
            
            rlist = ['.', '..']
            for m in self.meta:
                if path == os.path.dirname(m) and S_ISDIR(self.meta[m]['st_mode']) and m != "/":
                    if path == "/":
                        rlist.append(m[len(path):])
                    else:
                        rlist.append(m[len(path)+1:])
            rset = set()
            if buf:
                for d in buf:
                    rset |= set(d.keys())
                rlist.extend([x[len(path)+1:] for x in rset])
            self.readdircache[path] = rlist
            
            logging.debug("rank "+str(rank)+": READDIR_INT: "+ path +" rlist: "+str(rlist))
            return rlist


    def readdir(self, path, fh):
        global rank
        global tree
        logging.debug("rank "+str(rank)+": READDIR:"+path)
        if path not in self.meta:
            logging.error("rank "+str(rank)+": READDIR: "+path+" does not exist")
            return FuseOSError(ENOENT)
        else:
            self.rdlock.acquire()
            rlist = []
            try:
                logging.debug("rank "+str(rank)+": READDIR:"+path+" lock acquired")
                rlist = self.readdir_internal(path)
            finally:
                self.rdlock.release()
                logging.debug("rank "+str(rank)+": READDIR:"+path+" lock released")
                return rlist

    def rmdir(self, path):
        global rank
        logging.debug("rank "+str(rank)+": MKDIR: "+path)
        rlist = []
        for m in list(self.meta.keys()):
            if os.path.dirname(m) == path or m == path:
                self.meta.pop(m)
                if m not in rlist:
                    rlist.append(m)
        for m in list(self.data.keys()):
            if os.path.dirname(m) == path:
                datapath = os.path.join(self.datapoint, path[1:])
                os.remove(datapath)
                self.data.pop(m)
                if m not in rlist:
                    rlist.append(m)
        return rlist

    def setxattr(self, path, name, value, options, position=0):
        pass

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        pass

    def truncate(self, path, length, fh=None):
        pass

    def unlink(self, path):
        pass

    def utimens(self, path, times=None):
        pass

    def write(self, path, data, offset, fh):
        global rank
        logging.debug("rank "+str(rank)+": WRITE: "+path+", length: "+str(len(data))+", offset: "+str(offset))
        #write to the right place
        if path not in self.wcache and path in self.data:
            datapath = os.path.join(self.datapoint, path[1:])
            logging.debug("rank "+str(rank)+": WRITE: "+path+" to "+datapath)
            fd = open(datapath, 'rb')
            self.wcache[path] = bytearray(fd.read())
            fd.close()
        if offset == len(self.wcache[path]):
            self.wcache[path].extend(data)
        else:
            self.wcache[path] = self.wcache[path][:offset]+data
        return len(data)

    def release(self, path, fh):
        global misc
        global rank
        global size

        logging.debug("rank "+str(rank)+": RELEASE: "+path)
        if path in self.rcache:
            self.readlock.acquire()
            try:
                self.counttable[path] -= 1
                logging.debug("rank "+str(rank)+": RELEASE: "+path+" counttable: "+str(self.counttable[path]))
                if self.counttable[path] == 0:
                    self.counttable.pop(path)
                    self.rcache.pop(path)
            finally:
                self.readlock.release()
            #self.rcache.pop(path)
        if path in self.wcache:
            self.meta[path]["st_size"] = len(self.wcache[path])
            datapath = os.path.join(self.datapoint, path[1:])
            fd = open(datapath, 'wb')
            fd.write(self.wcache[path])
            fd.flush()
            fd.close()
            logging.debug("rank "+str(rank)+": RELEASE: write "+str(len(self.wcache[path]))+" bytes to " + datapath)
            
            '''
            send metadata
            '''
            dest = misc.findpeer(path)
            logging.debug("rank "+str(rank)+": RELEASE: send metadata of "+path+" to "+str(dest))
            packet = misc.packet("req", "meta", "RELEASE", {path: self.meta[path]}, rank, 0)
            comm.send(packet, dest=dest, tag=111)
            #logging.debug("rank "+str(rank)+": RELEASE: recv ack for "+rp["op"])
            self.wcache.pop(path)
        return 0

    def loadscatter(self, src):
        global datapoint
        global rank
        global size

        sflist = []
        for i in range(0, size):
            sflist.append([])
        if rank == 0:
            logging.debug("rank "+str(rank)+": LOADSCATTER "+src)
            flist = sorted(os.listdir(src))
            logging.debug("rank "+str(rank)+": LOADSCATTER: ready to scatter "+str(flist))
            for i in range(0, len(flist)):
                sflist[i%size].append(flist[i])
                '''
                temp tryout see if each node holds 25% data eliminates the failure on 16 nodes
                '''
                #sflist[i%size].append(flist[(i+1)%len(flist)])
                #sflist[i%size].append(flist[(i+2)%len(flist)])
                #sflist[i%size].append(flist[(i+3)%len(flist)])
        pflist = comm.scatter(sflist)
        logging.info("rank "+str(rank)+": LOADSCATTER: locally process "+str(pflist))
        
        dirs = set()
        files = []
        '''
        copy tar files from shared to local disk
        '''
        for f in pflist:
            shutil.copyfile(os.path.join(src, f), os.path.join(datapoint, f))
            t = tarfile.open(os.path.join(datapoint, f))
            ol = t.getmembers()
            for o in ol:
                if o.isdir():
                    dirs.add(o.name)
                elif o.isfile():
                    files.append(o.name)
                p = os.path.dirname(o.name)
                while p != "" and  p!= "/" and p not in dirs:
                    dirs.add(p)
                    p = os.path.dirname(p)
            t.extractall(datapoint)
            t.close()
            logging.debug("rank "+str(rank)+": LOADSCATTER: removing tar "+ f)
            os.remove(os.path.join(datapoint, f))
        logging.info("rank "+str(rank)+": LOADSCATTER: creating files: "+ str(len(files)))

        cdirs = comm.gather(list(dirs))
        if rank == 0:
            for l in cdirs:
                dirs |= set(l)
            logging.debug("rank "+str(rank)+": LOADSCATTER: creating dirs: "+ str(len(dirs)))

            ds = ["/"+d for d in dirs]
            self.mkdirs(ds, self.meta['/']['st_mode'])

        '''
        create metadata for files
        '''
        cmeta = {}
        #for i in range(size):
        #    cmeta.append({})
        
        for f in files:
            fstat = os.stat(os.path.join(datapoint, f))
            fp = os.path.join("/", f)
            h = misc.hash(os.path.join("/", f))
            m = dict(st_mode=(S_IFREG | fstat.st_mode), st_nlink=1, st_size=fstat.st_size, \
                     st_ctime=time(), st_mtime=time(), st_atime=time(), location=rank, key=h)
            #modulo = h % size
            cmeta[fp] = m
            self.data[os.path.join("/", f)] = os.path.join(datapoint, f)
        
        #for i in range(len(cmeta)):
        #    logging.debug("rank "+str(rank)+": LOADSCATTER: send metadata  "+str(len(cmeta[i]))+" entries to node "+str(i))

        buf = comm.allgather(cmeta)
        for d in buf:
            self.meta.update(d)
            logging.info("rank "+str(rank)+": LOADSCATTER: update metadata with "+str(len(d))+" entries")

        '''
        build readdircache
        '''
        ds = sorted(["/"+d for d in dirs])
        self.readdircache["/"] = ['.', '..']
        for d in ds:
            self.readdircache[d] = ['.', '..']
            dd = os.path.dirname(d)
            if dd in self.readdircache:
                self.readdircache[dd].append(os.path.basename(d))
        for c in buf:
            for m in c.keys():
                if m != "/":
                    d = os.path.dirname(m)
                    self.readdircache[d].append(os.path.basename(m))
        '''
        temp try for 25% cache
        '''
        #for d in self.readdircache:
        #    self.readdircache[d] = list(set(self.readdircache[d]))
        logging.info("rank "+str(rank)+": LOADSCATTER: build readdircache for: "+ str(len(ds))+" dirs")


    def loadbcast(self, src):
        global datapoint
        global rank
        global size
        bcast_buf_size = 1048576
        logging.info("rank "+str(rank)+": LOADBCAST "+src)
        flist = sorted(os.listdir(src))
        logging.debug("rank "+str(rank)+": LOADBCAST: ready to bcast "+str(flist))
        for f in flist:
            length = None
            st_size = 0
            if rank == 0:
                shutil.copyfile(os.path.join(src, f), os.path.join(datapoint, f))
                fstat = os.stat(os.path.join(datapoint, f))
                st_size = fstat.st_size
                length = comm.bcast(st_size)
            else:
                length = comm.bcast(st_size)
            logging.debug("rank "+str(rank)+": LOADBCAST: file size: "+str(length))
            
            count = 0
            sendbuf = bytearray()
            tpath = os.path.join(datapoint, f)
            if rank == 0:
                fd = open(tpath, 'rb')
                while count < length:
                    remain = length - count
                    bufsize = remain if remain < bcast_buf_size else bcast_buf_size
                    #logging.debug("rank "+str(rank)+": LOADBCAST: offset: "+str(count)+" bufsize: "+str(bufsize))
                    sendbuf=fd.read(bcast_buf_size)
                    recvbuf=comm.bcast(sendbuf)
                    count += bcast_buf_size
                fd.close()
            else:
                tpath = os.path.join(datapoint, f)
                ofd = open(tpath, 'wb')
                while count < length:
                    recvbuf = comm.bcast(sendbuf)
                    ofd.write(recvbuf)
                    ofd.flush()
                    #logging.debug("rank "+str(rank)+": LOADBCAST: offset: "+str(count)+" recvbuf: "+str(len(recvbuf)))
                    count += len(recvbuf)
                ofd.close()
                logging.debug("rank "+str(rank)+": LOADBCAST: received file size: "+str(count))
            
            dirs = set()
            files = []
            t = tarfile.open(tpath)
            ol = t.getmembers()
            for o in ol:
                if o.isdir():
                    dirs.add(o.name)
                elif o.isfile():
                    files.append(o.name)
                    p = os.path.dirname(o.name)
                    dirs.add(p)
            t.extractall(datapoint)
            t.close()
            #logging.debug("rank "+str(rank)+": LOADBCAST: removing tar "+ tpath)
            #os.remove(tpath)
            
            logging.info("rank "+str(rank)+": LOADBCAST: creating "+ str(len(dirs))+" dirs")
            ds = ["/"+d for d in dirs]
            self.mkdirs_local(ds, self.meta['/']['st_mode'])

            cmeta = {}
            logging.info("rank "+str(rank)+": LOADBCAST: adding files: "+ str(len(files)))
            for f in files:
                fstat = os.stat(os.path.join(datapoint, f))
                fp = os.path.join("/", f)
                h = misc.hash(os.path.join("/", f))
                m = dict(st_mode=(S_IFREG | fstat.st_mode), st_nlink=1, st_size=fstat.st_size, \
                         st_ctime=time(), st_mtime=time(), st_atime=time(), location=rank, key=h)
                cmeta[os.path.join("/", f)] = m
                self.data[os.path.join("/", f)] = os.path.join(datapoint, f)
            self.meta.update(cmeta)

            '''
            build readdircache
            '''
            ds = sorted(["/"+d for d in dirs])
            self.readdircache["/"] = ['.', '..']
            for d in ds:
                self.readdircache[d] = ['.', '..']
                dd = os.path.dirname(d)
                if dd in self.readdircache:
                    self.readdircache[dd].append(os.path.basename(d))
            for m in cmeta.keys():
                if m != "/":
                    d = os.path.dirname(m)
                    self.readdircache[d].append(os.path.basename(m))
            logging.info("rank "+str(rank)+": LOADBCAST: build readdircache for: "+ str(len(ds))+" dirs")

class Misc():
    def __init__(self):
        pass

    def findpeer(self, fname):
        global rank
        global size
        dest = self.hash(fname)%size
        logging.debug("rank "+str(rank)+": MISC.findpeer: dest: "+str(dest))
        return dest

    def hash(self, fname):
        #return zlib.adler32(bytes(fname, 'utf8')) & 0xffffffff
        return int(hashlib.md5(fname.encode('utf-8')).hexdigest()[:8], 16)%max_int

    def packet(self, mtype, dtype, op, data, orig, ret=0):
        '''
        mtype: message type, request or acknowledgement
        dtype: data type, metadat or data
        op:    operation
        data:  dict(), the data request
        orig:  originating rank
        ret:   return value of the request operation
        '''
        return dict(mtype=mtype, dtype=dtype, op=op, data=data, orig=orig, ret=ret)

if __name__ == '__main__':
    #if len(argv) != 2:
    #    print(('usage: %s --mount <mountpoint>' % argv[0]))
    #    exit(1)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint", help="the mount point of Fanstore")
    parser.add_argument("datapoint", help="the local directory to hold the data")
    parser.add_argument("--loadscatter", help="load and scatter the specified directory of tar balls to Fanstore")
    parser.add_argument("--loadbcast", help="load and broadcast the specified tar ball to Fanstore")
    args = parser.parse_args()
    
    logging.basicConfig(filename='/tmp/fuse-fanstore.log', \
        format='%(asctime)s %(levelname)-8s %(message)s', \
        level=logging.INFO, \
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Started')
    #logging.debug("I_MPI_EAGER_THRESHOLD: "+str(os.environ['I_MPI_EAGER_THRESHOLD']))
    #logging.debug("I_MPI_INTRANODE_EAGER_THRESHOLD: "+str(os.environ['I_MPI_INTRANODE_EAGER_THRESHOLD']))

    global comm
    comm = MPI.COMM_WORLD
    
    global rank
    rank = comm.Get_rank()

    global size
    size = comm.Get_size()

    global mqueue
    mqueue = queue.Queue()

    global mountpoint
    mountpoint = args.mountpoint
    logging.info("rank "+str(rank)+": mountpoint: "+mountpoint)

    global datapoint
    datapoint = args.datapoint
    logging.info("rank "+str(rank)+": datapoint: "+datapoint)

    global fanstore
    fanstore=Fanstore(datapoint)

    global misc
    misc=Misc()

    global tree
    tree = topology.Tree(size, rank)
    logging.info("rank "+str(rank)+": children: "+str(tree.getChild())+" parent: "+str(tree.getParent()))
    
    server = com.Server("server", comm, mqueue, fanstore, misc, tree, logging)
    server.start()
    logging.info("rank "+str(rank)+": server: started")

    worker = com.Worker("worker", comm, mqueue, fanstore, misc, tree, logging)
    worker.start()
    logging.info("rank "+str(rank)+": worker: started")

    #worker2 = com.Worker("worker2", comm, mqueue, fanstore, misc, tree, logging)
    #worker2.start()
    #logging.debug("rank "+str(rank)+": worker2: started")

    if args.loadscatter:
        fanstore.loadscatter(args.loadscatter)
    
    if args.loadbcast:
        fanstore.loadbcast(args.loadbcast)

    fuse = FUSE(fanstore, mountpoint, foreground=True, big_writes=True, direct_io=True)
