import aiomysql
import logging
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger(__name__)

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset="utf8mb4",
            autocommit=True,
            minsize=1,
            maxsize=10
        )
        logger.info("MySQL ulanishi o'rnatildi")
    return _pool


async def close_pool():
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


# ─── ORDERS ──────────────────────────────────────────────────────────────────

async def get_all_orders(status=None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            if status:
                await cur.execute(
                    "SELECT * FROM orders WHERE status=%s ORDER BY created_at DESC", (status,)
                )
            else:
                await cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
            return await cur.fetchall()


async def get_order_by_id(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
            return await cur.fetchone()


async def get_order_items(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM order_items WHERE order_id=%s", (order_id,)
            )
            return await cur.fetchall()


async def update_order_status(order_id: int, status: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE orders SET status=%s WHERE id=%s", (status, order_id)
            )


async def delete_order(order_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
            await cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))


# ─── PRODUCTS ────────────────────────────────────────────────────────────────

async def get_all_products():
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT p.*, c.name as category_name FROM products p "
                "LEFT JOIN categories c ON p.category_id=c.id ORDER BY p.id"
            )
            return await cur.fetchall()


async def get_product_by_id(product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
            return await cur.fetchone()


async def add_product(category_id: int, name: str, description: str,
                      price: float, image_url: str, badge: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO products (category_id, name, description, price, image_url, badge, is_active, sort_order) "
                "VALUES (%s, %s, %s, %s, %s, %s, 1, 0)",
                (category_id, name, description, price, image_url, badge)
            )
            return cur.lastrowid


async def update_product(product_id: int, name: str, description: str,
                         price: float, image_url: str, badge: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE products SET name=%s, description=%s, price=%s, "
                "image_url=%s, badge=%s WHERE id=%s",
                (name, description, price, image_url, badge, product_id)
            )


async def delete_product(product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM products WHERE id=%s", (product_id,))


async def toggle_product_status(product_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE products SET is_active = NOT is_active WHERE id=%s", (product_id,)
            )


# ─── CATEGORIES ──────────────────────────────────────────────────────────────

async def get_all_categories():
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM categories ORDER BY sort_order")
            return await cur.fetchall()


async def get_category_by_id(cat_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM categories WHERE id=%s", (cat_id,))
            return await cur.fetchone()


async def add_category(name: str, icon: str, sort_order: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO categories (name, icon, sort_order, is_active) VALUES (%s, %s, %s, 1)",
                (name, icon, sort_order)
            )
            return cur.lastrowid


async def update_category(cat_id: int, name: str, icon: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE categories SET name=%s, icon=%s WHERE id=%s",
                (name, icon, cat_id)
            )


async def delete_category(cat_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM categories WHERE id=%s", (cat_id,))


# ─── STATISTICS ──────────────────────────────────────────────────────────────

async def get_statistics():
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT COUNT(*) as total FROM orders")
            total_orders = (await cur.fetchone())["total"]

            await cur.execute("SELECT COUNT(*) as total FROM orders WHERE status='new'")
            new_orders = (await cur.fetchone())["total"]

            await cur.execute("SELECT SUM(total_price) as total FROM orders")
            total_revenue = (await cur.fetchone())["total"] or 0

            await cur.execute("SELECT COUNT(*) as total FROM products WHERE is_active=1")
            active_products = (await cur.fetchone())["total"]

            await cur.execute("SELECT COUNT(*) as total FROM categories WHERE is_active=1")
            active_categories = (await cur.fetchone())["total"]

            return {
                "total_orders": total_orders,
                "new_orders": new_orders,
                "total_revenue": total_revenue,
                "active_products": active_products,
                "active_categories": active_categories,
            }
