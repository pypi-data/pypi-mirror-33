from cmd2 import Cmd
from cmd2 import parsing
from . import explorer
import h5py
import os
import tree_format
import sys
import argparse
import re
import shlex
import pathlib


class CmdApp(Cmd):
    def __init__(self):
        Cmd.shortcuts.update({"!": "bang", "$": "shell"})
        Cmd.__init__(self)
        self.abbrev = True
        self.prompt = "[] > "
        self.explorer = None
        self.dir_stack = ["/"]
        self.__write_warn = True

    def postcmd(self, stop, line):
        self.prompt = "[] > "
        if self.explorer:
            self.prompt = "[{}: {}/] {} ".format(
                os.path.basename(self.explorer.filename),
                os.path.basename(self.explorer.working_dir),
                ">" if self.explorer.raw.mode == "r" else "+>",
            )
        return stop

    def do_source(self, args):
        Cmd.do_load(self, args)

    def do_load(self, args):
        """Load an hdf5 file."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="load", description=CmdApp.do_load.__doc__)
        parser.add_argument(
            "--mode",
            "-m",
            type=str,
            default="r",
            choices=("r", "w", "a", "r+"),
            help="File mode ([r]ead, [w]rite, [a]ppend)",
        )
        parser.add_argument("file", type=str, default="", nargs="?", help="The file to open.")
        parser.add_argument(
            "path", type=str, default="", nargs="?", help="Path within the HDF5 file"
        )
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if self.__write_warn and args.mode in ["a", "w", "r+"]:
            print(
                "Warning: writing operations are pre-alpha quality: have backups", file=sys.stderr
            )
            self.__write_warn = False
        path = args.path
        filename = args.file

        if filename == "":
            filename = self.explorer.filename
            path = self.explorer.working_dir
            self.explorer.close()

        self.explorer = explorer.H5Explorer.from_file(filename, mode=args.mode)
        self.explorer.change_dir(path)

    def do_ls(self, args):
        """List directory contents."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="ls", description=CmdApp.do_ls.__doc__)
        parser.add_argument(
            "directory", type=str, default=".", nargs="?", help="Path within the HDF5 file"
        )
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        dest = self.explorer[args.directory]

        for g in dest.groups:
            print(g + "/")

        for ds in dest.datasets:
            print(ds)

    def do_cd(self, args):
        """Change the working directory."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="cd", description=CmdApp.do_cd.__doc__)
        parser.add_argument(
            "path", type=str, default="/", nargs="?", help="Path within the HDF5 file"
        )
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        self.dir_stack.pop()
        self.dir_stack.append(args.path)
        self.explorer.change_dir(args.path)

    def do_pwd(self, args):
        """Print the working directory."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="pwd", description=CmdApp.do_pwd.__doc__)
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        print(self.explorer.working_dir)

    def do_pushd(self, args):
        """Add directories to the stack.

        Adds a directory to the top of the directory stack,
        making the new top of the stack the current working directory.
        With no arguments, exchanges the top two directories.
        """
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="pushd", description=CmdApp.do_pushd.__doc__)
        parser.add_argument(
            "dir",
            nargs="?",
            help="""Adds DIR to the directory stack at the top,
                    making it the new current working directory.""",
        )
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        if args.dir is None:
            if len(self.dir_stack) < 2:
                raise ValueError("pushd: no other directory")
            top = self.dir_stack.pop()
            second = self.dir_stack.pop()
            directory = second
            self.dir_stack.append(self.explorer.get_absolute_path(top))
            self.dir_stack.append(self.explorer.get_absolute_path(second))
        else:
            directory = args.dir
            self.dir_stack.append(self.explorer.get_absolute_path(directory))
        self.explorer.change_dir(directory)

    def do_popd(self, args):
        """Remove directories from the stack."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="popd", description=CmdApp.do_popd.__doc__)
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if len(self.dir_stack) <= 1:
            raise ValueError("popd: directory stack empty")
        self.dir_stack.pop()
        self.explorer.change_dir(self.dir_stack[-1])
        self.do_pwd("")

    def do_mkdir(self, args):
        """Make directories"""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="mkdir", description=CmdApp.do_mkdir.__doc__)
        parser.add_argument("directory", type=str, help="Path within the HDF5 file")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        h5_grp = self.explorer[args.directory + "/.."].raw
        h5_grp.create_group(args.directory)

    def do_rmdir(self, args):
        raise NotImplementedError

    def do_rm(self, args):
        """Copy files and directories."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="cp", description=CmdApp.do_cp.__doc__)
        parser.add_argument(
            "-f",
            "--force",
            action="store_const",
            const="f",
            dest="interaction",
            help="""if  an existing destination file cannot be opened,
                        remove it and try again (overrides a previous -i or -n option)""",
        )
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_const",
            const="i",
            dest="interaction",
            help="prompt before every removal (overrides a previous -f or -n option)",
        )
        parser.add_argument("-d", "--dir", action="store_true", help="remove empty directories")
        parser.add_argument(
            "-R", "-r", "--recursive", action="store_true", help="copy groups recursively"
        )
        parser.add_argument("file", type=str, nargs="+", help="The file to open.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if args.interaction is None:
            args.interaction = "i"

        for fil in args.file:
            try:
                fil = self.explorer.get_absolute_path(fil)
                self.explorer.dataset(fil)
            except ValueError as e:
                if "not exist" in e.args[0]:
                    print("rm: omitting '{}': No such dataset or group".format(fil))
                    continue
                elif not args.recursive:
                    group = self.explorer.group(fil)
                    if not args.dir or (len(group) != 0 or len(group.attrs) != 0):
                        print("rm: -r not specified; omitting group '{}'".format(fil))
                        continue
            force = args.interaction == "f"
            if args.interaction == "i":
                inp = input("rm: remove '{}'? ".format(fil))
                force = inp.lower() in ["y", "yes"]
            if force:
                del self.explorer[fil]

    def do_cat(self, args):
        raise NotImplementedError

    def do_head(self, args):
        raise NotImplementedError

    def do_tail(self, args):
        raise NotImplementedError

    def do_cp(self, args):
        """Copy files and directories."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="cp", description=CmdApp.do_cp.__doc__)
        parser.add_argument(
            "-f",
            "--force",
            action="store_const",
            const="f",
            dest="interaction",
            help="""if  an existing destination file cannot be opened,
                        remove it and try again (overrides a previous -i or -n option)""",
        )
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_const",
            const="i",
            dest="interaction",
            help="prompt before overwrite (overrides a previous -f or -n option)",
        )
        parser.add_argument(
            "-n",
            "--no-clobber",
            action="store_const",
            const="n",
            dest="interaction",
            default="i",
            help="do not overwrite an existing file (overrides a previous -f or -i option)",
        )
        parser.add_argument(
            "-R", "-r", "--recursive", action="store_true", help="copy groups recursively"
        )
        parser.add_argument(
            "-t",
            "--target-group",
            type=str,
            dest="target",
            help="copy all SOURCE arguments into GROUP",
        )
        parser.add_argument("source", type=str, nargs="+", help="The file to open.")
        parser.add_argument("dest", type=str, help="Path within the HDF5 file")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if args.interaction is None:
            args.interaction = "i"
        if args.target:
            dest = self.explorer.group(args.target)
            source = args.source + [args.dest]
        else:
            dest = args.dest
            source = args.source
            try:
                dest = self.explorer.group(dest)
            except ValueError:
                dest = self.explorer.get_absolute_path(dest)
                # Destination is not an existing group, keep string

        for src in source:
            try:
                self.explorer.dataset(src)
                src = self.explorer.get_absolute_path(src)
            except ValueError as e:
                if "not exist" in e.args[0]:
                    print("cp: omitting '{}': No such dataset or group".format(src))
                    continue
                elif not args.recursive:
                    print("cp: -r not specified; omitting group '{}'".format(src))
                    continue
                else:
                    src = self.explorer.group(src)
            try:
                self.explorer.raw.copy(src, dest)
            except ValueError:
                force = args.interaction == "f"
                d = dest
                if isinstance(dest, h5py.Group):
                    s = src
                    if not isinstance(src, (str, bytes, os.PathLike)):
                        s = src.name
                    d = "/".join((dest.name, os.path.basename(s)))
                if args.interaction == "i":
                    inp = input("cp: overwrite '{}'? ".format(d))
                    force = inp.lower() in ["y", "yes"]
                if force:
                    del self.explorer[d]
                    self.explorer.raw.copy(src, dest)

    def do_mv(self, args):
        """Move (rename) files."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="mv", description=CmdApp.do_mv.__doc__)
        parser.add_argument(
            "-f",
            "--force",
            action="store_const",
            const="f",
            dest="interaction",
            help="""if  an existing destination file cannot be opened,
                        remove it and try again (overrides a previous -i or -n option)""",
        )
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_const",
            const="i",
            dest="interaction",
            help="prompt before overwrite (overrides a previous -f or -n option)",
        )
        parser.add_argument(
            "-n",
            "--no-clobber",
            action="store_const",
            const="n",
            dest="interaction",
            default="i",
            help="do not overwrite an existing file (overrides a previous -f or -i option)",
        )
        parser.add_argument(
            "-t",
            "--target-group",
            type=str,
            dest="target",
            help="move all SOURCE arguments into GROUP",
        )
        parser.add_argument("source", type=str, nargs="+", help="The file to open.")
        parser.add_argument("dest", type=str, help="Path within the HDF5 file")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if args.interaction is None:
            args.interaction = "i"
        if args.target:
            dest = self.explorer.group(args.target)
            source = args.source + [args.dest]
        else:
            dest = args.dest
            source = args.source
            dest = self.explorer.get_absolute_path(dest)

        for src in source:
            try:
                self.explorer.dataset(src)
                src = self.explorer.get_absolute_path(src)
            except ValueError as e:
                if "not exist" in e.args[0]:
                    print("mv: omitting '{}': No such dataset or group".format(src))
                    continue
            try:
                self.explorer.raw.move(src, dest)
            except ValueError:
                force = args.interaction == "f"
                d = dest
                if isinstance(dest, h5py.Group):
                    s = src
                    if not isinstance(src, (str, bytes, os.PathLike)):
                        s = src.name
                    d = "/".join((dest.name, os.path.basename(s)))
                if args.interaction == "i":
                    inp = input("mv: overwrite '{}'? ".format(d))
                    force = inp.lower() in ["y", "yes"]
                if force:
                    del self.explorer[d]
                    self.explorer.raw.move(src, dest)

    def do_su(self, args):
        parser = argparse.ArgumentParser(prog="su", description=CmdApp.do_su.__doc__)
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        self.do_load("-ma")

    def do_sudo(self, args):
        """Elevate priveleges to write for one command."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(
            prog="sudo", description=CmdApp.do_sudo.__doc__, prefix_chars="\00"
        )
        parser.add_argument("command", nargs="+")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        if args.command[0] in ["-h", "--help"]:
            print(re.sub("\00", "-", parser.format_help()))
            return
        # guaranteed to be 'r' or 'r+' not 'w' which would be dangerous
        mode = self.explorer.raw.mode
        self.do_load("-ma")
        self.onecmd_plus_hooks(" ".join(args.command))
        self.do_load("-m" + mode)

    def do_bang(self, args):
        if args.strip() == "!":
            print(self.history[-2])
            cmd = self.history[-2]
        elif args.strip().isnumeric():
            print(self.history[-1 * int(args) - 1])
            cmd = self.history[-1 * int(args) - 1]
        else:
            history = self.history.copy()
            history.reverse()
            for cmdi in history:
                if cmdi.startswith(args):
                    print(cmdi)
                    cmd = cmdi
                    break
            raise ValueError("{}: event not found".format(args))

        # terminators needs to be set because of https://github.com/python-cmd2/cmd2/pull/463
        parser = parsing.StatementParser(terminators=[";"])
        cmd = parser.parse(cmd)
        self.onecmd(cmd)

    def do_clear(self, args):
        os.system("clear")

    def do_shape(self, args):
        """Print the shape of a dataset."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="shape", description=CmdApp.do_shape.__doc__)
        parser.add_argument(
            "-n",
            "--number",
            action="store_const",
            const="number",
            dest="kind",
            help="print number of elements, rather than full shape",
        )
        parser.add_argument(
            "-m",
            "--maxshape",
            action="store_const",
            const="maxshape",
            dest="kind",
            help="print maximum shape, rather than current shape",
        )
        parser.add_argument(
            "-c",
            "--chunks",
            action="store_const",
            const="chunks",
            dest="kind",
            help="print shape of chunks, rather than full shape",
        )
        parser.add_argument("dataset", type=str, help="The dataset.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        if args.kind == "number":
            print(self.explorer[args.dataset].size)

        elif args.kind == "maxshape":
            print(self.explorer[args.dataset].maxshape)

        elif args.kind == "chunks":
            print(self.explorer[args.dataset].chunks)

        else:
            print(self.explorer[args.dataset].shape)

    def do_resize(self, args):
        """Resize a dataset to a given shape."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="resize", description=CmdApp.do_resize.__doc__)
        parser.add_argument(
            "-a",
            "--axis",
            type=int,
            help="change length of a single axis, rather than the full shape",
        )
        parser.add_argument("dataset", type=str, help="The dataset.")
        parser.add_argument("shape", type=int, nargs="+", help="The shape.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        dataset = args.dataset
        shape = tuple(args.shape)
        if args.axis is not None:
            if len(shape) != 1:
                raise ValueError("Expected exactly one integer when changing axis size")
            self.explorer[dataset].resize(shape[0], axis=args.axis)
        else:
            self.explorer[dataset].resize(shape)

    def do_len(self, args):
        """Print the length of a dataset.

        Equivalent to the python len(dataset).
        """
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="len", description=CmdApp.do_len.__doc__)
        parser.add_argument("dataset", type=str, help="The dataset.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        print(self.explorer[args.dataset].len())

    def do_exit(self, args):
        return True

    def do_tree(self, args):
        """list contents of groups in a tree-like format."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="tree", description=CmdApp.do_tree.__doc__)
        parser.add_argument(
            "-s", "--shape", action="store_true", help="print the shape of datasets"
        )
        parser.add_argument(
            "directory", type=str, default="", nargs="?", help="Path within the HDF5 file"
        )
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        global __groupcount
        global __datasetcount
        __groupcount = 0
        __datasetcount = 0

        def children(item):
            if isinstance(item, h5py.Dataset):
                return []
            else:
                return [i[1] for i in item.items()]

        def format(item):
            name = os.path.basename(item.name)
            if name == "":
                name = "/"
            if isinstance(item, h5py.Dataset):
                if args.shape:
                    name = name + "  " + str(item.shape)
                global __datasetcount
                __datasetcount += 1
            elif isinstance(item, h5py.Group):
                global __groupcount
                __groupcount += 1
            return name

        group = self.explorer.group(args.directory)
        tree_format.print_tree(group, format, children)
        print("{} groups, {} datasets".format(__groupcount - 1, __datasetcount))

    def do_dtype(self, args):
        """Print the data type of a dataset."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="dtype", description=CmdApp.do_dtype.__doc__)
        parser.add_argument("dataset", type=str, help="The dataset.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        print(self.explorer[args.dataset].dtype)

    def do_comp(self, args):
        """Print the compression filter of a dataset."""
        args = shlex.split(args)
        parser = argparse.ArgumentParser(prog="comp", description=CmdApp.do_comp.__doc__)
        parser.add_argument("--opts", "-o", action="store_true", help="print compression options.")
        parser.add_argument("dataset", type=str, help="The dataset.")
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return

        print(self.explorer[args.dataset].compression)
        if args.opts:
            print(self.explorer[args.dataset].compression_opts)


def main():
    c = CmdApp()
    with open(pathlib.Path(__file__).parent / "VERSION") as f:
        version = f.read().strip()
    parser = argparse.ArgumentParser(description="Bash-like interface to HDF5 files")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(version))
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        default="r",
        choices=("r", "w", "a", "r+"),
        help="File mode ([r]ead, [w]rite, [a]ppend)",
    )
    parser.add_argument("file", type=str, default="", nargs="?", help="The file to open.")
    parser.add_argument("path", type=str, default="", nargs="?", help="Path within the HDF5 file")
    args, extras = parser.parse_known_args()
    if args.file:
        c.onecmd_plus_hooks("load -m{} {} {}".format(args.mode, args.file, args.path))
    sys.argv = [sys.argv[0]] + extras
    c.cmdloop()
    c.explorer.close()
