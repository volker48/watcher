import unittest

import os

from app import create_app
from models import db, Checkpoint
from monitor import checkpoint

os.environ['MONITOR_CONFIG'] = 'test_config.py'


class MonitorTestCase(unittest.TestCase):
    def setUp(self):
        self.real_app = create_app()
        self.real_app.testing = True
        self.app = self.real_app.test_client()
        self.context = self.real_app.app_context()
        self.context.push()
        db.create_all()

    def tearDown(self):
        self.context.pop()

    def test_checkpoint_none_existing(self):
        checkpoint('0000000000000b669184e67005840bdea784ee87276cdbd02479019a4dc16ff7')
        c = Checkpoint.query.filter_by(hash='0000000000000b669184e67005840bdea784ee87276cdbd02479019a4dc16ff7').one()
        assert c.hash == '0000000000000b669184e67005840bdea784ee87276cdbd02479019a4dc16ff7'

    def test_checkpoint_existing(self):
        c = Checkpoint(hash='0000000000000b669184e67005840bdea784ee87276cdbd02479019a4dc16ff7')
        db.session.add(c)
        db.session.commit()
        checkpoint('0000000000000a4013ee34b098e9731b232c268609c9308965b1159ba2b83a6c')

        new_checkpoint = Checkpoint.query.filter_by(
            hash='0000000000000a4013ee34b098e9731b232c268609c9308965b1159ba2b83a6c').one()
        assert new_checkpoint.hash == '0000000000000a4013ee34b098e9731b232c268609c9308965b1159ba2b83a6c'
