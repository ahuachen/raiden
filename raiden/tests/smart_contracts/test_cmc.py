# -*- coding: utf8 -*-
import pytest

from ethereum import tester
from ethereum.utils import sha3
from ethereum.tester import TransactionFailed

from raiden.network.rpc.client import get_contract_path


def test_cmc():
    library_path = get_contract_path('IterableMappingNCC.sol')
    ncc_path = get_contract_path('NettingChannelContract.sol')
    channel_manager_path = get_contract_path('ChannelManagerContract.sol')

    state = tester.state()
    assert state.block.number < 1150000
    state.block.number = 1158001
    assert state.block.number > 1150000
    lib_c = state.abi_contract(None, path=library_path, language="solidity")
    state.mine()
    lib_ncc = state.abi_contract(None, path=ncc_path, language="solidity")
    state.mine()
    c = state.abi_contract(None, path=channel_manager_path, language="solidity",
            libraries={'IterableMappingNCC': lib_c.address.encode('hex'),
            'NettingChannelContract': lib_ncc.address.encode('hex')},
            constructor_parameters=['0x0bd4060688a1800ae986e4840aebc924bb40b5bf'])

    # test key()
    # uncomment private in function to run test
    # vs = sorted((sha3('address1')[:20], sha3('address2')[:20]))
    # k0 = c.key(sha3('address1')[:20], sha3('address2')[:20])
    # assert k0 == sha3(vs[0] + vs[1])
    # k1 = c.key(sha3('address2')[:20], sha3('address1')[:20])
    # assert k1 == sha3(vs[0] + vs[1])
    # with pytest.raises(TransactionFailed):
        # c.key(sha3('address1')[:20], sha3('address1')[:20])

    # test newChannel()
    assert c.assetToken() == sha3('asset')[:20].encode('hex')
    nc1 = c.newChannel(sha3('address1')[:20], 30)
    nc2 = c.newChannel(sha3('address3')[:20], 30)
    with pytest.raises(TransactionFailed):
        c.newChannel(sha3('address1')[:20], 30)
    with pytest.raises(TransactionFailed):
        c.newChannel(sha3('address3')[:20], 30)

    # TODO test event

    # test get()
    print nc1[0]
    chn1 = c.get(sha3('address1')[:20]) # nc1[1] is msg.sender of newChannel
    assert chn1 == nc1[0] # nc1[0] is address of new NettingChannelContract
    chn2 = c.get(sha3('address3')[:20]) # nc2[1] is msg.sender of newChannel
    assert chn2 == nc2[0] # nc2[0] is msg.sender of newChannel
    with pytest.raises(TransactionFailed):  # should throw if key doesn't exist
        c.get(sha3('iDontExist')[:20])

    # test nettingContractsByAddress()
    msg_sender_channels = c.nettingContractsByAddress(nc1[1])
    assert len(msg_sender_channels) == 2
    # assert c.numberOfItems(nc1[1]) == 2  # uncomment private in function to run test
    address1_channels = c.nettingContractsByAddress(sha3('address1')[:20])
    assert len(address1_channels) == 1
    # assert c.numberOfItems(sha3('address1')[:20]) == 1 # uncomment private in function to run test
    address1_channels = c.nettingContractsByAddress(sha3('iDontExist')[:20])
    assert len(address1_channels) == 0
    # assert c.numberOfItems(sha3('iDontExist')[:20]) == 0  # uncomment private in function to run test

    # test getAllChannels()
    arr_of_items = c.getAllChannels()
    assert len(arr_of_items) == 4
    c.newChannel(sha3('address4')[:20])
    assert len(c.getAllChannels()) == 6
    # example usage to convert into list of tuples of participants
    # it = iter(arr_of_items)
    # zip(it, it)

