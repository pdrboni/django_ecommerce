from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from . import models
from uteis import utils

# Create your views here.
class AttachCoupon(View):
    def get(self, *args, **kwargs):
        coupon = self.request.GET.get('coupon')
        cart = self.request.session.get('cart')
        total_cart_and_shipment = utils.cart_totals(cart)

        try:
            coupon_discount = models.Coupon.objects.get(name=coupon)
            if not self.request.session.get('coupon'):
                self.request.session['coupon'] = {}
            
            saved_coupon = self.request.session['coupon']
            
            if len(list(saved_coupon.values())) >= 1:
                total_with_discount = total_cart_and_shipment - (total_cart_and_shipment*coupon_discount.discount)

        
                context = {
                    'coupon' : coupon_discount,
                    'discount': coupon_discount.discount*100,
                    'total_with_discount' : total_with_discount,
                    'cart' : cart,
                }
                self.request.session.save()
                messages.error(self.request, f"You've already applied this coupon")
                return render(self.request, 'product/cart.html', context)

            saved_coupon[coupon_discount.pk] = {
                'coupon_name': coupon_discount.name,
                'coupon_discount': coupon_discount.discount
            }

            self.request.session.save()

            total_with_discount = total_cart_and_shipment - (total_cart_and_shipment*coupon_discount.discount)
            messages.success(self.request, f'Coupon applied!')

        except models.Coupon.DoesNotExist:
            messages.error(self.request, 'Coupon not found.')
            return redirect('product:cart')
        
        context = {
            'coupon' : coupon_discount,
            'discount': coupon_discount.discount*100,
            'total_with_discount' : total_with_discount,
            'cart' : cart,
        }
        return render(self.request, 'product/cart.html', context)
    
class RemoveCoupon(View):
    def get(self, *args, **kwargs):
        coupon = self.request.GET.get('coupon')
        cart = self.request.session.get('cart')

        if self.request.session.get('coupon'):
            del self.request.session['coupon']
            self.request.session.save()
            messages.success(self.request, f'Coupon removed')
        else:
            messages.error(self.request, 'Coupon not found.')
            return redirect('product:cart')
        context = {
            'cart' : cart,
        }
        return render(self.request, 'product/cart.html', context)