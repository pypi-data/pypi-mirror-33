__all__ = ('AtomicLoop')
__version__ = '0.1.0'

import signal

class AtomicLoop:

    """
    Implements a context manager which provides you with plain boolean
    flag that can be used to control the iteration flow of a ``while``
    loop based on whether or not an interrupt/terminate signal was received.

    You can still kill the running process using ``SIGKILL``.

    Former inspiration:
    https://stackoverflow.com/a/21919644/7699136
    """

    def __init__(self, on_signal=None, on_exit=None):
        """
        :param on_signal: User-defined function that gets
            called on incoming SIGINT/SIGTERM. Function has to
            take 2 parameters. Details in :meth:`_signal_handler`
        :param on_exit: User-defined function that gets
            called _after_ the execution is finished. Function has to
            take 1 parameter. Details in :meth:`__exit__`
        :type on_signal: callable
        :type on_exit: callable
        """
        self.set_state(True)

        self.callback_on_signal = on_signal
        self.callback_on_exit = on_exit

        if on_signal is None:
            self.callback_on_signal = lambda s,f: None
        if on_exit is None:
            self.callback_on_exit = lambda i: None

    def set_state(self, state=False):
        """This is a stupid solution, but provides additional names
        for ``loop.run`` bool flag that could be used synonymously.
        Unfortunately, ``continue`` is a reserved word :(

        :param bool state: New flag state (whether or not we should
            continue with program execution)
        """
        self.run = state
        self.loop = state
        self.move = state
        self.cont = state
        self.keep = state
        self.keep_going = state
        self.uninterrupted = state

    def _signal_handler(self, sig, frame):
        """Handler function that gets called on incoming SIGINT/SIGTERM.
        Sets the internal flag and propagates the arguments to the
        user-defined callback function.
        
        For details on provided arguments, go to:
        https://docs.python.org/3/library/signal.html#signal.signal
        """
        self.set_state(False)
        self.callback_on_signal(sig, frame)

    def __enter__(self):
        """Invoked when entering the context (inside `with`).
        Resets the state; sets the listeners for
        interruption/termination signals and binds their callback
        to :meth:`_signal_handler`.
        """
        self.set_state(True)

        signal.signal(signal.SIGINT,  self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        return self

    def __exit__(self, *args):
        """Invoked when exiting the context (after `with` block).
        Calls user-defined function with a single boolean argument
        stating whether or not the execution was interrupted.
        """
        self.callback_on_exit(not self.uninterrupted)

