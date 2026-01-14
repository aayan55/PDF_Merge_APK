; Buildozer ile Kivy tabanlı PDF birleştirme aracı için APK yapı dosyası

[app]
title = PDF Birleştirme
package.name = pdfmerge
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

; Ana giriş dosyan (Kivy arayüzü)
main = pdf_merge_gui_kivy.py

; Uygulama sürümü
version = 0.1

; Android için gereken Python bağımlılıkları
requirements = python3,kivy,plyer,pypdf

; İkon ve splash isteğe bağlı, şimdilik default
icon.filename =
presplash.filename =

orientation = portrait

; Android izinleri (PDF okuma/yazma için depolama erişimi)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

; Android minimum / target API
android.minapi = 21
android.api = 33

; Desteklenen mimariler
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1

; Varsayılan: debug APK üret
; build komutu: buildozer android debug


