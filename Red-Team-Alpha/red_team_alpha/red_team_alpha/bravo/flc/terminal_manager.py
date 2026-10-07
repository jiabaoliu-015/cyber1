import pexpect

PROMPT = r"www-data@delta4:.*[#$] "

class TerminalManager:

    def __init__(self):
        self.shells = {}

    def shell(self, session_id):
        if session_id not in self.shells:
            s = pexpect.spawn(
                "/bin/bash --norc --noprofile",
                cwd="/opt/flc",
                env={
                    "HOME": "/opt/flc",
                    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"
                },
                encoding="utf-8",
                codec_errors="replace",
                echo=False,
                timeout=15
            )

            s.sendline("export PS1='www-data@delta4:\\w\\$ '")
            s.expect(PROMPT)

            self.shells[session_id] = s

        return self.shells[session_id]

    def execute(self, session_id, command):
        s = self.shell(session_id)

        s.sendline(command)
        s.expect(PROMPT)

        output = s.before

        if output.startswith(command + "\r\n"):
            output = output[len(command) + 2:]

        return output.rstrip()

terminal = TerminalManager()