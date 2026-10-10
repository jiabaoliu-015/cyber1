# Vulnerability List — CTF Project Reference

> **Source**: `vulnerabilities checklist draft.txt` (project root)
> **Status**: Converted to markdown checklist for easy reference
> **Note**: Original txt file remains unmodified.

---

## 📋 Vulnerability Categories

### 🔹 3 Network-Based Vulnerabilities

- [ ] **Telnet** — Plaintext protocol exposing credentials/data in transit
- [ ] **SSH Default Keys (MITM)** — Man-in-the-middle interception using default/known keys
- [ ] **ARP Spoofing** — ARP injection attacking network layer communications
- [ ] **Replay Attack** — Valid data injection or replay to trigger unintended actions

---

### 🔹 3 Types of Web-Based Vulnerabilities (SQLi, XSS, etc.)

- [ ] **Cookie Authentication** — Weak/missing cookie-based auth mechanisms
- [ ] **Path Traversal** — Accessing files/directories beyond intended paths (../ sequences)
- [ ] **XSS (Cross-Site Scripting)** — Injecting malicious scripts into user sessions
- [ ] **CSRF (Cross-Site Request Forgery)** — Forcing authenticated users to perform unintended actions
- [ ] **SQL Injection** — Injecting SQL statements to manipulate databases
- [ ] **Insecure Direct Object Reference / Broken Access Control** — IDOR vulnerabilities allowing unauthorized data access
- [ ] **File Upload Vulnerability** — Unrestricted/unvalidated file uploads accepting malicious content

---

### 🔹 Horizontal Privilege Escalation (3 Vulnerabilities)

### Horizontal Escalation Patterns:
- [ ] **Broken Access Control** — Users gaining access to resources they shouldn't
- [ ] **Permission Issues** — Misconfigured or missing permissions in system hierarchy
- [ ] **Misconfiguration** — General system errors enabling privilege bypass
- [ ] **Predictable Session Tokens / Credentials** — Guessable session identifiers enabling injection
- [ ] **Insecure API Authorization** — API endpoints lacking proper access validation

---

### 🔹 Vertical Privilege Escalation (3 Vulnerabilities)

### Vertical Escalation Patterns:
- [ ] **SUID Misuse** — Special files or scripts run with elevated privileges unexpectedly
- [ ] **Sudo Misconfiguration** — Incorrect sudo rules granting excessive user permissions
- [ ] **Schedule Task Exploit** — Cron/systemd job vulnerabilities enabling elevated access
- [ ] **Reused Credentials** — Shared credentials across systems enabling lateral movement
- [ ] **PATH Hijacking** — Injecting into PATH to execute arbitrary binaries

---

### 🔹 Reverse Engineering-Related Vulnerabilities

- [ ] **(Hard) Obfuscated Binary** — Code complexity hiding vulnerabilities or attack vectors
- [ ] **(Easy) Objdump/String** — Exploiting embedded strings or disassembly clues
- [ ] **(Medium) Hidden Functionality** — Undocumented features triggered by hardcoded access or modifications

---

## 🚀 Advanced Challenges

- [ ] **Side Channel — Timing Attacks?** — Timing-based information leakage vulnerabilities
- [ ] **Crypto — Non Classical (Seeded)** — Weak or seeded cryptographic implementations
- [ ] **Kernel** — Deep system layer vulnerabilities affecting process/memory

---

## 🔄 Extra Vulnerabilities (for swapping/expansion as needed)

### New Category: **Crypto/Secrets**
- [ ] **Hardcoded Keys** — Secrets embedded in source code or configuration
- [ ] **Weak Hashes** — Cryptographic hashes vulnerable to brute-force or collisions
- [ ] **Predictable Randomness** — Generated values that can be anticipated or reproduced
- [ ] **Exposed .env / Backup Files** — Sensitive configuration files accidentally exposed

### Network Additions:
- [ ] DNS Spoofing — DNS cache poisoning attacking network resolution
- [ ] Cleartext FTP/HTTP Credentials — Passwords sent over unencrypted protocols
- [ ] SMB Misconfiguration — Server Management Service vulnerable settings
- [ ] Weak Segmentation — Network partitions insufficient to contain attacks

### Web Additions:
- [ ] CSRF (re-listed for completeness)
- [ ] Command Injection — Shell command execution from user input
- [ ] SSRF (Server-Side Request Forgiting) — Server making unintended requests
- [ ] Session Fixation — Attacking session IDs to force user actions
- [ ] Exposed Admin/Debug Endpoints — Unrestricted access to administrative functions

### Horizontal Additions:
- [ ] IDOR (re-listed for completeness)
- [ ] Insecure API Authorization (re-listed for completeness)
- [ ] Incorrect File/Resource Permissions — Access violations on file systems

### Vertical Additions:
- [ ] Linux Capabilities Misuse — Capabilities misused granting unintended privileges
- [ ] PATH Hijacking (re-listed for completeness)
- [ ] Writable Privileged Scripts — Scripts in restricted directories writable by unauthorized users
- [ ] Cron/systemd Misconfiguration (re-listed for completeness)

---

## 📝 Notes

- This checklist serves as a **reference and planning document** for the CTF project
- Check items can be **ticked off** as vulnerabilities are implemented or confirmed
- Feel free to **add or swap items** from the "extra vulnerabilities" section as needed
- The original `vulnerabilities checklist draft.txt` remains unchanged

---

*Last updated: Project setup — converted to markdown for readability*