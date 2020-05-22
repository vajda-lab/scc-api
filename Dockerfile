### FTplus Submit Host
#
# A SGE submit host to buitl a DJango Data Gateway on
#

FROM local/c7-systemd
## https://hub.docker.com/_/centos/

MAINTAINER James Goebel <jkgoebel@bu.edu> BU Engineering IT

# Check syntax and needed ports for NFS and RPC
#EXPOSE 539
#EXPOSE 111
#EXPOSE 2049

WORKDIR /root
RUN yum -y install nfs-utils openssl.x86_64 openssl-devel.x86_64

# Mount SSC project share
RUN mkdir -p /projectnb/ftplus
RUN echo "scc-fs.bu.edu:/gpfs4/projectnb/ftplus /projectnb/ftplus nfs rw,bg,vers=3,tcp 0 0" >> /etc/fstab
#RUN mount -a

# Create the user drhall with the SCC Group ID for ftplus 338213
# Eventually we can user fbsubmit INC12895847
RUN groupadd -g 338213 ftplus
RUN useradd -g ftplus -d /projectnb/ftplus -m -s /sbin/nologin drhall

# the following should be redundant
# RUN usermod -aG ftplus drhall


# Setup SGE binaries 
# Note this is different Mike Dugan's sge.tar
# 1) Added /usr/local/sge/sge_root/util 
#    I think the install needed a script but I didn't note which :(
# 2) Added /usr/local/sge/sge_root/utilbin/linux-x64/
# 3) I symlinked /usr/local/sge/sge_root/lib/linux-x64/libssl3.so -> /lib64/libssl3.so
#    The symlink may not be needed after installing openssl-devel.x86_64
#
ADD sge.tar.gz /usr/local

# Setup SCC userkeys
ADD userkeys.tar.gz /var/sgeCA/port536/default

# How best to set the user to drhall?
# su drhall
# ENV USER drhall
RUN source /usr/local/sge/settings.sh

WORKDIR /projectnb/ftplus
#COPY test.sh .
#CMD ["qsub", "test.sh"]
CMD [ "/bin/bash" ]
