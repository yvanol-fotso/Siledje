"""
Widgets de graphiques pour l'accueil (pie, bar, donut).
"""

from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QPieSlice,
    QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis,
)
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from src.ui.views.base.base_view import Palette


class AccueilChart:
    """Fabrique de graphiques pour l'accueil."""

    @staticmethod
    def _apply_chart_theme(chart: QChart, chart_view: QChartView, is_dark: bool):
        bg = QColor(Palette.DARK_BG if is_dark else Palette.BASE_WHITE)
        text = QColor(Palette.DARK_TEXT if is_dark else Palette.ACCENT)
        grid = QColor(Palette.DARK_BORDER if is_dark else Palette.BORDER_GRAY)

        chart.setBackgroundBrush(QBrush(bg))
        chart.setBackgroundPen(QPen(Qt.NoPen))
        chart.setTitleBrush(QBrush(text))

        chart_view.setBackgroundBrush(QBrush(bg))
        chart_view.setStyleSheet(
            f"QChartView#chartView {{ background-color: {bg.name()}; border: none; }}"
        )

        for axis in chart.axes():
            axis.setLabelsColor(text)
            if isinstance(axis, QValueAxis):
                axis.setGridLineColor(grid)
            if hasattr(axis, "setTitleBrush"):
                axis.setTitleBrush(QBrush(text))

        for series in chart.series():
            if isinstance(series, QPieSeries):
                for sl in series.slices():
                    if sl.isLabelVisible():
                        sl.setLabelColor(text)

    @staticmethod
    def _attach_theme_hook(cv: QChartView, chart: QChart):
        cv.apply_theme = lambda is_dark, _c=chart, _v=cv: (
            AccueilChart._apply_chart_theme(_c, _v, is_dark)
        )

    @staticmethod
    def create_pie_chart(title: str, data: dict, colors: list) -> QChartView:
        series = QPieSeries()
        total = sum(data.values()) or 1
        for i, (label, value) in enumerate(data.items()):
            sl = series.append(label, value)
            sl.setLabelVisible(True)
            sl.setLabelPosition(QPieSlice.LabelOutside)
            sl.setBrush(QColor(colors[i % len(colors)]))
            sl.setPen(QPen(QColor("#ffffff"), 2))
            sl.setLabel(f"{label} {(value / total) * 100:.0f}%\n{value} art")
            sl.setLabelFont(QFont("Segoe UI", 8, QFont.Bold))
            sl.setLabelColor(QColor(Palette.ACCENT))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{sum(data.values())} articles")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))
        chart.setMargins(QMargins(10, 10, 10, 10))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setObjectName("chartView")
        cv.setFixedSize(280, 240)
        AccueilChart._attach_theme_hook(cv, chart)
        return cv

    @staticmethod
    def create_bar_chart(title: str, categories: list, values: list, color: str) -> QChartView:
        bar_set = QBarSet("Ventes")
        for v in values:
            bar_set.append(v)
        bar_set.setColor(QColor(color))
        bar_set.setBorderColor(QColor(Palette.ACCENT))

        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")
        series.setLabelsPosition(QBarSeries.LabelsOutsideEnd)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{sum(values) / 1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))

        ax = QBarCategoryAxis()
        ax.append(categories)
        ax.setLabelsFont(QFont("Segoe UI", 9))
        ax.setLabelsColor(QColor(Palette.ACCENT))
        chart.addAxis(ax, Qt.AlignBottom)
        series.attachAxis(ax)

        ay = QValueAxis()
        ay.setRange(0, max(values) * 1.2 if values else 1)
        ay.setTitleText("Ventes (FCFA)")
        ay.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        ay.setLabelsFont(QFont("Segoe UI", 9))
        ay.setLabelsColor(QColor(Palette.ACCENT))
        ay.setGridLineVisible(True)
        ay.setGridLineColor(QColor(Palette.BORDER_GRAY))
        chart.addAxis(ay, Qt.AlignLeft)
        series.attachAxis(ay)
        chart.legend().setVisible(False)

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setObjectName("chartView")
        cv.setFixedSize(350, 240)
        AccueilChart._attach_theme_hook(cv, chart)
        return cv

    @staticmethod
    def create_donut_chart(title: str, achieved: float, target: float, color: str) -> QChartView:
        series = QPieSeries()
        series.setHoleSize(0.5)

        pct = (achieved / target) * 100 if target else 0
        sl_a = series.append(f"{pct:.0f}%", achieved)
        sl_a.setBrush(QColor(color))
        sl_a.setPen(QPen(QColor("#ffffff"), 3))
        sl_a.setLabelVisible(True)
        sl_a.setLabelFont(QFont("Segoe UI", 9, QFont.Bold))
        sl_a.setLabelColor(QColor(Palette.ACCENT))
        sl_a.setExploded(True)
        sl_a.setExplodeDistanceFactor(0.05)
        sl_a.setLabel(f"{pct:.0f}%\n{achieved / 1000:.0f}k")

        sl_r = series.append("Restant", max(target - achieved, 0))
        sl_r.setBrush(QColor(Palette.SCROLLBAR_BG))
        sl_r.setPen(QPen(QColor(Palette.BORDER_GRAY), 2))
        sl_r.setLabelVisible(False)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"{title}\n{target / 1000:.0f}k FCFA")
        chart.setTitleFont(QFont("Segoe UI", 10, QFont.Bold))
        chart.setTitleBrush(QBrush(QColor(Palette.ACCENT)))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.setBackgroundBrush(QBrush(QColor(Palette.BASE_WHITE)))

        cv = QChartView(chart)
        cv.setRenderHint(QPainter.Antialiasing)
        cv.setObjectName("chartView")
        cv.setFixedSize(280, 240)
        AccueilChart._attach_theme_hook(cv, chart)
        return cv