#!/usr/bin/env python3
"""Convert a raw Ed25519 seed into a Technocore-compatible encrypted identity.

The Technocore reference client (zunmax/technocore-did-starter) reads an
encrypted identity.pem — it does NOT accept a raw seed. This tool bridges
that gap for people who generated their Ed25519 keys in bulk (or elsewhere):

    python seed_to_identity.py --seed-file seed.txt --out identity.pem

- Reads the 32-byte seed as 64 hex chars (with or without 0x) from a file
  (--seed-file) or interactively (getpass, never echoed, never logged).
- Writes identity.pem in the EXACT format the reference client creates:
  PEM, PKCS8, BestAvailableEncryption(passphrase). File mode 0600.
- Prints the public DID (did:key:z6Mk...) and verifies it.

Verify an existing identity.pem instead:

    python seed_to_identity.py --verify identity.pem

The passphrase is asked interactively (getpass) unless --passphrase-file
points at a 0600 file containing it. The seed and passphrase are NEVER
printed or written anywhere except the identity.pem you asked for.

Test vector (public, all-zero seed — safe to share, do NOT use it for real):
    seed 0x00 * 32  ->  did:key:z6MkiTBz1ymuepAQ4HEHYSF1H8quG5GLVVQR3djdX3mDooWp
"""
import argparse
import getpass
import os
import sys

import base58
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def did_from_private_key(private_key: Ed25519PrivateKey) -> str:
    """Mirror technocore_agent.py: did:key:z + base58btc(0xed 0x01 || pubkey)."""
    pub = private_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    did = "did:key:z" + base58.b58encode(b"\xed\x01" + pub).decode("ascii")
    if len(did) != len("did:key:") + 48 or not did.startswith("did:key:z6Mk"):
        raise ValueError(f"generated an invalid Ed25519 did:key: {did}")
    return did


def read_seed(args) -> bytes:
    if args.seed_file:
        raw = open(args.seed_file).read().strip()
    else:
        raw = getpass.getpass("Ed25519 seed (64 hex chars): ").strip()
    raw = raw[2:] if raw.startswith(("0x", "0X")) else raw
    try:
        seed = bytes.fromhex(raw)
    except ValueError:
        raise SystemExit("seed must be 64 hex characters (32 bytes)")
    if len(seed) != 32:
        raise SystemExit("seed must be exactly 32 bytes")
    return seed


def read_passphrase(args, *, confirm: bool) -> bytes:
    if args.passphrase_file:
        pw = open(args.passphrase_file, "rb").read().strip()
    else:
        pw = getpass.getpass("Passphrase for identity.pem (min 12 chars): ").encode()
        if confirm:
            pw2 = getpass.getpass("Repeat passphrase: ").encode()
            if pw != pw2:
                raise SystemExit("passphrases do not match")
    if len(pw) < 12:
        raise SystemExit("passphrase must be at least 12 characters")
    return pw


def cmd_convert(args) -> int:
    seed = read_seed(args)
    passphrase = read_passphrase(args, confirm=True)
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(passphrase),
    )
    if os.path.exists(args.out):
        raise SystemExit(f"refusing to overwrite existing file: {args.out}")
    fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(pem)
    print(f"wrote {args.out} (0600)")
    print(f"DID: {did_from_private_key(priv)}")
    return 0


def cmd_verify(args) -> int:
    passphrase = read_passphrase(args, confirm=False)
    data = open(args.identity, "rb").read()
    priv = serialization.load_pem_private_key(data, password=passphrase)
    if not isinstance(priv, Ed25519PrivateKey):
        raise SystemExit("identity.pem does not contain an Ed25519 private key")
    print(f"DID: {did_from_private_key(priv)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("convert", help="seed -> encrypted identity.pem")
    c.add_argument("--seed-file", help="file with 64 hex chars (else prompt)")
    c.add_argument("--out", default="identity.pem")
    c.add_argument("--passphrase-file", help="file with the passphrase (else prompt)")
    c.set_defaults(fn=cmd_convert)
    v = sub.add_parser("verify", help="print the DID inside an identity.pem")
    v.add_argument("identity")
    v.add_argument("--passphrase-file", help="file with the passphrase (else prompt)")
    v.set_defaults(fn=cmd_verify)
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
