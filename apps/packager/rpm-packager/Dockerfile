FROM fedora:latest

RUN dnf -y groupinstall 'Development Tools' && \
    dnf -y install rpm-build rpmdevtools

WORKDIR /workspace

CMD ["/bin/bash"]
