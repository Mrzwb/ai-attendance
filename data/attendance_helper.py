from enum import Enum

from pandas import DataFrame, Index

from .range_object import RangeObject
from .chart_helper import ChartData
from logger import logger

SPLIT = 8


class AttendanceType(Enum):
    LATE = "迟到"
    EARLY = "早退"
    ABSENT = "旷工"


class AttendanceHelper(ChartData):
    """
    考勤 图表工具
    """

    # @staticmethod
    # def is_likelihood(df: DataFrame) -> bool:
    #     """
    #     判断考勤报表头是否相似75%以上
    #     :param df:
    #     :return:
    #     """
    #     likelihood_percent = 0
    #     try:
    #         is_like_arr = df.columns.isin(list(REPORT_HEADER_ATT))
    #         count = is_like_arr.tolist().count(True)
    #         likelihood_percent = count / len(REPORT_HEADER_ATT) * 100
    #         logger.info(f"考勤报表相似度: ~{likelihood_percent}%")
    #         return likelihood_percent >= 75
    #     except Exception:
    #         logger.error(f"图表分析数据错误: {df}")
    #     return False

    @classmethod
    def has_columns(cls, df: DataFrame, columns: tuple):
        flag = True
        try:
            ls = []
            for c in columns:
                if c not in df.columns:
                    ls.append(c)
            if len(ls) > 0:
                logger.error(f"考勤图表分析缺少字段: {ls}")
                flag = False
        except RuntimeError:
            logger.error(f"图表分析数据错误: {df}")
            flag = False
        return flag

    @staticmethod
    def pie_data(df: DataFrame, rg: RangeObject = None) -> dict[str, list[tuple]]:
        """
          获取考勤饼图数据，按项目维度
        :param rg:
        :param df: 考勤数据， 适用表头 [日期,姓名,所属项目组,迟到,早退,旷工,申诉,备注]
        :return:
        """
        pie_data = {"迟到": [], "早退": [], "旷工": []}
        result = AttendanceHelper.statistic(df)
        if result is not None:
            result = df.groupby(["所属项目组"])[["迟到", "早退", "旷工"]].sum()
            pie_data_late = []
            pie_data_early = []
            pie_data_absent = []

            for proj in result.index:
                pie_data_late.append((f"{proj} - {result["迟到"][proj]}人", result["迟到"][proj]))
                pie_data_early.append((f"{proj} - {result["早退"][proj]}人", result["早退"][proj]))
                pie_data_absent.append((f"{proj} - {result["旷工"][proj]}人", result["旷工"][proj]))
            pie_data["迟到"] = pie_data_late[rg.start:rg.end] if rg else pie_data_late
            pie_data["早退"] = pie_data_early[rg.start:rg.end] if rg else pie_data_early
            pie_data["旷工"] = pie_data_absent[rg.start:rg.end] if rg else pie_data_absent
        return pie_data

    @staticmethod
    def single_bar_data(df: DataFrame, name: AttendanceType,  rg: RangeObject = None):
        pie_data = {"迟到": [], "早退": [], "旷工": []}
        result = AttendanceHelper.statistic(df)
        if result is not None:
            pie_data_late = []
            pie_data_early = []
            pie_data_absent = []
            for proj in result.index:
                pie_data_late.append((f"{proj}", result["迟到"][proj]))
                pie_data_early.append((f"{proj}", result["早退"][proj]))
                pie_data_absent.append((f"{proj}", result["旷工"][proj]))
            pie_data["迟到"] = pie_data_late[rg.start:rg.end] if rg else pie_data_late
            pie_data["早退"] = pie_data_early[rg.start:rg.end] if rg else pie_data_early
            pie_data["旷工"] = pie_data_absent[rg.start:rg.end] if rg else pie_data_absent
        return pie_data[name.value]

    @staticmethod
    def statistic(df: DataFrame, func: str = "sum"):
        if AttendanceHelper.has_columns(df, ('所属项目组', '迟到', '早退', '旷工')):
            return df.groupby(["所属项目组"])[["迟到", "早退", "旷工"]].agg(func)
        return None

    @staticmethod
    def get_itr_count(index: Index) -> int:
        count = index.size
        return count // SPLIT if count % SPLIT == 0 else count // SPLIT + 1

    @staticmethod
    def bar_data(df: DataFrame, rg: RangeObject = None):
        data = {
            'category': [],
            'data': {},
            'max': 10
        }
        result = AttendanceHelper.statistic(df)
        if result is not None:
            data['category'] = result.index.values.tolist()[rg.start:rg.end] if rg else result.index.values.tolist()
            data['data'] = {
                "迟到": result["迟到"].values[rg.start:rg.end] if rg else result["迟到"].values,
                "早退": result["早退"].values[rg.start:rg.end] if rg else result["早退"].values,
                "旷工": result["旷工"].values[rg.start:rg.end] if rg else result["旷工"].values
            }
            data['max'] = max([
                max(data['data']["迟到"]),
                max(data['data']["早退"]),
                max(data['data']["旷工"])
            ])
        return data

