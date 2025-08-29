# 🎵 SoundCloud Downloader

Утилита с графическим интерфейсом для скачивания лайкнутых треков с [SoundCloud](https://soundcloud.com/) через `scdl`.

## 🚀 Возможности
- Загрузка всех лайков по имени пользователя
- Выбор папки для загрузки
- Поддержка высокого качества (320kbps)
- Создание `.m3u` плейлиста
- Удобный лог и статус в GUI
- Тёмная тема с зелёными акцентами

## 📦 Установка
1. Установите Python **3.7+**
2. Установите зависимости:
   ```bash
   pip install scdl
   ```
3. Запустите:
   ```bash
   python scdl_downloader.py
   ```

## 🖥️ Готовая версия (.exe)
Скачайте последнюю версию из [Releases](https://github.com/IntalHub/SoundCloudDownloader/releases).

## 📷 Скриншоты
![main ui](screenshots/ui.png)

## 🔧 Сборка exe
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile soundcloud_downloader.py
```

## 👤 Автор
**Intally**  
📜 Лицензия: MIT
