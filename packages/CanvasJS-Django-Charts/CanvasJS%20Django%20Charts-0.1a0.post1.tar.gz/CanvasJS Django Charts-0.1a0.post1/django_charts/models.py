#! -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Chart(models.Model):

    title = models.CharField(_('Title'), max_length=100, null=True, blank=True)

    code = models.CharField(
        _('Code'), max_length=100, null=False, blank=False, unique=True
    )

    PIE = 1
    SPLINE = 2

    TYPE_OPTIONS = (
        (PIE, "pie"),
        (SPLINE, "spline")
    )

    type = models.IntegerField(
        _('Type'), null=False, blank=False, choices=TYPE_OPTIONS
    )

    data_url_name = models.CharField(
        _('Data URL Name'), max_length=255, blank=False, null=False,
        help_text=_("Django url name for getting the data from.")
    )

    desc = models.TextField(
        _('Description'), null=True, blank=True,
        help_text=_("Optional chart description")
    )

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class SPLineChart(Chart):

    """
    Data format expected to be returned from data_url:

        [
			{x: new Date(2002, 0), y: 2506000},
			{x: new Date(2003, 0), y: 2798000},
			{x: new Date(2004, 0), y: 3386000},
			{x: new Date(2005, 0), y: 6944000},
			{x: new Date(2006, 0), y: 6026000},
			{x: new Date(2007, 0), y: 2394000},
			{x: new Date(2008, 0), y: 1872000},
			{x: new Date(2009, 0), y: 2140000},
			{x: new Date(2010, 0), y: 7289000},
			{x: new Date(2011, 0), y: 4830000},
			{x: new Date(2012, 0), y: 2009000},
			{x: new Date(2013, 0), y: 2840000},
			{x: new Date(2014, 0), y: 2396000},
			{x: new Date(2015, 0), y: 1613000},
			{x: new Date(2016, 0), y: 2821000},
			{x: new Date(2017, 0), y: 2000000}
		]
    """

    x_axis_title = models.CharField(_("X axis title"), max_length=32, null=True, blank=True)
    x_axis_format = models.CharField(_("X axis format"), max_length=32, null=True, blank=True)
    x_axis_suffix = models.CharField(_("X axis suffix"), max_length=32, null=True, blank=True)
    x_axis_preix = models.CharField(_("X axis preix"), max_length=32, null=True, blank=True)
    x_axis_extra_options = models.CharField(_("X axis extra_options"), max_length=32, null=True, blank=True)

    y_axis_title = models.CharField(_("Y axis title"), max_length=32, null=True, blank=True)
    y_axis_format = models.CharField(_("Y axis format"), max_length=32, null=True, blank=True)
    y_axis_suffix = models.CharField(_("Y axis suffix"), max_length=32, null=True, blank=True)
    y_axis_preix = models.CharField(_("Y axis preix"), max_length=32, null=True, blank=True)
    y_axis_extra_options = models.CharField(_("Y axis extra_options"), max_length=32, null=True, blank=True)

    y_data_format = models.TextField(_("Y axis data format"), max_length=16, null=True, blank=True)
    x_data_format = models.TextField(_("X axis data format"), max_length=16, null=True, blank=True)

    class Meta:
        verbose_name = "SPLine Chart"
        verbose_name_plural = "SPLine Charts"

class PieChart(Chart):

    class Meta:
        verbose_name = "Pie Chart"
        verbose_name_plural = "Pie Charts"
