import yfinance as yf
import streamlit as st
import datetime
import pandas as pd
import cufflinks as cf
from plotly.offline import iplot
from utils import StockData

cf.go_offline()

@st.cache_data
def get_sp500_components():
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_companies_listed_on_B3")
    df = df[0]
    tickers = df["Ticker"].to_list()
    tickers_companies_dict = dict(
        zip(df["Ticker"], df["Company"])
    )
    return tickers, tickers_companies_dict

@st.cache_data
def initStockData(symbol):
    return StockData(symbol)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")

st.sidebar.header("Parâmetro de ações")
custom_ticker = st.sidebar.checkbox('Escrever código da ação', False)

available_tickers, tickers_companies_dict = get_sp500_components()

if not custom_ticker:
    ticker = st.sidebar.selectbox(
        "Ticker", 
        available_tickers, 
        format_func=tickers_companies_dict.get
    )


if custom_ticker:
    ticker = st.sidebar.text_input("Ticker", value="PETR4")

start_date = st.sidebar.date_input(
    "Start date", 
    datetime.date(2019, 1, 1)
)
end_date = st.sidebar.date_input(
    "End date", 
    datetime.date.today()
)
if start_date > end_date:
    st.sidebar.error("A data fim deve ser maior que a data início")
sd = initStockData(ticker+'.SA')
df = sd.data[start_date:end_date]

st.sidebar.header("Technical Analysis Parameters")
volume_flag = st.sidebar.checkbox(label="Adicionar volume")

exp_sma = st.sidebar.expander("SMA")
sma_flag = exp_sma.checkbox(label="Adicionar SMA")
sma_periods= exp_sma.number_input(
    label="SMA Periods", 
    min_value=1, 
    max_value=50, 
    value=20, 
    step=1
)

exp_bb = st.sidebar.expander("Bollinger Bands")
bb_flag = exp_bb.checkbox(label="Adicionar Bollinger Bands")
bb_periods= exp_bb.number_input(label="BB Periods", 
                                min_value=1, max_value=50, 
                                value=20, step=1)
bb_std= exp_bb.number_input(label="# of standard deviations", 
                            min_value=1, max_value=4, 
                            value=2, step=1)

exp_rsi = st.sidebar.expander("Relative Strength Index")
rsi_flag = exp_rsi.checkbox(label="Add RSI")
rsi_periods= exp_rsi.number_input(
    label="RSI Periods", 
    min_value=1, 
    max_value=50, 
    value=20, 
    step=1
)
rsi_upper= exp_rsi.number_input(label="RSI Upper", 
                                min_value=50, 
                                max_value=90, value=70, 
                                step=1)
rsi_lower= exp_rsi.number_input(label="RSI Lower", 
                                min_value=10, 
                                max_value=50, value=30, 
                                step=1)

st.title("Dashboard de análise técnica para ações brasileiras")
st.write("""
    ### Manual do usuário
    * Você pode selecionar qualquer empresa dos 450 constituintes da B3 ou digitar um código de ação personalizado
""")


data_exp = st.expander("Visualizar dados")
available_cols = df.columns.tolist()
columns_to_show = data_exp.multiselect(
    "Colunas", 
    available_cols, 
    default=available_cols
)
data_exp.dataframe(df[columns_to_show])
 
csv_file = convert_df_to_csv(df[columns_to_show])
data_exp.download_button(
    label="Baixar selecionados como CSV",
    data=csv_file,
    file_name=f"{ticker}_stock_prices.csv",
    mime="text/csv",
)
if ticker in tickers_companies_dict:
    title_str = f"Preço das ações da empresa {tickers_companies_dict[ticker]}"
else:
    title_str = f"Preço das ações da empresa {sd.long_name}"


qf = cf.QuantFig(df, title=title_str)
if volume_flag:
    qf.add_volume()
if sma_flag:
    qf.add_sma(periods=sma_periods)
if bb_flag:
    qf.add_bollinger_bands(periods=bb_periods,
                           boll_std=bb_std)
if rsi_flag:
    qf.add_rsi(periods=rsi_periods,
               rsi_upper=rsi_upper,
               rsi_lower=rsi_lower,
               showbands=True)
fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)

# Percentual growth in the last months and year
st.subheader("Crescimento Percentual")
last_month_growth = sd.get_percentage_growth(months=1)
last_3_months_growth = sd.get_percentage_growth(months=3)
last_year_growth = sd.get_percentage_growth(months=12)

# Define color based in the values
last_month_growth_color = "green" if last_month_growth and last_month_growth > 0 else "red"
last_3_months_growth_color = "green" if last_3_months_growth and last_3_months_growth > 0 else "red"
last_year_growth_color = "green" if last_year_growth and last_year_growth > 0 else "red"

# Estilo CSS para as porcentagens de crescimento
growth_style = "font-size: larger; font-weight: bold;"

# Exibir as porcentagens de crescimento com formatação
col5, col6, col7 = st.columns(3)
with col5:
    st.write("Último mês:")
    st.write(f"<span style='{growth_style} color: {last_month_growth_color};'>{last_month_growth}%</span>", unsafe_allow_html=True)
with col6:
    st.write("Últimos 3 Meses:")
    st.write(f"<span style='{growth_style} color: {last_3_months_growth_color};'>{last_3_months_growth}%</span>", unsafe_allow_html=True)
with col7:
    st.write("Último Ano:")
    st.write(f"<span style='{growth_style} color: {last_year_growth_color};'>{last_year_growth}%</span>", unsafe_allow_html=True)

# Indicators
st.subheader("Stock Indicators")
st.write("Stock Code:", ticker)

# Indicators formatting
dividend_yield = sd.dividend_yield
ebitda_margins = sd.ebitda_margins
pl = sd.pl
price_vp = sd.price_vp

# Set colors based on values
dividend_yield_color = "green" if dividend_yield and dividend_yield > 0 else "red"
ebitda_margins_color = "green" if ebitda_margins and ebitda_margins > 0 else "red"
pl_color = "green" if pl and pl > 0 else "red"
p_vp_color = "green" if price_vp and price_vp <= 1.1 else "red"

# CSS style for indicators
indicator_style = "font-size: xx-large; padding: 10px; background-color: lightgray; border-radius: 5px;"

# Display indicators side by side with formatting
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("Dividend Yield:")
    st.write(f"<span style='{indicator_style} color: {dividend_yield_color};'>{dividend_yield}</span>", unsafe_allow_html=True)
with col2:
    st.write("EBITDA Margins:")
    st.write(f"<span style='{indicator_style} color: {ebitda_margins_color};'>{ebitda_margins}</span>", unsafe_allow_html=True)
with col3:
    st.write("P/L (Preço/Lucro):")
    st.write(f"<span style='{indicator_style} color: {pl_color};'>{pl}</span>", unsafe_allow_html=True)
with col4:
    st.write("P/VP:")
    st.write(f"<span style='{indicator_style} color: {p_vp_color};'>{price_vp}</span>", unsafe_allow_html=True)
