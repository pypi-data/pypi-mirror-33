import os
from .base import Base
from neo.libs import utils
from neo.libs import orchestration as orch
from tabulate import tabulate


class Update(Base):
    """
usage:
        update
        update [-f PATH]

Update stack metadata

Options:
-h --help                           Print usage
-f PATH --file=PATH                 Set neo manifest file

Run 'neo update COMMAND --help' for more information on a command.
"""

    def execute(self):
        headers = ["ID", "Name", "Status", "Created", "Updated"]

        set_file = self.args["--file"]
        default_file = orch.check_manifest_file()

        if set_file:
            if os.path.exists(set_file):
                default_file = set_file
            else:
                utils.log_err("{} file is not exists!".format(set_file))
                exit()

        if not default_file:
            utils.log_err("Can't find neo.yml manifest file!")
            exit()

        deploy_init = orch.initialize(default_file)
        try:
            orch.do_update(deploy_init)
        except:
            utils.log_err("Update Stack failed...")
            exit()

        projects = utils.get_project(default_file)

        project_list = list()
        for project in projects:
            proj = orch.get_stack(project)
            if proj:
                project_list.append(proj)

        if len(project_list) > 0:
            print(tabulate(project_list, headers=headers, tablefmt="grid"))
