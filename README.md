# 🤖 Restaurant Admin Bot

Telegram orqali restoran boshqaruv tizimi (aiogram 3 + MySQL).

## 📋 Imkoniyatlar

- 📦 **Buyurtmalar** — ko'rish, status o'zgartirish, o'chirish
- 🍔 **Mahsulotlar** — qo'shish, o'chirish, aktiv/nofaol qilish
- 📂 **Kategoriyalar** — qo'shish, tahrirlash, o'chirish
- 📊 **Statistika** — umumiy ma'lumotlar

## ⚙️ O'rnatish

### 1. Repozitoriyani klonlash
```bash
git clone https://github.com/yourusername/telegram-admin-bot.git
cd telegram-admin-bot
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. `.env` fayl yaratish
```bash
cp .env.example .env
```
`.env` faylni oching va qiymatlarni to'ldiring:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ck540806_test
```

### 5. Botni ishga tushirish
```bash
python bot.py
```

## 🗄️ Ma'lumotlar bazasi tuzilishi

```sql
-- categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url TEXT,
    badge VARCHAR(50),
    is_active TINYINT(1) DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- orders
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(200),
    customer_phone VARCHAR(50),
    total_price DECIMAL(10,2) DEFAULT 0,
    status ENUM('new','confirmed','delivering','delivered','cancelled') DEFAULT 'new',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- order_items
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200),
    price DECIMAL(10,2) NOT NULL,
    qty INT DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## 📁 Fayl tuzilishi

```
telegram-admin-bot/
├── bot.py              # Asosiy fayl
├── config.py           # Sozlamalar
├── database.py         # MySQL operatsiyalari
├── requirements.txt    # Kutubxonalar
├── .env.example        # Muhit o'zgaruvchilari namunasi
├── .gitignore
├── handlers/
│   ├── main_menu.py    # Asosiy menyu
│   ├── orders.py       # Buyurtmalar
│   ├── products.py     # Mahsulotlar
│   └── categories.py   # Kategoriyalar
└── keyboards/
    └── keyboards.py    # Barcha klaviaturalar
```

## 🚀 GitHub'ga yuklash

```bash
git init
git add .
git commit -m "Initial commit: Restaurant Admin Bot"
git branch -M main
git remote add origin https://github.com/yourusername/telegram-admin-bot.git
git push -u origin main
```

## 📞 Admin ID olish

[@userinfobot](https://t.me/userinfobot) botga `/start` yuboring — u sizning Telegram ID'ingizni ko'rsatadi.
