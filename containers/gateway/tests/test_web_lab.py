import asyncio
import hashlib
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["CREW_PORTAL_DB"] = str(Path(tempfile.gettempdir()) / "webapp_slice_a_test.db")
os.environ["ENTRY_IMAGE"] = str(ROOT / "entry" / "access_artifact.png")

from webapp import app as module


class FakeRequest:
    def __init__(self, token: str, body: bytes = b""):
        self.cookies = {"webapp_session": token}
        self._body = body

    async def body(self) -> bytes:
        return self._body


def reset_fixture() -> str:
    try:
        Path(os.environ["CREW_PORTAL_DB"]).unlink()
    except FileNotFoundError:
        pass
    module.sessions.clear()
    module.init_db()
    token = "test-maintenance-session"
    module.sessions[token] = 1
    return token


def test_entry_image_and_expected_credentials():
    image = ROOT / "entry" / "access_artifact.png"
    assert image.exists()
    digest = hashlib.md5(image.read_bytes()).hexdigest()
    assert len(digest) == 32
    assert module.entry_md5() == digest


def test_fixture_contains_idor_target():
    reset_fixture()
    with module.connect() as db:
        own = db.execute("SELECT * FROM research WHERE id=1").fetchone()
        target = db.execute("SELECT * FROM research WHERE id=2").fetchone()
    assert own["owner_id"] == 1
    assert target["owner_id"] == 2
    assert "CTF{webapp_idor_thread_01}" in target["body"]
    assert "comms_relay.internal" in target["body"]


def test_sqli_search_reveals_hidden_archive_clue():
    token = reset_fixture()
    normal = module.search_research("comms_relay", FakeRequest(token))
    assert normal["results"]
    injected = module.search_research("' OR 1=1 -- ", FakeRequest(token))
    assert any(row["title"] == "Archive transfer exception" for row in injected["results"])
    assert any("CTF{webapp_sqli_thread_01b}" in row["body"] for row in injected["results"])


def test_stored_xss_is_retained_and_rendered_in_moderation_queue():
    token = reset_fixture()
    payload = b"subject=Review&message=%3Cimg+src%3Dx+onerror%3D%22document.body.dataset.webappXss%3D%27seen%27%22%3E"
    saved = asyncio.run(module.submit_feedback(FakeRequest(token, payload)))
    assert saved["status"] == "queued"
    queue = module.moderation_queue(FakeRequest(token))
    assert 'onerror="document.body.dataset.webappXss=\'seen\'"' in queue.body.decode()


def test_horizontal_profile_and_backup_boundaries_are_broken():
    token = reset_fixture()
    profile = module.profile("mira.chen", FakeRequest(token))
    assert profile["username"] == "mira.chen"
    assert "CTF{webapp_profile_horizontal_01}" in profile["private_note"]
    backup = module.backup(3, FakeRequest(token))
    assert backup["owner_id"] == 3
    assert "CTF{webapp_backup_horizontal_02}" in backup["contents"]


def test_horizontal_research_boundary_is_broken():
    token = reset_fixture()
    record = module.research(2, FakeRequest(token))
    assert record["owner_id"] == 2
    assert "CTF{webapp_idor_thread_01}" in record["body"]
