from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import (
    get_all_categories, get_category_by_id,
    add_category, update_category, delete_category
)
from keyboards.keyboards import (
    categories_menu_kb, categories_list_kb, category_detail_kb
)

router = Router()


class AddCategory(StatesGroup):
    name = State()
    icon = State()
    sort_order = State()


class EditCategory(StatesGroup):
    name = State()
    icon = State()


# ─── LIST ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "categories_list")
async def categories_list(callback: CallbackQuery):
    cats = await get_all_categories()
    if not cats:
        await callback.message.edit_text(
            "📭 Kategoriyalar yo'q.",
            reply_markup=categories_menu_kb()
        )
        return

    await callback.message.edit_text(
        f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)\n\nKategoriyani tanlang:",
        reply_markup=categories_list_kb(cats),
        parse_mode="HTML"
    )
    await callback.answer()


# ─── VIEW ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("category_view_"))
async def category_view(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[2])
    cat = await get_category_by_id(cat_id)

    if not cat:
        await callback.answer("❌ Kategoriya topilmadi!", show_alert=True)
        return

    text = (
        f"📂 <b>{cat.get('icon', '')} {cat['name']}</b>\n\n"
        f"🆔 ID: {cat['id']}\n"
        f"📊 Tartib: {cat['sort_order']}\n"
        f"📌 Status: {'🟢 Aktiv' if cat['is_active'] else '🔴 Nofaol'}\n"
        f"🕐 Yaratilgan: {cat['created_at']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=category_detail_kb(cat_id),
        parse_mode="HTML"
    )
    await callback.answer()


# ─── DELETE ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("category_delete_"))
async def category_delete(callback: CallbackQuery):
    cat_id = int(callback.data.split("_")[2])
    await delete_category(cat_id)
    await callback.answer("🗑 Kategoriya o'chirildi!", show_alert=True)

    cats = await get_all_categories()
    await callback.message.edit_text(
        f"📂 <b>Kategoriyalar</b> ({len(cats)} ta)\n\nKategoriyani tanlang:",
        reply_markup=categories_list_kb(cats),
        parse_mode="HTML"
    )


# ─── EDIT ────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("category_edit_"))
async def category_edit_start(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(cat_id=cat_id)
    await callback.message.edit_text("✏️ Yangi nomni kiriting:")
    await state.set_state(EditCategory.name)
    await callback.answer()


@router.message(EditCategory.name)
async def category_edit_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🎨 Yangi iconni kiriting (emoji, masalan: 🍔):")
    await state.set_state(EditCategory.icon)


@router.message(EditCategory.icon)
async def category_edit_icon(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_category(data["cat_id"], data["name"], message.text)
    await state.clear()
    await message.answer(
        f"✅ Kategoriya yangilandi!\n\n{message.text} <b>{data['name']}</b>",
        parse_mode="HTML",
        reply_markup=categories_menu_kb()
    )


# ─── ADD ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "category_add")
async def category_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("➕ <b>Yangi kategoriya qo'shish</b>\n\nNomini kiriting:",
                                     parse_mode="HTML")
    await state.set_state(AddCategory.name)
    await callback.answer()


@router.message(AddCategory.name)
async def category_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🎨 Icon (emoji) kiriting, masalan: 🍔")
    await state.set_state(AddCategory.icon)


@router.message(AddCategory.icon)
async def category_add_icon(message: Message, state: FSMContext):
    await state.update_data(icon=message.text)
    await message.answer("📊 Tartib raqamini kiriting (masalan: 1, 2, 3...):")
    await state.set_state(AddCategory.sort_order)


@router.message(AddCategory.sort_order)
async def category_add_sort(message: Message, state: FSMContext):
    try:
        sort_order = int(message.text)
    except ValueError:
        await message.answer("❌ Faqat son kiriting:")
        return

    data = await state.get_data()
    cat_id = await add_category(data["name"], data["icon"], sort_order)
    await state.clear()

    await message.answer(
        f"✅ <b>Kategoriya qo'shildi!</b>\n\n"
        f"{data['icon']} <b>{data['name']}</b>\n"
        f"🆔 ID: {cat_id}",
        parse_mode="HTML",
        reply_markup=categories_menu_kb()
    )
