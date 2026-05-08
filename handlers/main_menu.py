from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import get_statistics
from keyboards.keyboards import main_menu_kb, orders_menu_kb, products_menu_kb, categories_menu_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(CommandStart())
async def cmd_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda bu botga kirish huquqi yo'q!")
        return

    await message.answer(
        f"👋 Xush kelibsiz, <b>{message.from_user.first_name}</b>!\n\n"
        "🤖 <b>Admin Panel</b> — restoran boshqaruv tizimi\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = await get_statistics()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"📦 Jami buyurtmalar: <b>{stats['total_orders']}</b>\n"
        f"🆕 Yangi buyurtmalar: <b>{stats['new_orders']}</b>\n"
        f"💰 Jami daromad: <b>{int(stats['total_revenue']):,} so'm</b>\n"
        f"🍔 Aktiv mahsulotlar: <b>{stats['active_products']}</b>\n"
        f"📂 Aktiv kategoriyalar: <b>{stats['active_categories']}</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())


@router.message(F.text == "📦 Buyurtmalar")
async def orders_section(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📦 <b>Buyurtmalar</b>\n\nQaysi buyurtmalarni ko'rmoqchisiz?",
                         reply_markup=orders_menu_kb(), parse_mode="HTML")


@router.message(F.text == "🍔 Mahsulotlar")
async def products_section(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🍔 <b>Mahsulotlar bo'limi</b>",
                         reply_markup=products_menu_kb(), parse_mode="HTML")


@router.message(F.text == "📂 Kategoriyalar")
async def categories_section(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📂 <b>Kategoriyalar bo'limi</b>",
                         reply_markup=categories_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=main_menu_kb()
    )
    await callback.answer()
