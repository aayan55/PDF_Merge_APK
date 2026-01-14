# PDF Birleştirme Aracı - Test Rehberi

## Windows'ta Test Etme

Kivy uygulaması Windows'ta da çalışır! Android cihazınız olmadan test edebilirsiniz.

### 1. Gerekli Paketleri Kurun

```bash
pip install -r requirements.txt
```

veya sadece Kivy için:
```bash
pip install kivy pypdf
```

**Not:** Windows'ta test için `plyer` gerekli değildir - Tkinter otomatik kullanılır.

### 2. Uygulamayı Çalıştırın

```bash
python pdf_merge_gui_kivy.py
```

### 3. Özellikler

- ✅ Dosya Ekle: PDF dosyalarını seçebilirsiniz
- ✅ Seçileni Sil: Listeden dosya silebilirsiniz
- ✅ Listeyi Temizle: Tüm dosyaları temizler
- ✅ Yukarı/Aşağı: Dosya sıralamasını değiştirebilirsiniz
- ✅ Birleştir: PDF'leri birleştirir

## Android için APK Oluşturma

### Gereksinimler

1. **Linux veya WSL2** (Windows Subsystem for Linux) - Buildozer Linux gerektirir
2. **Buildozer** kurulumu
3. **Android SDK** ve **NDK**

### Adımlar

#### 1. WSL2 Kurulumu (Windows'ta)

```powershell
wsl --install
```

#### 2. Linux'ta Buildozer Kurulumu

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

pip3 install --user buildozer
```

#### 3. Buildozer Spec Dosyası Oluştur

```bash
buildozer init
```

`buildozer.spec` dosyasını düzenle:
- `title = PDF Birleştirme`
- `package.name = pdfmerge`
- `requirements = python3,kivy,plyer,pypdf`

#### 4. APK Oluştur

```bash
buildozer android debug
```

APK dosyası `bin/` klasöründe oluşturulur.

## Android Emulator ile Test

### Android Studio Kurulumu

1. [Android Studio](https://developer.android.com/studio) indirin ve kurun
2. Android Studio'yu açın
3. **Tools > Device Manager** menüsünden emülatör oluşturun
4. Emülatörü başlatın

### APK Yükleme

```bash
adb install bin/pdfmerge-0.1-arm64-v8a-debug.apk
```

veya APK'yı emülatöre sürükleyip bırakın.

## Alternatif: KivyMD (Material Design)

Daha modern bir görünüm için KivyMD kullanabilirsiniz:

```bash
pip install kivymd
```

## Sorun Giderme

### Windows'ta "plyer" hatası
- Sorun değil! Tkinter otomatik kullanılır.

### Buildozer hatası
- WSL2 veya Linux kullanın (Buildozer Windows'ta çalışmaz)

### Android'de dosya seçici çalışmıyor
- `plyer` paketinin kurulu olduğundan emin olun
- Android izinlerini kontrol edin (Manifest)

