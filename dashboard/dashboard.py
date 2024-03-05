import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Dashboard Penjualan", page_icon=":bar_chart:", layout="wide")

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

#def create_sum_order_category_df(df):
 #   sum_order_items_df = df.groupby("product_category_name_english").quantity_x.sum().sort_values(ascending=False).reset_index()
  #  return sum_order_items_df

def create_daily_rating_df(df,how):
    if how:
        daily_rating = df.groupby("product_category_name_english")["review_score"].mean().nlargest(5)
        return daily_rating
    else:
        daily_rating = df.groupby("product_category_name_english")["review_score"].mean().nsmallest(5)
        return daily_rating

def get_total_rating(df):
    return df['review_score'].mean()

def create_daily_category_sales_df(df):
    cat_sale = df.groupby("product_category_name_english")["order_item_id"].count().nlargest(10)
    return cat_sale


core_data = pd.read_csv("../sales_seller_customer_reviews_data.csv")
#geolocation_df = pd.read_csv("data/geolocation_dataset.csv")

#datetime_columns = ["order_purchase_timestamp"]
core_data.sort_values(by="order_purchase_timestamp", inplace=True)
core_data.reset_index(inplace=True)
core_data["order_purchase_timestamp"] = pd.to_datetime(core_data["order_purchase_timestamp"])

min_date = core_data["order_purchase_timestamp"].min()
max_date = core_data["order_purchase_timestamp"].max()

logo_url = "https://github.com/dicodingacademy/assets/raw/main/logo.png"

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(logo_url)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered = core_data[(core_data['order_purchase_timestamp']>=str(start_date)) &
                     (core_data["order_purchase_timestamp"]<=str(end_date))]

daily_category_sales_df = create_daily_category_sales_df(filtered)
daily_rating_best_df = create_daily_rating_df(filtered,True)
daily_rating_worst_df = create_daily_rating_df(filtered,False)
daily_orders_df = create_daily_orders_df(filtered)
total_rating = get_total_rating(filtered)


st.header('Dashboard Penjualan :sparkles:')

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = daily_orders_df.revenue.sum()
    st.metric("Total Revenue R$", value="{:.2f}".format(total_revenue))

with col3:
    st.metric("Average Rating", value="{:.2f}".format(total_rating))

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Total Penjualan di Tiap Kategori")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = "flare"#["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x=daily_rating_best_df.index, y=daily_rating_best_df.values, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Category", fontsize=30)
ax[0].set_title("Best Rated Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].set_xticklabels(labels=daily_rating_best_df.index,rotation="vertical")

sns.barplot(x=daily_rating_worst_df.index, y=daily_rating_worst_df.values, palette="flare_r", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Category", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Rated Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].set_xticklabels(labels=daily_rating_worst_df.index,rotation="vertical")

st.pyplot(fig)