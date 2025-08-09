
# Sports AI Platform - API Dokümantasyonu

## Kimlik Doğrulama Endpoints

### POST /api/auth/register
Yeni kullanıcı kaydı
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "first_name": "Ad",
  "last_name": "Soyad",
  "age": 28,
  "height": 175.0,
  "weight": 75.0,
  "gender": "male",
  "sport_type": "football",
  "years_experience": 5,
  "fitness_level": "intermediate",
  "training_frequency": 4
}
```

### POST /api/auth/login
Kullanıcı girişi
```json
{
  "email": "user@example.com", 
  "password": "secure_password"
}
```

## Antrenman Endpoints

### POST /api/training/generate
AI destekli antrenman planı oluşturma
```json
{
  "week_number": 1
}
```

### GET /api/training/plans
Kullanıcının antrenman planları

### GET /api/training/plans/{id}
Belirli antrenman planı detayları

## Performans Endpoints

### POST /api/performance/tests
Performans test sonucu kaydetme
```json
{
  "test_type": "vertical_jump",
  "primary_metric": "power", 
  "primary_value": 45.5,
  "primary_unit": "cm"
}
```

### GET /api/performance/analysis
Kapsamlı performans analizi

### GET /api/performance/baselines
Kullanıcının performans baseline'ları

## Kullanıcı Endpoints

### GET /api/users/dashboard
Dashboard verileri

### GET /api/users/stats
Detaylı kullanıcı istatistikleri
