FROM alpine
MAINTAINER ALAN	ALAN
RUN echo "http://dl-3.alpinelinux.org/alpine/edge/main/" >> /etc/apk/repositories
RUN echo "http://dl-3.alpinelinux.org/alpine/edge/testing/" >> /etc/apk/repositories
RUN apk update
#RUN apk -U upgrade
RUN apk --update add iptables
RUN apk --update add iproute2
RUN apk --update add bash
RUN apk --update add bird
RUN apk --update add bird6
RUN apk --update add radvd

RUN echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.all.forwarding = 1" >> /etc/sysctl.conf

ADD bin /usr/bin/
ADD etc /etc/
RUN chmod ugo+x /usr/bin/*

CMD ["/usr/bin/tail", "-f", "/dev/null"]

