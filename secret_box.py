#!/usr/bin/env python3
import argparse
import getpass
import os
from pathlib import Path
from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key(password: str, salt: bytes) -> bytes:
    # Derive a 32-byte (256-bit) key using Argon2id
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=65536,  # 64 MB RAM cost
        parallelism=2,
        hash_len=32,
        type=Type.ID,
    )

def lock_file(filepath: Path):
    if not filepath.exists():
        print(f"Error: {filepath} not found.")
        return
    password = getpass.getpass("Create vault password: ")
    confirm = getpass.getpass("Confirm vault password: ")
    if password != confirm or not password:
        print("Passwords did not match or were empty.")
        return

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    plaintext = filepath.read_bytes()

    ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)
    out_path = filepath.with_suffix(filepath.suffix + ".vault")
    out_path.write_bytes(salt + nonce + ciphertext)
    print(f"Encrypted -> {out_path} (Salt + Nonce + AES-256-GCM)")

def unlock_file(vaultpath: Path):
    if not vaultpath.exists():
        print(f"Error: {vaultpath} not found.")
        return
    password = getpass.getpass("Enter vault password: ")
    raw = vaultpath.read_bytes()

    salt, nonce, ciphertext = raw[:16], raw[16:28], raw[28:]
    key = derive_key(password, salt)

    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        print("\n=== Decrypted Vault Contents ===")
        print(plaintext.decode("utf-8"))
    except Exception:
        print("ACCESS DENIED: Wrong password or tampered vault file!")

def main():
    parser = argparse.ArgumentParser(description="Argon2id + AES-256-GCM Local Vault")
    parser.add_argument("action", choices=["lock", "unlock"], help="'lock' encrypts a file; 'unlock' decrypts it")
    parser.add_argument("file", help="Target file path")
    args = parser.parse_args()

    target = Path(args.file)
    if args.action == "lock":
        lock_file(target)
    else:
        unlock_file(target)

if __name__ == "__main__":
    main()

