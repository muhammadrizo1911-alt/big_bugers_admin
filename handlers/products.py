from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    get_all_products, get_product_by_id, add_product,
    delete_product, toggle_product_status, get_all_categories
)
from keyboards.keyboards import (
    products_menu_kb, products_list_kb, product_detail_kb, categories_select_kb
)

router = Router()


class AddProduct(StatesGroup):
    category = State()
    name = State()
    description = State()
    price = State()
    image_url = State()
    badge = State()


# ─── LIST ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "products_list")
async def products_list(callback: CallbackQuery):
    products = await get_all_products()
    if not products:
        await callback.message.edit_text(
            "📭 Mahsulotlar yo'q.",
            reply_markup=products_menu_kb()
        )
        return

    await callback.message.edit_text(
        f"🍔 <b>Mahsulotlar</b> ({len(products)} ta)\n\nMahsulotni tanlang:",
        reply_markup=products_list_kb(products),
        parse_mode="HTML"
    )
    await callback.answer()


# ─── VIEW ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("product_view_"))
async def product_view(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    p = await get_product_by_id(product_id)

    if not p:
        await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
        return

    status = "🟢 Aktiv" if p["is_active"] else "🔴 Nofaol"
    text = (
        f"🍔 <b>{p['name']}</b>\n\n"
        f"📝 {p['description']}\n\n"
        f"💰 Narx: <b>{int(p['price']):,} so'm</b>\n"
        f"🏷 Badge: <b>{p.get('badge', '-')}</b>\n"
        f"📌 Status: <b>{status}</b>\n"
        f"🆔 ID: {p['id']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=product_detail_kb(product_id, p["is_active"]),
        parse_mode="HTML"
    )
    await callback.answer()


# ─── TOGGLE ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("product_toggle_"))
async def product_toggle(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    await toggle_product_status(product_id)
    p = await get_product_by_id(product_id)

    status = "🟢 Aktiv" if p["is_active"] else "🔴 Nofaol"
    await callback.answer(f"Status o'zgartirildi: {status}", show_alert=True)

    text = (
        f"🍔 <b>{p['name']}</b>\n\n"
        f"📝 {p['description']}\n\n"
        f"💰 Narx: <b>{int(p['price']):,} so'm</b>\n"
        f"🏷 Badge: <b>{p.get('badge', '-')}</b>\n"
        f"📌 Status: <b>{status}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=product_detail_kb(product_id, p["is_active"]),
        parse_mode="HTML"
    )


# ─── DELETE ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("product_delete_"))
async def product_delete(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    await delete_product(product_id)
    await callback.answer("🗑 Mahsulot o'chirildi!", show_alert=True)

    products = await get_all_products()
    await callback.message.edit_text(
        f"🍔 <b>Mahsulotlar</b> ({len(products)} ta)\n\nMahsulotni tanlang:",
        reply_markup=products_list_kb(products),
        parse_mode="HTML"
    )


# ─── ADD ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "product_add")
async def product_add_start(callback: CallbackQuery, state: FSMContext):
    categories = await get_all_categories()
    await callback.message.edit_text(
        "➕ <b>Yangi mahsulot qo'shish</b>\n\nKategoriyani tanlang:",
        reply_markup=categories_select_kb(categories),
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.category)
    await callback.answer()


@router.callback_query(AddProduct.category, F.data.startswith("select_cat_"))
async def product_add_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    await callback.message.edit_text("📝 Mahsulot nomini kiriting:")
    await state.set_state(AddProduct.name)
    await callback.answer()


@router.message(AddProduct.name)
async def product_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📄 Tavsif kiriting:")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def product_add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Narxni kiriting (faqat son, masalan: 35000):")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def product_add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "").replace(" ", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat son kiriting:")
        return

    await state.update_data(price=price)
    await message.answer("🖼 Rasm URL manzilini kiriting (yoki — kiriting):")
    await state.set_state(AddProduct.image_url)


@router.message(AddProduct.image_url)
async def product_add_image(message: Message, state: FSMContext):
    image_url = message.text if message.text != "-" else ""
    await state.update_data(image_url=image_url)
    await message.answer("🏷 Badge kiriting (masalan: Yangi, Hit, Achchiq, yoki — kiriting):")
    await state.set_state(AddProduct.badge)


@router.message(AddProduct.badge)
async def product_add_badge(message: Message, state: FSMContext):
    badge = message.text if message.text != "-" else ""
    data = await state.get_data()

    product_id = await add_product(
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price=data["price"],
        image_url=data["image_url"],
        badge=badge
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Mahsulot qo'shildi!</b>\n\n"
        f"🍔 <b>{data['name']}</b>\n"
        f"💰 Narx: {int(data['price']):,} so'm\n"
        f"🆔 ID: {product_id}",
        parse_mode="HTML",
        reply_markup=products_menu_kb()
    )
