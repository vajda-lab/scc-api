# FTplus Configuration Notes

## Setup NFS v3

```
# yum install nfs-utils
```

use this fstab line:
```
## SCC
#scc-fs.bu.edu:/projectnb/ftplus /projectnb/ftplus nfs rw,bg,intr,nfsvers=3,proto=tcp 0 0
## modern version as some of the flags have changed or been deprecated
scc-fs.bu.edu:/projectnb/ftplus /projectnb/ftplus nfs rw,bg,vers=3,tcp 0 0
````
The data has moved on the server. Please change your fstab to use:
```
scc-fs:/gpfs4/projectnb/ftplus
```
```
$ mkdir -p /projectnb/ftplus

[root@ftplus ~]# mount -a
mount.nfs: backgrounding "scc-fs.bu.edu:/projectnb/ftplus"
mount.nfs: mount options: "rw,bg,intr,nfsver=3,proto=tcp"
```

Setup User
------------

add this line to /etc/group:
```
ftplus:*:338213:awake,vajda,drhall.ftplus
```

Setup User key
---------------

On scc1:
```
$ cd /var/sgeCA/sge_qmaster/default/userkeys
$ tar cf /tmp/keys.tar user1 user2 ...
````
Only get keys for the specific users that need to submit jobs.
The root user key is ok to take so root will be able to run qstat,
but he won't be able to submit jobs.

On client host install keys with:

transfer keys.tar file over
```
$ mkdir -p /var/sgeCA/port536/default/userkeys
$ cd /var/sgeCA/port536/default/userkeys
$ tar xf /path/to/keys.tar
```

Setup SGE
------------
Install libssl
```
# yum install openssl-devel.x86_64 openssl.x86_64
```

Both machines have been added to the sge config as submit hosts. You'll want to grab:
```
$ scp scc1:/usr/local/sge/client/sge.tar
```

and install it in /usr/local/sge and set your environment with:
```
$ source /usr/local/sge/settings.[c]sh
```

Test Mounts
-------------

jobs will run from the user's home directory on the execution host

```
[root@ftplus projectnb]# mount -av
/                        : ignored
/boot                    : already mounted
swap                     : ignored
mount.nfs: trying text-based options 'bg,vers=3,tcp,addr=10.48.225.26'
mount.nfs: prog 100003, trying vers=3, prot=6
mount.nfs: portmap query failed: RPC: Timed out
mount.nfs: trying text-based options 'bg,vers=3,tcp,addr=10.48.225.25'
mount.nfs: prog 100003, trying vers=3, prot=6
mount.nfs: portmap query failed: RPC: Timed out
mount.nfs: trying text-based options 'bg,vers=3,tcp,addr=10.48.225.24'
mount.nfs: prog 100003, trying vers=3, prot=6
mount.nfs: portmap query failed: RPC: Timed out
mount.nfs: backgrounding "scc-fs.bu.edu:/projectnb/ftplus"
mount.nfs: mount options: "rw,bg,vers=3,tcp"
/projectnb/ftplus        : successfully mounted
```

```
# nmap -T4 -A -v 10.48.225.25
PORT      STATE  SERVICE        VERSION
79/tcp    closed finger
146/tcp   closed iso-tp0
987/tcp   closed unknown
1272/tcp  closed cspmlockmgr
2040/tcp  closed lam
3007/tcp  closed lotusmtap
4004/tcp  closed pxc-roid
7070/tcp  closed realserver
8042/tcp  closed fs-agent
16993/tcp closed amt-soap-https
49176/tcp closed unknown
```

Test SGE
------------
```
[root@ftplus userkeys]# qsub -b y printenv
```

Test libssl install
------------------------
There's a symlink issue with libssl, that Mike Dugan says may need the dev lib installed.

```
[root@ftplus userkeys]# ldconfig -p|grep ssl
        libssl3.so (libc6,x86-64) => /lib64/libssl3.so
        libssl.so.10 (libc6,x86-64) => /lib64/libssl.so.10
        libevent_openssl-2.0.so.5 (libc6,x86-64) => /lib64/libevent_openssl-2.0.so.5


Important: symlink the name libssl.so
[root@ftplus lib64]# ln -s libssl.so.1.0.2k libssl.so

[root@ftplus lib64]# ls -lahF | grep ssl
lrwxrwxrwx.  1 root root   29 Mar  3 18:19 libevent_openssl-2.0.so.5 -> libevent_openssl-2.0.so.5.1.9*
-rwxr-xr-x.  1 root root  24K Jun 13  2014 libevent_openssl-2.0.so.5.1.9*
-rwxr-xr-x.  1 root root 362K Dec 10 15:48 libssl3.so*
lrwxrwxrwx.  1 root root   16 Mar 23 11:32 libssl.so -> libssl.so.1.0.2k*
lrwxrwxrwx.  1 root root   16 Jan 23 07:36 libssl.so.10 -> libssl.so.1.0.2k*
-rwxr-xr-x.  1 root root 460K Aug  8  2019 libssl.so.1.0.2k*
-rw-r--r--.  1 root root   65 Aug  8  2019 .libssl.so.1.0.2k.hmac
lrwxrwxrwx.  1 root root   22 Jan 23 07:36 .libssl.so.10.hmac -> .libssl.so.1.0.2k.hmac
```

Things to Look at
-------------------
FTmap:
server/public_html/param/env/appvars.php.tmplt

