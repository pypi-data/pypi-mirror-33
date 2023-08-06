#! -*- coding: utf-8 -*-
from django.template import Library
from django.urls import reverse

register = Library()

from django_charts import models

@register.inclusion_tag('charts/js/spline.js.html')
def add_spline_chart_js(chart_code):
    chart = models.SPLineChart.objects.get(code=chart_code)

    data = {
        'code': chart_code,
        'title': chart.title,
        'x_axis_title' : chart.x_axis_title,
        'x_axis_format' : chart.x_axis_format,
        'x_axis_suffix' : chart.x_axis_suffix,
        'x_axis_preix' : chart.x_axis_preix,
        'x_axis_extra_options' : chart.x_axis_extra_options,
        'y_axis_title' : chart.y_axis_title,
        'y_axis_format' : chart.y_axis_format,
        'y_axis_suffix' : chart.y_axis_suffix,
        'y_axis_preix' : chart.y_axis_preix,
        'y_axis_extra_options' : chart.y_axis_extra_options,
        'y_data_format' : chart.y_data_format,
        'x_data_format' : chart.x_data_format,

        'data_url': reverse(chart.data_url_name),
    }

    return data

@register.inclusion_tag('charts/html/spline.html')
def add_spline_chart_html(chart_code):
    data = {'code': chart_code}
    return data

@register.inclusion_tag('charts/js/pie.js.html')
def add_pie_chart_js(chart_code):
    chart = models.PieChart.objects.get(code=chart_code)

    data = {
        'code': chart_code,
        'title': chart.title,
        # 'x_axis_title' : chart.x_axis_title,
        # 'x_axis_format' : chart.x_axis_format,
        # 'x_axis_suffix' : chart.x_axis_suffix,
        # 'x_axis_preix' : chart.x_axis_preix,
        # 'x_axis_extra_options' : chart.x_axis_extra_options,
        # 'y_axis_title' : chart.y_axis_title,
        # 'y_axis_format' : chart.y_axis_format,
        # 'y_axis_suffix' : chart.y_axis_suffix,
        # 'y_axis_preix' : chart.y_axis_preix,
        # 'y_axis_extra_options' : chart.y_axis_extra_options,
        # 'y_data_format' : chart.y_data_format,
        # 'x_data_format' : chart.x_data_format,

        'data_url': reverse(chart.data_url_name),
    }

    return data

@register.inclusion_tag('charts/html/pie.html')
def add_pie_chart_html(chart_code):
    data = {'code': chart_code}
    return data