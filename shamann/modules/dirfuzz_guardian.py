import subprocess
from .base_guardian import BaseGuardian

import threading
import requests
from queue import Queue

class DirFuzzGuardian:
    @staticmethod
    def run_scan(target: str, options: str = "") -> dict:
        import argparse, shlex

        parser = argparse.ArgumentParser()
        parser.add_argument("-w", "--wordlist", required=True)
        parser.add_argument("-t", "--threads", type=int, default=10)
        args = parser.parse_args(shlex.split(options))

        q = Queue()
        results = []

        def worker():
            while not q.empty():
                word = q.get()
                url = f"{target.rstrip('/')}/{word}"
                try:
                    r = requests.get(url, timeout=5)
                    if r.status_code < 400:
                        results.append(f"{r.status_code} - {url}")
                except:
                    pass
                q.task_done()

        with open(args.wordlist, "r") as f:
            for line in f:
                word = line.strip()
                if word:
                    q.put(word)

        threads = []
        for _ in range(args.threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        q.join()

        return {
            "target": target,
            "status": "success",
            "found": results
        }
