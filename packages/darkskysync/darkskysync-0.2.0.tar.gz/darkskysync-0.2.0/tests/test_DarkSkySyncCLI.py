'''
Created on Sep 23, 2013

@author: J. Akeret
'''

from darkskysync.DarkSkySyncCLI import DarkSkySyncCLI
from mock import MagicMock


class TestDarkSkySyncCLI(object):

    args = {'--all': False,
            '--config': None,
            '--dry_run': False,
            '--force': True,
            '--help': False,
            '--recursive': False,
            '--template': None,
            '--verbose': True,
            '--version': False,
            '<name>': None,
            '<path>': None,
            'avail': False,
            'list': False,
            'load': False,
            'remove': False}

    def setup(self):
        self.cli = DarkSkySyncCLI()

    def test_dispatch_avail(self):
        dam = MagicMock()
        dam.avail.return_value = []

        args = TestDarkSkySyncCLI.args.copy()

        args["avail"] = True

        self.cli.dispatch(dam, args)

        dam.avail.assert_called_with(path=None)

    def test_dispatch_list(self):
        dam = MagicMock()
        dam.list.return_value = []

        args = TestDarkSkySyncCLI.args.copy()
        args["list"] = True
        args["--recursive"] = False

        self.cli.dispatch(dam, args)
        dam.list.assert_called_with(path=None, recursive=False)

        args["--recursive"] = True
        self.cli.dispatch(dam, args)
        dam.list.assert_called_with(path=None, recursive=True)

        args["<path>"] = ["path1", "path2"]
        args["--recursive"] = False

        self.cli.dispatch(dam, args)
        dam.list.assert_called_with(path=["path1", "path2"], recursive=False)

        args["--recursive"] = True
        self.cli.dispatch(dam, args)
        dam.list.assert_called_with(path=["path1", "path2"], recursive=True)

    def test_dispatch_load(self):
        dam = MagicMock()
        dam.load.return_value = []

        args = TestDarkSkySyncCLI.args.copy()
        args["load"] = True
        args["<name>"] = None
        args["--dry_run"] = False
        args["--force"] = False

        self.cli.dispatch(dam, args)
        dam.load.assert_called_with(None, False, False)

        args["--dry_run"] = True
        args["--force"] = True
        self.cli.dispatch(dam, args)
        dam.load.assert_called_with(None, True, True)

        args["<name>"] = ["name1", "name2"]
        args["--dry_run"] = False
        args["--force"] = False

        self.cli.dispatch(dam, args)
        dam.load.assert_called_with(["name1", "name2"], False, False)

        args["--dry_run"] = True
        args["--force"] = True
        self.cli.dispatch(dam, args)
        dam.load.assert_called_with(["name1", "name2"], True, True)

    def test_dispatch_remove(self):
        dam = MagicMock()
        dam.remove.return_value = None

        args = TestDarkSkySyncCLI.args.copy()

        args["remove"] = True
        args["<name>"] = None
        args["--all"] = False

        self.cli.dispatch(dam, args)
        dam.remove.assert_called_with(None, False)

        args["--all"] = True

        self.cli.dispatch(dam, args)
        dam.remove.assert_called_with(None, True)

        args["<name>"] = ["name1", "name2"]
        args["--all"] = False

        self.cli.dispatch(dam, args)
        dam.remove.assert_called_with(["name1", "name2"], False)

        args["--all"] = True

        self.cli.dispatch(dam, args)
        dam.remove.assert_called_with(["name1", "name2"], True)
