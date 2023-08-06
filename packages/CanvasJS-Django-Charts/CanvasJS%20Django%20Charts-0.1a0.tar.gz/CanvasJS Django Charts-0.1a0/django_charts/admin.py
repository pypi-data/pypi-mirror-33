from django.contrib import admin
from django_charts import models



class AdminSPLineCharts(admin.ModelAdmin):
    list_display = ('title', 'desc')


class AdminPieCharts(admin.ModelAdmin):
    list_display = ('title', 'desc')


admin.site.register(models.SPLineChart, AdminSPLineCharts)
admin.site.register(models.PieChart, AdminPieCharts)
