"""Implementation of OceanDB plugin based in BigchainDB"""
from oceandb_driver_interface.plugin import AbstractPlugin
from oceandb_bigchaindb_driver.instance import get_database_instance, generate_key_pair
from bigchaindb_driver.exceptions import BadRequest


class Plugin(AbstractPlugin):
    """BigchainDB ledger plugin for `Ocean DB's Python reference
    implementation <https://github.com/oceanprotocol/oceandb-bigchaindb-driver>`_.
    Plugs in a BigchainDB instance as the persistence layer for Ocean Db
    related actions.
    """
    BURN_ADDRESS = 'BurnBurnBurnBurnBurnBurnBurnBurnBurnBurnBurn'

    def __init__(self, config):
        """Initialize a :class:`~.Plugin` instance and connect to BigchainDB.
        Args:
            *nodes (str): One or more URLs of BigchainDB nodes to
                connect to as the persistence layer
        """
        self.driver = get_database_instance(config)
        self.user = generate_key_pair(config['secret'])
        self.namespace = config['db.namespace']

    @property
    def type(self):
        """str: the type of this plugin (``'BigchainDB'``)"""
        return 'BigchainDB'

    def write(self, obj):
        prepared_creation_tx = self.driver.instance.transactions.prepare(
            operation='CREATE',
            signers=self.user.public_key,
            asset={
                'namespace': self.namespace,
                'data': obj
            },
            metadata={
                'namespace': self.namespace,
                'data': obj
            }
        )

        signed_tx = self.driver.instance.transactions.fulfill(
            prepared_creation_tx,
            private_keys=self.user.private_key
        )
        print('bdb::write::{}'.format(signed_tx['id']))
        # TODO Change to send_commit when we update to the new version
        return self.driver.instance.transactions.send(signed_tx)

    def read(self, tx_id):
        value = [
            {
                'data': transaction['metadata'],
                'id': transaction['id'],
                'tx': transaction
            }
            for transaction in self.driver.instance.transactions.get(asset_id=tx_id)
        ][-1]['data']['data']
        print('bdb::read::{}'.format(value))
        return value

    def update(self, metadata, unspent=None):
        try:
            if not unspent:
                sent_tx = self.write(metadata)
                print('bdb::put::{}'.format(sent_tx['id']))
                return sent_tx
            else:
                sent_tx = self.put(metadata, unspent)
                print('bdb::put::{}'.format(sent_tx['id']))
                return sent_tx

        except BadRequest as e:
            print(e)

    def list(self, search_from=None, search_to=None, offset=None, limit=None):
        all = self.driver.instance.metadata.get(search=self.namespace)
        list = []
        for id in all:
            try:
                list.append(self.read(id['id']))
            except:
                pass

        return list[0:limit]

    def query(self, query_string):
        query_string = ' "{}" '.format(query_string)
        print('bdb::get::{}'.format(query_string))
        assets = self.driver.instance.assets.get(search=query_string)
        print('bdb::result::len {}'.format(len(assets)))
        return assets

    def put(self, metadata, unspent):
        output_index = 0
        output = unspent['outputs'][output_index]

        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': output_index,
                'transaction_id': unspent['id']
            },
            'owners_before': output['public_keys']
        }

        prepared_transfer_tx = self.driver.instance.transactions.prepare(
            operation='TRANSFER',
            asset=unspent['asset'] if 'id' in unspent['asset'] else {'id': unspent['id']},
            inputs=transfer_input,
            recipients=self.user.public_key,
            metadata={
                'namespace': self.namespace,
                'data': metadata
            }
        )

        signed_tx = self.driver.instance.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.user.private_key,
        )
        # TODO Change to send_commit when we update to the new version
        return self.driver.instance.transactions.send(signed_tx)

    def delete(self, unspent):
        output_index = 0
        output = unspent['outputs'][output_index]

        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': output_index,
                'transaction_id': unspent['id']
            },
            'owners_before': output['public_keys']
        }

        prepared_transfer_tx = self.driver.instance.transactions.prepare(
            operation='TRANSFER',
            asset=unspent['asset'] if 'id' in unspent['asset'] else {'id': unspent['id']},
            inputs=transfer_input,
            recipients=self.BURN_ADDRESS,
            metadata={
                'namespace': 'burned',

            }
        )

        signed_tx = self.driver.instance.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.user.private_key,
        )
        # TODO Change to send_commit when we update to the new version
        return self.driver.instance.transactions.send(signed_tx)
