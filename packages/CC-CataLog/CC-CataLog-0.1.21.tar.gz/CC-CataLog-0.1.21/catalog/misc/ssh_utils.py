#Typing imports
import typing as typ

#External imports
import subprocess,os

#Internal Imports




class SSHClient(object):
    def __init__(self
                ,hostname : str
                ,username : str
                )->None:
        """
        Object for interacting across ssh terminals

        Parameters
        ----------
        hostname : str
            hostname of the server to be interacted with. (i.e. login.stanford.edu)
        username : str
            username of the current user
        """

        self.hostname = hostname
        self.username = username

        def scp(self):
            return

        def exec_command(self):
            return

        def _check_connection(self):
            return
