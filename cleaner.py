import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

TIMEOUT = 10
LOG_FILE = "m3u_tester.log"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def log_write(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def test_link(url):
    start = time.time()
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)
        elapsed = round(time.time() - start, 2)

        if 200 <= r.status_code < 400:
            msg = f"[OK] {url} ({elapsed}s)"
            print(GREEN + msg + RESET)
            log_write(msg)
            return True
        else:
            msg = f"[FAIL] {url} → HTTP {r.status_code} ({elapsed}s)"
            print(RED + msg + RESET)
            log_write(msg)
            return False

    except Exception as e:
        elapsed = round(time.time() - start, 2)
        msg = f"[ERROR] {url} ({elapsed}s) → {str(e)}"
        print(RED + msg + RESET)
        log_write(msg)
        return False


def process_m3u(file_path):
    print(CYAN + f"\n📺 Dosya işleniyor: {file_path}" + RESET)
    log_write(f"\n=== Processing file: {file_path} ===")

    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)

    working_file = f"{name}-calisan.m3u"
    broken_file = f"{name}-bozuk.m3u"

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    entries = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            if i + 1 < len(lines):
                info = lines[i].strip()
                url = lines[i + 1].strip()
                entries.append((info, url))
                i += 2
                continue
        i += 1

    total = len(entries)
    print(f"📦 Toplam kanal: {total}")
    log_write(f"Total channels: {total}")

    start_time = time.time()
    working = []
    broken = []

    with ThreadPoolExecutor(max_workers=15) as ex:
        results = list(ex.map(lambda e: test_link(e[1]), entries))

    for (info, url), status in zip(entries, results):
        if status:
            working.append((info, url))
        else:
            broken.append((info, url))

    # Output writer
    def write_list(filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            for info, url in data:
                f.write(info + "\n")
                f.write(url + "\n")

    write_list(working_file, working)
    write_list(broken_file, broken)

    elapsed_total = round(time.time() - start_time, 2)
    print(f"\n{GREEN}✔ Çalışan kanal sayısı: {len(working)} → {working_file}{RESET}")
    print(f"{RED}✖ Çalışmayan kanal sayısı: {len(broken)} → {broken_file}{RESET}")
    print(f"{YELLOW}⏱ Toplam süre: {elapsed_total} saniye{RESET}")

    log_write(f"Working channels: {len(working)}")
    log_write(f"Broken channels: {len(broken)}")
    log_write(f"Completed in {elapsed_total}s\n")


def main():
    print(CYAN + "📁 Klasör taranıyor..." + RESET)
    log_write("\n===== M3U TEST AI Script Start: " +
              datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " =====")

    cwd = os.getcwd()
    for file in os.listdir(cwd):
        if file.endswith(".m3u"):
            process_m3u(os.path.join(cwd, file))

    print(GREEN + "\n🏁 Tüm işlemler tamamlandı!" + RESET)
    print(f"📄 Log dosyası: {LOG_FILE}")


if __name__ == "__main__":
    main()
