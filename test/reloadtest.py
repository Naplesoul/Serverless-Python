import time

from userland import action
import importlib


def test():
    while True:
        try:
            while True:
                try:
                    action.act()
                    time.sleep(0.5)
                except Exception as e:
                    print(repr(e))
        except KeyboardInterrupt:
            print("recv keyboard interrupt")
            importlib.reload(action)


if __name__ == "__main__":
    test()
