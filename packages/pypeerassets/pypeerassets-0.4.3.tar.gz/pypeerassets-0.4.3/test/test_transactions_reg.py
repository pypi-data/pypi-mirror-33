import pytest
import time
from decimal import Decimal

from btcpy.structs.transaction import (
    Locktime,
    TxOut,
    MutableTransaction,
    PeercoinMutableTx,
    Transaction
)

from btcpy.structs.script import P2pkhScript

from pypeerassets.transactions import (
    calculate_tx_fee,
    make_raw_transaction,
    p2pkh_script,
    tx_output,
    sign_transaction
)

from pypeerassets.networks import net_query
import pypeerassets as pa


def test_sign_transaction():

    network_params = net_query('tppc')

    provider = pa.Cryptoid(network='tppc')
    key = pa.Kutil(network='tppc',
                   privkey=bytearray.fromhex('9e321f5379c2d1c4327c12227e1226a7c2e08342d88431dcbb0063e1e715a36c')
                   )
    dest_address = pa.Kutil(network='tppc').address
    unspent = provider.select_inputs(key.address, 1)

    output = tx_output(network='tppc',
                       value=Decimal(0.1),
                       n=0, script=p2pkh_script(network='tppc',
                                                address=dest_address)
                       )

    unsigned = PeercoinMutableTx(version=1,
                                 timestamp=int(time.time()),
                                 ins=unspent['utxos'],
                                 outs=[output],
                                 locktime=Locktime(0),
                                 network=network_params.btcpy_constants
                                 )

    assert isinstance(sign_transaction(provider, unsigned, key), Transaction)

