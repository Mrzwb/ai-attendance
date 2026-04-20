import re
import pandas as pd
from pandas import DataFrame


def read_excel(file: str) -> DataFrame:
    df = pd.read_excel(file).fillna(value='')
    return format_date(df)


def format_date(df: DataFrame) -> DataFrame:
    """
        格式化时间
    :param df:
    :return:
    """
    for column in df.columns:
        if pd.api.types.is_datetime64_dtype(df[column]):
            df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df


def is_excel(file: str) -> bool:
    matcher = re.match('.*\.(?:xls|xlsx)$', file, flags=re.IGNORECASE)
    return matcher is not None


def concat_excel(files: list[DataFrame]) -> DataFrame:
    df_frames = [f for f in files]
    if len(df_frames) > 0:
        return pd.concat(df_frames)
    return None

