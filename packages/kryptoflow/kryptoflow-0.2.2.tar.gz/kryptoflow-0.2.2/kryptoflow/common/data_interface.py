import os
import logging

from datetime import datetime, timedelta
import pandas

from rx import Observable, Observer

from kryptoflow.definitions import SAVED_MODELS
from kafka_tfrx.stream import KafkaStream
from kryptoflow.ml.dataset import one_hot_encode


_logger = logging.getLogger('root')


def rows_to_df(rows, categorical=list([])):
    df = pandas.DataFrame(rows)
    df.index = pandas.to_datetime(df['ts'])
    df['ts'] = pandas.to_datetime(df['ts'])
    df['time_diff'] = df['ts'].diff().dt.seconds.div(1, fill_value=0)
    if categorical:
        df = one_hot_encode(df, categorical)
    df = df.drop('ts', 1)
    return df


def stream_from_start(observer):
    stream = KafkaStream.avro_consumer(topic='gdax', offset='start')
    source = Observable \
        .from_(stream) \
        .subscribe(observer())


def get_historic_data(offset, max_points=None):
    stream = KafkaStream.avro_consumer(topic='gdax', offset=offset)
    source = Observable \
        .from_(stream) \
        .take_while(lambda value: datetime.now() -
                                  datetime.strptime(value['ts'], '%Y-%m-%d %H:%M:%S') > timedelta(seconds=5))

    a = source.to_blocking()
    if max_points:
        return [msg for msg in a][-max_points:]

    else:
        return [msg for msg in a]

