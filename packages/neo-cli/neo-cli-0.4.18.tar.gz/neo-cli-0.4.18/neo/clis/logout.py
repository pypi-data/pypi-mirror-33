from neo.clis.base import Base
from neo.libs import login as login_lib


class Logout(Base):
    """
usage: login

Log out from Neo Cloud
	"""

    def execute(self):
        login_lib.do_logout()
