# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.tools import lazy


class ProductVisibility(WebsiteSale):
    """Class defined for customizing the shop page in the website"""

    @http.route()
    def shop(self, category=None, ppg=False):
        """Function defined for showing only the selected
         products for thr logged in customer"""
        res = super(ProductVisibility, self).shop(self, category=category)
        user = request.env.user
        categ = user.product_category_ids
        for rec in categ:
            product = request.env['product.template'].search(
                [('public_categ_ids', 'in', rec.id)])
            p_count = request.env['product.template'].search_count(
                [('public_categ_ids', 'in', rec.id)])
        res.qcontext['pager']['page_count'] = 1
        categ_bins = lazy(lambda: TableCompute().process(product, ppg))
        bins = lazy(
            lambda: TableCompute().process(user.product_ids, ppg=1))
        pricelist = request.env['product.pricelist'].browse(
            request.session.get('website_sale_current_pl'))
        products_prices = lazy(lambda: product._get_sales_prices(pricelist))
        if user.product_ids:
            res.qcontext.update({
                'products': user.product_ids,
                'category': user.product_ids.public_categ_ids,
                'bins': bins,
            })
        elif user.product_category_ids:
            for rec in user.product_category_ids:
                res.qcontext.update({
                    'search_product': product,
                    'products': product,
                    'category': rec,
                    'search_count': p_count,
                    'pricelist': pricelist,
                    'get_product_prices': lambda product: lazy(
                        lambda: products_prices[product.id]),
                    'bins': categ_bins,
                })
        return res
