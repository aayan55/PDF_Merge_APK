"""Tkinter tabanlı PDF birleştirme aracı."""

from __future__ import annotations

import threading
from pathlib import Path
from tkinter import (
    END,
    SINGLE,
    ACTIVE,
    filedialog,
    messagebox,
    ttk,
    Tk,
    StringVar,
    Listbox,
)

from pypdf import PdfReader, PdfWriter

WINDOW_TITLE = "PDF Birleştirme Aracı"
DEFAULT_OUTPUT = "birlesik.pdf"


class PDFMergeApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry("620x420")
        self.root.minsize(580, 380)

        self.pdf_listbox = Listbox(self.root, selectmode=SINGLE)
        self.status_var = StringVar(value="Hazır")
        self.output_var = StringVar(value=DEFAULT_OUTPUT)

        self._build_ui()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        # Dosya listesi
        list_frame = ttk.LabelFrame(main_frame, text="Seçilen PDF Dosyaları")
        list_frame.pack(fill="both", expand=True)

        self.pdf_listbox = Listbox(list_frame, selectmode=SINGLE)
        self.pdf_listbox.pack(fill="both", expand=True, side="left", padx=(0, 8), pady=8)

        control_frame = ttk.Frame(list_frame)
        control_frame.pack(side="left", fill="y", pady=8)

        ttk.Button(control_frame, text="Dosya Ekle", command=self.add_files).pack(
            fill="x", pady=2
        )
        ttk.Button(control_frame, text="Seçileni Sil", command=self.remove_selected).pack(
            fill="x", pady=2
        )
        ttk.Button(control_frame, text="Listeyi Temizle", command=self.clear_list).pack(
            fill="x", pady=2
        )
        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(control_frame, text="Yukarı", command=lambda: self.move_item(-1)).pack(
            fill="x", pady=2
        )
        ttk.Button(control_frame, text="Aşağı", command=lambda: self.move_item(1)).pack(
            fill="x", pady=2
        )

        # Çıktı ayarları
        output_frame = ttk.LabelFrame(main_frame, text="Çıktı")
        output_frame.pack(fill="x", pady=(12, 4))

        ttk.Entry(output_frame, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True, padx=(8, 4), pady=8
        )
        ttk.Button(output_frame, text="Kaydet...", command=self.select_output).pack(
            side="left", padx=(0, 8), pady=8
        )

        # Alt kısım
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x")

        ttk.Button(bottom_frame, text="Birleştir", command=self.merge_clicked).pack(
            side="right", padx=8
        )
        ttk.Label(bottom_frame, textvariable=self.status_var).pack(
            side="left", padx=8
        )

    # ------------------------------------------------------------ Actions --
    def add_files(self) -> None:
        filenames = filedialog.askopenfilenames(
            title="PDF dosyalarını seç",
            filetypes=[("PDF Dosyaları", "*.pdf")],
        )
        for filename in filenames:
            if filename not in self.pdf_listbox.get(0, END):
                self.pdf_listbox.insert(END, filename)

    def remove_selected(self) -> None:
        selected = self.pdf_listbox.curselection()
        if selected:
            self.pdf_listbox.delete(selected[0])

    def clear_list(self) -> None:
        self.pdf_listbox.delete(0, END)

    def move_item(self, direction: int) -> None:
        index = self.pdf_listbox.curselection()
        if not index:
            return
        idx = index[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= self.pdf_listbox.size():
            return
        value = self.pdf_listbox.get(idx)
        self.pdf_listbox.delete(idx)
        self.pdf_listbox.insert(new_idx, value)
        self.pdf_listbox.selection_set(new_idx)
        self.pdf_listbox.activate(new_idx)

    def select_output(self) -> None:
        initial_name = self.output_var.get() or DEFAULT_OUTPUT
        file_path = filedialog.asksaveasfilename(
            title="Çıktı PDF dosyasını seç",
            defaultextension=".pdf",
            initialfile=initial_name,
            filetypes=[("PDF Dosyaları", "*.pdf")],
        )
        if file_path:
            self.output_var.set(file_path)

    # ------------------------------------------------------------- Merge --
    def merge_clicked(self) -> None:
        pdf_paths = list(self.pdf_listbox.get(0, END))
        if len(pdf_paths) < 2:
            messagebox.showwarning(
                "Uyarı", "En az iki PDF dosyası seçmelisiniz."
            )
            return

        output = self.output_var.get().strip()
        if not output:
            messagebox.showwarning("Uyarı", "Çıktı dosya adını giriniz.")
            return

        self.set_status("Birleştiriliyor...")
        threading.Thread(
            target=self._merge_worker,
            args=(pdf_paths, Path(output)),
            daemon=True,
        ).start()

    def _merge_worker(self, pdf_paths: list[str], output: Path) -> None:
        try:
            writer = PdfWriter()
            for path in pdf_paths:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("wb") as fh:
                writer.write(fh)
        except Exception as exc:  # pragma: no cover - Tk mesajları
            self.root.after(
                0,
                lambda: messagebox.showerror("Hata", f"Birleştirme başarısız: {exc}"),
            )
            self.set_status("Hata oluştu")
            return

        self.root.after(
            0,
            lambda: messagebox.showinfo(
                "Başarılı", f"PDF'ler '{output}' dosyasında birleştirildi."
            ),
        )
        self.set_status("Tamamlandı")

    def set_status(self, message: str) -> None:
        self.status_var.set(message)


def main() -> None:
    root = Tk()
    PDFMergeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

