# Look into Airflow for scheduling https://www.saturncloud.io/s/job-scheduling-with-python/
import datetime as dt
from pandas_datareader import data as web
from pandas_datareader._utils import RemoteDataError
from financeAnalysis.models import StockTicker, StockTickerHistory
from .advanced_analysis import advanced_analysis, decisionTreePrediction,show_buy_sell_points, svr_prediction_build_plot, ticker_overview, showRSI
from financeAnalysis.backend.StockScreener import buy_signal_indicator
from financeAnalysis.backend.MLBuySell import do_ml


def populate_todays_history(date=dt.datetime(2020,11,2)):
    for ticker in StockTicker.objects.filter(updated_time__lt=date).order_by('id'):
        write_stock_history_to_database(ticker.id, date)
        ticker.update(updated_time=dt.datetime.today()).save()
    do_ml()


#The date was already updated during the initial population of dates
    #This should not update the stockticker updated time as that keeps track of the last time
    #populate dates was ran for a ticker successfully
def repopulate_todays_history(date=dt.datetime.today()):
    for ticker in StockTickerHistory.objects.filter(updated_on__date=date).order_by('id'):
        repopulate_stock_history(ticker, date)

def repopulate_stock_history(history, date=dt.datetime.today()):
    date = date.date()
    if history.updated_on.date() == date:
        if not history.plot:
            ticker_overview(history.symbol_id, date)
        if not history.rsi:
            showRSI(history.symbol_id, date)
        if not history.svr_plot:
            svr_prediction_build_plot(history.symbol_id, date)
        if not history.decision_tree_plot:
            decisionTreePrediction(history.symbol_id, date)
        if not history.sma_plot:
            show_buy_sell_points(history.symbol_id, date)

def backpopulate_stock_history_2020():
    populate_todays_history()


def write_stock_history_to_database(row, start):
    end = dt.date.today()
    if start is None:
        start=dt.datetime(2020,11,2)
    print('Fetching {}  on {}'.format(row, start))
    try:
        df = web.get_data_yahoo(row.replace('.','-'), start=start, end=end)
        df.reset_index(inplace=True)
        df.set_index("Date", inplace=True)
        for i in df.iterrows():
            StockTickerHistory.objects.update_or_create(symbol_id=row, close=i[1]['Close'],
                                           low=i[1]['Low'], high=i[1]['High'],
                                           open=i[1]['Open'], volume=i[1]['Volume'],
                                           adjusted_close=i[1]['Adj Close'], updated_on=i[0])

        recently_updated = StockTickerHistory.objects.filter(symbol_id=row).filter(updated_on__gte=start).values('updated_on')
        for date in recently_updated:
            advanced_analysis(row, date['updated_on'])
            buy_signal_indicator(row, date['updated_on'])
        StockTicker.objects.filter(id=row).update(updated_time=end)
    except RemoteDataError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('remote error ' + row)
    except KeyError:
        StockTicker.objects.filter(id=row).update(updated_time=end)
        print('key error ' + row)

