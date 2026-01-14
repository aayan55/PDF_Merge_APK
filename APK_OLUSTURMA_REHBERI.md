# APK Oluşturma Rehberi (Windows'ta WSL Kullanmadan)

Windows'ta WSL kullanmadan APK oluşturmanın en pratik yolu **GitHub Actions** kullanmaktır.

## Seçenek 1: GitHub Actions (Önerilen - Ücretsiz)

### Avantajlar:
- ✅ Windows'ta çalışır (tarayıcıdan yönetilir)
- ✅ Ücretsiz (herkese açık repolar için)
- ✅ Otomatik APK oluşturma
- ✅ APK dosyasını indirebilirsiniz

### Adımlar:

#### 1. GitHub'da Repository Oluşturun

1. [GitHub](https://github.com) hesabı oluşturun (yoksa)
2. Yeni bir repository oluşturun
3. Repository'yi local'e clone edin veya mevcut klasörünüzü git repository'si yapın

#### 2. Projeyi GitHub'a Yükleyin

```bash
# Mevcut klasörünüzde
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
git push -u origin main
```

#### 3. GitHub Actions'ı Tetikleyin

1. GitHub'da repository'nize gidin
2. **Actions** sekmesine tıklayın
3. **Build Android APK** workflow'unu seçin
4. **Run workflow** butonuna tıklayın
5. İşlem tamamlanınca (5-15 dakika) **Artifacts** bölümünden APK'yı indirin

#### 4. APK'yı İndirin

1. Actions sekmesinde tamamlanan workflow'a tıklayın
2. **Artifacts** bölümünden **pdf-merge-apk** dosyasını indirin
3. ZIP dosyasını açın ve APK'yı çıkarın

---

## Seçenek 2: Docker Desktop (Windows'ta)

### Gereksinimler:
- Docker Desktop for Windows

### Adımlar:

#### 1. Docker Desktop'u Kurun

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) indirin
2. Kurun ve başlatın

#### 2. Docker Container'ı Çalıştırın

```powershell
# Proje klasörünüzde
docker run -it --rm -v ${PWD}:/home/user/hostcwd kivy/buildozer buildozer android debug
```

**Not:** Bu yöntem için özel bir Docker image gerekiyor. Daha kolay olan GitHub Actions'ı öneririm.

---

## Seçenek 3: Bulut VM Kullanımı (Geçici)

1. Ücretsiz bulut VM servisleri kullanabilirsiniz (Google Cloud, AWS free tier)
2. Linux VM oluşturup Buildozer kurun
3. Projenizi yükleyip APK oluşturun

**Not:** Bu yöntem daha karmaşık ve zaman alıcıdır.

---

## Hızlı Başlangıç (GitHub Actions)

Eğer GitHub kullanmak istiyorsanız:

1. `git init` (klasörünüzde)
2. GitHub'da repository oluşturun
3. Dosyaları push edin
4. Actions sekmesinden APK oluşturun
5. APK'yı indirin

**Soru:** GitHub kullanmak ister misiniz, yoksa başka bir yöntem mi denemek istersiniz?

