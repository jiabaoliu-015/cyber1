import os
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def create_ftp_server():
    authorizer = DummyAuthorizer()
    share_dir = Path(__file__).resolve().parent / "ftp_share"
    authorizer.add_anonymous(str(share_dir), perm="elr")

    class ChallengeFTPHandler(FTPHandler):
        pass

    ChallengeFTPHandler.authorizer = authorizer
    ChallengeFTPHandler.banner = "Aerospace Research FTP Server"
    ChallengeFTPHandler.passive_ports = range(30000, 30010)
    # PASV clients need the Docker host address, not the container address.
    # EPSV clients use the address of their existing control connection.
    ChallengeFTPHandler.masquerade_address = os.environ.get("FTP_PUBLIC_HOST") or None

    return FTPServer(("0.0.0.0", 2121), ChallengeFTPHandler)


if __name__ == "__main__":
    server = create_ftp_server()
    try:
        server.serve_forever()
    finally:
        server.close_all()
