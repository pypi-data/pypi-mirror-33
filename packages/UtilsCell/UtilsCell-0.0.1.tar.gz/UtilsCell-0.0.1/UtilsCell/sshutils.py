#!/usr/bin/env python
# coding=utf-8
"""
This runs a command on a remote host using SSH. At the prompts enter hostname,
user, password and the command.
"""

import pexpect
import getpass, os, traceback


# user: ssh 主机的用户名
# host：ssh 主机的域名
# password：ssh 主机的密码
# command：即将在远端 ssh 主机上运行的命令
def ssh_command(user, host, password, command):
    """
    This runs a command on the remote host. This could also be done with the
    pxssh class, but this demonstrates what that class does at a simpler level.
    This returns a pexpect.spawn object. This handles the case when you try to
    connect to a new host and ssh asks you if you want to accept the public key
    fingerprint and continue connecting.
    """
    ssh_newkey = 'Are you sure you want to continue connecting'
    # 为 ssh 命令生成一个 spawn 类的子程序对象.
    child = pexpect.spawn('ssh -l %s %s %s' % (user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    # 如果登录超时，打印出错信息，并退出.
    if i == 0:  # Timeout
        print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(child.before, child.after)
        return None
    # 如果 ssh 没有 public key，接受它.
    if i == 1:  # SSH does not have the public key. Just accept it.
        child.sendline('yes')
        child.expect('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0:  # Timeout
            print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(child.before, child.after)
        return None
    # 输入密码.
    child.sendline(password)
    return child


def main():
    host = '10.30.2.205'
    user = 'spark'
    password = 'python'
    command = 'ps -ef|grep sparkdemo_uuid'
    # # 获得用户指定 ssh 主机域名.
    # host = input('Hostname: ')
    # # 获得用户指定 ssh 主机用户名.
    # user = input('User: ')
    # # 获得用户指定 ssh 主机密码.
    # password = getpass.getpass()
    # # 获得用户指定 ssh 主机上即将运行的命令.
    # command = input('Enter the command: ')
    child = ssh_command(user, host, password, command)
    # 匹配 pexpect.EOF
    child.expect(pexpect.EOF)
    # 输出命令结果.
    result = [i for i in child.before.decode('utf-8').split('\n') if i.strip()]
    line = 0
    for i in result:
        print(line, ':', i)
        line += 1


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        os._exit(1)
