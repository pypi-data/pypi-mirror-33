"""The uchroot tool used for light-weight container execution."""
import plumbum as pb
import benchbuild.tool as t


class Uchroot(t.Tool):
    NAME = 'uchroot'
    VERSION = 'HEAD'

    def available(self):
        try:
            cmd = pb.local[self.name]
        except pb.CommandNotFound:
            cmd = None
        return cmd is not None