"""Instructor content survives reset; learner changes do not."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'web'))
from app import Database
from baseline import read_baseline, restore


class ResetTests(unittest.TestCase):
    def test_restores_deleted_or_changed_flags_and_discards_runtime_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'seed.json'
            path.write_text(json.dumps({'version':1,'messages':[{'username':'captain','message':'FLAG{initial_test_flag}'}], 'memos':{'captain':'Instructor note'}}))
            seed = read_baseline(path)
            db = Database(Path(folder)/'db.sqlite', 'password123', 'password321')
            restore(db, seed)
            original = db.messages()['messages'][0]
            db.delete_message({'username':'captain','role':'captain'}, original['id'])
            db.add_message('crew', 'Learner message')
            db.add_message('captain', 'Learner using captain credentials')
            db.save_memo('crew', 'Learner memo', 0)
            db.save_memo('captain', 'Changed instructor memo', 1)
            token = db.authenticate('captain','password321')
            restore(db, read_baseline(path))
            rows = db.messages()['messages']
            self.assertEqual([row['message'] for row in rows], ['FLAG{initial_test_flag}'])
            self.assertEqual(db.memo('captain')['content'], 'Instructor note')
            self.assertEqual(db.memo('crew')['content'], '')
            self.assertIsNone(db.user(token))
            restore(db, seed)
            self.assertEqual(db.messages()['total'], 1)

    def test_challenge_records_and_access_grants_return_to_seed(self):
        seed = read_baseline(ROOT/'baseline/board.json')
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder)/'db.sqlite', 'password123', 'password321')
            restore(db, seed)
            with db.roster_connect() as conn:
                conn.execute("UPDATE station_events SET detail='tampered'")
            with db.manifest_connect() as conn:
                conn.execute("DELETE FROM manifests")
            with db.operations_connect() as conn:
                conn.execute("INSERT INTO ops_grants VALUES('learner-grant',9999999999)")
            with db.connect() as conn:
                conn.execute("INSERT INTO tickets(owner,subject,description,created_at) VALUES('crew','test','test','now')")
            restore(db, seed)
            with db.roster_connect() as conn:
                self.assertIn('CTF{LAST_CONTACT_', conn.execute('SELECT detail FROM station_events').fetchone()[0])
            with db.connect() as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0], 0)
            with db.operations_connect() as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM ops_grants').fetchone()[0], 0)
            with db.manifest_connect() as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM manifests').fetchone()[0], 3)

    def test_each_flag_has_its_own_runtime_database(self):
        seed = read_baseline(ROOT/'baseline/board.json')
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder)/'db.sqlite', 'password123', 'password321')
            restore(db, seed)
            self.assertEqual(len({db.roster_path, db.operations_path, db.manifest_path}), 3)
            tables = {}
            for name, connection in [('roster', db.roster_connect),
                                     ('operations', db.operations_connect),
                                     ('manifest', db.manifest_connect)]:
                with connection() as conn:
                    tables[name] = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertIn('station_events', tables['roster'])
            self.assertIn('challenge_secrets', tables['operations'])
            self.assertIn('manifests', tables['manifest'])
            self.assertNotIn('challenge_secrets', tables['roster'])
            self.assertNotIn('manifests', tables['roster'])
            self.assertNotIn('station_events', tables['operations'])
            self.assertNotIn('manifests', tables['operations'])
            self.assertNotIn('station_events', tables['manifest'])
            self.assertNotIn('challenge_secrets', tables['manifest'])

    def test_invalid_baseline_rejected_before_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'seed.json'
            path.write_text('{"version":1,"messages":[{"username":"missing","message":"bad"}]}')
            with self.assertRaises(ValueError):
                read_baseline(path)

if __name__ == '__main__':
    unittest.main(verbosity=2)
