import tkinter as tk
from tkinter import ttk, messagebox

from hill_cipher import hill_encrypt, hill_decrypt, validate_matrix
from vigenere_cipher import vigenere_encrypt, vigenere_decrypt
from rail_fence_cipher import rail_fence_encrypt, rail_fence_decrypt


RAIL_COUNT = 5


class CryptoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kriptografi Berantai — Hill → Vigenère → Rail Fence")
        self.geometry("1120x760")
        self.minsize(980, 680)

        self.mode = tk.StringVar(value="Enkripsi")
        self.matrix_size = tk.IntVar(value=2)

        self._build_style()
        self._build_ui()
        self._update_matrix()

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Result.TLabel", font=("Consolas", 13, "bold"))

    def _build_ui(self):
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer,
            text="Kriptografi Berantai",
            style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            outer,
            text="Hill Cipher → Vigenère → Rail Fence (5 rail)",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        top = ttk.Frame(outer)
        top.pack(fill="x")

        input_frame = ttk.LabelFrame(top, text="Input", padding=12)
        input_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.input_label = ttk.Label(input_frame, text="Plaintext:")
        self.input_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.input_text = tk.Text(input_frame, height=5, wrap="word", font=("Consolas", 11))
        self.input_text.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.input_text.insert("1.0", "RAHASIA")

        ttk.Label(input_frame, text="Key Vigenère:").grid(row=2, column=0, sticky="w", pady=(12, 5))
        self.vigenere_key = ttk.Entry(input_frame, font=("Consolas", 11))
        self.vigenere_key.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.vigenere_key.insert(0, "SONY")

        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)

        key_frame = ttk.LabelFrame(top, text="Key Hill Cipher", padding=12)
        key_frame.pack(side="right", fill="y")

        ttk.Label(key_frame, text="Ukuran matriks:").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(
            key_frame,
            textvariable=self.matrix_size,
            values=(2, 3),
            state="readonly",
            width=8
        )
        combo.grid(row=0, column=1, sticky="w", padx=(8, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self._update_matrix())

        self.matrix_frame = ttk.Frame(key_frame)
        self.matrix_frame.grid(row=1, column=0, columnspan=2, pady=(10, 8))
        self.matrix_entries = []

        ttk.Label(key_frame, text="Rail Fence: 5 rail (tetap)").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(5, 0)
        )

        action = ttk.Frame(outer)
        action.pack(fill="x", pady=12)

        ttk.Radiobutton(
            action, text="Enkripsi", variable=self.mode, value="Enkripsi",
            command=self._mode_changed
        ).pack(side="left")
        ttk.Radiobutton(
            action, text="Dekripsi", variable=self.mode, value="Dekripsi",
            command=self._mode_changed
        ).pack(side="left", padx=(15, 0))

        ttk.Button(
            action, text="PROSES", style="Action.TButton",
            command=self.process
        ).pack(side="left", padx=(25, 8))
        ttk.Button(
            action, text="BERSIHKAN",
            command=self.clear_all
        ).pack(side="left")

        result_frame = ttk.LabelFrame(outer, text="Hasil & Proses", padding=12)
        result_frame.pack(fill="both", expand=True)

        self.result_text = tk.Text(
            result_frame, wrap="word", font=("Consolas", 10),
            state="disabled"
        )
        self.result_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            result_frame, orient="vertical", command=self.result_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self._mode_changed()

    def _update_matrix(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        n = self.matrix_size.get()
        defaults = {
            2: [[3, 10], [15, 9]],
            3: [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
        }[n]

        self.matrix_entries = []
        for r in range(n):
            row = []
            for c in range(n):
                e = ttk.Entry(self.matrix_frame, width=6, justify="center", font=("Consolas", 11))
                e.grid(row=r, column=c, padx=3, pady=3)
                e.insert(0, str(defaults[r][c]))
                row.append(e)
            self.matrix_entries.append(row)

    def _mode_changed(self):
        mode = self.mode.get()
        self.input_label.config(text="Plaintext:" if mode == "Enkripsi" else "Ciphertext:")
        self.input_text.delete("1.0", "end")
        if mode == "Enkripsi":
            self.input_text.insert("1.0", "RAHASIA")

    def _get_matrix(self):
        matrix = []
        try:
            for row in self.matrix_entries:
                matrix.append([int(cell.get().strip()) for cell in row])
        except ValueError:
            raise ValueError("Semua elemen matriks Hill harus berupa bilangan bulat.")
        return matrix

    def _set_result(self, text):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def _fmt_matrix(self, matrix):
        return "\n".join("  " + "  ".join(f"{x:>4}" for x in row) for row in matrix)

    def process(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        key = self.vigenere_key.get().strip()

        if not text:
            messagebox.showwarning("Input kosong", "Masukkan plaintext/ciphertext terlebih dahulu.")
            return
        if not key:
            messagebox.showwarning("Key kosong", "Masukkan key Vigenère.")
            return

        try:
            matrix = self._get_matrix()
            valid = validate_matrix(matrix)
            if isinstance(valid, dict) and not valid.get("valid", False):
                raise ValueError(valid.get("error", "Matriks Hill tidak valid."))
            elif valid is False:
                raise ValueError("Matriks Hill tidak valid.")

            if self.mode.get() == "Enkripsi":
                self._encrypt(text, key, matrix)
            else:
                self._decrypt(text, key, matrix)
        except Exception as exc:
            messagebox.showerror("Proses gagal", str(exc))

    def _encrypt(self, plaintext, key, matrix):
        hill = hill_encrypt(plaintext, matrix)
        if not hill["success"]:
            raise ValueError(hill["error"])

        vig = vigenere_encrypt(hill["ciphertext"], key)
        if not vig["success"]:
            raise ValueError(vig["error"])

        rail = rail_fence_encrypt(vig["ciphertext"], RAIL_COUNT)
        if not rail["success"]:
            raise ValueError(rail["error"])

        lines = [
            "=== ENKRIPSI BERURUTAN ===",
            "",
            "Input plaintext:",
            plaintext,
            "",
            "1. HILL CIPHER",
            f"Matriks {hill['matrix_size']}x{hill['matrix_size']}:",
            self._fmt_matrix(matrix),
            f"Normalisasi : {hill['normalized_plaintext']}",
            f"Padding     : {hill['padded_plaintext']}  (X={hill['padding_length']})",
            f"Hasil Hill  : {hill['ciphertext']}",
            "",
            "2. VIGENÈRE",
            f"Key         : {vig['key']}",
            f"Repeated key: {vig['repeated_key']}",
            f"Hasil       : {vig['ciphertext']}",
            "",
            "3. RAIL FENCE",
            f"Rail        : {RAIL_COUNT}",
            f"Hasil akhir : {rail['ciphertext']}",
            "",
            "===========================",
            f"CIPHERTEXT AKHIR: {rail['ciphertext']}",
            "===========================",
        ]
        self._set_result("\n".join(lines))

    def _decrypt(self, ciphertext, key, matrix):
        rail = rail_fence_decrypt(ciphertext, RAIL_COUNT)
        if not rail["success"]:
            raise ValueError(rail["error"])

        vig = vigenere_decrypt(rail["plaintext"], key)
        if not vig["success"]:
            raise ValueError(vig["error"])

        # Hill needs original plaintext length to remove padding.
        # We infer it from the recovered Hill ciphertext length only when
        # there is no padding ambiguity; for the normal pipeline, the
        # Hill ciphertext has even/3-multiple length and the final block
        # padding is represented by X. The user can still get the exact
        # original plaintext when Hill's decrypted text ends in X.
        #
        # To preserve exact original length for common inputs, remove a
        # single trailing X produced by Hill padding. This matches the
        # provided hill_cipher implementation.
        hill_ciphertext = vig["plaintext"]

        candidates = []
        for original_len in range(max(0, len(hill_ciphertext) - matrix.__len__() + 1), len(hill_ciphertext) + 1):
            h = hill_decrypt(hill_ciphertext, matrix, original_len)
            if h["success"] and h["plaintext"] == h["decrypted_padded_text"][:original_len]:
                candidates.append(h)

        if not candidates:
            hill = hill_decrypt(hill_ciphertext, matrix)
        else:
            # Prefer the length indicated by a trailing X padding convention.
            padded = candidates[-1]
            hill = padded
            if hill.get("decrypted_padded_text", "").endswith("X"):
                trimmed = hill["decrypted_padded_text"][:-1]
                hill["plaintext"] = trimmed
                hill["original_plaintext_length"] = len(trimmed)

        if not hill["success"]:
            raise ValueError(hill["error"])

        lines = [
            "=== DEKRIPSI BERURUTAN ===",
            "",
            "Input ciphertext:",
            ciphertext,
            "",
            "1. RAIL FENCE DECRYPT",
            f"Rail        : {RAIL_COUNT}",
            f"Hasil       : {rail['plaintext']}",
            "",
            "2. VIGENÈRE DECRYPT",
            f"Key         : {vig['key']}",
            f"Repeated key: {vig['repeated_key']}",
            f"Hasil       : {vig['plaintext']}",
            "",
            "3. HILL DECRYPT",
            f"Matriks {len(matrix)}x{len(matrix)}:",
            self._fmt_matrix(matrix),
            f"Inverse     : {hill.get('inverse_matrix')}",
            f"Hasil       : {hill['plaintext']}",
            "",
            "===========================",
            f"PLAINTEXT AKHIR: {hill['plaintext']}",
            "===========================",
        ]
        self._set_result("\n".join(lines))

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.vigenere_key.delete(0, "end")
        self.vigenere_key.insert(0, "SONY")
        self._update_matrix()
        self._set_result("")


if __name__ == "__main__":
    app = CryptoGUI()
    app.mainloop()
