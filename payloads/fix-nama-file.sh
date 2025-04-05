#!/bin/bash

echo "[*] Memulai proses normalisasi nama file & folder..."

find . -depth | while IFS= read -r f; do
  # Normalisasi nama: hapus kutip, ganti spasi dengan underscore
  new=$(echo "$f" | tr -d "'" | sed 's/ /_/g' | sed 's/_$//')

  if [[ "$f" != "$new" ]]; then
    echo "[+] Rename: '$f' -> '$new'"
    mv "$f" "$new"
  fi
done

echo "[✓] Selesai! Semua nama file/folder sudah dirapikan."
