# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import datetime

from django.db.models import Count, Sum
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.dashboard import DashboardMoneyBlock
from shuup.admin.menu import ORDERS_MENU_CATEGORY
from shuup.admin.utils.permissions import get_default_model_permissions
from shuup.admin.utils.urls import admin_url
from shuup.front.models import StoredBasket


def get_unfinalized_cart_block(request, days=14):
    days = int(days)

    early_cutoff = now() - datetime.timedelta(days=days)
    # The `hours` value for `late_cutoff` should maybe be tunable somehow.
    # Either way, we're currently considering baskets abandoned if they've been
    # unupdated for two hours.
    late_cutoff = now() - datetime.timedelta(hours=2)

    shop = request.shop
    data = (
        StoredBasket.objects.filter(shop=shop, currency=shop.currency)
        .filter(updated_on__range=(early_cutoff, late_cutoff), product_count__gte=0)
        .exclude(deleted=True, finished=True, persistent=True)
        .aggregate(count=Count("id"), sum=Sum("taxful_total_price_value"))
    )
    if not data["count"]:
        return

    return DashboardMoneyBlock(
        id="abandoned_carts_%d" % days,
        color="red",
        title=_("Abandoned Cart Value"),
        value=(data.get("sum") or 0),
        currency=shop.currency,
        icon="fa fa-calculator",
        subtitle=_("Based on {b} carts over the last {d} days").format(
            b=data.get("count"), d=days)
    )


class CartAdminModule(AdminModule):
    name = "Cart"

    def get_dashboard_blocks(self, request):
        unfinalized_block = get_unfinalized_cart_block(request, days=14)
        if unfinalized_block:
            yield unfinalized_block

    def get_urls(self):
        return [
            admin_url(
                "^carts/$",
                "shuup.front.admin_module.carts.views.CartListView",
                name="cart.list",
                permissions=get_default_model_permissions(StoredBasket),
            ),
        ]

    def get_menu_category_icons(self):
        return {self.name: "fa fa-cart"}

    def get_required_permissions(self):
        return get_default_model_permissions(StoredBasket)

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Carts"),
                icon="fa fa-shopping-cart",
                url="shuup_admin:cart.list",
                category=ORDERS_MENU_CATEGORY,
                subcategory="orders",
                aliases=[_("Show carts")]
            ),
        ]
