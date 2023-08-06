from neo.clis.base import Base
from neo.libs import login as login_lib


class Login(Base):
    """
usage: login

Log in to Neo Cloud
"""

    def execute(self):

        return login_lib.do_login()
