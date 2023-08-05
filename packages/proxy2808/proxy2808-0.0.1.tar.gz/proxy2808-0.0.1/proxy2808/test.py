import logging
import sys

from proxy2808 import Client

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(ch)

"""
Note: Get IP for use with Release IP interface
"""

if __name__ == '__main__':
    # write your user name
    username = 'daoxu_test'
    # write your password
    password = '123456huangdaoxu'
    # create a client instance
    cli = Client(username=username, password=password, token_change_on_login=False, enhanced_auth=False)
    # get the number of proxies
    rsp_list = cli.get_proxies(amount=5, expire_seconds=60)
    # you should release proxies when you want to change IPs,you could release one two or more
    cli.release_all()
