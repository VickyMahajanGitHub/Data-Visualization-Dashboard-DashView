import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="DashView - Dashboard", page_icon="📈", layout="wide")

@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="supermarkt_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )

    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

df = get_data_from_excel()

st.sidebar.header("Please Filter Here:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique(),
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

df_selection = df.query(
    "City == @city & Customer_type ==@customer_type & Gender == @gender"
)

if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

st.title("📈 DashView: Dashboard")
st.markdown("##")

total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("""---""")

sales_by_product_line = df_selection.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

sales_by_hour = df_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

st.plotly_chart(fig_hourly_sales, use_container_width=True)
st.plotly_chart(fig_product_sales, use_container_width=True)

fig_product_pie = px.pie(
    sales_by_product_line,
    values='Total',
    names=sales_by_product_line.index,
    title="<b>Sales Distribution by Product Line</b>",
    template="plotly_white",
)
fig_product_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_product_pie, use_container_width=True)

sales_trend_over_time = df_selection.groupby(pd.Grouper(key='Date', freq='ME'))['Total'].sum().reset_index()
fig_sales_trend = px.line(
    sales_trend_over_time,
    x='Date',
    y='Total',
    title="<b>Sales Trend Over Time</b>",
    template="plotly_white",
)
fig_sales_trend.update_xaxes(title_text='Date')
fig_sales_trend.update_yaxes(title_text='Total Sales')
st.plotly_chart(fig_sales_trend, use_container_width=True)

# Adding a Box Plot
fig_box_plot = px.box(
    df_selection,
    x="Product line",
    y="Total",
    title="<b>Sales Distribution by Product Line (Box Plot)</b>",
    template="plotly_white",
)
fig_box_plot.update_xaxes(title_text="Product Line")
fig_box_plot.update_yaxes(title_text="Total Sales")
st.plotly_chart(fig_box_plot, use_container_width=True)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
