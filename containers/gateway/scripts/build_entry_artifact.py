from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import hashlib

root = Path(__file__).resolve().parents[1]
entry = root / "entry"
entry.mkdir(exist_ok=True)
path = entry / "access_artifact.png"

img = Image.new("RGB", (1200, 700), "#172235")
d = ImageDraw.Draw(img)
# Coriolis orbital-station briefing image. Metadata remains the recovery clue.
d.ellipse((670, 165, 1060, 555), outline="#79c7dd", width=9)
d.ellipse((745, 240, 985, 480), fill="#365976", outline="#e9eef6", width=6)
d.rectangle((630, 338, 1100, 382), fill="#a7bbd2")
d.rectangle((870, 130, 900, 585), fill="#a7bbd2")
d.ellipse((798, 293, 932, 427), fill="#172235", outline="#79c7dd", width=7)
d.text((70, 70), "CORIOLIS // INCIDENT FILE", fill="#e9eef6")
d.text((70, 115), "Keep this file exactly as it is.", fill="#cbd5e1")
d.text((70, 155), "Copies have a habit of losing the details that matter.", fill="#cbd5e1")

meta = PngImagePlugin.PngInfo()
meta.add_text("maintenance_label", "CREW_PORTAL-RCV-01")
meta.add_text("maintenance_username", "maint-recovery")
meta.add_text("recovery_portal", "http://127.0.0.1:8080/")
meta.add_text("note", "The preserved original is the recovery proof.")
img.save(path, pnginfo=meta, optimize=False)

md5 = hashlib.md5(path.read_bytes()).hexdigest()
(entry / "ENTRY_MD5.txt").write_text(md5 + "\n")

email = """Subject: Coriolis incident archive — original attachment\nTime: 02:13\n\nCrew access brief:\n\nThe attached image is the original station incident file. Keep it exactly as received: copies can lose the details needed for recovery.\n\nThe maintenance label remains with the original file. Use the supplied station portal to inspect the crew records and reconstruct what happened.\n\nAttachment: access_artifact.png\n"""
(entry / "access_note.txt").write_text(email)
print(path)
print(md5)
