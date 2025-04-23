# 📅 FastAPI asosidagi loyiha: "Online Kurs Platformasi"

## 🌟 Umumiy maqsad
Foydalanuvchilar ro'yxatdan o'tib, onlayn kurslarga yozilishi, video darslarni ko'rishi va izoh qoldirishi mumkin bo'lgan platforma yaratish.

## 🚀 Ishga tushirish bo'yicha qo'llanma

### 📋 Talablar
- Python 3.8+
- [Virtual environment](https://docs.python.org/3/library/venv.html)

### 🔧 O'rnatish

1. **Repositoryni klonlash**
   ```bash
   git clone <repository-url>
   cd FastApi-TZ
   ```

2. **Virtual muhitni yaratish va faollashtirish**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Kerakli kutubxonalarni o'rnatish**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ma'lumotlar bazasini yaratish**
   ```bash
   python init_db.py
   ```

5. **Serverni ishga tushirish**
   ```bash
   # Windows PowerShell
   .\run.ps1

   # Linux/Mac
   ./run.sh

   # Yoki to'g'ridan-to'g'ri
   uvicorn main:app --reload
   ```

6. **Dasturni ochish**
   Brauzerda [http://127.0.0.1:8000](http://127.0.0.1:8000) manzilini oching
   API dokumentatsiyasi: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 🔑 Test hisoblar
- **Admin:** 
  - Email: admin@example.com
  - Parol: adminpassword

- **Foydalanuvchi:** 
  - Email: test@example.com
  - Parol: testpassword

## 📚 API Endpointlar

### 👤 Foydalanuvchilar (Auth & Users)
- `POST /api/v1/login/access-token` - Tizimga kirish va JWT token olish
- `GET /api/v1/users/me` - Joriy foydalanuvchi ma'lumotlarini olish
- `PUT /api/v1/users/me` - Foydalanuvchi ma'lumotlarini yangilash
- `POST /api/v1/users/` - Yangi foydalanuvchi yaratish (ro'yxatdan o'tish)
- `GET /api/v1/users/` - Barcha foydalanuvchilar ro'yxatini olish (admin uchun)

### 📖 Kurslar (Courses)
- `GET /api/v1/courses/` - Barcha kurslar ro'yxatini olish
- `POST /api/v1/courses/` - Yangi kurs yaratish
- `GET /api/v1/courses/{id}` - Kurs ma'lumotlarini olish
- `PUT /api/v1/courses/{id}` - Kurs ma'lumotlarini yangilash
- `DELETE /api/v1/courses/{id}` - Kursni o'chirish
- `POST /api/v1/courses/{id}/enroll` - Kursga yozilish

### 📝 Darslar (Lessons)
- `GET /api/v1/lessons/` - Barcha darslar ro'yxatini olish
- `POST /api/v1/lessons/` - Yangi dars yaratish
- `GET /api/v1/lessons/{id}` - Dars ma'lumotlarini olish (izohlar va reytinglar bilan)
- `PUT /api/v1/lessons/{id}` - Dars ma'lumotlarini yangilash
- `DELETE /api/v1/lessons/{id}` - Darsni o'chirish

### 💬 Izohlar (Comments)
- `GET /api/v1/comments/` - Foydalanuvchi izohlarini olish
- `POST /api/v1/comments/` - Darsga izoh qoldirish
- `GET /api/v1/comments/by-lesson/{lesson_id}` - Dars bo'yicha izohlarni olish
- `DELETE /api/v1/comments/{id}` - Izohni o'chirish

### ⭐ Baholash (Ratings)
- `POST /api/v1/ratings/` - Darsni baholash
- `GET /api/v1/ratings/by-lesson/{lesson_id}` - Darsning barcha reytinglarini ko'rish
- `GET /api/v1/ratings/average/lesson/{lesson_id}` - Darsning o'rtacha reytingini olish
- `DELETE /api/v1/ratings/{id}` - Reytingni o'chirish

## 🏗️ Loyiha strukturasi
```
Online Kurs Platformasi/
├── app/                      # Asosiy dastur kodi
│   ├── api/                  # API endpointlar
│   │   └── api_v1/           # API v1 versiyasi
│   │       ├── endpoints/    # API endpointlar
│   │       └── api.py        # API router
│   ├── core/                 # Asosiy konfiguratsiya
│   ├── crud/                 # CRUD operatsiyalari
│   ├── db/                   # Ma'lumotlar bazasi
│   ├── models/               # SQLAlchemy modellar
│   ├── schemas/              # Pydantic schemalar
│   ├── services/             # Biznes logikasi
│   ├── tests/                # Testlar
│   └── utils/                # Yordamchi funksiyalar
├── .venv/                    # Virtual muhit
├── main.py                   # Dastur entry point
├── init_db.py                # Ma'lumotlar bazasini yaratish
├── requirements.txt          # Kerakli kutubxonalar
├── run.ps1                   # Windows uchun ishga tushirish
├── run.sh                    # Linux/Mac uchun ishga tushirish
└── README.md                 # Loyiha haqida ma'lumot
```

## 👥 Jamoalar va ularning vazifalari

### 1-jamoa: **Foydalanuvchilar boshqaruvi (Auth & Users)**
- Ro'yxatdan o'tish (register)
- Kirish (login, JWT token)
- Profilni ko'rish va tahrirlash
- Admin uchun foydalanuvchilar ro'yxati

### 2-jamoa: **Kurslar boshqaruvi**
- Kurslar CRUD
- Kursga yozilgan foydalanuvchilar
- Kurslar bo'yicha filter/search

### 3-jamoa: **Video darslar (Lessons)**
- Darslar CRUD
- Darsga video va matn biriktirish
- O'quvchilar uchun ko'rish interfeysi

### 4-jamoa: **Izohlar va baholash**
- Darsga izoh qoldirish
- 1-5 yulduzli baholash
- O'rtacha reyting hisoblash

### 5-jamoa: **Admin panel va statistika**
- Kurslar, foydalanuvchilar, darslar statistikasi
- Faollik monitoringi
- Eng ko'p ko'rilgan darslar

## 🔧 Texnologiyalar
- FastAPI
- SQLAlchemy
- SQLite (development) / PostgreSQL (production)
- Pydantic
- JWT autentifikatsiya

