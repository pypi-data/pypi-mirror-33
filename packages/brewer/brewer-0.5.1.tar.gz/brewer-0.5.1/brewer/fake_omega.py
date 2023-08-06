from random import randint

"""
This is a version of the omega class with bogus data.
It doesn't use any hardware, but it behaves like the actual omega would.
This is used for testing.

Some of this may look weird and redundant, but it's necessary to imitate
the actual omega class. Take a look at them side by side.
"""


class FakeOmega():
    """
    See above. This is just to mock the actual `Omega` class. All methods callable on the `Omega` class are callable here.
    """
    def __init__(self, ):
        self.pv_temp = randint(60, 120)
        self.sv_temp = randint(121, 175)
        # You may notice there is no is_running() method.
        # It will just return this value. It's not needed.
        self.is_pid_running = False

    def safeguard(self, item, types):
        for type in types:
            if isinstance(item, type):
                return True
        raise ValueError(
            "Safeguard failed, %s does not match given types of %s" % (item, types))

    def pv(self):
        return float(self.pv_temp)

    def sv(self):
        return float(self.sv_temp)

    def set_sv(self, temp):
        self.safeguard(temp, [int, float])
        self.sv_temp = temp
        return True

    def run(self):
        self.is_pid_running = True
        return True

    def stop(self):
        self.is_pid_running = False
        return True

    def is_running(self):
        return self.is_pid_running
