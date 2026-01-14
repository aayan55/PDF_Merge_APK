"""Kivy tabanlı PDF birleştirme aracı - Windows ve Android uyumlu."""

from __future__ import annotations

import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

# Renk şeması - Açık tema
COLOR_BG = (0.96, 0.96, 0.96, 1)  # Açık gri arka plan
COLOR_TEXT = (0.15, 0.15, 0.15, 1)  # Koyu metin
COLOR_TEXT_SECONDARY = (0.4, 0.4, 0.4, 1)  # İkincil metin
COLOR_BUTTON = (0.26, 0.58, 0.84, 1)  # Açık mavi buton
COLOR_BUTTON_PRESSED = (0.2, 0.48, 0.74, 1)  # Basılı buton
COLOR_SELECTED = (0.7, 0.85, 1.0, 1)  # Seçili öğe arka plan
COLOR_BORDER = (0.8, 0.8, 0.8, 1)  # Kenar çizgisi

try:
    from plyer import filechooser
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

from pypdf import PdfReader, PdfWriter

WINDOW_TITLE = "PDF Birleştirme Aracı"
DEFAULT_OUTPUT = "birlesik.pdf"


class PDFMergeApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pdf_files = []
        self.selected_index = None
        
        # Ekran boyutuna göre ölçek faktörü
        # 480px genişlik için 1.0, diğerleri için orantılı
        try:
            screen_width = Window.width if Window.width > 0 else 480
        except:
            screen_width = 480
        self.scale = max(0.7, min(1.5, screen_width / 480.0))  # 0.7 ile 1.5 arası

    def build(self):
        self.title = WINDOW_TITLE
        
        # Arka plan rengini ayarla
        Window.clearcolor = COLOR_BG
        
        # Ekran boyutunu tekrar kontrol et (Android'de build zamanında doğru olabilir)
        try:
            screen_width = Window.width if Window.width > 0 else 480
        except:
            screen_width = 480
        self.scale = max(0.7, min(1.5, screen_width / 480.0))
        
        padding = int(10 * self.scale)
        spacing = int(10 * self.scale)
        root = BoxLayout(orientation="vertical", padding=padding, spacing=spacing)

        # Başlık
        title_label = Label(
            text="PDF Birleştirme Aracı",
            size_hint_y=None,
            height=int(40 * self.scale),
            font_size=int(20 * self.scale),
            bold=True,
            color=COLOR_TEXT
        )
        root.add_widget(title_label)

        # Dosya listesi
        list_label = Label(
            text="Seçilen PDF Dosyaları:",
            size_hint_y=None,
            height=int(30 * self.scale),
            font_size=int(14 * self.scale),
            color=COLOR_TEXT
        )
        root.add_widget(list_label)

        # ScrollView ile liste
        scroll = ScrollView()
        self.file_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter("height"))
        scroll.add_widget(self.file_list)
        root.add_widget(scroll)

        # Kontrol butonları
        control_layout = BoxLayout(size_hint_y=None, height=int(40 * self.scale), spacing=int(5 * self.scale))
        
        btn_add = Button(text="Dosya Ekle", on_press=self.add_files, font_size=int(14 * self.scale))
        btn_remove = Button(text="Seçileni Sil", on_press=self.remove_selected, font_size=int(14 * self.scale))
        btn_clear = Button(text="Listeyi Temizle", on_press=self.clear_list, font_size=int(14 * self.scale))
        
        control_layout.add_widget(btn_add)
        control_layout.add_widget(btn_remove)
        control_layout.add_widget(btn_clear)
        root.add_widget(control_layout)

        # Sıralama butonları
        order_layout = BoxLayout(size_hint_y=None, height=int(40 * self.scale), spacing=int(5 * self.scale))
        btn_up = Button(text="Yukarı", on_press=lambda x: self.move_item(-1), font_size=int(14 * self.scale))
        btn_down = Button(text="Aşağı", on_press=lambda x: self.move_item(1), font_size=int(14 * self.scale))
        order_layout.add_widget(btn_up)
        order_layout.add_widget(btn_down)
        root.add_widget(order_layout)

        # Çıktı ayarları
        output_label = Label(
            text="Çıktı Dosya Adı:",
            size_hint_y=None,
            height=int(30 * self.scale),
            font_size=int(14 * self.scale),
            color=COLOR_TEXT
        )
        root.add_widget(output_label)

        output_layout = BoxLayout(size_hint_y=None, height=int(40 * self.scale), spacing=int(5 * self.scale))
        self.output_input = TextInput(
            text=DEFAULT_OUTPUT,
            multiline=False,
            foreground_color=COLOR_TEXT,
            background_color=(1, 1, 1, 1),
            font_size=int(14 * self.scale)
        )
        btn_output = Button(text="Kaydet...", size_hint_x=None, width=int(100 * self.scale), on_press=self.select_output, font_size=int(14 * self.scale))
        output_layout.add_widget(self.output_input)
        output_layout.add_widget(btn_output)
        root.add_widget(output_layout)

        # Birleştir butonu ve durum
        bottom_layout = BoxLayout(size_hint_y=None, height=int(50 * self.scale), spacing=int(10 * self.scale))
        self.status_label = Label(text="Hazır", size_hint_x=None, width=int(200 * self.scale), color=COLOR_TEXT, font_size=int(14 * self.scale))
        btn_merge = Button(text="Birleştir", size_hint_x=None, width=int(150 * self.scale), on_press=self.merge_clicked, font_size=int(14 * self.scale))
        bottom_layout.add_widget(self.status_label)
        bottom_layout.add_widget(btn_merge)
        root.add_widget(bottom_layout)

        return root

    def add_files(self, instance):
        """PDF dosyaları ekle."""
        if not PLYER_AVAILABLE:
            self.show_error("Dosya seçici bulunamadı. Lütfen plyer kurun: pip install plyer")
            return
        
        try:
            result = filechooser.open_file(
                title="PDF dosyalarını seç",
                filters=[("PDF Dosyaları", "*.pdf")]
            )
            if result:
                paths = result if isinstance(result, list) else [result]
                for path in paths:
                    if path not in self.pdf_files:
                        self.pdf_files.append(path)
                self.update_file_list()
        except Exception as e:
            self.show_error(f"Dosya seçme hatası: {e}")

    def remove_selected(self, instance):
        """Seçili dosyayı sil."""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.pdf_files):
            self.pdf_files.pop(self.selected_index)
            self.selected_index = None
            self.update_file_list()
        else:
            self.show_info("Lütfen silmek için bir dosya seçin (üzerine tıklayın)")

    def clear_list(self, instance):
        """Listeyi temizle."""
        self.pdf_files = []
        self.selected_index = None
        self.update_file_list()

    def move_item(self, direction):
        """Dosya sırasını değiştir."""
        if self.selected_index is None:
            self.show_info("Lütfen taşımak için bir dosya seçin")
            return
        idx = self.selected_index
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self.pdf_files):
            return
        self.pdf_files[idx], self.pdf_files[new_idx] = self.pdf_files[new_idx], self.pdf_files[idx]
        self.selected_index = new_idx
        self.update_file_list()

    def select_output(self, instance):
        """Çıktı dosya konumunu seç."""
        if not PLYER_AVAILABLE:
            self.show_error("Dosya seçici bulunamadı. Lütfen plyer kurun: pip install plyer")
            return
        
        try:
            result = filechooser.save_file(
                title="Çıktı PDF dosyasını seç",
                filters=[("PDF Dosyaları", "*.pdf")]
            )
            if result:
                path = result[0] if isinstance(result, list) else result
                self.output_input.text = path
        except Exception as e:
            self.show_error(f"Çıktı seçme hatası: {e}")

    def on_file_click(self, instance, index):
        """Dosya seçildiğinde."""
        self.selected_index = index
        self.update_file_list()

    def update_file_list(self):
        """Dosya listesini güncelle."""
        self.file_list.clear_widgets()
        for i, path in enumerate(self.pdf_files):
            filename = Path(path).name
            label = Label(
                text=f"{i+1}. {filename}",
                size_hint_y=None,
                height=int(30 * self.scale),
                text_size=(None, None),
                halign="left",
                color=COLOR_TEXT,
                font_size=int(14 * self.scale)
            )
            label.bind(on_touch_down=lambda w, t, idx=i: self.on_file_click(w, idx) if w.collide_point(*t.pos) else False)
            if i == self.selected_index:
                label.color = (0.2, 0.5, 0.8, 1)  # Seçili öğe için mavi ton
            self.file_list.add_widget(label)

    def merge_clicked(self, instance):
        """PDF'leri birleştir."""
        if len(self.pdf_files) < 2:
            self.show_error("En az iki PDF dosyası seçmelisiniz.")
            return

        output = self.output_input.text.strip()
        if not output:
            self.show_error("Çıktı dosya adını giriniz.")
            return

        self.status_label.text = "Birleştiriliyor..."
        instance.disabled = True
        
        threading.Thread(
            target=self._merge_worker,
            args=(self.pdf_files.copy(), Path(output), instance),
            daemon=True,
        ).start()

    def _merge_worker(self, pdf_paths: list[str], output: Path, merge_button) -> None:
        """PDF birleştirme işlemini gerçekleştir."""
        try:
            writer = PdfWriter()
            for path in pdf_paths:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("wb") as fh:
                writer.write(fh)
            
            def show_success(dt):
                self.show_success(f"PDF'ler '{output.name}' dosyasında birleştirildi.")
                self.status_label.text = "Tamamlandı"
                merge_button.disabled = False
            
            Clock.schedule_once(show_success, 0)
        except Exception as exc:
            def show_err(dt):
                self.show_error(f"Birleştirme başarısız: {exc}")
                self.status_label.text = "Hata oluştu"
                merge_button.disabled = False
            Clock.schedule_once(show_err, 0)

    def show_error(self, message: str):
        """Hata popup göster."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message, text_size=(None, None)))
        btn = Button(text="Tamam", size_hint_y=None, height=40)
        popup = Popup(
            title="Hata",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def show_info(self, message: str):
        """Bilgi popup göster."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message, text_size=(None, None)))
        btn = Button(text="Tamam", size_hint_y=None, height=40)
        popup = Popup(
            title="Bilgi",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def show_success(self, message: str):
        """Başarı popup göster."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=message, text_size=(None, None)))
        btn = Button(text="Tamam", size_hint_y=None, height=40)
        popup = Popup(
            title="Başarılı",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()


def main() -> None:
    PDFMergeApp().run()


if __name__ == "__main__":
    main()
