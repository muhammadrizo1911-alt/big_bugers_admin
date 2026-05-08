from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ─── MAIN MENU ───────────────────────────────────────────────────────────────

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Buyurtmalar"), KeyboardButton(text="🍔 Mahsulotlar")],
            [KeyboardButton(text="📂 Kategoriyalar"), KeyboardButton(text="📊 Statistika")],
        ],
        resize_keyboard=True
    )


# ─── ORDERS ──────────────────────────────────────────────────────────────────

def orders_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆕 Yangi", callback_data="orders_new"),
            InlineKeyboardButton(text="✅ Tasdiqlangan", callback_data="orders_confirmed"),
        ],
        [
            InlineKeyboardButton(text="🚚 Yetkazilmoqda", callback_data="orders_delivering"),
            InlineKeyboardButton(text="✔️ Yetkazilgan", callback_data="orders_delivered"),
        ],
        [InlineKeyboardButton(text="📋 Barchasi", callback_data="orders_all")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])


def order_detail_kb(order_id: int, status: str):
    builder = InlineKeyboardBuilder()

    status_buttons = {
        "new": ("✅ Tasdiqlash", "confirmed"),
        "confirmed": ("🚚 Yetkazishga berish", "delivering"),
        "delivering": ("✔️ Yetkazildi", "delivered"),
    }

    if status in status_buttons:
        text, next_status = status_buttons[status]
        builder.button(
            text=text,
            callback_data=f"order_status_{order_id}_{next_status}"
        )

    builder.button(text="❌ O'chirish", callback_data=f"order_delete_{order_id}")
    builder.button(text="🔙 Orqaga", callback_data="orders_all")
    builder.adjust(1)
    return builder.as_markup()


# ─── PRODUCTS ────────────────────────────────────────────────────────────────

def products_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Mahsulotlar ro'yxati", callback_data="products_list")],
        [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="product_add")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])


def product_detail_kb(product_id: int, is_active: int):
    status_text = "🔴 O'chirish" if is_active else "🟢 Yoqish"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status_text, callback_data=f"product_toggle_{product_id}")],
        [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"product_delete_{product_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="products_list")],
    ])


def products_list_kb(products: list):
    builder = InlineKeyboardBuilder()
    for p in products:
        status = "🟢" if p["is_active"] else "🔴"
        builder.button(
            text=f"{status} {p['name']} - {int(p['price'])} so'm",
            callback_data=f"product_view_{p['id']}"
        )
    builder.button(text="➕ Yangi qo'shish", callback_data="product_add")
    builder.button(text="🔙 Orqaga", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()


def categories_select_kb(categories: list):
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(text=c["name"], callback_data=f"select_cat_{c['id']}")
    builder.button(text="❌ Bekor qilish", callback_data="products_list")
    builder.adjust(2)
    return builder.as_markup()


# ─── CATEGORIES ──────────────────────────────────────────────────────────────

def categories_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Kategoriyalar ro'yxati", callback_data="categories_list")],
        [InlineKeyboardButton(text="➕ Yangi kategoriya qo'shish", callback_data="category_add")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])


def categories_list_kb(categories: list):
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(
            text=f"{c.get('icon', '')} {c['name']}",
            callback_data=f"category_view_{c['id']}"
        )
    builder.button(text="➕ Yangi qo'shish", callback_data="category_add")
    builder.button(text="🔙 Orqaga", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()


def category_detail_kb(cat_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"category_edit_{cat_id}")],
        [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"category_delete_{cat_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="categories_list")],
    ])


def confirm_kb(action: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_action"),
        ]
    ])
