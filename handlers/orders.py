from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_all_orders, get_order_by_id, get_order_items, update_order_status, delete_order
from keyboards.keyboards import orders_menu_kb, order_detail_kb

router = Router()

STATUS_LABELS = {
    "new": "🆕 Yangi",
    "confirmed": "✅ Tasdiqlangan",
    "delivering": "🚚 Yetkazilmoqda",
    "delivered": "✔️ Yetkazilgan",
    "cancelled": "❌ Bekor qilingan",
}


def order_text(order: dict, items: list) -> str:
    status = STATUS_LABELS.get(order["status"], order["status"])
    items_text = "\n".join(
        f"  • {item['product_name']} x{item['qty']} — {int(item['price']):,} so'm"
        for item in items
    )
    return (
        f"📦 <b>Buyurtma #{order['order_number']}</b>\n\n"
        f"👤 Mijoz: <b>{order['customer_name']}</b>\n"
        f"📞 Telefon: <b>{order['customer_phone']}</b>\n"
        f"💰 Jami: <b>{int(order['total_price']):,} so'm</b>\n"
        f"📌 Status: <b>{status}</b>\n"
        f"🕐 Vaqt: <b>{order['created_at']}</b>\n\n"
        f"🛒 <b>Mahsulotlar:</b>\n{items_text}"
    )


async def show_orders(callback: CallbackQuery, status=None):
    orders = await get_all_orders(status)
    if not orders:
        label = STATUS_LABELS.get(status, "barcha") if status else "barcha"
        await callback.message.edit_text(
            f"📭 {label} buyurtmalar yo'q.",
            reply_markup=orders_menu_kb()
        )
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    for o in orders:
        status_icon = STATUS_LABELS.get(o["status"], "❓")
        builder.button(
            text=f"{status_icon} #{o['order_number']} — {o['customer_name']} ({int(o['total_price']):,} so'm)",
            callback_data=f"order_view_{o['id']}"
        )
    builder.button(text="🔙 Orqaga", callback_data="back_orders_menu")
    builder.adjust(1)

    await callback.message.edit_text(
        f"📋 <b>Buyurtmalar ro'yxati</b> ({len(orders)} ta):",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "orders_all")
async def orders_all(callback: CallbackQuery):
    await show_orders(callback, status=None)
    await callback.answer()


@router.callback_query(F.data == "orders_new")
async def orders_new(callback: CallbackQuery):
    await show_orders(callback, status="new")
    await callback.answer()


@router.callback_query(F.data == "orders_confirmed")
async def orders_confirmed(callback: CallbackQuery):
    await show_orders(callback, status="confirmed")
    await callback.answer()


@router.callback_query(F.data == "orders_delivering")
async def orders_delivering(callback: CallbackQuery):
    await show_orders(callback, status="delivering")
    await callback.answer()


@router.callback_query(F.data == "orders_delivered")
async def orders_delivered(callback: CallbackQuery):
    await show_orders(callback, status="delivered")
    await callback.answer()


@router.callback_query(F.data.startswith("order_view_"))
async def order_view(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)
    items = await get_order_items(order_id)

    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    await callback.message.edit_text(
        order_text(order, items),
        reply_markup=order_detail_kb(order_id, order["status"]),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_status_"))
async def order_change_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_id = int(parts[2])
    new_status = parts[3]

    await update_order_status(order_id, new_status)
    order = await get_order_by_id(order_id)
    items = await get_order_items(order_id)

    await callback.message.edit_text(
        order_text(order, items),
        reply_markup=order_detail_kb(order_id, new_status),
        parse_mode="HTML"
    )
    await callback.answer(f"✅ Status o'zgartirildi: {STATUS_LABELS.get(new_status)}")


@router.callback_query(F.data.startswith("order_delete_"))
async def order_delete(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    await delete_order(order_id)
    await callback.answer("🗑 Buyurtma o'chirildi!", show_alert=True)
    await show_orders(callback, status=None)


@router.callback_query(F.data == "back_orders_menu")
async def back_orders_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📦 <b>Buyurtmalar</b>\n\nQaysi buyurtmalarni ko'rmoqchisiz?",
        reply_markup=orders_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()
