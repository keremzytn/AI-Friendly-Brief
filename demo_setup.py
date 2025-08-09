#!/usr/bin/env python3
"""
Sports AI Platform Demo Setup Script
"""

import json
import os
from datetime import datetime

def create_sample_data():
    """Create sample data for demo purposes"""
    
    # Sample user data
    sample_user = {
        "email": "demo@sportsai.com",
        "first_name": "Demo",
        "last_name": "Kullanıcı",
        "age": 28,
        "height": 175.0,
        "weight": 75.0,
        "gender": "male",
        "sport_type": "football",
        "years_experience": 5,
        "fitness_level": "intermediate",
        "training_frequency": 4,
        "has_injuries": False
    }
    
    # Sample training plan data
    sample_training_plan = {
        "plan_name": "Week 1 - Strength Focus",
        "week_number": 1,
        "training_type": "strength",
        "target_adaptations": {
            "muscle_fiber_types": {
                "type_2_activation": 0.8,
                "type_1_endurance": 0.2
            },
            "energy_systems": {
                "phosphocreatine": 0.5,
                "glycolytic": 0.3,
                "oxidative": 0.2
            }
        },
        "expected_duration": 60,
        "difficulty_score": 7.5,
        "sessions": [
            {
                "session_name": "Training Day 1",
                "session_number": 1,
                "primary_focus": "Power",
                "warm_up_duration": 10,
                "main_duration": 40,
                "cool_down_duration": 10
            },
            {
                "session_name": "Training Day 2", 
                "session_number": 2,
                "primary_focus": "Strength",
                "warm_up_duration": 10,
                "main_duration": 40,
                "cool_down_duration": 10
            }
        ]
    }
    
    # Sample performance test data
    sample_performance_tests = [
        {
            "test_type": "vertical_jump",
            "primary_metric": "power",
            "primary_value": 45.5,
            "primary_unit": "cm",
            "test_date": datetime.utcnow().isoformat(),
            "improvement_from_baseline": 0.0,
            "percentile_rank": 65.5
        },
        {
            "test_type": "sprint_20m",
            "primary_metric": "speed", 
            "primary_value": 3.2,
            "primary_unit": "seconds",
            "test_date": datetime.utcnow().isoformat(),
            "improvement_from_baseline": 0.0,
            "percentile_rank": 72.3
        }
    ]
    
    return {
        "user": sample_user,
        "training_plan": sample_training_plan,
        "performance_tests": sample_performance_tests
    }

def generate_demo_api_responses():
    """Generate sample API responses for frontend testing"""
    
    sample_data = create_sample_data()
    
    # API responses structure
    api_responses = {
        "auth": {
            "login": {
                "message": "Login successful",
                "user": sample_data["user"],
                "access_token": "demo_access_token_here",
                "refresh_token": "demo_refresh_token_here"
            },
            "register": {
                "message": "User registered successfully",
                "user": sample_data["user"],
                "access_token": "demo_access_token_here",
                "refresh_token": "demo_refresh_token_here"
            }
        },
        "users": {
            "dashboard": {
                "user_profile": sample_data["user"],
                "stats": {
                    "total_trainings": 5,
                    "total_performances": 8,
                    "current_week": 2,
                    "profile_completeness": 95.5,
                    "bmi": 24.5,
                    "bmi_category": "Normal"
                },
                "recent_activity": [
                    {
                        "type": "training_session",
                        "title": "Training Day 1 - Power Focus",
                        "date": datetime.utcnow().isoformat(),
                        "status": "completed"
                    },
                    {
                        "type": "performance_test",
                        "title": "Vertical Jump Test",
                        "date": datetime.utcnow().isoformat(),
                        "status": "completed"
                    }
                ]
            }
        },
        "training": {
            "generate": {
                "message": "Training plan generated successfully",
                "plan": sample_data["training_plan"],
                "ai_analysis": {
                    "predicted_improvements": {
                        "power": {"expected_improvement_percentage": 8.5, "confidence_score": 0.82},
                        "strength": {"expected_improvement_percentage": 12.3, "confidence_score": 0.89},
                        "speed": {"expected_improvement_percentage": 5.2, "confidence_score": 0.76}
                    }
                }
            },
            "plans": {
                "plans": [sample_data["training_plan"]],
                "total_count": 1
            }
        },
        "performance": {
            "tests": {
                "tests": sample_data["performance_tests"],
                "total_count": 2
            },
            "analysis": {
                "overall_score": 78.5,
                "trends": {
                    "vertical_jump": {"trend": "improving", "slope": 0.15},
                    "sprint_20m": {"trend": "stable", "slope": 0.02}
                },
                "strengths": [
                    {"metric": "power", "progress": 85.2, "improvement": 8.5}
                ],
                "weaknesses": [
                    {"metric": "endurance", "progress": 45.8, "improvement": -2.1}
                ]
            }
        }
    }
    
    return api_responses

def create_demo_files():
    """Create demo files and documentation"""
    
    # Create demo data directory
    os.makedirs("demo_data", exist_ok=True)
    
    # Generate sample data
    demo_data = generate_demo_api_responses()
    
    # Save to JSON file
    with open("demo_data/sample_api_responses.json", "w", encoding="utf-8") as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)
    
    # Create project structure documentation
    project_structure = """
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
"""
    
    with open("PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(project_structure)
    
    # Create API documentation
    api_docs = """
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
"""
    
    with open("API_DOCUMENTATION.md", "w", encoding="utf-8") as f:
        f.write(api_docs)
    
    print("✅ Demo files created successfully!")
    print(f"📁 Demo data: demo_data/sample_api_responses.json")
    print(f"📋 Project structure: PROJECT_STRUCTURE.md")
    print(f"📖 API documentation: API_DOCUMENTATION.md")

def main():
    """Main demo setup function"""
    print("🚀 Sports AI Platform Demo Setup")
    print("=" * 50)
    
    create_demo_files()
    
    print("\n📊 Sample Data Generated:")
    demo_data = generate_demo_api_responses()
    
    print(f"👤 User: {demo_data['auth']['login']['user']['first_name']} {demo_data['auth']['login']['user']['last_name']}")
    print(f"🏃 Sport: {demo_data['auth']['login']['user']['sport_type']}")
    print(f"💪 Fitness Level: {demo_data['auth']['login']['user']['fitness_level']}")
    print(f"📈 Training Plans: {len(demo_data['training']['plans']['plans'])}")
    print(f"🎯 Performance Tests: {len(demo_data['performance']['tests']['tests'])}")
    
    print("\n🎉 Demo setup completed!")
    print("\nNext steps:")
    print("1. Install backend dependencies: pip install -r backend/requirements.txt")
    print("2. Run backend: cd backend && python app.py")
    print("3. Install frontend dependencies: cd frontend && npm install")
    print("4. Run frontend: cd frontend && ng serve")

if __name__ == "__main__":
    main()