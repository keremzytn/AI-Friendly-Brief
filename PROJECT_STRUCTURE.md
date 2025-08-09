
# Sports AI Platform - Proje Yapısı

## Backend (Python/Flask)
```
backend/
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── .env                   # Environment variables
├── models/               # Veritabanı modelleri
│   ├── __init__.py
│   ├── user.py           # Kullanıcı modeli
│   ├── training.py       # Antrenman modelleri
│   └── performance.py    # Performans modelleri
├── api/                  # API endpoint'leri
│   ├── __init__.py
│   ├── auth.py           # Kimlik doğrulama
│   ├── users.py          # Kullanıcı yönetimi
│   ├── training.py       # Antrenman yönetimi
│   └── performance.py    # Performans takibi
└── ai/                   # AI modülleri
    ├── __init__.py
    └── training_optimizer.py # AI antrenman optimizasyonu
```

## Frontend (Angular)
```
frontend/
├── package.json          # NPM bağımlılıkları
├── angular.json          # Angular konfigürasyonu
├── tsconfig.json         # TypeScript konfigürasyonu
├── src/
│   ├── index.html        # Ana HTML
│   ├── main.ts           # Angular bootstrap
│   ├── styles.scss       # Global stiller
│   └── app/
│       ├── app.module.ts # Ana modül
│       ├── components/   # UI bileşenleri
│       ├── services/     # API servisleri
│       ├── models/       # TypeScript interfaceleri
│       └── guards/       # Route guard'ları
```

## Özellikler

### 1. AI Destekli Antrenman Optimizasyonu
- Kullanıcı profiline göre kişiselleştirilmiş antrenman planları
- Tip 2 kas liflerini aktive eden egzersizler
- Mitokondri kapasitesini artıran aerobik çalışmalar
- Yaşa bağlı performans kaybını önleyici protokoller

### 2. Performans Takip Sistemi
- Dikey sıçrama (patlayıcı güç)
- 20m sprint (hız)
- T-test (çeviklik) 
- Nabız toparlanma süresi (kardiyorespiratuvar kapasite)
- AI analizi ile gelişim öngörüleri

### 3. Adaptif Program Güncelleme
- Haftalık performans testleri
- Otomatik program ayarlamaları
- İlerleme takibi ve hedef belirleme
- Risk faktörü analizi

### 4. Kullanıcı Arayüzü
- Modern, responsive tasarım
- Gerçek zamanlı dashboard
- Detaylı performans raporları
- Interaktif grafikler ve analizler
