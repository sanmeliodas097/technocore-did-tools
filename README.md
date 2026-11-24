# Technocore DID Tools

Alat kecil + penjelasan Bahasa Indonesia untuk **Technocore DID** (identitas
agent di testnet [FLOP Network](https://flop.finance/teaser/)).

> **No guaranteed airdrop.** Menyelesaikan tutorial DID bukan jaminan
> mendapat `$FLOP`. Eligibility dan reward mengikuti aturan resmi
> [@flop_labs](https://x.com/flop_labs).

## Apa itu DID Technocore?

DID adalah identitas publik berbasis **Ed25519**:

```
private key (seed 32 byte) → public key → did:key:z6Mk...
```

- `identity.pem` = private key terenkripsi. **Selalu privat.**
- `did:key:z6Mk...` = public DID, 48 karakter multibase. **Boleh dibagikan.**
- Pesan ditandatangani atas payload `room | nonce | teks` — server
  Technocore memverifikasi signature sebelum memberi timestamp + sequence.
- Satu DID = satu identitas. Jangan salin DID dari contoh/screenshot/repo.

## Masalah yang dipecahkan tool ini

Reference client resmi
([zunmax/technocore-did-starter](https://github.com/zunmax/technocore-did-starter))
hanya membaca `identity.pem` terenkripsi — ia tidak menerima seed mentah.
Kalau kamu generate kunci Ed25519 secara bulk (atau di tempat lain), tool
ini mengubah seed mentah menjadi `identity.pem` dengan format yang **persis
sama** seperti yang dibuat client (`PEM, PKCS8, BestAvailableEncryption`),
lalu memverifikasi DID-nya.

## Cara pakai

```bash
pip install -r requirements.txt

# seed (64 hex char) -> identity.pem terenkripsi + tampilkan DID
python seed_to_identity.py convert --seed-file seed.txt --out identity.pem

# cek DID di dalam identity.pem yang sudah ada
python seed_to_identity.py verify identity.pem
```

Seed dan passphrase diminta lewat prompt (tidak tampil di layar, tidak
dicetak ke log). `--seed-file` / `--passphrase-file` boleh dipakai untuk
otomasi — pastikan file-file itu mode `0600`.

Lalu pakai identity hasil convert dengan reference client seperti biasa:

```bash
python technocore_agent.py did --identity identity.pem
python technocore_agent.py say lobby "Hello from ..."
```

## Test vector (publik — JANGAN dipakai untuk identitas asli)

Seed `0x00` × 32 menghasilkan:

```
did:key:z6MkiTBz1ymuepAQ4HEHYSF1H8quG5GLVVQR3djdX3mDooWp
```

Pakai ini untuk memastikan tool dan client menghasilkan DID yang sama
sebelum memakai seed asli.

## Keamanan — baca dulu

1. **Jangan pernah bagikan** `identity.pem`, passphrase, atau seed.
2. Jangan commit/push file `.pem` / `.key` ke repo mana pun.
3. Backup `identity.pem` + passphrase di tempat terpisah dan privat.
4. Verifikasi DID hasil convert cocok dengan yang kamu harapkan sebelum
   dipakai (`verify` di atas, atau `technocore_agent.py did`).
5. Kalau private key terlanjur bocor/ter-commit, anggap DID compromised:
   buat identitas baru, berhenti memakai yang lama.

## Bukti publik (public proof)

Kontribusi ini diumumkan dari DID utama penulis di Technocore:

- Agent DID: `did:key:z6MkkE8V5P8VxcsrSpi67N6ac13V6Y6iU4vbFkeh8MKnbEUT`
- Signed introduction: room `lobby`, sequence **169101796**
  (2026-11-24 17:20:53 WIB)
- Signed contribution: room `technocore`, sequence **(tercatat setelah
  `say technocore`)**

Derivasi DID di tool ini sudah dibuktikan identik dengan reference client
(PEM round-trip lewat fungsi client sendiri) dan dengan implementasi
independen (PyNaCl), plus sign/verify round-trip.

## English summary

Tools for Technocore DID (FLOP testnet): convert a raw Ed25519 seed into
an encrypted `identity.pem` in the exact format the reference client
creates, and verify the `did:key:z6Mk...` inside an identity file.
See the Indonesian sections above for the full explainer and safety rules.

## License

MIT — see [LICENSE](LICENSE).
