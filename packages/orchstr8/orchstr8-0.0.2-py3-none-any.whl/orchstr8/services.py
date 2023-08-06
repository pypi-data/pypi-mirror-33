import os
import sys
import time
import shutil
import asyncio
import zipfile
import tarfile
import logging
import tempfile
import subprocess
import requests
from binascii import hexlify
from typing import Type

import twisted
twisted.internet.base.DelayedCall.debug = True

from twisted.python import log as twisted_log
twisted_log.PythonLoggingObserver().start()

from electrumx.server.controller import Controller
from electrumx.server.env import Env
from torba.wallet import Wallet
from torba.baseledger import BaseLedger
from torba.manager import WalletManager

root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class TorbaService:

    def __init__(self, manager_class, ledger_class, verbose=False):
        # type: (Type[WalletManager], Type[BaseLedger], bool) -> None
        self.manager_class = manager_class
        self.ledger_class = ledger_class
        self.verbose = verbose
        self.manager = None  # type: WalletManager
        self.ledger = None  # type: BaseLedger
        self.wallet = None  # type: Wallet
        self.data_path = None  # type: str

    async def start(self):
        self.data_path = tempfile.mkdtemp()
        wallet_file_name = os.path.join(self.data_path, 'my_wallet.json')
        with open(wallet_file_name, 'w') as wf:
            wf.write('{"version": 1, "accounts": []}\n')
        self.manager = self.manager_class.from_config({
            'ledgers': {
                self.ledger_class.get_id(): {
                    'default_servers': [('localhost', 1984)],
                    'data_path': self.data_path
                }
            },
            'wallets': [wallet_file_name]
        })
        self.ledger = self.manager.ledgers[self.ledger_class]
        self.wallet = self.manager.default_wallet
        self.wallet.generate_account(self.ledger)
        await self.manager.start().asFuture(asyncio.get_event_loop())

    async def stop(self, cleanup=True):
        await self.manager.stop().asFuture(asyncio.get_event_loop())
        cleanup and self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)


class ElectrumXService:

    def __init__(self, coin_class, verbose=False):
        self.coin_class = coin_class
        self.verbose = verbose
        self.controller = None
        self.data_path = None

    async def start(self):
        self.data_path = tempfile.mkdtemp()
        conf = {
            'DB_DIRECTORY': self.data_path,
            'DAEMON_URL': 'http://rpcuser:rpcpassword@localhost:50001/',
            'REORG_LIMIT': '100',
            'TCP_PORT': '1984'
        }
        os.environ.update(conf)
        self.controller = Controller(Env(self.coin_class))
        self.controller.start_time = time.time()
        await self.controller.start_servers()
        await self.controller.tcp_server_started.wait()

    async def stop(self, cleanup=True):
        await self.controller.shutdown()
        cleanup and self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)


class BlockchainProcess(asyncio.SubprocessProtocol):

    IGNORE_OUTPUT = [
        b'keypool keep',
        b'keypool reserve',
        b'keypool return',
    ]

    def __init__(self, verbose=False):
        self.ready = asyncio.Event()
        self.stopped = asyncio.Event()
        self.verbose = verbose

    def pipe_data_received(self, fd, data):
        if self.verbose and not any(ignore in data for ignore in self.IGNORE_OUTPUT):
            print(data.decode('ascii'))
        if b'Error:' in data:
            self.ready.set()
            raise SystemError(data.decode('ascii'))
        elif b'Done loading' in data:
            self.ready.set()
        elif b'Shutdown: done' in data:
            self.stopped.set()

    def process_exited(self):
        self.stopped.set()


class BlockchainService:

    def __init__(self, url, daemon, cli, verbose=False):
        self.latest_release_url = url
        self.project_dir = os.path.dirname(os.path.dirname(__file__))
        self.bin_dir = os.path.join(self.project_dir, 'bin')
        self.daemon_bin = os.path.join(self.bin_dir, daemon)
        self.cli_bin = os.path.join(self.bin_dir, cli)
        self.verbose = verbose
        self.data_path = None
        self.protocol = None
        self.transport = None

    @property
    def exists(self):
        return (
            os.path.exists(self.cli_bin) and
            os.path.exists(self.daemon_bin)
        )

    def download(self):
        downloaded_file = os.path.join(
            self.bin_dir,
            self.latest_release_url[self.latest_release_url.rfind('/')+1:]
        )

        if not os.path.exists(self.bin_dir):
            os.mkdir(self.bin_dir)

        if not os.path.exists(downloaded_file):
            print('Downloading: {}'.format(self.latest_release_url))
            r = requests.get(self.latest_release_url, stream=True)
            with open(downloaded_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        if downloaded_file.endswith('.zip'):
            with zipfile.ZipFile(downloaded_file) as zf:
                zf.extractall(self.bin_dir)
                # zipfile bug https://bugs.python.org/issue15795
                os.chmod(self.cli_bin, 0o755)
                os.chmod(self.daemon_bin, 0o755)

        elif downloaded_file.endswith('.tar.gz'):
            with tarfile.open(downloaded_file) as tar:
                tar.extractall(self.bin_dir)

        return self.exists

    def ensure(self):
        return self.exists or self.download()

    async def start(self):
        assert self.ensure()
        self.data_path = tempfile.mkdtemp()
        loop = asyncio.get_event_loop()
        asyncio.get_child_watcher().attach_loop(loop)
        command = (
            self.daemon_bin,
            '-datadir={}'.format(self.data_path),
            '-printtoconsole', '-regtest', '-server', '-txindex',
            '-rpcuser=rpcuser', '-rpcpassword=rpcpassword', '-rpcport=50001'
        )
        print(' '.join(command))
        self.transport, self.protocol = await loop.subprocess_exec(
            lambda: BlockchainProcess(self.verbose), *command
        )
        await self.protocol.ready.wait()

    async def stop(self, cleanup=True):
        try:
            self.transport.terminate()
            await self.protocol.stopped.wait()
        finally:
            if cleanup:
                self.cleanup()

    def cleanup(self):
        shutil.rmtree(self.data_path, ignore_errors=True)

    async def _cli_cmnd(self, *args):
        cmnd_args = [
            self.cli_bin, '-datadir={}'.format(self.data_path), '-regtest',
            '-rpcuser=rpcuser', '-rpcpassword=rpcpassword', '-rpcport=50001'
        ] + list(args)
        self.verbose and print(' '.join(cmnd_args))
        loop = asyncio.get_event_loop()
        asyncio.get_child_watcher().attach_loop(loop)
        process = await asyncio.create_subprocess_exec(
            *cmnd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        out, err = await process.communicate()
        self.verbose and print(out.decode().strip())
        return out.decode().strip()

    def generate(self, blocks):
        return self._cli_cmnd('generate', str(blocks))

    def get_raw_change_address(self):
        return self._cli_cmnd('getrawchangeaddress')

    async def get_balance(self):
        return float(await self._cli_cmnd('getbalance'))

    def send_to_address(self, address, credits):
        return self._cli_cmnd('sendtoaddress', address, str(credits))

    def send_raw_transaction(self, tx):
        return self._cli_cmnd('sendrawtransaction', tx.decode())

    def decode_raw_transaction(self, tx):
        return self._cli_cmnd('decoderawtransaction', hexlify(tx.raw).decode())

    def get_raw_transaction(self, txid):
        return self._cli_cmnd('getrawtransaction', txid, '1')
