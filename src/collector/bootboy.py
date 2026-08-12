#
# Title: bootboy.py
# Description: generate configuration file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import json
import importlib
import os
import platform
import socket
import subprocess
import sys
import time
from typing import Sequence

yaml = None
if importlib.util.find_spec("yaml") is not None:
    yaml = importlib.import_module("yaml")


class BootBoy:

    def run_command(self, cmd: Sequence[str]) -> tuple[int, str, str]:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

    def can_manage_systemd(self, service_name: str) -> bool:
        if platform.system() != "Linux":
            print(f"{service_name} management skipped on non-Linux host.")
            return False

        if os.geteuid() != 0:
            print(f"{service_name} management skipped: must run as root (systemd boot path).")
            return False

        return True

    def run_systemctl(self, action: str, service_name: str) -> tuple[int, str]:
        # Use --no-block for start so systemd queues the job and returns
        # immediately, preventing a deadlock when bootboy itself runs under systemd.
        cmd = ["systemctl", "--no-block", action, service_name] if action == "start" else ["systemctl", action, service_name]
        returncode, _, stderr = self.run_command(cmd)
        return returncode, stderr

    def report_service_failure(self, service_name: str) -> None:
        print(f"{service_name} failed to reach active state.")

        commands = [
            ("systemctl status", ["systemctl", "status", "--no-pager", "--full", service_name]),
            ("recent journal", ["journalctl", "-u", service_name, "-n", "20", "--no-pager"]),
        ]

        for label, cmd in commands:
            returncode, stdout, stderr = self.run_command(cmd)
            details = stdout or stderr
            if returncode == 0 and details:
                print(f"--- {label}: {service_name} ---")
                print(details)
            elif details:
                print(f"--- {label} unavailable for {service_name} ---")
                print(details)

    def verify_service_active(self, service_name: str) -> None:
        # --no-block returns immediately; give systemd a moment to actually
        # start (or fail to start) the service before checking.
        time.sleep(2)
        returncode, _ = self.run_systemctl("is-active", service_name)
        if returncode == 0:
            print(f"{service_name} is active.")
        else:
            self.report_service_failure(service_name)

    def configuration(self, target: str) -> str:
        print(f"BootBoy: configuring {target}")

        if yaml is None:
            print("PyYAML is required to generate config.yaml.")
            sys.exit(1)

        # Build the path to the admin JSON file
        admin_json_path = f"/var/wombat/admin/{target}.json"

        try:
            with open(admin_json_path, "r") as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error reading {admin_json_path}: {e}")
            sys.exit(1)

        # Compose new config dict for YAML output
        receiver = config_data.get("receiver", {})
        geo_loc = config_data.get("geoLoc", {})
        crate_name = config_data.get("crateName", "xxx")
        host_name = config_data.get("hostName", target)
        host_type = config_data.get("type", "xxx")

        yaml_config = {
            "crateName": crate_name,
            "equipment": {
                "hostName": host_name,
                "hostType": host_type,
            },
            "receiver": {
                "antenna": receiver.get("antenna", "xxx"),
                "mode": "default",
                "receiverId": receiver.get("id", "xxx"),
                "task": receiver.get("task", "xxx"),
                "type": receiver.get("type", "xxx"),
            },
            "freshDir": "/var/wombat/fresh/capybara",
            "geoLoc": geo_loc,
        }

        # Write to config.yaml in the current directory
        try:
            with open("config.yaml", "w") as f:
                yaml.dump(yaml_config, f, default_flow_style=False)
            print("config.yaml generated successfully.")
        except Exception as e:
            print(f"Error writing config.yaml: {e}")
            sys.exit(1)

        return receiver.get("task", "xxx")

    def crontab(self) -> None:
        crontab_entry = "13 * * * * $HOME/github/mellow-capybara-v1/bin/collector.sh > /dev/null 2>&1"

        # Always overwrite — collector is dedicated to this workload and must have
        # exactly one cron entry.
        new_crontab = crontab_entry + "\n"
        try:
            proc = subprocess.run(["crontab", "-u", "wombat", "-"], input=new_crontab, text=True)
            if proc.returncode == 0:
                print("Crontab updated for capybara.")
            else:
                print("Failed to update capybara crontab.")
        except Exception as e:
            print(f"Error updating capybara crontab: {e}")

    def execute(self, target: str) -> None:
        task = self.configuration(target)

        self.crontab()

        service_name = "bogus"
        if task == "capybara-v1-dev1-fast":
            service_name = "vdl2-dev01.service"
        elif task == "capybara-v1-dev2-fast":
            service_name = "vdl2-dev02.service"
        elif task == "capybara-v1-dev3-fast":
            service_name = "vdl2-dev03.service"
        elif task == "capybara-v1-dev4-fast":
            service_name = "vdl2-dev04.service"
        else:
            print(f"BootBoy: unknown task {task} for {target}")

        if not self.can_manage_systemd(service_name):
            return

        returncode, stderr = self.run_systemctl("start", service_name)
        if returncode == 0:
            print(f"{service_name} start queued")
            self.verify_service_active(service_name)
        else:
            print(f"Failed to start {service_name}: {stderr}")

#
#
#
if __name__ == "__main__":
    target = socket.gethostname()
    # target = "pi4k"

    bb = BootBoy()
    bb.execute(target)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
