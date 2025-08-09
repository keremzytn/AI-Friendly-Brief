Proje Tanımı (AI-Friendly Brief)

Amaç:
Bu proje, sporcularda yaşa bağlı performans kaybını önlemek ve özellikle tip 2 kas liflerini ile mitokondri hacmini korumak amacıyla geliştirilmiş bir yapay zekâ destekli web platformudur.
Sistem, spor branşına özgü antrenman protokollerini kullanarak kişiselleştirilmiş performans artırma programları üretir ve zamanla kullanıcının gelişimine göre uyum sağlar.

⸻

Nasıl Çalışır?
	1.	Veri Toplama
	•	Kullanıcı sisteme yaş, boy, kilo, spor branşı, pozisyon, antrenman geçmişi gibi bilgileri girer.
	•	Opsiyonel olarak nabız, GPS, dikey sıçrama yüksekliği gibi sensör verileri de eklenebilir.
	2.	Yapay Zekâ Analizi
	•	Sistem, makine öğrenmesi algoritmaları ile kullanıcının mevcut performans profilini çıkarır.
	•	Yaş, fiziksel özellikler ve spor branşına özel gereklilikler dikkate alınarak en uygun yüklenme tipi belirlenir.
	3.	Program Üretimi
	•	Tip 2 kas liflerini aktive eden yüksek yoğunluklu kısa süreli egzersizler
	•	Mitokondri kapasitesini artıran orta tempo aerobik çalışmalar
	•	Branşa özgü çeviklik, sürat ve güç odaklı hareketler
	•	Test bazlı geri bildirim sistemi ile her hafta güncellenen program
	4.	Gelişim Takibi
	•	Haftalık ölçümler:
	•	Dikey sıçrama (patlayıcı güç)
	•	20 m sprint (hız)
	•	T-test (çeviklik)
	•	Nabız toparlanma süresi (kardiyorespiratuvar kapasite)
	•	Sonuçlar yapay zekâya geri beslenir → program adaptif şekilde güncellenir.

⸻

Teknoloji ve Altyapı
	•	Frontend: Web tabanlı kullanıcı arayüzü (HTML/CSS/JS, ileride React/Vue)
	•	Backend: Python (Flask/Django) + AI model servisi
	•	AI Modeli:
	•	Kullanıcı geçmiş verilerinden progression prediction
	•	Egzersiz yüklenme optimizasyonu
	•	Antrenman-performans ilişkisini modelleyen regresyon ve sınıflandırma algoritmaları
	•	Veritabanı: Kullanıcı profilleri, antrenman geçmişi, test sonuçları (PostgreSQL/MySQL)
	•	Opsiyonel Sensör Entegrasyonu: Nabız bandı, hız sensörü, dikey sıçrama ölçer

⸻

Proje Çıktıları
	•	Kişiye özel, haftalık güncellenen antrenman planları
	•	Performans gelişim raporları
	•	Branşa özgü egzersiz kütüphanesi

⸻

💡 Kısa Özet Tek Cümlede:
“Bu sistem, sporcuların yaşlanmayla gelen performans düşüşünü önlemek için, bireysel veriye dayalı, yapay zekâ destekli ve haftalık olarak güncellenen antrenman programları sunar.”
