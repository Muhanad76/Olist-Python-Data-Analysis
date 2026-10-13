# ============================================================
# Olist Data Analysis Project
# مشروع تحليل بيانات متجر Olist
# ============================================================

# Import libraries | استيراد المكتبات
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. Load Data | تحميل البيانات
# ============================================================

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent / "data"

orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")

print("Data loaded successfully!")


# ============================================================
# 2. Data Preparation | تجهيز البيانات
# ============================================================

# Convert date columns to datetime format
# تحويل أعمدة التاريخ إلى صيغة التاريخ والوقت

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"], errors="coerce"
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"], errors="coerce"
)


# Check missing values | فحص القيم المفقودة
print("\nMissing values in orders:")
print(orders.isnull().sum())


# Check duplicate rows | فحص الصفوف المكررة
print("\nDuplicate rows:")
print("Orders:", orders.duplicated().sum())
print("Payments:", payments.duplicated().sum())
print("Order Items:", order_items.duplicated().sum())
print("Customers:", customers.duplicated().sum())
print("Products:", products.duplicated().sum())


# Check order status distribution | توزيع حالات الطلبات
print("\nOrder Status Distribution:")
print(orders["order_status"].value_counts())


# ============================================================
# 3. Order Status and Delivery Analysis
# تحليل حالات الطلبات ومدة التوصيل
# ============================================================

# Order status distribution | توزيع حالات الطلبات
order_status = orders["order_status"].value_counts()

print("\n--- Order Status Analysis ---")
print(order_status)


# Calculate delivery duration | حساب مدة التوصيل بالأيام
orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)


# Calculate late delivery | حساب التأخير في التوصيل
orders["late_delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)


# Keep delivered orders for delivery analysis
# اختيار الطلبات التي تم تسليمها لتحليل التوصيل
delivered_orders = orders[
    orders["order_status"].eq("delivered")
].copy()


# Calculate delivery KPIs | حساب مؤشرات التوصيل
average_delivery_days = delivered_orders["delivery_days"].mean()

late_orders = delivered_orders[
    delivered_orders["late_delivery_days"] > 0
]

late_delivery_rate = (
    len(late_orders) / len(delivered_orders) * 100
    if len(delivered_orders) > 0
    else 0
)


# Calculate cancellation rate | حساب نسبة الإلغاء
total_orders = len(orders)

cancelled_orders = orders[
    orders["order_status"].eq("canceled")
]

cancellation_rate = (
    len(cancelled_orders) / total_orders * 100
    if total_orders > 0
    else 0
)
print("\n--- Delivery Rate Validation ---")
print("Delivered orders:", len(delivered_orders))
print("Late orders:", len(late_orders))
print("Cancelled orders:", len(cancelled_orders))
print("Total orders:", total_orders)

# Display delivery KPIs | عرض مؤشرات التوصيل
print("\n--- Delivery KPIs ---")
print(f"Average delivery time: {average_delivery_days:.2f} days")
print(f"Late delivery rate: {late_delivery_rate:.2f}%")
print(f"Cancellation rate: {cancellation_rate:.2f}%")


# ============================================================
# 4. Payment Analysis | تحليل المدفوعات
# ============================================================

# Payment method distribution | توزيع طرق الدفع
payment_methods = payments["payment_type"].value_counts()

print("\n--- Payment Methods ---")
print(payment_methods)


# Payment value by method | قيمة المدفوعات حسب الطريقة
payment_summary = (
    payments.groupby("payment_type")
    .agg(
        total_payment=("payment_value", "sum"),
        average_payment=("payment_value", "mean"),
        number_of_payments=("payment_type", "count")
    )
    .sort_values("total_payment", ascending=False)
)

print("\n--- Payment Summary ---")
print(payment_summary.round(2))


# ============================================================
# 5. Sales Analysis | تحليل المبيعات
# ============================================================

# Total sales and freight by order
# إجمالي قيمة المنتجات والشحن لكل طلب
order_sales = (
    order_items.groupby("order_id")
    .agg(
        sales=("price", "sum"),
        freight=("freight_value", "sum")
    )
    .reset_index()
)


# Payment value by order | إجمالي المدفوعات لكل طلب
order_payments = (
    payments.groupby("order_id")
    .agg(
        payment_value=("payment_value", "sum")
    )
    .reset_index()
)


# Combine sales and payments | دمج المبيعات والمدفوعات
order_level = order_sales.merge(
    order_payments,
    on="order_id",
    how="left"
)


# Calculate sales KPIs | حساب مؤشرات المبيعات
total_sales = order_level["sales"].sum()
total_freight = order_level["freight"].sum()
average_order_value = order_level["sales"].mean()


# Display sales KPIs | عرض مؤشرات المبيعات
print("\n--- Sales KPIs ---")
print(f"Total product sales: {total_sales:,.2f}")
print(f"Total freight value: {total_freight:,.2f}")
print(f"Average order value: {average_order_value:,.2f}")
print(f"Orders with sales: {len(order_level):,}")


# ============================================================
# 6. Sales by State | تحليل المبيعات حسب الولاية
# ============================================================

# Merge orders with customer data
# دمج الطلبات مع بيانات العملاء
orders_customers = orders.merge(
    customers,
    on="customer_id",
    how="left"
)


# Merge sales with order and customer data
# دمج المبيعات مع الطلبات وبيانات العملاء
sales_by_state = order_level.merge(
    orders_customers[["order_id", "customer_state"]],
    on="order_id",
    how="left"
)


# Calculate sales by state | حساب المبيعات حسب الولاية
state_sales = (
    sales_by_state.groupby("customer_state")
    .agg(
        total_sales=("sales", "sum"),
        total_orders=("order_id", "nunique")
    )
    .sort_values("total_sales", ascending=False)
)

print("\n--- Top 10 States by Sales ---")
print(state_sales.head(10).round(2))


# ============================================================
# 7. Sales by Product Category
# تحليل المبيعات حسب فئة المنتج
# ============================================================

# Merge order items with product categories
# دمج تفاصيل الطلبات مع فئات المنتجات
items_products = order_items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)


# Calculate sales by category | حساب المبيعات حسب الفئة
category_sales = (
    items_products.groupby("product_category_name", dropna=False)
    .agg(
        total_sales=("price", "sum"),
        total_items=("order_item_id", "count")
    )
    .sort_values("total_sales", ascending=False)
)

print("\n--- Top 10 Product Categories ---")
print(category_sales.head(10).round(2))

# ============================================================
# 8. Monthly Trends | الاتجاهات الشهرية
# ============================================================

# Monthly order count | عدد الطلبات شهريًا
monthly_orders = (
    orders.dropna(subset=["order_purchase_timestamp"])
    .assign(
        month=lambda df: df["order_purchase_timestamp"].dt.to_period("M")
    )
    .groupby("month")
    .size()
    .rename("total_orders")
)


# Monthly product sales | مبيعات المنتجات شهريًا
# Use the order purchase date for each order
# استخدام تاريخ إنشاء الطلب لتحديد شهر المبيعات
order_months = orders[
    ["order_id", "order_purchase_timestamp"]
].dropna(subset=["order_purchase_timestamp"]).copy()

order_months["month"] = (
    order_months["order_purchase_timestamp"].dt.to_period("M")
)

monthly_sales_data = order_level.merge(
    order_months[["order_id", "month"]],
    on="order_id",
    how="inner"
)

monthly_sales = (
    monthly_sales_data.groupby("month")["sales"]
    .sum()
    .rename("total_sales")
)


print("\n--- Monthly Trends ---")
print("Monthly orders:")
print(monthly_orders.tail(12))

print("\nMonthly product sales:")
print(monthly_sales.tail(12))

# ============================================================
# 9. Visualizations | الرسوم البيانية
# ============================================================

# Chart 1: Monthly product sales
# الرسم الأول: المبيعات الشهرية
plt.figure(figsize=(12, 5))
monthly_sales.sort_index().plot(kind="line", marker="o")
plt.title("Monthly Product Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# Chart 2: Monthly order count
# الرسم الثاني: عدد الطلبات شهريًا
plt.figure(figsize=(12, 5))
monthly_orders.sort_index().plot(kind="line", marker="o")
plt.title("Monthly Order Trend")
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


# Chart 3: Top 10 product categories by sales
# الرسم الثالث: أعلى 10 فئات منتجات من حيث المبيعات
top_categories = category_sales.head(10).sort_values("total_sales")

plt.figure(figsize=(12, 6))
top_categories["total_sales"].plot(kind="barh")
plt.title("Top 10 Product Categories by Sales")
plt.xlabel("Total Sales")
plt.ylabel("Product Category")
plt.tight_layout()
plt.show()


# Chart 4: Top 10 states by sales
# الرسم الرابع: أعلى 10 ولايات من حيث المبيعات
top_states = state_sales.head(10).sort_values("total_sales")

plt.figure(figsize=(10, 6))
top_states["total_sales"].plot(kind="barh")
plt.title("Top 10 States by Product Sales")
plt.xlabel("Total Sales")
plt.ylabel("State")
plt.tight_layout()
plt.show()


# Final message | رسالة انتهاء التحليل
print("\nAnalysis completed successfully!")