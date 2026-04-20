from pandas import DataFrame

from .chart_helper import ChartData


class FinanceHelp(ChartData):
    """
    财务 图表工具
    """

    @staticmethod
    def pie_data(df: DataFrame) -> dict[str, list[tuple]]:
        pass

    @staticmethod
    def bar_data(df: DataFrame):
        pass
