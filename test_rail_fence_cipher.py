# Test Rail Fence + integrasi pipeline. Jalankan dari folder yang sama dengan file cipher:
#   python -m unittest test_rail_fence_cipher -v
# Kelas integrasi otomatis di-skip jika hill_cipher.py / vigenere_cipher.py tidak ditemukan.

import unittest

from rail_fence_cipher import (
    RAIL_COUNT,
    normalize_plaintext,
    build_rail_pattern,
    format_rail_grid,
    rail_fence_encrypt,
    rail_fence_decrypt,
)


def sample_text(n):
    # Teks uji deterministik sepanjang n dengan huruf bervariasi
    return "".join(chr(65 + (i * 7 + 3) % 26) for i in range(n))


class TestPattern(unittest.TestCase):
    def test_rail_count_is_5(self):
        self.assertEqual(RAIL_COUNT, 5)

    def test_pattern_k5(self):
        self.assertEqual(build_rail_pattern(10, 5), [0, 1, 2, 3, 4, 3, 2, 1, 0, 1])

    def test_pattern_k2(self):
        self.assertEqual(build_rail_pattern(5, 2), [0, 1, 0, 1, 0])

    def test_pattern_shorter_than_rails(self):
        self.assertEqual(build_rail_pattern(3, 5), [0, 1, 2])


class TestEncrypt(unittest.TestCase):
    def test_golden_from_pipeline(self):
        r = rail_fence_encrypt("RJIZWSJX")
        self.assertTrue(r["success"])
        self.assertEqual(r["ciphertext"], "RJXIJZSW")

    def test_ten_letters(self):
        # Rail1=AI, Rail2=BHJ, Rail3=CG, Rail4=DF, Rail5=E
        self.assertEqual(rail_fence_encrypt("ABCDEFGHIJ")["ciphertext"], "AIBHJCGDFE")

    def test_short_inputs(self):
        self.assertEqual(rail_fence_encrypt("A")["ciphertext"], "A")
        self.assertEqual(rail_fence_encrypt("AB")["ciphertext"], "AB")
        self.assertEqual(rail_fence_encrypt("ABC")["ciphertext"], "ABC")
        self.assertEqual(rail_fence_encrypt("ABCD")["ciphertext"], "ABCD")

    def test_exactly_five_letters_is_identity(self):
        # Tiap huruf jatuh di rail berbeda, urutan baca sama dengan urutan tulis
        self.assertEqual(rail_fence_encrypt("ABCDE")["ciphertext"], "ABCDE")

    def test_six_letters(self):
        # Rail4 berisi D dan F
        self.assertEqual(rail_fence_encrypt("ABCDEF")["ciphertext"], "ABCDFE")

    def test_length_and_letters_preserved(self):
        for n in (1, 7, 8, 9, 33, 100):
            teks = sample_text(n)
            hasil = rail_fence_encrypt(teks)["ciphertext"]
            self.assertEqual(len(hasil), n)
            # Transposisi tidak boleh mengubah distribusi huruf sama sekali
            self.assertEqual(sorted(hasil), sorted(teks))


class TestDecrypt(unittest.TestCase):
    def test_golden_from_pipeline(self):
        r = rail_fence_decrypt("RJXIJZSW")
        self.assertTrue(r["success"])
        self.assertEqual(r["plaintext"], "RJIZWSJX")

    def test_ten_letters(self):
        self.assertEqual(rail_fence_decrypt("AIBHJCGDFE")["plaintext"], "ABCDEFGHIJ")

    def test_any_length_is_accepted(self):
        # Berbeda dengan Hill, Rail Fence tidak punya syarat kelipatan blok
        for n in (1, 2, 3, 4, 5, 6, 11, 13):
            self.assertTrue(rail_fence_decrypt(sample_text(n))["success"])


class TestRoundTrip(unittest.TestCase):
    def test_default_rails_lengths_1_to_80(self):
        for n in range(1, 81):
            teks = sample_text(n)
            c = rail_fence_encrypt(teks)["ciphertext"]
            self.assertEqual(rail_fence_decrypt(c)["plaintext"], teks, "gagal pada n=%d" % n)

    def test_other_rail_counts(self):
        for k in range(2, 10):
            for n in range(1, 41):
                teks = sample_text(n)
                c = rail_fence_encrypt(teks, rails=k)["ciphertext"]
                self.assertEqual(rail_fence_decrypt(c, rails=k)["plaintext"], teks)

    def test_long_input(self):
        teks = sample_text(5000)
        c = rail_fence_encrypt(teks)["ciphertext"]
        self.assertEqual(rail_fence_decrypt(c)["plaintext"], teks)

    def test_text_ending_with_x_is_untouched(self):
        # Rail Fence tidak boleh membuang atau menambah huruf X
        for teks in ("HELLOX", "XX", "X", "ABCXXX"):
            c = rail_fence_encrypt(teks)["ciphertext"]
            self.assertEqual(rail_fence_decrypt(c)["plaintext"], teks)


class TestNormalizationAndValidation(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_plaintext("Aku pergi!"), "AKUPERGI")
        self.assertEqual(normalize_plaintext("ß"), "")

    def test_encrypt_normalizes_input(self):
        r = rail_fence_encrypt("rjiz wsjx\n")
        self.assertEqual(r["normalized_input"], "RJIZWSJX")
        self.assertEqual(r["ciphertext"], "RJXIJZSW")

    def test_empty_inputs_rejected(self):
        for bad in ("", "   ", "123 !!", None, 42):
            self.assertFalse(rail_fence_encrypt(bad)["success"], repr(bad))
            self.assertFalse(rail_fence_decrypt(bad)["success"], repr(bad))
        self.assertIn("tidak boleh kosong", rail_fence_encrypt("")["error"])

    def test_invalid_rails_rejected(self):
        for bad in (1, 0, -3, 5.0, True, "5", None):
            self.assertFalse(rail_fence_encrypt("ABCDEF", rails=bad)["success"], repr(bad))
            self.assertFalse(rail_fence_decrypt("ABCDEF", rails=bad)["success"], repr(bad))


class TestVisualizationData(unittest.TestCase):
    def test_grid_shape_and_one_letter_per_column(self):
        r = rail_fence_encrypt("RJIZWSJX")
        grid = r["grid"]
        self.assertEqual(len(grid), 5)
        for baris in grid:
            self.assertEqual(len(baris), 8)
        for kolom in range(8):
            terisi = [grid[b][kolom] for b in range(5) if grid[b][kolom] is not None]
            self.assertEqual(len(terisi), 1)

    def test_reading_grid_rowwise_gives_ciphertext(self):
        r = rail_fence_encrypt(sample_text(37))
        baca = "".join(ch for baris in r["grid"] for ch in baris if ch is not None)
        self.assertEqual(baca, r["ciphertext"])

    def test_rail_rows_cover_all_positions(self):
        r = rail_fence_encrypt(sample_text(23))
        semua = sorted(p for row in r["rail_rows"] for p in row["positions"])
        self.assertEqual(semua, list(range(23)))
        self.assertEqual("".join(row["text"] for row in r["rail_rows"]), r["ciphertext"])

    def test_steps_use_1_based_rails(self):
        r = rail_fence_encrypt("RJIZWSJX")
        self.assertEqual([s["rail"] for s in r["steps"]], [1, 2, 3, 4, 5, 4, 3, 2])
        self.assertEqual([s["char"] for s in r["steps"]], list("RJIZWSJX"))

    def test_empty_rails_are_representable(self):
        # Teks 2 huruf: rail 3-5 kosong, tetapi grid tetap 5 baris
        r = rail_fence_encrypt("AB")
        self.assertEqual(len(r["grid"]), 5)
        self.assertEqual([row["text"] for row in r["rail_rows"]], ["A", "B", "", "", ""])

    def test_decrypt_grid_reconstruction(self):
        r = rail_fence_decrypt("RJXIJZSW")
        self.assertEqual(r["rail_rows"][0]["text"], "R")
        self.assertEqual(r["rail_rows"][1]["text"], "JX")
        self.assertEqual(r["grid"][0][0], "R")
        self.assertEqual(r["grid"][4][4], "W")

    def test_format_rail_grid_exact(self):
        expected = "\n".join([
            "Rail 1  R . . . . . . .",
            "Rail 2  . J . . . . . X",
            "Rail 3  . . I . . . J .",
            "Rail 4  . . . Z . S . .",
            "Rail 5  . . . . W . . .",
        ])
        self.assertEqual(format_rail_grid(rail_fence_encrypt("RJIZWSJX")["grid"]), expected)


class TestFullPipelineIntegration(unittest.TestCase):
    # Test terpenting: urutan lapisan dan metadata. Memakai file Hill dan Vigenere milik tim.

    KEY_2 = [[3, 10], [15, 9]]
    KEY_3 = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]

    def setUp(self):
        try:
            import hill_cipher
            import vigenere_cipher
        except ImportError:
            self.skipTest("hill_cipher.py / vigenere_cipher.py tidak ditemukan")
        self.hill = hill_cipher
        self.vig = vigenere_cipher

    def encrypt_all(self, teks, key, vkey):
        h = self.hill.hill_encrypt(teks, key)
        v = self.vig.vigenere_encrypt(h["ciphertext"], vkey)
        r = rail_fence_encrypt(v["ciphertext"])
        return h, v, r

    def decrypt_all(self, final_cipher, key, vkey, panjang_asli):
        r = rail_fence_decrypt(final_cipher)
        v = self.vig.vigenere_decrypt(r["plaintext"], vkey)
        h = self.hill.hill_decrypt(v["plaintext"], key, panjang_asli)
        return h["plaintext"]

    def test_golden_rahasia(self):
        h, v, r = self.encrypt_all("RAHASIA", self.KEY_2, "SONY")
        self.assertEqual(h["ciphertext"], "ZVVBEEWZ")
        self.assertEqual(v["ciphertext"], "RJIZWSJX")
        self.assertEqual(r["ciphertext"], "RJXIJZSW")
        self.assertEqual(h["original_plaintext_length"], 7)
        self.assertEqual(self.decrypt_all(r["ciphertext"], self.KEY_2, "SONY", 7), "RAHASIA")

    def test_round_trip_various_texts_and_sizes(self):
        teks_uji = ["A", "AB", "HELLOX", "XX", "X", "ABCXXX", "Aku pergi ke kampus!",
                    "INFORMATIKA", sample_text(50), sample_text(101)]
        for key in (self.KEY_2, self.KEY_3):
            for teks in teks_uji:
                h, v, r = self.encrypt_all(teks, key, "SONY")
                asli = normalize_plaintext(teks)
                # Rail Fence tidak mengubah panjang hasil Hill (sudah termasuk padding)
                self.assertEqual(len(r["ciphertext"]), len(h["padded_plaintext"]))
                hasil = self.decrypt_all(r["ciphertext"], key, "SONY", h["original_plaintext_length"])
                self.assertEqual(hasil, asli, "gagal: %r ukuran %d" % (teks, len(key)))


if __name__ == "__main__":
    unittest.main()