# Jobdesk Rail Fence: tahap terakhir product cipher Hill -> Vigenere -> Rail Fence (k=5).
# Input berupa output Vigenere (sudah A-Z). Rail Fence adalah transposisi murni: huruf tidak
# diganti, hanya dipindah posisinya, jadi panjang output SELALU sama dengan panjang input
# (tanpa padding, sehingga originalPlaintextLength dari Hill tetap berlaku apa adanya).
# Kontrak: rail_fence_encrypt(plaintext, rails=5) -> {success, error, ..., ciphertext},
#          rail_fence_decrypt(ciphertext, rails=5) -> {success, error, ..., plaintext}.
# Acuan: RJIZWSJX + k=5 -> RJXIJZSW. Pure Python, tanpa import agar standalone.
#
# Konvensi data visualisasi (untuk tim GUI):
#   - "index" / "positions" memakai indeks posisi 0-based pada teks (sama seperti Vigenere).
#   - "rail" memakai nomor 1-based (Rail 1 = paling atas) agar sama dengan tampilan PRD.
#   - "grid" adalah list sepanjang `rails` baris; grid[0] = Rail 1. Setiap baris sepanjang
#     teks, berisi huruf pada posisi zig-zag dan None pada sel kosong.

# PRD: jumlah rail tetap 5 dan tidak boleh diubah user. Parameter `rails` pada fungsi hanya
# ada supaya test bisa memakai k lain; pipeline dan GUI harus selalu memakai RAIL_COUNT.
RAIL_COUNT = 5


def normalize_plaintext(text):
    # Samakan dengan Hill/Vigenere: buang spasi/simbol, sisakan A-Z kapital saja.
    # len(u) == 1 mencegah huruf seperti 'ß' (upper() -> 'SS') lolos sebagai dua karakter.
    hasil = ""
    for ch in text:
        u = ch.upper()
        if len(u) == 1 and 'A' <= u <= 'Z':
            hasil += u
    return hasil


def validate_rails(rails):
    # Jumlah rail harus bilangan bulat >= 2. Dengan 1 rail tidak ada zig-zag sama sekali.
    # type(...) is int dipakai (bukan isinstance) karena True/False adalah subclass int.
    if type(rails) is not int:
        return {"valid": False, "error": "Jumlah rail harus berupa bilangan bulat."}
    if rails < 2:
        return {"valid": False, "error": "Jumlah rail minimal 2 agar terbentuk pola zig-zag."}
    return {"valid": True, "error": None}


def build_rail_pattern(length, rails):
    # Menghitung rail (0-based) untuk setiap posisi huruf, mengikuti gerak zig-zag:
    # 0,1,2,...,rails-1,rails-2,...,1,0,1,... dan seterusnya.
    # Pola dihitung dari indeks saja (bukan dari grid yang diisi), jadi tetap benar
    # untuk teks yang lebih pendek dari jumlah rail, misalnya 1-4 huruf pada k=5.
    pattern = []
    rail = 0
    direction = 1
    for _ in range(length):
        pattern.append(rail)
        # Balik arah saat menyentuh rail paling atas atau paling bawah
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return pattern


def group_positions_by_rail(pattern, rails):
    # Mengelompokkan posisi teks per rail, urut dari kiri ke kanan.
    # Membaca rail 1 sampai rail terakhir berurutan = urutan ciphertext.
    per_rail = [[] for _ in range(rails)]
    for pos in range(len(pattern)):
        per_rail[pattern[pos]].append(pos)
    return per_rail


def build_grid(chars, pattern, rails):
    # Grid rails x panjang teks; hanya sel zig-zag yang terisi, sisanya None.
    length = len(chars)
    grid = [[None] * length for _ in range(rails)]
    for pos in range(length):
        grid[pattern[pos]][pos] = chars[pos]
    return grid


def build_steps(chars, pattern):
    # Satu entri per huruf, tinggal di-loop tim GUI untuk menampilkan posisi dan rail-nya.
    steps = []
    for i in range(len(chars)):
        steps.append({"index": i, "char": chars[i], "rail": pattern[i] + 1})
    return steps


def build_rail_rows(texts_per_rail, per_rail):
    # Ringkasan per rail: nomor rail, posisi huruf pada teks, dan potongan teks pada rail itu.
    rows = []
    for r in range(len(per_rail)):
        rows.append({"rail": r + 1, "positions": per_rail[r], "text": texts_per_rail[r]})
    return rows


def format_rail_grid(grid):
    # Teks multi-baris untuk visualisasi zig-zag; sel kosong ditulis '.'
    lines = []
    for r in range(len(grid)):
        cells = [ch if ch is not None else "." for ch in grid[r]]
        lines.append("Rail {}  {}".format(r + 1, " ".join(cells)))
    return "\n".join(lines)


def rail_fence_encrypt(plaintext, rails=RAIL_COUNT):
    """
    Enkripsi Rail Fence:
      1. Normalisasi input (A-Z kapital saja)
      2. Tulis huruf secara zig-zag pada `rails` baris
      3. Baca baris demi baris (rail 1 dulu, lalu rail 2, dst.) -> ciphertext
    Contoh k=5: RJIZWSJX -> RJXIJZSW
    """
    cek_rail = validate_rails(rails)
    if not cek_rail["valid"]:
        return {"success": False, "error": cek_rail["error"]}
    if not isinstance(plaintext, str) or len(plaintext.strip()) == 0:
        return {"success": False, "error": "Plaintext tidak boleh kosong."}
    normal = normalize_plaintext(plaintext)
    if len(normal) == 0:
        return {"success": False, "error": "Plaintext tidak mengandung huruf A-Z yang valid."}

    pattern = build_rail_pattern(len(normal), rails)
    per_rail = group_positions_by_rail(pattern, rails)

    # Teks pada tiap rail = huruf pada posisi-posisi rail tersebut, urut kiri ke kanan
    texts_per_rail = []
    for positions in per_rail:
        texts_per_rail.append("".join(normal[p] for p in positions))
    ciphertext = "".join(texts_per_rail)

    return {
        "success": True, "error": None,
        "normalized_input": normal,
        "rails": rails,
        "grid": build_grid(normal, pattern, rails),
        "rail_rows": build_rail_rows(texts_per_rail, per_rail),
        "steps": build_steps(normal, pattern),
        "ciphertext": ciphertext
    }


def rail_fence_decrypt(ciphertext, rails=RAIL_COUNT):
    """
    Dekripsi Rail Fence (kebalikan enkripsi):
      1. Normalisasi input
      2. Hitung pola zig-zag dari panjang teks, lalu tentukan berapa huruf tiap rail
      3. Potong ciphertext berurutan sesuai jumlah huruf tiap rail
      4. Kembalikan setiap potongan ke posisi zig-zag aslinya, baca dari kiri ke kanan
    """
    cek_rail = validate_rails(rails)
    if not cek_rail["valid"]:
        return {"success": False, "error": cek_rail["error"]}
    if not isinstance(ciphertext, str) or len(ciphertext.strip()) == 0:
        return {"success": False, "error": "Ciphertext tidak boleh kosong."}
    normal = normalize_plaintext(ciphertext)
    if len(normal) == 0:
        return {"success": False, "error": "Ciphertext tidak mengandung huruf A-Z yang valid."}

    pattern = build_rail_pattern(len(normal), rails)
    per_rail = group_positions_by_rail(pattern, rails)

    # Isi tiap posisi dari potongan ciphertext milik rail-nya
    hasil = [None] * len(normal)
    texts_per_rail = []
    cursor = 0
    for positions in per_rail:
        potongan = normal[cursor:cursor + len(positions)]
        texts_per_rail.append(potongan)
        for j in range(len(positions)):
            hasil[positions[j]] = potongan[j]
        cursor += len(positions)
    plaintext = "".join(hasil)

    return {
        "success": True, "error": None,
        "normalized_input": normal,
        "rails": rails,
        "grid": build_grid(hasil, pattern, rails),
        "rail_rows": build_rail_rows(texts_per_rail, per_rail),
        "steps": build_steps(hasil, pattern),
        "plaintext": plaintext
    }

# Integrasi: vigenere_cipher.vigenere_encrypt(...)["ciphertext"] -> rail_fence_encrypt(...)["ciphertext"] (k=5).
# Dekripsi: rail_fence_decrypt(final_ciphertext)["plaintext"] -> vigenere_decrypt -> hill_decrypt.
# Panjang tidak berubah, jadi originalPlaintextLength milik Hill diteruskan apa adanya.