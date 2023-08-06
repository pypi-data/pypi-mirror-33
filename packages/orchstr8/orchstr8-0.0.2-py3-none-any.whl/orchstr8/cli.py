import sys
import asyncio
from orchstr8.conductor import FullStack


def main():
    stack = FullStack(verbose=True)
    if sys.argv[-1] == 'download':
        stack.blockchain.ensure()
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(stack.start())
            print('========== Services Started ========')
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(stack.stop())
