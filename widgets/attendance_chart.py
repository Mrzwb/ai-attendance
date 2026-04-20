from PySide6.QtGui import QPainter, Qt, QFont

from PySide6.QtCharts import (QAreaSeries, QBarSet, QChart, QChartView,
                              QLineSeries, QPieSeries, QScatterSeries,
                              QSplineSeries, QStackedBarSeries, QPieSlice, QBarSeries, QAbstractBarSeries,
                              QBarCategoryAxis, QValueAxis, QPercentBarSeries)
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget, QLayout, QScrollBar
from pandas import DataFrame
from data import AttendanceHelper, AttendanceType, RangeObject


class AttendanceChart(QWidget):
    _data: DataFrame = None

    _rg: RangeObject = None

    def __init__(self, data: DataFrame, rg: RangeObject = None):
        QWidget.__init__(self)
        self._data = [] if data is None or data.empty else data
        self._font = QFont()
        self._font.setPointSize(5)
        self.gridLayout = QGridLayout()
        self.charts = []
        self._rg = rg

        # Area Chart
        chart_view = QChartView(self.create_bar_chart())
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridLayout.addWidget(chart_view, 1, 0, 1, 2)
        self.charts.append(chart_view)

        # Line Chart
        chart_view = QChartView(self.create_pie_chart())
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridLayout.addWidget(chart_view, 1, 2)
        self.charts.append(chart_view)

        # Single Bar
        chart_view = QChartView(self.create_single_bar_chart(AttendanceType.LATE))
        self.gridLayout.addWidget(chart_view, 2, 0)
        self.charts.append(chart_view)

        # Single Bar
        chart_view = QChartView(self.create_single_bar_chart(AttendanceType.EARLY))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridLayout.addWidget(chart_view, 2, 1)
        self.charts.append(chart_view)

        # Single Bar
        chart_view = QChartView(self.create_single_bar_chart(AttendanceType.ABSENT))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridLayout.addWidget(chart_view, 2, 2)
        self.charts.append(chart_view)

        # layout
        self.setLayout(self.gridLayout)

    def create_pie_chart(self):
        chart = QChart()
        chart.setTitle("项目迟到人数")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        series = QPieSeries(chart)
        chart.legend().hide()

        # obtain data
        data = AttendanceHelper.pie_data(self._data, self._rg)["迟到"]

        for item in data:
            slc = series.append(item[0], item[1])
            slc.setLabelVisible()
            #slc.setExploded()
            slc.setLabelFont(self._font)
            slc.setLabelArmLengthFactor(0.1)
        series.setPieSize(0.6)
        series.setUseOpenGL(True)
        chart.addSeries(series)
        return chart

    def create_bar_chart(self):
        chart = QChart()
        chart.setTitle("项目考勤汇总")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        #chart.legend().hide()
        series = QBarSeries(chart)

        # obtain data
        chart_data = AttendanceHelper.bar_data(self._data, self._rg)

        # axis_x
        axis_x = QBarCategoryAxis()
        axis_x.setLabelsVisible(True)
        axis_x.setLabelsFont(self._font)
        axis_x.setGridLineVisible(True)
        axis_x.append(chart_data['category'])
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        # axis_y
        axis_y = QValueAxis()
        axis_y.setLabelsFont(self._font)
        axis_y.setLabelFormat("%d")
        axis_y.setRange(0, chart_data['max'])
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        for item in chart_data['data'].items():
            barset = QBarSet(f"{item[0]}")
            barset.setLabelFont(self._font)
            for dt in item[1]:
                barset.append(dt)
            series.append(barset)

        #series.setLabelsPosition(QBarSeries.LabelsPosition.LabelsOutsideEnd)
        series.setLabelsVisible(True)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        chart.addSeries(series)

        return chart

    def create_single_bar_chart(self, name: AttendanceType):
        chart = QChart()
        chart.setTitle(f"项目{name.value}汇总")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        chart.legend().setFont(self._font)
        series = QBarSeries(chart)

        # obtain data
        chart_data = AttendanceHelper.single_bar_data(self._data, name, self._rg)

        for item in chart_data:
            barset = QBarSet(f"{item[0]}")
            barset.setLabelFont(self._font)
            barset.append(item[1])
            series.append(barset)

        #series.setLabelsPosition(QBarSeries.LabelsPosition.LabelsOutsideEnd)
        series.setLabelsVisible(True)
        chart.addSeries(series)
        return chart
