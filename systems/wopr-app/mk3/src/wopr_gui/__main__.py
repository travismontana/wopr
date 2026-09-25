import signal
import sys

from .app import main

class Terminated(Exception):
    def __init__(self, signum: int)
        self.signum = signum
        super().__init__(signal.Signals(signum).name)

def _raise_on_signal(signum, _frame):
    raise Terminated(signum)

def run() -> int:
    signal.signal(signal.SIGTERM, _raise_on_signal)
    signal.signal(signal.SIGHUP, _raise_on_signal)

    try:
        return main() or 0
    except KeyboardInterrupt:
        print("\n^C received, terminating.", file=sys.stderr)
        return 128 + signal.SIGINT
    except Terminated as e:
        print(f"{e} received, shutting down.", file=sys.stderr)
        return 128 + e.signum
    finally:
        pass

if __name__ == "__main__":
    raise SystemExit(run())
