########################
Description
########################

This tool build QAT packages on different OS's and check build results.
It starts by downloading a QAT package from artifactory to server,
then turn on VM's with different OS's and send pacakge to all.
Next install pacakge with checking results and parsing it
into .html file. This tool work on local server jenkins
and send notification after periodicaly builds
with .html file results. It constist of main two python scripts
that can be run independently: multi_update_os.py and package_build_validation.py

########################
How to add more OS'es / different kernels.
########################

1. Copy desired OS img to server (eg. /lib/libvirt/images/bigHDD )
2. Create new VM in QEMU/KVM manager. You can either:
    - import existing .qcow2 system image
    - install OS from .img or other image-type file
    - cloning existing VM make problems with IP so please avoid this method
If you want to have Intel Next Kernel on it add _INK at the end of VM name. Only OS's with dnf installed can have Intel Next Kernel installed.
3. Check in VM IP is provided. If not click "refresh" in VM network options near IP.
4. Make sure the VM have all cpm required libaries

    * Useful commands for VM without Intel Next Kernel:

        `dnf install -y kernel-core kernel-modules kernel-devel kernel-headers gcc yasm zlib-devel systemd-devel readline-devel openssl-devel gcc-c++ boost-devel elfutils-libelf-devel make libnl3 libnl3-devel`

        `apt install zlib1g-dev yasm libboost-all-dev libsystemd-dev libreadline6-dev libssl-dev build-essential libudev-dev libnl-3-dev libnl-genl-3-dev linux-generic pkg-config`
    * For Intel Next Kernel:

        `dnf install -y flex bison gcc yasm zlib-devel systemd-devel readline-devel openssl-devel gcc-c++ boost-devel elfutils-libelf-devel make libnl3-devel`
    
    * Additionally for Centos8.4/RHEL8.4:

        `wget http://mirror.centos.org/centos/8/PowerTools/x86_64/os/Packages/yasm-1.3.0-7.el8.x86_64.rpm`
        
        `yum install ./yasm-1.3.0-7.el8.x86_64.rpm`

5. Enable root acount and SSH root login on VM if not enabled by default.
6. Copy ssh keys from server to VM using VM ip. `ssh-copy-id root@virtual_network_interface_ip where virtual_network_interface_ip can be found in VM info.
7. Add aditional position in VM_OS_list.json with:
    - name - KVM/Virsh name of VM.
    - kernel - default kernel, can leave empty it will auto-fill.
    - IP - IP of VM virtual network interface , can be found in QEMU/KVM manager settings.
    - OS - how it should be displayed in HTML raport
    - UPDATE_CMD - command used to update kernel e.g. 'dnf upgrade', ' apt-get -y update && apt-get -y dist-upgrade' .Leave empty to do not perform updates.


########################
Install requirments
########################
Note 1:
On backbone3 Ubuntu20.04 were puting machine to sleep (and make SSH connection unavailable) due to no physical device interaction. To prevent this i used mask command:
    
    `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target`

To revert the process use:
    
    `sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.targ`

Neded packages:
    - Python 3.8+
    - sendmail (or other mail server configured)
    - Jenkins with plugins:
        - SSH Agent Plugin
        - SSH Build Agents plugin
        - Pipeline
        - Copy Artifact Plugin
        - Email Extension Plugin

https://plugins.jenkins.io/ws-cleanup
