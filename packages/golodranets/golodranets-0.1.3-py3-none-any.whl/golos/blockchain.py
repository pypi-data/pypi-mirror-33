import hashlib
import json
import logging
import time
import warnings
from typing import Union

from golos.consts import DATABASE_API, OPERATION_HISTORY_API
from golos.instance import shared_steemd_instance
from golos.steemd import Steemd
from golos.utils import parse_time

logger = logging.getLogger(__name__)

virtual_operations = [
    "fill_convert_request",
    "author_reward",
    "curation_reward",
    "comment_reward",
    "liquidity_reward",
    "interest",
    "fill_vesting_withdraw",
    "fill_order",
    "shutdown_witness",
    "fill_transfer_from_savings",
    "hardfork",
    "comment_payout_update",
    'comment_benefactor_reward',
    'return_vesting_delegation'
]

class Blockchain(object):
    """ Access the blockchain and read data from it.

    Args:
        steemd_instance (Steemd): Steemd() instance to use when accessing a RPC
        mode (str): `irreversible` or `head`. `irreversible` is default.
    """

    def __init__(self, steemd_instance=None, mode="irreversible"):
        self.steem = steemd_instance or shared_steemd_instance()
        self.config = self.steem.get_config()

        if mode == "irreversible":
            self.mode = 'last_irreversible_block_num'
        elif mode == "head":
            self.mode = "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.steem.get_dynamic_global_properties()

    def get_current_block_num(self):
        """ This call returns the current block
        """
        return self.info().get(self.mode)

    def get_current_block(self):
        """ This call returns the current block
        """
        return self.steem.get_block(self.get_current_block_num())

    def stream_from(self,
                    start_block=None,
                    end_block=None,
                    batch_operations=False,
                    full_blocks=False,
                    only_virtual_ops=False,
                    **kwargs):
        """ This call yields raw blocks or operations depending on
        ``full_blocks`` param.

        By default, this generator will yield operations, one by one.
        You can choose to yield lists of operations, batched to contain
        all operations for each block with ``batch_operations=True``.
        You can also yield full blocks instead, with ``full_blocks=True``.

        Args:
            start_block (int): Block to start with. If not provided, current (head) block is used.
            end_block (int): Stop iterating at this block. If not provided, this generator will run forever (streaming mode).
            batch_operations (bool): (Defaults to False) Rather than yielding operations one by one,
                yield a list of all operations for each block.
            full_blocks (bool): (Defaults to False) Rather than yielding operations, return raw, unedited blocks as
                provided by steemd. This mode will NOT include virtual operations.
        """

        _ = kwargs  # we need this
        # Let's find out how often blocks are generated!
        block_interval = self.config.get("STEEMIT_BLOCK_INTERVAL") or 3

        is_reversed = end_block and start_block > end_block

        if not start_block:
            start_block = self.get_current_block_num()

        while True:
            head_block = self.get_current_block_num()

            range_params = (start_block, head_block + 1)
            if end_block is not None and start_block > end_block:
                range_params = (start_block, max(0, end_block - 2), -1)

            for block_num in range(*range_params):
                if end_block is not None:
                    if is_reversed and block_num < end_block:
                        raise StopIteration("Reached stop block at: #%s" % block_num)
                    elif not is_reversed and block_num > end_block:
                        raise StopIteration("Reached stop block at: #%s" % block_num)

                if full_blocks:
                    block = self.steem.get_block(block_num)
                    # inject block number
                    block.update({"block_num": block_num})
                    yield block
                elif batch_operations:
                    yield self.steem.get_ops_in_block(block_num, only_virtual_ops)
                else:
                    ops = self.steem.get_ops_in_block(block_num, only_virtual_ops)
                    for op in ops:
                        # avoid yielding empty ops
                        if op:
                            yield op

            # next round
            start_block = head_block + 1
            time.sleep(block_interval)

    def reliable_stream(self,
                        start_block=None,
                        block_interval=None,
                        update_interval=False,
                        batch_operations=False,
                        full_blocks=False,
                        timeout=None,
                        **kwargs):
        """

        A version of stream_from() intended for use in services that NEED
        reliable (nonstop) streaming

        By default, works same as stream_from() but will also keep trying
        until getting a response from steemd, allowing catching up after
        server downtime.

        Warnings: To ensure reliability, this method does some weird
        none-standard things with the steemd client

        Args:

        start_block (int): Block to start with. If not provided, current
        (head) block is used.

        block_interval (int): Time between block generations. If not
        provided, will attempt to query steemd for this value

        batch_operations (bool): (Defaults to False) Rather than yielding
        operations one by one, yield a list of all operations for each
        block.

        full_blocks (bool): (Defaults to False) Rather than yielding
        operations, return raw, unedited blocks as provided by steemd. This
        mode will NOT include virtual operations.

        timeout (int): Time to wait on response from steemd before assuming
        timeout and retrying queries. If not provided, this will default to
        block_interval/4 for all queries except get_block_interval() -
        where it will default to 2 seconds for initial setup

        """

        def get_reliable_client(_timeout):
            # we want to fail fast and try the next node quickly
            return Steemd(
                nodes=self.steem.nodes,
                retries=1,
                timeout=_timeout,
                re_raise=True)

        def reliable_query(_client, _method, _api, *_args):
            # this will ALWAYS eventually return, at all costs
            while True:
                try:
                    return _client.call(_method, *_args, api=_api)
                except Exception as e:
                    logger.error(
                        'Error: %s' % str(s),
                        extra=dict(
                            exc=e,
                            response=retval,
                            api_name=_api,
                            api_method=_method,
                            api_args=_args))
                    time.sleep(1)

        def get_reliable_block_interval(_client):
            return reliable_query(_client, 'get_config',
                                  DATABASE_API).get('STEEMIT_BLOCK_INTERVAL') or 3

        def get_reliable_current_block(_client):
            return reliable_query(_client, 'get_dynamic_global_properties',
                                  DATABASE_API).get(self.mode)

        def get_reliable_blockdata(_client, _block_num):
            return reliable_query(_client, 'get_block', DATABASE_API,
                                  block_num)

        def get_reliable_ops_in_block(_client, _block_num):
            return reliable_query(_client, 'get_ops_in_block', OPERATION_HISTORY_API,
                                  block_num, False)

        if timeout is None:
            if block_interval is None:
                _reliable_client = get_reliable_client(2)
                block_interval = get_reliable_block_interval(_reliable_client)
            else:
                timeout = block_interval / 4
                _reliable_client = get_reliable_client(timeout)
        else:
            _reliable_client = get_reliable_client(timeout)
        if block_interval is None:
            block_interval = get_reliable_block_interval(_reliable_client)
        if start_block is None:
            start_block = get_reliable_current_block(_reliable_client)

        while True:
            sleep_interval = block_interval / 4
            head_block = get_reliable_current_block(_reliable_client)

            for block_num in range(start_block, head_block + 1):
                if full_blocks:
                    yield get_reliable_current_block(_reliable_client,
                                                     head_block)
                elif batch_operations:
                    yield get_reliable_ops_in_block(_reliable_client,
                                                    head_block)
                else:
                    for reliable_ops in get_reliable_ops_in_block(
                            _reliable_client, head_block):
                        yield reliable_ops

                sleep_interval = sleep_interval / 2

            time.sleep(sleep_interval)
            start_block = head_block + 1

    def stream(self,
               filter_by: Union[str, list] = list(),
               *args,
               **kwargs):
        """ Yield a stream of specific operations, starting with current head block.

            This method can work in 2 modes:
            1. Whether only real operations are requested, it will use get_block() API call, so you don't need to have
            neigher operation_history nor accunt_history plugins enabled.
            2. Whether you're requesting any of the virtual operations, your node should have operation_history or
            accunt_history plugins enabled and appropriate settings for the history-related params should be set
            (history-start-block, history-whitelist-ops or history-blacklist-ops).

            The dict output is formated such that ``type`` caries the operation type, timestamp and block_num are taken
            from the block the operation was stored in and the other key depend on the actual operation.

            Args:
                start_block (int): Block to start with. If not provided, current (head) block is used.
                end_block (int): Stop iterating at this block. If not provided, this generator will run forever (streaming mode).
                filter_by (str, list): List of operations to filter for
        """
        if isinstance(filter_by, str):
            filter_by = [filter_by]

        if not bool(set(filter_by).intersection(virtual_operations)):
            # uses get_block instead of get_ops_in_block
            for block in self.stream_from(full_blocks=True, *args, **kwargs):
                for tx in block.get("transactions"):
                    for op in tx["operations"]:
                        if not filter_by or op[0] in filter_by:
                            r = {
                                "type": op[0],
                                "timestamp": block.get("timestamp"),
                                "block_num": block.get("block_num")
                            }
                            r.update(op[1])
                            yield r
        else:
            # uses get_ops_in_block
            kwargs["only_virtual_ops"] = not bool(set(filter_by).difference(virtual_operations))
            for op in self.stream_from(full_blocks=False, *args, **kwargs):
                if kwargs.get('raw_output'):
                    yield op

                if not filter_by or op["op"][0] in filter_by:
                    r = {
                        "_id": self.hash_op(op),
                        "type": op["op"][0],
                        "timestamp": op.get("timestamp"),
                        "block_num": op.get("block"),
                        "trx_id": op.get("trx_id")
                    }
                    r.update(op["op"][1])
                    yield r

    def history(self,
                filter_by: Union[str, list] = list(),
                start_block=1,
                end_block=None,
                raw_output=False,
                **kwargs):
        """ Yield a stream of historic operations.

        Similar to ``Blockchain.stream()``, but starts at beginning of chain unless ``start_block`` is set.

        Args:
            filter_by (str, list): List of operations to filter for
            start_block (int): Block to start with. If not provided, start of blockchain is used (block 1).
            end_block (int): Stop iterating at this block. If not provided, this generator will run forever.
            raw_output (bool): (Defaults to False). If True, return ops in a unmodified steemd structure.
        """
        return self.stream(
            filter_by=filter_by,
            start_block=start_block,
            end_block=end_block,
            raw_output=raw_output,
            **kwargs
        )

    def ops(self, *args, **kwargs):
        raise DeprecationWarning('Blockchain.ops() is deprecated. Please use Blockchain.stream_from() instead.')

    def replay(self, **kwargs):
        warnings.warn('Blockchain.replay() is deprecated. Please use Blockchain.history() instead.')
        return self.history(**kwargs)

    @staticmethod
    def hash_op(event: dict):
        """ This method generates a hash of blockchain operation. """
        data = json.dumps(event, sort_keys=True)
        return hashlib.sha1(bytes(data, 'utf-8')).hexdigest()

    def get_all_usernames(self, *args, **kwargs):
        """ Fetch the full list of GOLOS usernames. """
        _ = args, kwargs
        warnings.warn('Blockchain.get_all_usernames() is now at Steemd.get_all_usernames().')
        return self.steem.get_all_usernames()
