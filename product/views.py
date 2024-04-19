from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from uteis import utils

from . import models
from profile_user.models import Profile
from coupon.models import Coupon

# Create your views here.

class ProductsList(ListView):
    model = models.Product
    template_name = 'product/list.html'
    context_object_name = 'products'
    paginate_by = 5
    ordering = ['-id']

class Search(ProductsList):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get("termo") or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs
        
        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(name__icontains=termo) |
            Q(short_description__icontains=termo) |
            Q(long_description__icontains=termo)
        )

        self.request.session.save()
        return qs

class ProductDetail(DetailView):
    model = models.Product
    template_name = 'product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

class AddToCart(View):
    def get(self, *args, **kwargs):
        '''if self.request.session.get('cart'):
            del self.request.session['cart']
            self.request.session.save()'''

        http_referer = self.request.META.get('HTTP_REFERER', reverse('product:list'))
        variation_id = self.request.GET.get('vid')
        product_id = self.request.GET.get('vid2')
        
        

        if product_id:

            product = get_object_or_404(models.Product, id=product_id)
            product_name = product.name
            unit_price = product.marketing_price
            promotional_unit_price = product.promotional_marketing_price
            quantity = 1
            slug = product.slug
            image = product.image
            if image:
                image = image.name
            else:
                image=''

            if product.stock < 1:
                messages.error(self.request, 'Insuficient stock')
                return redirect(http_referer)

            if not self.request.session.get('cart'):
                self.request.session['cart'] = {}
                self.request.session.save()

            cart = self.request.session['cart']

            

            if product_id in list(cart.keys()):
                cart_quantity = cart[product_id]['quantity']
                cart_quantity += 1

                if product.stock < cart_quantity:
                    messages.warning(self.request, f'Insuficient stcok, we have only {product.stock} unities of {product_name}')
                    return redirect(f'/{slug}')


                cart[product_id]['quantity'] = cart_quantity
                cart[product_id]['quantitative_price'] = unit_price * cart_quantity
                cart[product_id]['promotional_quantitative_price'] = promotional_unit_price * cart_quantity


            else:
                cart[product_id] = {
                    'product_id' : product_id,
                    'product_name' : product_name,
                    'unit_price' : unit_price,
                    'promotional_unit_price' : promotional_unit_price,
                    'quantitative_price' : unit_price,
                    'promotional_quantitative_price' : promotional_unit_price,
                    'quantity' : 1,
                    'slug' : slug,
                    'height' : product.height,
                    'weight' : product.weight,
                    'depth' : product.depth,
                    'width' : product.width,
                    'image' : image,
                }                
            self.request.session.save()

            messages.success(self.request, f'Product {product_name} added to your cart')
            return redirect(http_referer)


        if variation_id == None:
            messages.error(self.request, 'Choose an option')
            return redirect(http_referer)

        if not variation_id:
            messages.error(self.request, "Product doesn't exists")
            return redirect(http_referer)


        
        variation = get_object_or_404(models.Variation, id=variation_id)
        variation_id = f'1-{variation_id}'
        variation_stock = variation.stock
        product = variation.product

        product_id = product.id
        product_name = product.name
        variation_name = variation.name
        unit_price = variation.price
        promotional_unit_price = variation.promotional_price
        quantity = 1
        slug = product.slug
        image = product.image
        if image:
            image = image.name
        else:
            image=''

        if variation.stock < 1:
            messages.error(self.request, 'Insuficient stock')
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            self.request.session['cart'] = {}
            self.request.session.save()

        cart = self.request.session['cart']

        if variation_id in cart:
            cart_quantity = cart[variation_id]['quantity']
            cart_quantity += 1

            if variation_stock < cart_quantity:
                messages.warning(self.request, f'Insuficient stock, we only have {variation_stock} unities of {product_name} {variation_name}')
                return redirect(f'/{slug}')


            cart[variation_id]['quantity'] = cart_quantity
            cart[variation_id]['quantitative_price'] = unit_price * cart_quantity
            cart[variation_id]['promotional_quantitative_price'] = promotional_unit_price * cart_quantity


        else:
            cart[variation_id] = {
                'product_id' : product_id,
                'product_name' : product_name,
                'variation_name' : variation_name,
                'variation_id' : variation_id,
                'unit_price' : unit_price,
                'promotional_unit_price' : promotional_unit_price,
                'quantitative_price' : unit_price,
                'promotional_quantitative_price' : promotional_unit_price,
                'quantity' : 1,
                'slug' : slug,
                'height' : product.height,
                'weight' : product.weight,
                'depth' : product.depth,
                'width' : product.width,
                'image' : image,
            }
        self.request.session.save()
        messages.success(self.request, f'Product {product_name} {variation_name} added to your cart')
        return redirect(http_referer)


class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get('HTTP_REFER', reverse('product:list'))
        variation_id = self.request.GET.get('vid')
        product_id = self.request.GET.get('vid2')
        '''frete = self.request.session.get('frete')'''

        if not variation_id and not product_id:
            return redirect(http_referer)
        
        if not self.request.session.get('cart'):
            return redirect(http_referer)

        if variation_id not in self.request.session['cart'] and product_id not in self.request.session['cart']:
            return redirect(http_referer)

        if variation_id:
            cart = self.request.session['cart'][variation_id]
            
            context = {
            'cart': self.request.session.get('cart', {}),
            #'frete': frete
            }

            messages.success(self.request, f'product {cart["product_name"]} {cart["variation_name"]} was removed from your cart')
            del self.request.session['cart'][variation_id]
            self.request.session.save()
            return render(self.request, 'product/cart.html', context)
        else:
            cart = self.request.session['cart'][product_id]

            context = {
            'cart': self.request.session.get('cart', {}),
            #'frete': frete
            }

            del self.request.session['cart'][product_id]
            self.request.session.save()

            if not self.request.session.get('cart'):
                messages.error(
                    self.request,
                    'Empty cart.'
                )
                return redirect('product:list')

            messages.success(self.request, f'Product {cart["product_name"]} removed from your cart')
            return render(self.request, 'product/cart.html', context)
        

class Cart(View):
    def get(self, *args, **kwargs):
        
        # pego perfil para pegar o cep
        # implemento API
        # passo para o contexto os valores da API
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'To access your cart, you need to be registered.')
            return redirect('profile_user:create')

        '''perfil = get_object_or_404(Perfil.objects.filter(user=self.request.user))
    
        url = "https://www.melhorenvio.com.br/api/v2/me/shipment/calculate"

        payload = {
            "from": { "postal_code": f"{perfil.cep}" },
            "to": { "postal_code": "90570020" },
            "package": {
                "height": 4,
                "width": 12,
                "length": 17,
                "weight": 1
            }
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMDQ2NjVjNjAyN2MyODVlMWQyOTc2MjY1OTZiNTE2ZGIwZTMyMDY4M2NjOGZlYTVjMDlkYmVhYzljZTJhZDVhNmI5ZTBlZDVjNTY2ZjE1YzIiLCJpYXQiOjE3MDg1MzY4ODYuODAwODQ3LCJuYmYiOjE3MDg1MzY4ODYuODAwODUsImV4cCI6MTc0MDE1OTI4Ni43ODgzMiwic3ViIjoiOWI2M2JiNjgtOTkyNi00YjYxLWI0MzgtZTcxZThjNDhmYTMwIiwic2NvcGVzIjpbInNoaXBwaW5nLWNhbGN1bGF0ZSJdfQ.WWYMSq0ys7MasoZkcC852JyHMattfAG_cuY9hqohMrd0S1blAKeoCNsU_oAMrfJrQy0h6fPe33dXQL74Jzzg3GD7KshT-zVB8yqPp7pqparBr4SmOUAjsSNgVYwmGxR4FOxl6ZtnDl5_eyQV7iVU_DZDAS1UUw6y2vyFDmk6pZgdxiyraCIr7X6zxHzWDMXiMQogk7YdmDyRN107hbFovxjVM2_dtNmLsz418QNjfI-op2YsHOhLZ--p8id-SIV9PA2DG3Zn4EoAGYCVYmDba5VF3wSUc0hhLWCIJjezN8ewXABwKrgOhqLPDUEfwn043fW2yLiR7yk2Kp6zNogoxDQjJFcRalEEOG7qQrxOkQO-aWeXPMr2kbg0BGK2mcIOKhulpoYswGi2iSPNMPpwzrKl1qv03FqF1r1CeLnNsVlfKIdQQ4Cjw7bItyaSuyHNzQAbk2-NNO2zbSGGoPTPFkG4fkHhMn5mH7EPl5_8j-8w3vsmrTESScNOAuQk9lAOhLaokRz7R2VwsHJg37PongP3BFqdUo2ZESnMKfG9WSYCraO9jrBi3U2kF-mKFES-A9m5xfVjxWUWh3S4zdoU95u4O7YrkXbMR0IMV9M6Acl40YX5_NFbC9IFLgl5ZA5XiNWThRV1gLjjBTD4qZXzgbjZYTveN6syv3XmpcyIwXA",
            "User-Agent": "Aplicação pedrobg2707@gmail.com"
        }

        retorno = requests.post(url, json=payload, headers=headers).json()

        list_de_transportadoras_valores = [ item for item in retorno if 'price' in item]
        list_de_transportadoras_names = [ price['name'] for price in list_de_transportadoras_valores]
        list_de_transportadoras_valores = [ price['price'] for price in list_de_transportadoras_valores]
        empresa_frete = list_de_transportadoras_names[0]
        valor_frete = list_de_transportadoras_valores[0]'''

        cart = self.request.session.get('cart', {})
        coupon = self.request.session.get('coupon', {})
        coupon_list = list(coupon.values())
        
        if len(coupon_list) >= 1:
            coupon_discount = Coupon.objects.get(name=coupon_list[0]['coupon_name'])
            total_cart_and_shipment = utils.cart_totals(cart)
            total_with_discount = total_cart_and_shipment - (total_cart_and_shipment*coupon_discount.discount)

            '''total_cart = sum([total_quant['quantitative_price'] for total_quant in cart.values()]) + float(valor_frete)

            frete = self.request.session.get('frete', {})
            self.request.session['frete'] = round(float(valor_frete), 2)'''
            
            self.request.session.save()

            #print(self.request.session.get('frete', {}))

            context = {
                'coupon' : coupon_discount,
                'discount': coupon_discount.discount*100,
                'total_with_discount' : total_with_discount,
                'cart' : cart,
                #'frete' : round(float(valor_frete), 2)
            }

        else:
            self.request.session.save()

            context = {
                'cart' : cart,
                #'frete' : round(float(valor_frete), 2)
            }

        return render(self.request, 'product/cart.html', context)


class OrderResume(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('profile_user:create')

        profile = Profile.objects.filter(user=self.request.user).exists()

        if not profile:
            messages.error(
                self.request,
                'User without profile. Update your info.'
            )
            return redirect('profile_user:create')



        contexto = {
            'user': self.request.user,
            'cart': self.request.session['cart'],

        }

        return render(self.request, 'product/orderresume.html', contexto)