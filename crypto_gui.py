import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from hill_cipher import (
    hill_encrypt,
    hill_decrypt,
    validate_matrix
)

from vigenere_cipher import (
    vigenere_encrypt,
    vigenere_decrypt
)

from rail_fence_cipher import (
    rail_fence_encrypt,
    rail_fence_decrypt
)


class CryptoGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Kriptografi Hill - Vigenere - Rail Fence"
        )

        self.root.geometry("1250x750")
        self.root.minsize(1100, 650)

        # Menyimpan panjang plaintext asli
        self.original_plaintext_length = None

        self.create_widgets()

    # ============================================================
    # MAIN GUI
    # ============================================================

    def create_widgets(self):

        # ========================================================
        # TITLE
        # ========================================================

        title = tk.Label(
            self.root,
            text="KRIPTOGRAFI HILL - VIGENÈRE - RAIL FENCE",
            font=("Arial", 20, "bold")
        )

        title.pack(
            pady=(15, 3)
        )

        subtitle = tk.Label(
            self.root,
            text="Hill → Vigenère → Rail Fence",
            font=("Arial", 11)
        )

        subtitle.pack(
            pady=(0, 10)
        )

        # ========================================================
        # MODE
        # ========================================================

        mode_frame = tk.LabelFrame(
            self.root,
            text="Mode",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )

        mode_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.mode = tk.StringVar(
            value="encrypt"
        )

        tk.Radiobutton(
            mode_frame,
            text="Enkripsi",
            variable=self.mode,
            value="encrypt",
            command=self.mode_changed
        ).pack(
            side="left",
            padx=15
        )

        tk.Radiobutton(
            mode_frame,
            text="Dekripsi",
            variable=self.mode,
            value="decrypt",
            command=self.mode_changed
        ).pack(
            side="left",
            padx=15
        )

        # ========================================================
        # CONFIGURATION ONE ROW
        # ========================================================

        config_frame = tk.LabelFrame(
            self.root,
            text="Konfigurasi",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )

        config_frame.pack(
            fill="x",
            padx=15,
            pady=5
        )

        # --------------------------------------------------------
        # PLAINTEXT / CIPHERTEXT
        # --------------------------------------------------------

        tk.Label(
            config_frame,
            text="Plaintext:"
        ).grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="w"
        )

        self.input_entry = tk.Entry(
            config_frame,
            width=25,
            font=("Arial", 10)
        )

        self.input_entry.grid(
            row=0,
            column=1,
            padx=5
        )

        self.input_entry.insert(
            0,
            "RAHASIA"
        )

        # Upload
        self.upload_button = tk.Button(
            config_frame,
            text="UPLOAD TXT",
            width=12,
            command=self.upload_txt
        )

        self.upload_button.grid(
            row=0,
            column=2,
            padx=5
        )

        # --------------------------------------------------------
        # VIGENERE KEY
        # --------------------------------------------------------

        tk.Label(
            config_frame,
            text="Key:"
        ).grid(
            row=0,
            column=3,
            padx=(15, 5)
        )

        self.key_entry = tk.Entry(
            config_frame,
            width=12,
            font=("Arial", 10)
        )

        self.key_entry.grid(
            row=0,
            column=4,
            padx=5
        )

        self.key_entry.insert(
            0,
            "SONY"
        )

        # --------------------------------------------------------
        # MATRIX SIZE
        # --------------------------------------------------------

        tk.Label(
            config_frame,
            text="Matriks:"
        ).grid(
            row=0,
            column=5,
            padx=(15, 5)
        )

        self.matrix_size = tk.StringVar(
            value="2"
        )

        self.matrix_combo = ttk.Combobox(
            config_frame,
            textvariable=self.matrix_size,
            values=["2", "3"],
            state="readonly",
            width=4
        )

        self.matrix_combo.grid(
            row=0,
            column=6,
            padx=5
        )

        self.matrix_combo.bind(
            "<<ComboboxSelected>>",
            self.update_matrix
        )

        # --------------------------------------------------------
        # MATRIX
        # --------------------------------------------------------

        self.matrix_frame = tk.Frame(
            config_frame
        )

        self.matrix_frame.grid(
            row=0,
            column=7,
            padx=5
        )

        self.matrix_entries = []

        self.create_matrix(
            2
        )

        # --------------------------------------------------------
        # RAIL
        # --------------------------------------------------------

        tk.Label(
            config_frame,
            text="Rail:"
        ).grid(
            row=0,
            column=8,
            padx=(15, 5)
        )

        self.rail_entry = tk.Entry(
            config_frame,
            width=5,
            justify="center"
        )

        self.rail_entry.grid(
            row=0,
            column=9,
            padx=5
        )

        self.rail_entry.insert(
            0,
            "5"
        )

        # ========================================================
        # BUTTON
        # ========================================================

        button_frame = tk.Frame(
            self.root
        )

        button_frame.pack(
            pady=10
        )

        tk.Button(
            button_frame,
            text="PROSES",
            width=16,
            height=2,
            font=("Arial", 10, "bold"),
            command=self.process
        ).pack(
            side="left",
            padx=8
        )

        tk.Button(
            button_frame,
            text="SIMPAN HASIL",
            width=16,
            height=2,
            command=self.save_result
        ).pack(
            side="left",
            padx=8
        )

        tk.Button(
            button_frame,
            text="BERSIHKAN",
            width=16,
            height=2,
            command=self.clear_all
        ).pack(
            side="left",
            padx=8
        )

        # ========================================================
        # RESULT - FULL AREA
        # ========================================================

        output_frame = tk.LabelFrame(
            self.root,
            text="Hasil Proses",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )

        output_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(5, 10)
        )

        # Text + scrollbar
        text_frame = tk.Frame(
            output_frame
        )

        text_frame.pack(
            fill="both",
            expand=True
        )

        self.output_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Consolas", 11),
            state="disabled"
        )

        self.output_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar_y = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.output_text.yview
        )

        scrollbar_y.pack(
            side="right",
            fill="y"
        )

        self.output_text.configure(
            yscrollcommand=scrollbar_y.set
        )

        # ========================================================
        # STATUS BAR
        # ========================================================

        self.status_var = tk.StringVar(
            value="Siap. Masukkan teks lalu tekan PROSES."
        )

        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padx=10
        )

        status.pack(
            fill="x",
            side="bottom"
        )

    # ============================================================
    # MATRIX
    # ============================================================

    def create_matrix(self, size):

        # Hapus matrix lama
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        self.matrix_entries = []

        # Default matrix
        if size == 2:

            defaults = [
                [3, 10],
                [15, 9]
            ]

        else:

            defaults = [
                [6, 24, 1],
                [13, 16, 10],
                [20, 17, 15]
            ]

        # Matrix dibuat horizontal/inline
        for i in range(size):

            row = []

            for j in range(size):

                entry = tk.Entry(
                    self.matrix_frame,
                    width=5,
                    justify="center",
                    font=("Arial", 9)
                )

                entry.grid(
                    row=i,
                    column=j,
                    padx=2,
                    pady=2
                )

                entry.insert(
                    0,
                    str(defaults[i][j])
                )

                row.append(entry)

            self.matrix_entries.append(
                row
            )

    def update_matrix(self, event=None):

        size = int(
            self.matrix_size.get()
        )

        self.create_matrix(
            size
        )

        self.status_var.set(
            f"Matriks {size}x{size} dipilih."
        )

    # ============================================================
    # GET MATRIX
    # ============================================================

    def get_matrix(self):

        size = int(
            self.matrix_size.get()
        )

        matrix = []

        for i in range(size):

            row = []

            for j in range(size):

                value = (
                    self.matrix_entries[i][j]
                    .get()
                    .strip()
                )

                if value == "":

                    raise ValueError(
                        "Semua elemen matriks harus diisi."
                    )

                try:

                    number = int(
                        value
                    )

                except ValueError:

                    raise ValueError(
                        "Elemen matriks harus berupa angka."
                    )

                row.append(
                    number
                )

            matrix.append(
                row
            )

        return matrix

    # ============================================================
    # EXTRACT RESULT
    # ============================================================

    def extract_result(
        self,
        result,
        preferred_keys
    ):

        # Kalau string
        if isinstance(
            result,
            str
        ):

            return result

        # Kalau dictionary
        if isinstance(
            result,
            dict
        ):

            if result.get(
                "success"
            ) is False:

                raise ValueError(
                    result.get(
                        "error",
                        "Proses cipher gagal."
                    )
                )

            for key in preferred_keys:

                if key in result:

                    value = result[key]

                    if value is not None:

                        return str(
                            value
                        )

            raise ValueError(
                "Format hasil cipher tidak dikenali."
            )

        raise ValueError(
            "Format hasil cipher tidak dikenali."
        )

    # ============================================================
    # PROCESS
    # ============================================================

    def process(self):

        try:

            # ----------------------------------------------------
            # INPUT
            # ----------------------------------------------------

            text = (
                self.input_entry
                .get()
                .strip()
            )

            if not text:

                messagebox.showwarning(
                    "Input Kosong",
                    "Masukkan plaintext/ciphertext."
                )

                return

            # ----------------------------------------------------
            # KEY
            # ----------------------------------------------------

            key = (
                self.key_entry
                .get()
                .strip()
            )

            if not key:

                raise ValueError(
                    "Key Vigenère tidak boleh kosong."
                )

            # ----------------------------------------------------
            # RAIL
            # ----------------------------------------------------

            try:

                rails = int(
                    self.rail_entry
                    .get()
                    .strip()
                )

            except ValueError:

                raise ValueError(
                    "Jumlah rail harus berupa angka."
                )

            if rails < 2:

                raise ValueError(
                    "Jumlah rail minimal adalah 2."
                )

            # ----------------------------------------------------
            # MATRIX
            # ----------------------------------------------------

            matrix = self.get_matrix()

            validation = validate_matrix(
                matrix
            )

            if not validation["valid"]:

                raise ValueError(
                    validation["message"]
                )

            # ====================================================
            # ENKRIPSI
            # ====================================================

            if self.mode.get() == "encrypt":

                # ------------------------------------------------
                # HILL
                # ------------------------------------------------

                hill_result = hill_encrypt(
                    text,
                    matrix
                )

                if not hill_result["success"]:

                    raise ValueError(
                        hill_result["error"]
                    )

                hill_text = hill_result[
                    "ciphertext"
                ]

                self.original_plaintext_length = (
                    hill_result[
                        "original_plaintext_length"
                    ]
                )

                # ------------------------------------------------
                # VIGENERE
                # ------------------------------------------------

                vigenere_raw = vigenere_encrypt(
                    hill_text,
                    key
                )

                vigenere_text = self.extract_result(
                    vigenere_raw,
                    [
                        "ciphertext",
                        "result",
                        "text",
                        "encrypted_text"
                    ]
                )

                # ------------------------------------------------
                # RAIL FENCE
                # ------------------------------------------------

                rail_raw = rail_fence_encrypt(
                    vigenere_text,
                    rails
                )

                rail_text = self.extract_result(
                    rail_raw,
                    [
                        "ciphertext",
                        "result",
                        "text",
                        "encrypted_text"
                    ]
                )

                # ------------------------------------------------
                # OUTPUT
                # ------------------------------------------------

                result = (
                    "============================================================\n"
                    "                     HASIL ENKRIPSI\n"
                    "============================================================\n\n"

                    "PLAINTEXT AWAL\n"
                    f"{text}\n\n"

                    "------------------------------------------------------------\n"
                    "1. HILL CIPHER\n"
                    "------------------------------------------------------------\n"
                    f"{hill_text}\n\n"

                    "------------------------------------------------------------\n"
                    "2. VIGENÈRE CIPHER\n"
                    "------------------------------------------------------------\n"
                    f"{vigenere_text}\n\n"

                    "------------------------------------------------------------\n"
                    f"3. RAIL FENCE ({rails} RAILS)\n"
                    "------------------------------------------------------------\n"
                    f"{rail_text}\n\n"

                    "============================================================\n"
                    "                    CIPHERTEXT AKHIR\n"
                    "============================================================\n\n"
                    f"{rail_text}\n"
                )

                self.show_result(
                    result
                )

                self.status_var.set(
                    "Enkripsi berhasil."
                )

            # ====================================================
            # DEKRIPSI
            # ====================================================

            else:

                # ------------------------------------------------
                # RAIL FENCE
                # ------------------------------------------------

                rail_raw = rail_fence_decrypt(
                    text,
                    rails
                )

                rail_text = self.extract_result(
                    rail_raw,
                    [
                        "plaintext",
                        "result",
                        "text",
                        "decrypted_text"
                    ]
                )

                # ------------------------------------------------
                # VIGENERE
                # ------------------------------------------------

                vigenere_raw = vigenere_decrypt(
                    rail_text,
                    key
                )

                vigenere_text = self.extract_result(
                    vigenere_raw,
                    [
                        "plaintext",
                        "result",
                        "text",
                        "decrypted_text"
                    ]
                )

                # ------------------------------------------------
                # HILL
                # ------------------------------------------------

                hill_result = hill_decrypt(
                    vigenere_text,
                    matrix,
                    original_plaintext_length=(
                        self.original_plaintext_length
                    )
                )

                if not hill_result["success"]:

                    raise ValueError(
                        hill_result["error"]
                    )

                hill_text = hill_result[
                    "plaintext"
                ]

                # ------------------------------------------------
                # OUTPUT
                # ------------------------------------------------

                result = (
                    "============================================================\n"
                    "                     HASIL DEKRIPSI\n"
                    "============================================================\n\n"

                    "CIPHERTEXT AWAL\n"
                    f"{text}\n\n"

                    "------------------------------------------------------------\n"
                    f"1. RAIL FENCE ({rails} RAILS)\n"
                    "------------------------------------------------------------\n"
                    f"{rail_text}\n\n"

                    "------------------------------------------------------------\n"
                    "2. VIGENÈRE CIPHER\n"
                    "------------------------------------------------------------\n"
                    f"{vigenere_text}\n\n"

                    "------------------------------------------------------------\n"
                    "3. HILL CIPHER\n"
                    "------------------------------------------------------------\n"
                    f"{hill_text}\n\n"

                    "============================================================\n"
                    "                     PLAINTEXT AKHIR\n"
                    "============================================================\n\n"
                    f"{hill_text}\n"
                )

                self.show_result(
                    result
                )

                self.status_var.set(
                    "Dekripsi berhasil."
                )

        except Exception as e:

            error_text = (
                "============================================================\n"
                "                         ERROR\n"
                "============================================================\n\n"
                f"{str(e)}\n"
            )

            self.show_result(
                error_text
            )

            self.status_var.set(
                "Proses gagal."
            )

            messagebox.showerror(
                "Error",
                str(e)
            )

    # ============================================================
    # SHOW RESULT
    # ============================================================

    def show_result(
        self,
        result
    ):

        self.output_text.config(
            state="normal"
        )

        self.output_text.delete(
            "1.0",
            tk.END
        )

        self.output_text.insert(
            "1.0",
            result
        )

        self.output_text.config(
            state="disabled"
        )

    # ============================================================
    # MODE
    # ============================================================

    def mode_changed(self):

        if self.mode.get() == "encrypt":

            self.status_var.set(
                "Mode Enkripsi: Hill → Vigenère → Rail Fence"
            )

        else:

            self.status_var.set(
                "Mode Dekripsi: Rail Fence → Vigenère → Hill"
            )

    # ============================================================
    # UPLOAD TXT
    # ============================================================

    def upload_txt(self):

        file_path = filedialog.askopenfilename(
            title="Pilih File TXT",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            path = Path(
                file_path
            )

            try:

                content = path.read_text(
                    encoding="utf-8-sig"
                )

            except UnicodeDecodeError:

                content = path.read_text(
                    encoding="cp1252"
                )

            # Karena sekarang input berupa Entry,
            # ambil isi TXT dan masukkan sebagai satu baris.
            content = (
                content
                .replace("\r", "")
                .replace("\n", " ")
                .strip()
            )

            self.input_entry.delete(
                0,
                tk.END
            )

            self.input_entry.insert(
                0,
                content
            )

            self.status_var.set(
                f"File berhasil dimuat: {path.name}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Gagal membaca file:\n{e}"
            )

    # ============================================================
    # SAVE RESULT
    # ============================================================

    def save_result(self):

        result = self.output_text.get(
            "1.0",
            "end-1c"
        ).strip()

        if not result:

            messagebox.showwarning(
                "Tidak Ada Hasil",
                "Belum ada hasil proses."
            )

            return

        file_path = filedialog.asksaveasfilename(
            title="Simpan Hasil",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:

            Path(
                file_path
            ).write_text(
                result,
                encoding="utf-8"
            )

            self.status_var.set(
                "Hasil berhasil disimpan."
            )

            messagebox.showinfo(
                "Berhasil",
                "Hasil berhasil disimpan."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Gagal menyimpan hasil:\n{e}"
            )

    # ============================================================
    # CLEAR
    # ============================================================

    def clear_all(self):

        self.input_entry.delete(
            0,
            tk.END
        )

        self.output_text.config(
            state="normal"
        )

        self.output_text.delete(
            "1.0",
            tk.END
        )

        self.output_text.config(
            state="disabled"
        )

        self.key_entry.delete(
            0,
            tk.END
        )

        self.key_entry.insert(
            0,
            "SONY"
        )

        self.rail_entry.delete(
            0,
            tk.END
        )

        self.rail_entry.insert(
            0,
            "5"
        )

        self.original_plaintext_length = None

        # Reset matrix ke 2x2
        self.matrix_size.set(
            "2"
        )

        self.create_matrix(
            2
        )

        self.status_var.set(
            "Semua input dan hasil telah dibersihkan."
        )


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CryptoGUI(
        root
    )

    root.mainloop()