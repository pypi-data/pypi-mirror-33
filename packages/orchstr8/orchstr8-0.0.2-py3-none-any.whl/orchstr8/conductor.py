import os
import logging
import importlib

from twisted.internet import defer

from torba.manager import WalletManager

from orchstr8.services import TorbaService, ElectrumXService, BlockchainService


def get_ledger_from_environment():
    if 'LEDGER' not in os.environ:
        raise ValueError('Environment variable LEDGER must point to a torba based ledger module.')
    module_name = os.environ['LEDGER'].split('-')[-1]  # tox support
    return importlib.import_module(module_name)


def get_electrumx_from_ledger(ledger_module):
    electrumx_path, regtest_class_name = ledger_module.__electrumx__.rsplit('.', 1)
    electrumx_module = importlib.import_module(electrumx_path)
    return getattr(electrumx_module, regtest_class_name)


def set_logging(ledger_module, verbosity):
    level = logging.DEBUG if verbosity else logging.WARNING
    defer.setDebugging(verbosity)
    logging.getLogger('torba').setLevel(level)
    logging.getLogger('asyncio').setLevel(level)
    logging.getLogger('twisted').setLevel(level)
    logging.getLogger('electrumx').setLevel(level)
    logging.getLogger(ledger_module.__name__).setLevel(level)
    logging.getLogger(ledger_module.__electrumx__.split('.')[0]).setLevel(level)


class ServerStack(object):

    def __init__(self, ledger_module=None, verbose=False):
        if ledger_module is None:
            ledger_module = get_ledger_from_environment()
        set_logging(ledger_module, verbose)
        self.blockchain = BlockchainService(
            ledger_module.__node_url__,
            os.path.join(ledger_module.__node_bin__, ledger_module.__node_daemon__),
            os.path.join(ledger_module.__node_bin__, ledger_module.__node_cli__),
            verbose
        )
        self.electrumx = ElectrumXService(get_electrumx_from_ledger(ledger_module), verbose)
        self.ledger_module = ledger_module

    async def start(self):
        await self.blockchain.start()
        await self.blockchain.generate(200)
        await self.electrumx.start()

    async def stop(self, cleanup=True):
        try:
            await self.electrumx.stop(cleanup=cleanup)
        except Exception as e:
            print(e)

        try:
            await self.blockchain.stop(cleanup=cleanup)
        except Exception as e:
            print(e)


class FullStack(ServerStack):

    def __init__(self, wallet_manager_class=WalletManager, ledger_module=None, verbose=False):
        super().__init__(ledger_module, verbose)
        self.wallet = TorbaService(wallet_manager_class, self.ledger_module.RegTestLedger, verbose)

    async def start(self):
        await super().start()
        await self.wallet.start()

    async def stop(self, cleanup=True):
        try:
            await self.wallet.stop(cleanup=cleanup)
        except Exception as e:
            print(e)

        await super().stop(cleanup)
