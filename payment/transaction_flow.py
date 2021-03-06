from .blockchain import Blockchain
from .log import get as get_log
from typing import Callable, List, Generator
from .models import TransactionRecord


log = get_log()


class TransactionFlow():
    """class that saves the last cursor when getting transactions."""
    def __init__(self, cursor):
        self.cursor = cursor

    def _yield_transactions(self, get_records: Callable[[str], List[TransactionRecord]]) -> Generator[TransactionRecord, None, None]:
        """yield transactions from the given function."""
        records = get_records(self.cursor)
        while records:
            for record in records:
                if (record.type == 'payment'
                        and record.asset_code == Blockchain.asset_code
                        and record.asset_issuer == Blockchain.asset_issuer):
                    yield record
                self.cursor = record.paging_token
            records = get_records(self.cursor)

    def get_address_transactions(self, address):
        """get KIN payment transactions for given address."""
        def get_address_records(cursor):
            return Blockchain.get_address_records(address, cursor, 100)

        for record in self._yield_transactions(get_address_records):
            yield Blockchain.get_transaction_data(record.transaction_hash)

    def get_transactions(self, addresses):
        def get_all_records(cursor):
            return Blockchain.get_all_records(cursor, 100)

        for record in self._yield_transactions(get_all_records):
            if record.to_address in addresses:
                yield record.to_address, Blockchain.get_transaction_data(record.transaction_hash)
            elif record.from_address in addresses:
                yield record.from_address, Blockchain.get_transaction_data(record.transaction_hash)
            # else - address is not watched
