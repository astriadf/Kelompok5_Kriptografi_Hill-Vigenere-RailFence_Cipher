# Utilitas alfabet

def char_to_num(char):
    # Huruf kapital ke angka 0-25, contoh 'A' -> 0
    return ord(char) - ord('A')


def num_to_char(num):
    # Angka 0-25 ke huruf kapital, selalu dimoduluskan agar tidak negatif
    return chr(positive_mod(num, 26) + ord('A'))


def normalize_plaintext(text):
    """
    Sisakan huruf A-Z kapital saja, contoh 'Aku pergi!' -> 'AKUPERGI'.
    """
    result = ""
    for char in text:
        upper_char = char.upper()
        if 'A' <= upper_char <= 'Z':
            result += upper_char
    return result


# Aritmetika modular

def positive_mod(a, m):
    # Sisa bagi yang selalu positif, contoh positive_mod(-123, 26) -> 7
    return ((a % m) + m) % m


def gcd(a, b):
    # Menghitung GCD dari dua bilangan menggunakan algoritma Euclidean.
    # Pastikan kedua nilai positif
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    # Gunakan algoritma Euclidean sampai sisa pembagian bernilai 0.
    while b != 0:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    # Menghitung invers modular dari a terhadap m
    # Mencari x sehingga (a * x) ≡ 1 (mod m).
    
    # Pastikan a berada dalam rentang 0 sampai m - 1 
    a = positive_mod(a, m)

    # Extended Euclidean Algorithm
    # Inisialisasi nilai untuk iterasi
    old_r, r = a, m
    old_s, s = 1, 0

    # Cari GCD sekaligus koefisien untuk mendapatkan invers
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s

    # Jika GCD bukan 1, a tidak punya invers modulo m
    if old_r != 1:
        return None

    # Ambil hasil akhirnya dalam rentang modulo m
    return positive_mod(old_s, m)


# Operasi matriks

def determinant_2x2(K):
    # Menghitung determinan matriks 2x2.
    # Rumus: det(K) = K[0][0]*K[1][1] - K[0][1]*K[1][0], yaitu: ad - bc

    return K[0][0] * K[1][1] - K[0][1] * K[1][0]


def determinant_3x3(K):
    """
    Menghitung determinan matriks 3x3 menggunakan ekspansi kofaktor sepanjang baris pertama (Laplace Expansion).
    Rumus:
      det = K[0][0] * (K[1][1]*K[2][2] - K[1][2]*K[2][1])
          - K[0][1] * (K[1][0]*K[2][2] - K[1][2]*K[2][0])
          + K[0][2] * (K[1][0]*K[2][1] - K[1][1]*K[2][0])
    Setiap suku adalah elemen baris pertama dikali determinan matriks minor 2x2 yang tersisa (dengan tanda +, -, +).
    """
    # Ekspansi kofaktor pada baris pertama
    term0 = K[0][0] * (K[1][1] * K[2][2] - K[1][2] * K[2][1])
    term1 = K[0][1] * (K[1][0] * K[2][2] - K[1][2] * K[2][0])
    term2 = K[0][2] * (K[1][0] * K[2][1] - K[1][1] * K[2][0])
    return term0 - term1 + term2


def determinant(K):
    # Pilih perhitungan determinan berdasarkan ukuran matriks
    size = len(K)
    if size == 2:
        return determinant_2x2(K)
    elif size == 3:
        return determinant_3x3(K)
    else:
        raise ValueError("Ukuran matriks tidak didukung. Gunakan 2x2 atau 3x3.")


def matrix_vector_multiply(K, vec):
    """
    Melakukan perkalian matriks m*m dengan vektor kolom m*1.
    Rumus: result[i] = sum(K[i][j] * vec[j] for j in range(m)) mod 26
    Ini adalah inti dari enkripsi/dekripsi Hill Cipher:
      Enkripsi: C = K * P mod 26
      Dekripsi: P = K_inv * C mod 26
    """
    size = len(K)
    result = []
    for i in range(size):
        total = 0
        for j in range(size):
            total += K[i][j] * vec[j]
        # Terapkan modulo 26 untuk menghasilkan indeks alfabet yang valid
        result.append(positive_mod(total, 26))
    return result


def inverse_matrix_2x2(K, det_inv_mod26):
    """
    Menghitung invers matriks 2x2 modulo 26.
    Langkah:
      1. Hitung adjugat: adj(K) = [[d, -b], [-c, a]]
      2. K^-1 = det_inv * adj(K) mod 26
    Contoh: K = [[3,10],[15,9]], det_inv = 15
      adj = [[9,-10],[-15,3]]
      K^-1 = 15 * [[9,-10],[-15,3]] mod 26 = [[5,6],[9,19]]
    """
    # Adjugat matriks 2x2
    adj = [
        [ K[1][1], -K[0][1]],
        [-K[1][0],  K[0][0]]
    ]
    # Kalikan setiap elemen adjugat dengan invers determinan, lalu mod 26
    size = 2
    result = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(positive_mod(det_inv_mod26 * adj[i][j], 26))
        result.append(row)
    return result


def cofactor_3x3(K, skip_row, skip_col):
    """
    Menghitung kofaktor elemen (skip_row, skip_col) dari matriks 3x3.
    Kofaktor C_ij = (-1)^(i+j) * det(minor_ij)
    di mana minor_ij adalah matriks 2x2 setelah menghapus baris i dan kolom j.
    """
    # Buat matriks minor (2x2) dengan menghapus baris skip_row dan kolom skip_col
    minor = []
    for r in range(3):
        if r == skip_row:
            continue
        row = []
        for c in range(3):
            if c == skip_col:
                continue
            row.append(K[r][c])
        minor.append(row)

    # Tanda kofaktor: (-1)^(i+j)
    sign = 1 if (skip_row + skip_col) % 2 == 0 else -1
    return sign * determinant_2x2(minor)


def inverse_matrix_3x3(K, det_inv_mod26):
    """
    Menghitung invers matriks 3x3 modulo 26.
    Langkah:
      1. Hitung matriks kofaktor (9 elemen)
      2. Transpose matriks kofaktor -> matriks adjugat
      3. K^-1 = det_inv * adj(K) mod 26
    """
    size = 3

    # Langkah 1: Hitung matriks kofaktor
    cofactor_matrix = []
    for r in range(size):
        row = []
        for c in range(size):
            row.append(cofactor_3x3(K, r, c))
        cofactor_matrix.append(row)

    # Langkah 2: Transpose matriks kofaktor untuk mendapatkan adjugat
    # Adjugat[i][j] = CofactorMatrix[j][i]
    adj = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(cofactor_matrix[j][i])
        adj.append(row)

    # Langkah 3: K^-1 = det_inv * adj mod 26
    result = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(positive_mod(det_inv_mod26 * adj[i][j], 26))
        result.append(row)
    return result


# Validasi matriks kunci

def validate_matrix(K):
    """
    Memvalidasi matriks kunci Hill Cipher.
    Syarat kevalidan: gcd(det(K) mod 26, 26) == 1
    (Matriks harus memiliki invers modulo 26)

    Mengembalikan dict dengan informasi lengkap:
    {
        "valid": bool,
        "det": int,               # determinan asli
        "det_mod26": int,         # determinan mod 26
        "gcd_result": int,        # gcd(det_mod26, 26)
        "det_inv_mod26": int|None, # invers modular determinan
        "inverse_matrix": list|None, # matriks invers mod 26
        "message": str            # pesan status
    }
    """
    # Hitung determinan matriks
    det = determinant(K)

    # Hitung determinan modulo 26 (harus positif)
    det_mod26 = positive_mod(det, 26)

    # Hitung GCD untuk cek kevalidan
    gcd_result = gcd(det_mod26, 26)

    if gcd_result != 1:
        # Matriks tidak valid — tidak memiliki invers modulo 26
        message = (
            "Matriks kunci tidak valid.\n\n"
            "det(K) = {det}\n"
            "det(K) mod 26 = {det_mod26}\n"
            "gcd({det_mod26}, 26) = {gcd_result}\n\n"
            "Matriks tidak memiliki inverse modulo 26.\n"
            "Silakan masukkan matriks kunci yang lain."
        ).format(det=det, det_mod26=det_mod26, gcd_result=gcd_result)

        return {
            "valid": False,
            "det": det,
            "det_mod26": det_mod26,
            "gcd_result": gcd_result,
            "det_inv_mod26": None,
            "inverse_matrix": None,
            "message": message
        }

    # Hitung invers modular determinan
    det_inv_mod26 = mod_inverse(det_mod26, 26)

    # Hitung invers matriks modulo 26 berdasarkan ukuran
    size = len(K)
    if size == 2:
        inv_matrix = inverse_matrix_2x2(K, det_inv_mod26)
    else:
        inv_matrix = inverse_matrix_3x3(K, det_inv_mod26)

    message = (
        "\u2713 Valid Hill Cipher Key\n\n"
        "det(K) = {det}\n"
        "det(K) mod 26 = {det_mod26}\n"
        "gcd({det_mod26}, 26) = 1"
    ).format(det=det, det_mod26=det_mod26)

    return {
        "valid": True,
        "det": det,
        "det_mod26": det_mod26,
        "gcd_result": gcd_result,
        "det_inv_mod26": det_inv_mod26,
        "inverse_matrix": inv_matrix,
        "message": message
    }


# Pembagian blok dan padding

def divide_into_blocks(text, block_size):
    """
    Membagi teks menjadi blok-blok sesuai ukuran matriks.
    Jika blok terakhir belum penuh, ditambahkan karakter padding 'X'
    sampai jumlah karakter dalam blok terakhir sama dengan block_size.

    Mengembalikan dict:
    {
        "padded_text": str,     # teks setelah padding
        "blocks": list,         # list string blok
        "padding_length": int   # jumlah karakter padding yang ditambahkan
    }
    """
    # Hitung berapa banyak padding yang diperlukan
    remainder = len(text) % block_size
    if remainder == 0:
        padding_length = 0
    else:
        padding_length = block_size - remainder

    # Tambahkan padding 'X'
    padded_text = text + 'X' * padding_length

    # Bagi teks menjadi blok-blok
    blocks = []
    i = 0
    while i < len(padded_text):
        blocks.append(padded_text[i:i + block_size])
        i += block_size

    return {
        "padded_text": padded_text,
        "blocks": blocks,
        "padding_length": padding_length
    }


# Enkripsi: C = K x P mod 26 per blok

def hill_encrypt(plaintext, key_matrix):
    """
    Melakukan enkripsi Hill Cipher.

    Proses:
      1. Normalisasi plaintext (huruf kapital, hapus non-alfabet)
      2. Simpan panjang asli (original_plaintext_length)
      3. Bagi menjadi blok sesuai ukuran matriks
      4. Tambahkan padding 'X' jika diperlukan
      5. Untuk setiap blok: C = K x P mod 26
      6. Gabungkan blok terenkripsi menjadi ciphertext

    Parameter:
      plaintext  (str)       : Teks asli (boleh mengandung spasi, tanda baca)
      key_matrix (list[list]): Matriks kunci 2x2 atau 3x3

    Mengembalikan dict dengan kunci:
      success                  (bool)
      error                    (str|None)
      normalized_plaintext     (str)
      original_plaintext_length(int)
      padded_plaintext         (str)
      padding_length           (int)
      matrix_size              (int)
      key_matrix               (list[list])
      determinant              (int)
      determinant_mod26        (int)
      gcd_result               (int)
      inverse_matrix           (list[list])
      blocks                   (list[str])
      encrypted_blocks         (list[str])
      ciphertext               (str)
    """
    # --- Validasi input plaintext ---
    if not plaintext or len(plaintext.strip()) == 0:
        return {"success": False, "error": "Plaintext tidak boleh kosong."}

    matrix_size = len(key_matrix)

    # --- Validasi format elemen matriks ---
    for i in range(matrix_size):
        for j in range(matrix_size):
            val = key_matrix[i][j]
            # Cek apakah nilai adalah integer atau float yang mewakili integer
            if not isinstance(val, (int, float)):
                return {
                    "success": False,
                    "error": "Setiap elemen matriks harus berupa angka."
                }
            # Pastikan tidak NaN atau Infinity (edge case float)
            # Implementasi manual karena tidak boleh menggunakan math.isnan
            if val != val:  # NaN check: NaN != NaN adalah True
                return {
                    "success": False,
                    "error": "Setiap elemen matriks harus berupa angka valid."
                }

    # --- Validasi matriks kunci ---
    validation = validate_matrix(key_matrix)
    if not validation["valid"]:
        return {"success": False, "error": validation["message"]}

    # --- Normalisasi plaintext ---
    normalized = normalize_plaintext(plaintext)
    if len(normalized) == 0:
        return {
            "success": False,
            "error": "Plaintext tidak mengandung karakter alfabet yang valid."
        }

    # Simpan panjang plaintext setelah normalisasi, SEBELUM padding.
    # Metadata ini penting untuk dekripsi yang benar (lihat Bagian 7).
    original_plaintext_length = len(normalized)

    # --- Bagi menjadi blok dan tambahkan padding jika perlu ---
    block_result = divide_into_blocks(normalized, matrix_size)
    padded_plaintext = block_result["padded_text"]
    blocks = block_result["blocks"]
    padding_length = block_result["padding_length"]

    # --- Enkripsi setiap blok ---
    encrypted_blocks = []
    for block in blocks:
        # Konversi blok huruf ke vektor numerik (A=0, ..., Z=25)
        plain_vec = [char_to_num(c) for c in block]

        # Enkripsi: C = K x P mod 26
        # (perkalian matriks kunci dengan vektor plaintext, modulo 26)
        cipher_vec = matrix_vector_multiply(key_matrix, plain_vec)

        # Konversi vektor numerik kembali ke huruf
        encrypted_blocks.append("".join(num_to_char(n) for n in cipher_vec))

    # Gabungkan semua blok terenkripsi menjadi ciphertext
    ciphertext = "".join(encrypted_blocks)

    return {
        "success": True,
        "error": None,
        "normalized_plaintext": normalized,
        "original_plaintext_length": original_plaintext_length,
        "padded_plaintext": padded_plaintext,
        "padding_length": padding_length,
        "matrix_size": matrix_size,
        "key_matrix": key_matrix,
        "determinant": validation["det"],
        "determinant_mod26": validation["det_mod26"],
        "gcd_result": validation["gcd_result"],
        "inverse_matrix": validation["inverse_matrix"],
        "blocks": blocks,
        "encrypted_blocks": encrypted_blocks,
        "ciphertext": ciphertext
    }


# Dekripsi: P = K^-1 x C mod 26, padding dipotong pakai panjang asli

def hill_decrypt(ciphertext, key_matrix, original_plaintext_length=None):
    """
    Melakukan dekripsi Hill Cipher.

    Proses:
      1. Normalisasi ciphertext (hapus non-alfabet, kapitalkan)
      2. Bagi ciphertext menjadi blok sesuai ukuran matriks
      3. Untuk setiap blok: P = K^-1 x C mod 26
      4. Gabungkan blok terdekripsi
      5. Hapus padding menggunakan original_plaintext_length

    CATATAN PENTING tentang penghapusan padding:
      Program TIDAK boleh menghapus semua 'X' di akhir teks.
      Misal: plaintext asli 'HELLOX' setelah enkripsi-dekripsi
      menghasilkan 'HELLOXX' (dengan 1 padding X). Jika kita hapus
      semua trailing X, hasilnya salah 'HELLO'. Dengan menggunakan
      original_plaintext_length=6, hasilnya benar 'HELLOX'.

    Parameter:
      ciphertext               (str)     : Teks terenkripsi
      key_matrix               (list[list]): Matriks kunci 2x2 atau 3x3
      original_plaintext_length(int|None): Panjang plaintext asli sebelum padding.
                                           Jika None, tidak ada pemotongan padding.

    Mengembalikan dict dengan kunci:
      success                  (bool)
      error                    (str|None)
      ciphertext               (str)
      key_matrix               (list[list])
      inverse_matrix           (list[list])
      blocks                   (list[str])
      decrypted_blocks         (list[str])
      decrypted_padded_text    (str)
      original_plaintext_length(int)
      padding_length           (int)
      plaintext                (str)
    """
    # --- Validasi input ciphertext ---
    if not ciphertext or len(ciphertext.strip()) == 0:
        return {"success": False, "error": "Ciphertext tidak boleh kosong."}

    # Normalisasi ciphertext (hanya ambil karakter A-Z)
    normalized_cipher = normalize_plaintext(ciphertext)
    if len(normalized_cipher) == 0:
        return {
            "success": False,
            "error": "Ciphertext tidak mengandung karakter alfabet yang valid."
        }

    matrix_size = len(key_matrix)

    # --- Validasi format elemen matriks ---
    for i in range(matrix_size):
        for j in range(matrix_size):
            val = key_matrix[i][j]
            if not isinstance(val, (int, float)):
                return {
                    "success": False,
                    "error": "Setiap elemen matriks harus berupa angka."
                }

    # --- Validasi dan ambil invers matriks ---
    validation = validate_matrix(key_matrix)
    if not validation["valid"]:
        return {"success": False, "error": validation["message"]}

    inverse_matrix = validation["inverse_matrix"]

    # --- Bagi ciphertext menjadi blok ---
    block_result = divide_into_blocks(normalized_cipher, matrix_size)
    blocks = block_result["blocks"]
    padding_length = block_result["padding_length"]

    # --- Dekripsi setiap blok ---
    decrypted_blocks = []
    for block in blocks:
        # Konversi blok huruf ke vektor numerik
        cipher_vec = [char_to_num(c) for c in block]

        # Dekripsi: P = K^-1 x C mod 26
        # (perkalian invers matriks kunci dengan vektor ciphertext, modulo 26)
        plain_vec = matrix_vector_multiply(inverse_matrix, cipher_vec)

        # Konversi vektor numerik kembali ke huruf
        decrypted_blocks.append("".join(num_to_char(n) for n in plain_vec))

    # Gabungkan semua blok terdekripsi (masih termasuk padding)
    decrypted_padded_text = "".join(decrypted_blocks)

    # --- Hapus padding menggunakan metadata original_plaintext_length ---
    # PENTING: Gunakan panjang asli, bukan hapus trailing 'X'.
    # Ini mencegah penghapusan karakter 'X' yang memang bagian dari plaintext.
    if original_plaintext_length is not None and original_plaintext_length > 0:
        plaintext = decrypted_padded_text[:original_plaintext_length]
    else:
        # Jika tidak ada informasi panjang asli, kembalikan teks penuh
        plaintext = decrypted_padded_text

    actual_original_length = (
        original_plaintext_length
        if original_plaintext_length is not None
        else len(decrypted_padded_text)
    )

    return {
        "success": True,
        "error": None,
        "ciphertext": normalized_cipher,
        "key_matrix": key_matrix,
        "inverse_matrix": inverse_matrix,
        "blocks": blocks,
        "decrypted_blocks": decrypted_blocks,
        "decrypted_padded_text": decrypted_padded_text,
        "original_plaintext_length": actual_original_length,
        "padding_length": padding_length,
        "plaintext": plaintext
    }


# Bantuan tampilan untuk GUI

def format_blocks(blocks):
    """
    Menghasilkan representasi blok dengan pemisah ' | ' untuk tampilan GUI.
    Contoh: ['RA','HA','SI','AX'] -> 'RA | HA | SI | AX'
    """
    return " | ".join(blocks)


def format_matrix(matrix):
    """
    Menghasilkan representasi matriks sebagai string multi-baris.
    Contoh: [[3,10],[15,9]] -> '3  10\n15  9'
    """
    rows = []
    for row in matrix:
        rows.append("  ".join(str(val) for val in row))
    return "\n".join(rows)


def format_encrypt_result(result):
    # Menghasilkan ringkasan enkripsi untuk ditampilkan oleh GUI.
    if not result["success"]:
        return "ERROR: " + result["error"]

    lines = [
        "=" * 50,
        "HASIL ENKRIPSI HILL CIPHER",
        "=" * 50,
        "",
        "--- Matriks Kunci ---",
        format_matrix(result["key_matrix"]),
        "",
        "--- Validasi Matriks ---",
        "det(K)        = {}".format(result["determinant"]),
        "det(K) mod 26 = {}".format(result["determinant_mod26"]),
        "gcd           = {}".format(result["gcd_result"]),
        "",
        "--- Invers Matriks (mod 26) ---",
        format_matrix(result["inverse_matrix"]),
        "",
        "--- Proses Plaintext ---",
        "Normalized    : {}".format(result["normalized_plaintext"]),
        "Panjang asli  : {}".format(result["original_plaintext_length"]),
        "Padded        : {}".format(result["padded_plaintext"]),
        "Padding       : {} karakter 'X'".format(result["padding_length"]),
        "",
        "--- Blok ---",
        "Plaintext : {}".format(format_blocks(result["blocks"])),
        "Ciphertext: {}".format(format_blocks(result["encrypted_blocks"])),
        "",
        "--- Hasil ---",
        "Ciphertext: {}".format(result["ciphertext"]),
        "=" * 50,
    ]
    return "\n".join(lines)


def format_decrypt_result(result):
    """
    Menghasilkan ringkasan dekripsi untuk ditampilkan oleh GUI.
    """
    if not result["success"]:
        return "ERROR: " + result["error"]

    lines = [
        "=" * 50,
        "HASIL DEKRIPSI HILL CIPHER",
        "=" * 50,
        "",
        "--- Invers Matriks (mod 26) ---",
        format_matrix(result["inverse_matrix"]),
        "",
        "--- Blok ---",
        "Ciphertext  : {}".format(format_blocks(result["blocks"])),
        "Decrypted   : {}".format(format_blocks(result["decrypted_blocks"])),
        "",
        "--- Hasil ---",
        "Padded text : {}".format(result["decrypted_padded_text"]),
        "Plaintext   : {}".format(result["plaintext"]),
        "=" * 50,
    ]
    return "\n".join(lines)


