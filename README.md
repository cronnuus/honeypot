# SSH and Web Honeypot

## Purpose
The purpose of this project is to provide a safe and controlled way to observe how attackers behave when targeting common services. By running these honeypots, researchers and students can learn about brute force attempts, malicious traffic patterns, and the types of commands or exploits attackers try to use. This project is designed as a learning tool to improve cybersecurity awareness, practice log analysis, and better understand real-world attack techniques without putting production systems at risk.

---

## Description
This project includes two honeypots:
- **SSH Honeypot** – Built with Python and Paramiko, it acts like an SSH server and logs attacker credentials and commands.
- **Web Honeypot** – Simulates a vulnerable WordPress site to capture malicious login attempts and traffic.

---

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/honeypot.git
   
2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   
4. **Run a honeypot:**
   ```bash
   python ssh_honeypot.py
   ```
   
   or
   
   ```
   python web_honeypot.py

## Logs

* SSH logs are saved in
  ```bash
  ssh_logs/

* Web logs are saved in
  ```bash
  web_logs/

## Disclaimer
This project is for **educational purposes only**.
