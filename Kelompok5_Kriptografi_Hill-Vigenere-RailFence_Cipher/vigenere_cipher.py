# Jobdesk Vigenere: tahap tengah product cipher Hill -> Vigenere -> Rail Fence (k=5).
# Input berupa output Hill (sudah A-Z), key huruf A-Z diulang periodik, output sama panjang tanpa padding.
# Kontrak: vigenere_encrypt(plaintext, key) -> {success, ciphertext, repeated_key, steps},
# vigenere_decrypt(ciphertext, key) -> {success, plaintext, repeated_key, steps}.
# Acuan PRD: THISPLAINTEXT + SONY -> LVVQHZNGFHRVL. Pure Python, tanpa import agar standalone.

def positive_mod(a, m):
    return ((a % m) + m) % m

def char_to_num(c):
    return ord(c) - ord('A')

def num_to_char(n):
    return chr(positive_mod(n, 26) + ord('A'))

def normalize_plaintext(text):
    # Samakan dengan Hill: buang spasi/simbol, sisakan A-Z kapital saja
    hasil = ""
    for ch in text:
        u = ch.upper()
        if 'A' <= u <= 'Z':
            hasil += u
    return hasil

def validate_vigenere_key(key):
    # Key wajib huruf A-Z saja, karena dipakai sebagai geseran 0-25
    if key is None or len(key.strip()) == 0:
        return {"valid": False, "normalized_key": None, "error": "Vigenere key tidak boleh kosong."}
    bersih = normalize_plaintext(key)
    if len(bersih) == 0 or len(bersih) != len(key.strip()):
        return {"valid": False, "normalized_key": None, "error": "Vigenere key harus berupa huruf A-Z tanpa angka, spasi, atau simbol."}
    return {"valid": True, "normalized_key": bersih, "error": None}

def repeat_vigenere_key(normalized_key, length):
    # Ulangi key secara periodik sampai sepanjang teks, potong sisanya
    ulang = ""
    for i in range(length):
        ulang += normalized_key[i % len(normalized_key)]
    return ulang

def vigenere_encrypt(plaintext, key):
    if not plaintext or len(plaintext.strip()) == 0:
        return {"success": False, "error": "Plaintext tidak boleh kosong."}
    cek = validate_vigenere_key(key)
    if not cek["valid"]:
        return {"success": False, "error": cek["error"]}
    normal = normalize_plaintext(plaintext)
    if len(normal) == 0:
        return {"success": False, "error": "Plaintext tidak mengandung huruf A-Z yang valid."}
    kunci_bersih = cek["normalized_key"]
    kunci_ulang = repeat_vigenere_key(kunci_bersih, len(normal))
    steps = []
    out = ""
    for i in range(len(normal)):
        p = char_to_num(normal[i])
        k = char_to_num(kunci_ulang[i])
        c = positive_mod(p + k, 26)
        rc = num_to_char(c)
        out += rc
        # Satu entri per huruf, tinggal di-loop tim GUI untuk tampilkan Z+S=R
        steps.append({
            "index": i,
            "plain_char": normal[i], "plain_num": p,
            "key_char": kunci_ulang[i], "key_num": k,
            "calc": p + k, "result_num": c, "result_char": rc
        })
    return {
        "success": True, "error": None,
        "normalized_input": normal,
        "key": kunci_bersih, "repeated_key": kunci_ulang,
        "steps": steps, "ciphertext": out
    }

def vigenere_decrypt(ciphertext, key):
    if not ciphertext or len(ciphertext.strip()) == 0:
        return {"success": False, "error": "Ciphertext tidak boleh kosong."}
    cek = validate_vigenere_key(key)
    if not cek["valid"]:
        return {"success": False, "error": cek["error"]}
    normal = normalize_plaintext(ciphertext)
    if len(normal) == 0:
        return {"success": False, "error": "Ciphertext tidak mengandung huruf A-Z yang valid."}
    kunci_bersih = cek["normalized_key"]
    kunci_ulang = repeat_vigenere_key(kunci_bersih, len(normal))
    steps = []
    out = ""
    for i in range(len(normal)):
        c = char_to_num(normal[i])
        k = char_to_num(kunci_ulang[i])
        # Python % sudah positif, positive_mod dipakai agar aman saat nanti port ke JS
        p = positive_mod(c - k, 26)
        rp = num_to_char(p)
        out += rp
        steps.append({
            "index": i,
            "cipher_char": normal[i], "cipher_num": c,
            "key_char": kunci_ulang[i], "key_num": k,
            "calc": c - k, "result_num": p, "result_char": rp
        })
    return {
        "success": True, "error": None,
        "normalized_input": normal,
        "key": kunci_bersih, "repeated_key": kunci_ulang,
        "steps": steps, "plaintext": out
    }
    
# Integrasi: hill_cipher.hill_encrypt(teks, matriks)["ciphertext"] -> vigenere_encrypt(...)["ciphertext"] -> rail_fence_encrypt(..., k=5).
# Metadata originalPlaintextLength milik Hill, Vigenere tidak menambah/mengurangi panjang jadi teruskan apa adanya.