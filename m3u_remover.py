import requests
import os

TIMEOUT = 10


def test_link(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, stream=True)
        return 200 <= r.status_code < 400
    except:
        return False


def clean_m3u(file_path):
    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)

    output_file = f"{name}-temiz.m3u"

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

    print(f"Toplam kanal: {len(entries)}")

    cleaned = []
    seen_names = set()

    for info, url in entries:
        # Kanal adı EXTINF içinden çıkarılıyor
        # Ör: #EXTINF:-1 tvg-id="" group-title="TR",Kanal Adı
        name = info.split(",")[-1].strip().lower()

        if name in seen_names:
            print(f"🔁 Tekrarlayan kanal atlandı: {name}")
            continue

        print(f"⏳ Test ediliyor: {name}")

        if test_link(url):
            print(f"✔ Çalışıyor: {name}")
            cleaned.append((info, url))
            seen_names.add(name)
        else:
            print(f"❌ Çalışmıyor (silindi): {name}")

    # Sonuç dosyası yazma
    with open(output_file, "w", encoding="utf-8") as f:
        for info, url in cleaned:
            f.write(info + "\n")
            f.write(url + "\n")

    print(f"\n🎉 Temiz liste oluşturuldu → {output_file}")
    print(f"✔ Toplam çalışan ve tekrarsız kanal: {len(cleaned)}")


if __name__ == "__main__":
    file_name = input("Temizlenecek M3U dosyasının adını yazın: ")
    clean_m3u(file_name)
