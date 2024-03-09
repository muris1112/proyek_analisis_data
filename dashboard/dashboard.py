import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium


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

@st.cache_data
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

def create_state_rating_df(df):
    state_rating = df.groupby("customer_state")["review_score"].mean().sort_values(ascending=False)
    return state_rating

def create_state_revenue_df(df):
    state_revenue = df.groupby("customer_state")['price'].sum().sort_values(ascending=False)
    return state_revenue

def create_customer_payment_type_df(df):
    cust_df = df.drop_duplicates(subset=['customer_id'])
    cust_pt = cust_df.groupby("payment_type")['customer_id'].count().sort_values(ascending=False)
    return cust_pt

def create_customer_state_origins_df(df):
    cust_df = df.drop_duplicates(subset=['customer_id'])
    cust_so = cust_df.groupby("customer_state")['customer_id'].count().sort_values(ascending=False)
    return cust_so

def create_customer_map(df):
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
    df.drop_duplicates(subset=["customer_id"],inplace=True)
    states_df=df.groupby('customer_state').size().reset_index(name="customer_total")
    folium.Choropleth(
        geo_data="brazil_geo.json", # menggunakan file JSON geografi dari Brazil, didapatkan di
        name="choropleth",
        data=states_df,
        columns=["customer_state", "customer_total"], # mencari banyak pelanggan di masing-masing state menggunakan kode state
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=.3,
        legend_name="Penjualan di tiap state",
    ).add_to(m)

    # peta akan disimpan secara terpisah dengan format html di /dashboard/map.html
    #m.save("dashboard/map.html")
    return m

@st.cache_data
def load_core_data():
    return pd.read_csv("dashboard/all_data.csv")

core_data = load_core_data()
st.dataframe(core_data)
core_data.sort_values(by="order_purchase_timestamp", inplace=True)
core_data.reset_index(inplace=True)
core_data["order_purchase_timestamp"] = pd.to_datetime(core_data["order_purchase_timestamp"])

min_date = core_data["order_purchase_timestamp"].min()
max_date = core_data["order_purchase_timestamp"].max()

logo = "dashboard/logo.jpg"

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(logo)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# filter data agar sesuai dengan range yang dipilih
filtered = core_data[(core_data['order_purchase_timestamp']>=str(start_date)) &
                     (core_data["order_purchase_timestamp"]<=str(end_date))]

#inisiasi dataframe yang diperlukan
daily_category_sales_df = create_daily_category_sales_df(filtered)
daily_rating_best_df = create_daily_rating_df(filtered,True)
daily_rating_worst_df = create_daily_rating_df(filtered,False)
daily_orders_df = create_daily_orders_df(filtered)
state_rating = create_state_rating_df(filtered)
total_rating = get_total_rating(filtered)
state_revenue = create_state_revenue_df(filtered)
customer_payment_type = create_customer_payment_type_df(filtered)
customer_state_origins = create_customer_state_origins_df(filtered)

#membuat header
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

colors = "flare"
st.markdown("---")
st.subheader("Top 10 Kategori dengan Penjualan Tertinggi")

fig, ax = plt.subplots(figsize=(45,15))
sns.barplot(x=daily_category_sales_df.index,y=daily_category_sales_df.values,palette=colors)
sns.despine()
ax.set_ylabel(None)
ax.set_xlabel("Kategori", fontsize=30)
ax.set_title("Top 10 Kategori dengan Penjualan Terbanyak", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
ax.set_xticklabels(labels=daily_category_sales_df.index,rotation="vertical")

st.pyplot(fig)

st.markdown("---")

st.subheader("Top 10 State dengan Revenue Tertinggi")

fig, ax = plt.subplots(figsize=(45,15))
sns.barplot(x=state_revenue.index,y=state_revenue.values,palette=colors)
sns.despine()
ax.set_ylabel(None)
ax.set_xlabel("Kategori", fontsize=30)
ax.set_title("Top 10 Kategori dengan Penjualan Terbanyak", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
ax.set_xticklabels(labels=state_revenue.index,rotation="vertical")

st.pyplot(fig)

st.markdown("---")

st.subheader("Kategori dengan Rating Terbaik dan Terburuk")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 15))
colors = "flare"

yticks_rating = [1,2,3,4,5]

sns.barplot(x=daily_rating_best_df.index, y=daily_rating_best_df.values, palette=colors, ax=ax[0])
sns.despine()
ax[0].set_ylabel("Rating", fontsize=30)
ax[0].set_yticks(yticks_rating)
ax[0].set_xlabel("Category", fontsize=30)
ax[0].set_title("Best Rated Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
ax[0].set_xticklabels(labels=daily_rating_best_df.index,rotation="vertical")

sns.barplot(x=daily_rating_worst_df.index, y=daily_rating_worst_df.values, palette="flare_r", ax=ax[1])
ax[1].set_ylabel("Rating", fontsize=30)
ax[1].set_yticks(yticks_rating)
ax[1].set_xlabel("Category", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("left")
ax[1].yaxis.tick_left()
ax[1].set_title("Worst Rated Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].set_xticklabels(labels=daily_rating_worst_df.index,rotation="vertical")

st.pyplot(fig)

st.markdown("---")

st.subheader("Rerata Rating di Tiap State")
fig, ax = plt.subplots(figsize=(45,15))

sns.barplot(x=state_rating.index,y=state_rating.values,palette=colors)
ax.set_ylabel(None)
ax.set_yticks(yticks_rating)
ax.set_xlabel("Kategori", fontsize=30)
ax.set_title("Rata-rata Rating di Tiap State", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)
ax.set_xticklabels(labels=state_rating.index,rotation="vertical")

st.pyplot(fig)

st.markdown("---")

tab1,tab2,tab3 = st.tabs(["Tipe Pembayaran","Asal Pelanggan","Peta Pelanggan"])

with tab1:
    st.subheader("Tipe Pembayaran yang Dipilih Pelanggan")
    fig, ax = plt.subplots(figsize=(45,15))

    sns.barplot(x=customer_payment_type.index,y=customer_payment_type.values,palette=colors)
    ax.set_ylabel(None)
    ax.set_xlabel("Tipe Pembayaran", fontsize=30)
    ax.set_title("Tipe Pembayaran yang Dipilih Pelanggan", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)
    ax.set_xticklabels(labels=customer_payment_type.index,rotation="vertical")
    st.pyplot(fig)

with tab2:
    st.subheader("State Asal Pelanggan")
    fig, ax = plt.subplots(figsize=(45,15))

    sns.barplot(x=customer_state_origins.index,y=customer_state_origins.values,palette=colors)
    ax.set_ylabel(None)
    ax.set_xlabel("State", fontsize=30)
    ax.set_title("State Asal Pelanggan", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)
    ax.set_xticklabels(labels=customer_state_origins.index,rotation="vertical")
    st.pyplot(fig)

with tab3:
    st.subheader("Peta Pelanggan")
    # memanggil fungsi create_customer_map untuk membuat file map.html yang sudah update
    #create_customer_map(filtered)
    #st.components.v1.html(open("dashboard/map.html", "r").read(), width=700, height=500)
    st_folium(create_customer_map(filtered),width=500)