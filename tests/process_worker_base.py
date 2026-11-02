class Worker():

    def __call__(self, *args, **kwargs):
        self.work()
        
    def work(self):
        pass