
class API:

    def __init__(self,from_id,op,msg,handle):
        self.op = op
        self.handle = handle
        self.from_id = from_id
        self.msg = msg
        self.res = "Not handle "
        if self.op == self.__class__.__name__.lower():
            self.res = self.handle()

    def handle(self):
        raise NotImplementedError("must implemment " )
