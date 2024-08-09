class A:
    def __init__(self):
        self.a = 1

    def get_a(self):
        return self.a

    def set_a(self, a):
        class B:
            def __init__(self):
                self.a = a

            def get_a(self):
                return self.a
