from typing import Any
from django.db.models.query import QuerySet
from django.http.request import HttpRequest as HttpRequest
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from uteis import utils

from coupon.models import Coupon
from product.models import Variation, Product
from .models import Order, OrderItem
from profile_user.models import Profile

# Create your views here.

class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args: Any, **kwargs: Any):
        if not self.request.user.is_authenticated:
            return redirect('profile_user:create')
        return super().dispatch(*args, **kwargs)
    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(user=self.request.user)
        return qs


class OrderPayment(DispatchLoginRequiredMixin, DetailView):
    template_name = 'order/payment.html'
    model = Order
    pk_url_kwarg = 'pk'
    context_obj_name = 'order'

class SaveOrder(View):
    template_name = 'order/payment.html'
    

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'You must be logged to finish the order')
            return redirect('profile_use:create')
        
        if not self.request.session.get('cart'):
            messages.error(self.request, 'Your cart is empty.')
            return redirect('product:list')
        
        cart = self.request.session.get('cart')

        products_cart_ids = [p if not p.startswith('1-') else None for p in cart ]
        variations_cart_ids = [v[2:] if v.startswith('1-') else None for v in cart if v is not None ]
        bd_products = list(
            Product.objects.filter(id__in=products_cart_ids)
        )
        bd_variation = list(
            Variation.objects.filter(id__in=variations_cart_ids)
        )
        

        for variation in bd_variation:
            vid = f'1-{variation.id}'
            stock = variation.stock

            cart_qtd = cart[vid]['quantity']
            unit_price = cart[vid]['unit_price']
            promotional_unit_price = cart[vid]['promotional_unit_price']

            error_msg_stock = ''

            if stock < cart_qtd:
                cart[vid]['quantity'] = stock
                cart[vid]['quantitative_price'] = stock * unit_price
                cart[vid]['promotional_quantitative_price'] = stock * promotional_unit_price

                error_msg_stock = f"The product {cart[vid]['product_name']} {cart[vid]['variation_name']} it's out of stock. We ajust the quantities in your cart as the stock available."

            if error_msg_stock:
                messages.error(self.request, error_msg_stock)
                self.request.session.save()
                return redirect('product:cart')
            
        for product in bd_products:
            pid = str(product.id)
            stock = product.stock

            cart_qtd = cart[pid]['quantity']
            unit_price = cart[pid]['unit_price']
            promotional_unit_price = cart[pid]['promotional_unit_price']

            error_msg_stock = ''

            if stock < cart_qtd:
                cart[pid]['quantity'] = stock
                cart[pid]['quantitative_price'] = stock * unit_price
                cart[pid]['promotional_quantitative_price'] = stock * promotional_unit_price

                error_msg_stock = f"The product {cart[pid]['product_name']} it's out of stock. We ajust the quantities in your cart as the stock available."

            if error_msg_stock:
                messages.error(self.request, error_msg_stock)
                self.request.session.save()
                return redirect('product:cart')
        
        if self.request.session.get('coupon'):
            coupon = self.request.session.get('coupon')
            coupon_list = list(coupon.values())[0]
            coupon_name = coupon_list['coupon_name']
            coupon_discount = Coupon.objects.get(name=coupon_name)

        qtd_total_cart = utils.cart_total_qtd(cart)
        total_cart_value = utils.cart_totals(cart)

        total_cart_value_plus_ship_discount = total_cart_value - total_cart_value*coupon_discount.discount

        order = Order(
            user=self.request.user,
            total=total_cart_value_plus_ship_discount,
            status='C',
            qtd_total=qtd_total_cart,
            applied_coupon=coupon_discount or None
            )
        
        order.save()

        for k in cart.keys():
            if str(k).startswith('1-'):
                OrderItem.objects.bulk_create(
                    [
                        OrderItem(
                            order=order,
                            product=cart[k]['product_name'],
                            product_id=cart[k]['product_id'],
                            variation=cart[k]['variation_name'],
                            variation_id=cart[k]['variation_id'],
                            price=cart[k]['quantitative_price'],
                            promotional_price=cart[k]['promotional_quantitative_price'],
                            quantity=cart[k]['quantity'],
                            image=cart[k]['image'],
                        )
                            
                    ]
                )

            else:
                OrderItem.objects.bulk_create(
                    [
                        OrderItem(
                            order=order,
                            product=cart[k]['product_name'],
                            product_id=cart[k]['product_id'],
                            price=cart[k]['quantitative_price'],
                            promotional_price=cart[k]['promotional_quantitative_price'],
                            quantity=cart[k]['quantity'],
                            image=cart[k]['image'],
                        )
                            
                    ]
                )
        #del self.request.session['frete']
        del self.request.session['cart']
        del self.request.session['coupon']
        return redirect(
            reverse(
                'order:payment',
                kwargs={
                    'pk':order.pk
                }
            )
            )

class OrderDetails(DispatchLoginRequiredMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'order/details.html'
    pk_url_kwarg = 'pk'
    
class List(DispatchLoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'order/list.html'
    paginate_by = 10
    ordering = ['-id']
