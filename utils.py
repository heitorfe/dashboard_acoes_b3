YEARS_LIMIT = 30
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests

class StockData:
    
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.info = self.get_stock_info()
        self.get_main_features()
        self.data = self.get_stock_data()
        
    def get_stock_data(self):
        # Definir a data de início como 10 anos atrás a partir da data atual
        end_date = pd.to_datetime('today').strftime('%Y-%m-%d')
        start_date = (pd.to_datetime('today') - pd.DateOffset(years=YEARS_LIMIT)).strftime('%Y-%m-%d')

        data = yf.download(self.stock_code, start=start_date, end=end_date)

        # Filtrar as colunas desejadas (Data, Fechamento, Volume)
        # data = data.reset_index()
        # data = data[['Date', 'Close', 'Volume']]

        # data.rename(columns = {'Close' : 'Price'}, inplace=True)
        data['StockCode'] = self.stock_code

        return data
    
    def get_stock_info(self):
        
        stock = yf.Ticker(self.stock_code)
        info = stock.info
        
        return info
    
    def get_stock_feature(self, feature):
       
        if feature in self.info:
            
            if type(self.info[feature]) == float:
                result = round(self.info[feature], 2)
            else:
                result = self.info[feature]

            print('sim', feature, result)
            return result
        else:
            print('não', feature)
            return None

    def get_main_features(self):
        
        self.type = 'FII' if 'FII' in self.get_stock_feature('shortName') else 'Enterprise'
        self.previous_close = self.get_stock_feature('previousClose')
        self.dividend_rate = self.get_stock_feature('dividendRate')
        self.volume = self.get_stock_feature('volume')
        self.dividend_yield = self.get_stock_feature('dividendYield')
        self.ebitda_margins = self.get_stock_feature('ebitdaMargins')
        self.previous_close = self.get_stock_feature('previousClose')
        self.pl = self.get_stock_feature('trailingPE')
        self.price_vp = self.get_stock_feature('priceToBook')
        self.ev_ebitda = self.get_stock_feature('enterpriseToEbitda')
        self.gross_margins = self.get_stock_feature('grossMargins')
        self.operating_cash_flow = self.get_stock_feature('operatingCashflow')
        self.last_dividend_value = self.get_stock_feature('lastDividendValue')
        self.last_dividend_date = pd.to_datetime(self.get_stock_feature('lastDividendDate'), unit = 's')
        self.last_dividend_date = (self.last_dividend_date.strftime("%d/%m/%Y") 
                                   if self.last_dividend_date 
                                   else self.last_dividend_date)
        self.long_name = self.get_stock_feature('longName')
        self.day_trade_volume_avg_10_days = self.get_stock_feature('averageDailyVolume10Day')

    def get_percentage_growth(self, months, extra=0):
        start_date = datetime.today() - timedelta(days=30*months + extra)
        start_date = start_date.strftime('%Y-%m-%d')  # Converter para string no formato correto
        end_date = self.data.index.max()
        start_price = self.data.loc[self.data.index == start_date, 'Close'].values
        end_price = self.data.loc[self.data.index == end_date, 'Close'].values

        if start_price:
            percentage_growth = ((end_price - start_price) / start_price) * 100
            return round(percentage_growth[0], 2)
        else:
            extra += 1
            return self.get_percentage_growth(months, extra=extra)
        
       
