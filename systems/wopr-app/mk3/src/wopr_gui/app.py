import signal
import socket
import sys

from PySide6.QtCore import QSocketNotifier
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow

HANDLED_SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


class SignalBridge:
    """Unix signals -> Qt event loop via the self-pipe trick."""

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.received: int | None = None
        self._rsock, self._wsock = socket.socketpair()
        for s in (self._rsock, self._wsock):
            s.setblocking(False)
        signal.set_wakeup_fd(self._wsock.fileno())
        self._notifier = QSocketNotifier(self._rsock.fileno(), QSocketNotifier.Type.Read)
        self._notifier.activated.connect(self._drain)
        for sig in HANDLED_SIGNALS:
            signal.signal(sig, self._handle)

    def _drain(self) -> None:
        # Just running Python here lets the interpreter dispatch the pending handler.
        try:
            while self._rsock.recv(64):
                pass
        except BlockingIOError:
            pass

    def _handle(self, signum: int, _frame) -> None:
        if self.received is not None:          # second signal: stop being polite
            signal.signal(signum, signal.SIG_DFL)
            signal.raise_signal(signum)
            return
        self.received = signum
        print(f"\n{signal.Signals(signum).name} received, shutting down.", file=sys.stderr)
        self.app.quit()

    def close(self) -> None:
        signal.set_wakeup_fd(-1)
        self._notifier.setEnabled(False)
        self._rsock.close()
        self._wsock.close()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    bridge = SignalBridge(app)
    # app.aboutToQuit.connect(...)                     # ◀ future: release camera, flush db, etc.
    window = MainWindow()
    window.show()
    rc = app.exec()
    bridge.close()
    return 128 + bridge.received if bridge.received else rc
