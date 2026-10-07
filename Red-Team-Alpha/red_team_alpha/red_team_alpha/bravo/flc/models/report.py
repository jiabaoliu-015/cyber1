import subprocess

class ReportExporter:
    """
    Low-level logistics report executor.
    """

    def __init__(self, report_name="default"):
        self.report_name = report_name

    def execute(self):

        cmd = f"/opt/flc/tools/generate_report.sh {self.report_name}"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=5
        )

        return result.stdout + result.stderr

class ReportJob:
    """
    Background report task.
    """

    def __init__(self, exporter):
        self.exporter = exporter

    def run(self):
        return self.exporter.execute()