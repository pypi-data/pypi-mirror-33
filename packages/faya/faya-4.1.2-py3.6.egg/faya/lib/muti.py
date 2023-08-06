from multiprocessing import Pool, Manager


class Multithread(object):
    def __init__(self):
        self.queue = _Queue()

    @staticmethod
    def execute(f, data_list):
        pool = Pool()
        pool.map(f, data_list)
        pool.close()
        pool.join()


class _Queue(object):
    def __init__(self):
        self.q = Manager().Queue()

    def put_q(self):
        [self.q.put(each) for each in self.dl]

    def execute(self, fun, datalist):
        self.dl = datalist
        self.len = range(0, len(datalist))
        self.f = fun
        pool = Pool()
        self.put_q()
        pool.map(self.dummy, self.len)
        pool.close()
        pool.join()

    def dummy(self, placeholder):
        self.f(self.q.get())


if __name__ == '__main__':
    l = range(0, 5)


    def p(n):
        print(n)


    mp = Multithread()
    mp.execute(p, l)

    print('=' * 10 + 'q' + '=' * 10)

    mp.queue.execute(p,l)
