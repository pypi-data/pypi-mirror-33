import datetime
import time
from QUANTAXIS.QAUtil import (DATABASE, QASETTING,
                              QA_util_get_real_date, QA_util_log_info,
                              QA_util_to_json_from_pandas, trade_date_sse)

from QUANTAXIS.QAFetch.QAbinance import QA_fetch_symbol, QA_fetch_kline
import pymongo

# binance的历史数据只是从2017年7月开始有，以前的貌似都没有保留 . author:Will
BINANCE_MIN_DATE = datetime.datetime(2017, 7, 1)


def QA_SU_save_binance(frequency):
    symbol_list = QA_fetch_symbol()
    col = QASETTING.client.binance[frequency]
    col.create_index(
        [("symbol", pymongo.ASCENDING), ("start_time", pymongo.ASCENDING)])

    end = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for index, symbol_info in enumerate(symbol_list):
        QA_util_log_info('The {} of Total {}'.format
                         (symbol_info['symbol'], len(symbol_list)))
        QA_util_log_info('DOWNLOAD PROGRESS {} '.format(str(
            float(index / len(symbol_list) * 100))[0:4] + '%')
                         )
        ref = col.find({"symbol": symbol_info['symbol']}).sort("start_time", -1)

        if ref.count() > 0:
            start_stamp = ref.next()['start_time'] / 1000
            start_time = datetime.datetime.fromtimestamp(start_stamp)
            QA_util_log_info('UPDATE_SYMBOL \n Trying updating {} from {} to {}'.format(
                symbol_info['symbol'], start_time, end))
        else:
            start_time = BINANCE_MIN_DATE
            QA_util_log_info('NEW_SYMBOL \n Trying downloading {} from {} to {}'.format(
                symbol_info['symbol'], start_time, end))

        data = QA_fetch_kline(symbol_info['symbol'],
                              time.mktime(start_time.timetuple()), time.mktime(end.timetuple()), frequency)
        if len(data) == 0:
            QA_util_log_info('SYMBOL {} from {} to {} has no data'.format(
                symbol_info['symbol'], start_time, end))
            continue
        col.insert_many(data)


def QA_SU_save_binance_1min():
    QA_SU_save_binance('1m')


def QA_SU_save_binance_1day():
    QA_SU_save_binance("1d")


def QA_SU_save_binance_1hour():
    QA_SU_save_binance("1h")


def QA_SU_save_symbols():
    symbols = QA_fetch_symbol()
    col = QASETTING.client.binance.symbols
    if col.find().count() == len(symbols):
        QA_util_log_info("SYMBOLS are already existed and no more to update")
    else:
        QA_util_log_info("Delete the original symbols collections")
        QASETTING.client.binance.drop_collection("symbols")
        QA_util_log_info("Downloading the new symbols")
        col.insert_many(symbols)
        QA_util_log_info("Symbols download is done! Thank you man!")


if __name__ == '__main__':
    QA_SU_save_symbols()
