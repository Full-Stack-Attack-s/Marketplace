from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .forms import AddressForm, ProductForm, UserProfileEditForm,  StoreVerificationForm, UserProfileForm, UserEditForm
from .models import Product_variants, Product_images, OrderItems, ProductAttributeValues, Products, UserProfiles, \
    models, CategoryAttributes, Addresses, Stocks, Warehouses, StoreProfiles, Carts, \
    CartItems , Favorites, Categories, Messages, Users
from django.db.models import Q
from django.core.paginator import Paginator


# def index(request):
    ## Достаем варианты и сразу "приклеиваем" к ним родительский товар
    ## Ограничим до 20 штук для главной страницы
    # variants = models.Product_variants.objects.select_related('product_id').all()[:20]
    
    ## Отправляем в шаблон под тем именем, которое ты используешь в цикле
    # return render(request, "index.html", {"products_variants": variants})



@login_required
def manage_products(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Products, id=product_id, seller=request.user)
        
        if 'delete' in request.POST:
            product.delete()
            return redirect('manage_products')
            
        # Логика быстрого сохранения
        new_status = request.POST.get('status')
        if new_status:
            product.status = new_status
            product.save(update_fields=['status'])

        variant = product.product_variants_set.first()
        if variant:
            new_price = request.POST.get('price')
            if new_price:
                variant.price = new_price
                variant.save(update_fields=['price'])
                
            new_stock = request.POST.get('stock')
            if new_stock and new_stock.isdigit():
                stock_record = Stocks.objects.filter(product_variant=variant).first()
                if stock_record:
                    stock_record.quantity = int(new_stock)
                    stock_record.save(update_fields=['quantity'])
                    
        return redirect('manage_products')

    products = Products.objects.filter(seller=request.user).prefetch_related('product_variants_set', 'product_images_set').order_by('-created_at')
    return render(request, 'products_list.html', {'products': products})

# ============================================
# views.py
# ============================================
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CategoryAttributes, StoreProfiles, UserProfiles, Products, Product_variants, Stocks, Product_images
from .forms import ProductForm, StoreVerificationForm, UserProfileForm

@login_required
def seller_dashboard(request):
    user = request.user
    store_profile, _ = StoreProfiles.objects.get_or_create(user=user)
    
    if request.method == 'POST' and 'update_order_status' in request.POST:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        from .models import Orders
        from django.shortcuts import get_object_or_404
        order = get_object_or_404(Orders, id=order_id)
        # Проверка: заказ должен содержать товары этого продавца
        if OrderItems.objects.filter(order=order, product_variant__product__seller=user).exists():
            order.status = new_status
            order.save()
            return redirect('seller_dashboard')
    
    # 1. Активные товары
    active_products = Products.objects.filter(seller=user, status='active').count()
    
    # 2. Новые заказы (по товарам этого продавца)
    new_orders = OrderItems.objects.filter(
        product_variant__product__seller=user, 
        order__status='pending'
    ).count()
    
    # 3. Общая выручка (только оплаченные/завершенные)
    sales_total = OrderItems.objects.filter(
        product_variant__product__seller=user, 
        order__status__in=['paid', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0.00

    # 4. Последние заказы
    recent_orders = OrderItems.objects.filter(
        product_variant__product__seller=user
    ).select_related('order', 'product_variant__product').order_by('-order__created_at')[:5]

    # 5. Топ-3 продаваемых товара
    top_selling = OrderItems.objects.filter(
        product_variant__product__seller=user,
        order__status__in=['paid', 'completed']
    ).values(
        'product_variant__product__name', 
        'product_variant__product__id'
    ).annotate(
        total_qty=Sum('quantity'), 
        total_sum=Sum('total_price')
    ).order_by('-total_qty')[:3]

    return render(request, 'seller_dashboard.html', {
        'active_products': active_products,
        'new_orders': new_orders,
        'sales_total': sales_total,
        'recent_orders': recent_orders,
        'store_profile': store_profile,
        'top_selling': top_selling,
    })

@login_required
def seller_profile(request):
    user_profile, _ = UserProfiles.objects.get_or_create(user=request.user)
    store_profile, _ = StoreProfiles.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'update_user' in request.POST:
            user_form = UserProfileForm(request.POST, instance=user_profile)
            store_form = StoreVerificationForm(instance=store_profile)
            if user_form.is_valid():
                user_form.save()
                return redirect('seller_profile')
                
        elif 'verify_store' in request.POST:
            user_form = UserProfileForm(instance=user_profile)
            store_form = StoreVerificationForm(request.POST, request.FILES, instance=store_profile)
            if store_form.is_valid():
                store = store_form.save(commit=False)
                # Если уже подтвержден - не сбрасываем статус при обновлении лого/описания
                if store_profile.verification_status != 'approved':
                    store.verification_status = 'pending'
                store.save()
                return redirect('seller_profile')
    else:
        user_form = UserProfileForm(instance=user_profile)
        store_form = StoreVerificationForm(instance=store_profile)
        
    return render(request, 'seller_profile.html', {
        'user_form': user_form,
        'store_form': store_form,
        'store_profile': store_profile,
    })

def get_category_attributes(request, category_id):
    # Получаем все атрибуты, привязанные к конкретной категории
    attrs = CategoryAttributes.objects.filter(category_id=category_id)
    data = [
        {
            "id": a.id,
            "label": a.label,   # основное поле для отображения
            "name": a.label,    # алиас для совместимости с JS
            "is_required": a.is_required,
            "type": a.type,
        } for a in attrs
    ]
    return JsonResponse(data, safe=False)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            price = form.cleaned_data.get('price', 0)
            stock_qty = form.cleaned_data.get('stock', 0)
            selected_warehouse = form.cleaned_data.get('warehouse')

            # 1. СОЗДАЕМ ВАРИАНТ
            variant = Product_variants.objects.create(
                product=product,
                price=price
            )

            # 2. СОХРАНЯЕМ ДИНАМИЧЕСКИЕ АТРИБУТЫ
            for key, value in request.POST.items():
                if key.startswith('attr_') and value.strip():
                    attr_label = key.replace('attr_', '')
                    try:
                        attribute_def = CategoryAttributes.objects.get(
                            label=attr_label,
                            category=product.category
                        )
                        ProductAttributeValues.objects.update_or_create(
                            product=product,
                            attribute=attribute_def,
                            defaults={'value': value}
                        )
                    except CategoryAttributes.DoesNotExist:
                        continue

            # 3. ОСТАТКИ
            if selected_warehouse:
                Stocks.objects.create(
                    product_variant=variant,
                    warehouse=selected_warehouse,
                    quantity=stock_qty
                )

            # 4. НЕСКОЛЬКО ФОТОГРАФИЙ (новый функционал)
            images = request.FILES.getlist('images')
            for idx, img_file in enumerate(images):
                Product_images.objects.create(
                    product=product,
                    image=img_file,
                    is_main=(idx == 0),   # Первая фото — главная
                    sort_order=idx + 1
                )

            # Обратная совместимость: одиночное поле 'image' из формы
            single_image = form.cleaned_data.get('image')
            if single_image and not images:
                Product_images.objects.create(product=product, image=single_image, is_main=True)

            return redirect('manage_products')
    else:
        form = ProductForm(user=request.user)
    return render(request, 'add_product.html', {'form': form, 'title': 'Добавить товар'})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id, seller=request.user)
    variant = product.product_variants_set.first()
    image = product.product_images_set.first()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            form.save()

            price = form.cleaned_data.get('price', 0)
            stock_qty = form.cleaned_data.get('stock', 0)
            selected_warehouse = form.cleaned_data.get('warehouse')

            # 1. Сохраняем атрибуты в правильную таблицу
            for key, value in request.POST.items():
                if key.startswith('attr_') and value.strip():
                    attr_label = key.replace('attr_', '')
                    try:
                        attribute_def = CategoryAttributes.objects.get(
                            label=attr_label,
                            category=product.category
                        )
                        ProductAttributeValues.objects.update_or_create(
                            product=product,
                            attribute=attribute_def,
                            defaults={'value': value}
                        )
                    except CategoryAttributes.DoesNotExist:
                        continue

            # 2. Обновляем или создаем вариант (только цену)
            if variant:
                variant.price = price
                variant.save()
            else:
                variant = Product_variants.objects.create(
                    product=product,
                    price=price
                )

            if selected_warehouse:
                Stocks.objects.update_or_create(
                    product_variant=variant,
                    warehouse=selected_warehouse,
                    defaults={'quantity': stock_qty}
                )

            # 3. Новые фотографии (мульти-загрузка)
            new_images = request.FILES.getlist('images')
            existing_count = product.product_images_set.count()
            for idx, img_file in enumerate(new_images):
                Product_images.objects.create(
                    product=product,
                    image=img_file,
                    is_main=(existing_count == 0 and idx == 0),
                    sort_order=existing_count + idx + 1
                )

            # Обратная совместимость: одиночное поле 'image'
            single_image = form.cleaned_data.get('image')
            if single_image and not new_images:
                if image:
                    image.image = single_image
                    image.save()
                else:
                    Product_images.objects.create(product=product, image=single_image, is_main=True)

            return redirect('manage_products')
    else:
        initial_data = {}
        if variant:
            initial_data['price'] = variant.price
            stock_record = Stocks.objects.filter(product_variant=variant).first()
            if stock_record:
                initial_data['stock'] = stock_record.quantity
                initial_data['warehouse'] = stock_record.warehouse
        form = ProductForm(instance=product, initial=initial_data, user=request.user)

    # Достаем реальные значения атрибутов
    existing_attrs = {
        item.attribute.label: item.value
        for item in product.attribute_values.select_related('attribute').all()
    }

    return render(request, 'add_product.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product,
        'variant': variant,
        'existing_attrs_json': json.dumps(existing_attrs, ensure_ascii=False)
    })

@login_required
def profile(request):
    from .models import Orders, Favorites, Addresses
    user_profile, _ = UserProfiles.objects.get_or_create(user=request.user)
    
    # Адрес доставки
    default_address = request.user.addresses.filter(is_default=True).first() or request.user.addresses.first()

    # Статистика
    favorites_count = Favorites.objects.filter(user=request.user).count()
    orders_count = Orders.objects.filter(user=request.user).count()
    recent_orders = Orders.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'default_address': default_address,
        'favorites_count': favorites_count,
        'orders_count': orders_count,
        'recent_orders': recent_orders,
        'reviews_count': 0,
    })

@login_required
def profile_edit(request):
    from .models import UserProfiles, Addresses
    from .forms import UserProfileEditForm, AddressForm
    
    user_profile, _ = UserProfiles.objects.get_or_create(user=request.user)
    address = request.user.addresses.filter(is_default=True).first() or request.user.addresses.first()

    if request.method == 'POST':
        if 'update_user' in request.POST:
            profile_form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')
        elif 'update_address' in request.POST:
            country = request.POST.get('country', '').strip()
            city = request.POST.get('city', '').strip()
            street = request.POST.get('street', '').strip()
            zip_code = request.POST.get('zip_code', '').strip()
            
            if any([country, city, street, zip_code]):
                if address:
                    address.country = country
                    address.city = city
                    address.street = street
                    address.zip_code = zip_code
                    address.save()
                else:
                    address = Addresses.objects.create(
                        user=request.user, 
                        country=country, 
                        city=city, 
                        street=street, 
                        zip_code=zip_code, 
                        is_default=True
                    )
            return redirect('profile')
    
    profile_form = UserProfileEditForm(instance=user_profile)
    return render(request, 'profile_edit.html', {
        'profile_form': profile_form,
        'user_profile': user_profile,
        'address': address,
    })

@login_required
def quick_update_product(request, product_id):
    if request.method == 'POST':
        # Находим товар (только если он принадлежит текущему продавцу)
        product = get_object_or_404(Products, id=product_id, seller=request.user)
        
        # Обновляем статус
        new_status = request.POST.get('status')
        if new_status in ['draft', 'active', 'archived']: # Проверяем, что статус допустимый
            product.status = new_status
            product.save()
            
        # Обновляем цену
        new_price = request.POST.get('price')
        if new_price:
            # Находим первую вариацию товара (где лежит цена)
            variant = product.product_variants_set.first()
            if variant:
                variant.price = new_price
                variant.save()
                
    return redirect('seller_dashboard')

def get_attributes(request, category_id):
    # Получаем все атрибуты, привязанные к конкретной категории
    attrs = CategoryAttributes.objects.filter(category_id=category_id)
    data = [
        {
            "id": a.id, 
            "label": a.label, 
            "type": a.type # 'string', 'number' или 'select'
        } for a in attrs
    ]
    return JsonResponse(data, safe=False)


def index(request):
    #Cчитаем реальные остатки прямо внутри SQL-запроса
    popular_products = Products.objects.filter(status='active').annotate(
        # Суммируем количество со всех складов для всех вариантов товара.
        # Coalesce нужен, чтобы заменить NULL на 0, если складов еще нет.
        total_quantity=Coalesce(Sum('product_variants__stock__quantity'), 0, output_field=IntegerField()),
        total_reserved=Coalesce(Sum('product_variants__stock__reserved_quantity'), 0, output_field=IntegerField())
    ).annotate(
        # Считаем свободный остаток: всё, что на складе МИНУС то, что уже в чужих заказах
        available_stock=F('total_quantity') - F('total_reserved')
    ).filter(
        # ЖЕСТКИЙ ФИЛЬТР: выводим на витрину только те товары, где есть хотя бы 1 свободная штука
        available_stock__gt=0
    ).order_by('-sales_count')[:30] # Ограничим до 30 самых популярных товаров
    user_favorites = []
    if request.user.is_authenticated:
        # Собираем ID всех лайкнутых товаров текущего юзера
        from .models import Favorites  # Не забудь импорт!
        user_favorites = Favorites.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'index.html', {
        'products': popular_products,
        'user_favorites': list(user_favorites)})









#///////////////////////////////////////////////////////////////////
# def cart(request):
#     return render(request, "cart.html")
#  для поиска или создания корзины
def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
        request.session['cart_initialized'] = True  # Заставляет Django отправить cookie

    # корзина по ключу сессии
    cart, created = Carts.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={'user': request.user if request.user.is_authenticated else None}
    )
    return cart


# страница корзины
def cart(request):
    cart = get_or_create_cart(request)
    items = cart.items.all()  # related_name='items' из твоих моделей

    # общую сумму
    total_price = sum(item.product_variant.price * item.quantity for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total_price": total_price,
    })


#  "В корзину" (для JS)
@require_POST
def add_to_cart(request, variant_id):
    cart = get_or_create_cart(request)
    variant = get_object_or_404(Product_variants, id=variant_id)

    # есть ли уже такой товар в корзине
    item, created = CartItems.objects.get_or_create(
        cart=cart,
        product_variant=variant
    )

    if not created:
        item.quantity += 1
        item.save()

    #  чтобы JS понял что всё ок
    return JsonResponse({
        'status': 'ok',
        'cart_count': cart.items.count()
    })


def cards(request):
    return render(request, "cards.html")
def catalog(request):
    # Берем только корневые категории и подтягиваем детей (до 2 уровня вложенности)
    root_categories = Categories.objects.filter(parent__isnull=True).prefetch_related('children__children')
    return render(request, "catalog.html", {'root_categories': root_categories})

def checkout_view(request):
    # 1. Если сессии еще нет (гость ничего не делал на сайте), Джанго должен её физически создать
    if not request.session.session_key:
        request.session.create()

    # 2. Забираем сгенерированный ключ (например, '5b3v2xjf...')
    current_session_key = request.session.session_key

    # 3. Создаем заказ и подставляем ключ в поле session_key
    order = models.Orders.objects.create(
        session_key=current_session_key,
        
        # Сразу умная проверка: если юзер авторизован, пишем его объект в user_id. 
        # Если нет (аноним) — пишем None (это разрешено твоим null=True)
        user_id=request.user if request.user.is_authenticated else None
    )
    
    # ... дальше логика добавления конкретных товаров в этот заказ ...

    return render(request, "catalog.html")

@require_POST
@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    favorite, created = Favorites.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True

    favorites_count = Favorites.objects.filter(user=request.user).count()
    return JsonResponse({
        'status': 'ok', 
        'is_favorite': is_favorite,
        'favorites_count': favorites_count
    })

@login_required
def favorites(request):
    fav_items = Favorites.objects.filter(user=request.user).select_related('product').prefetch_related('product__product_variants_set')
    return render(request, 'favorites.html', {'favorites': fav_items})


@require_POST
def update_cart_quantity(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItems, id=item_id, cart=cart)
    
    try:
        data = json.loads(request.body)
        new_quantity = int(data.get('quantity', 1))
        if new_quantity > 0:
            item.quantity = new_quantity
            item.save()
            
            # Пересчитываем общую сумму
            total_price = sum(i.product_variant.price * i.quantity for i in cart.items.all())
            item_total = item.product_variant.price * item.quantity
            
            return JsonResponse({
                'status': 'ok', 
                'total_price': float(total_price),
                'item_total': float(item_total)
            })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItems, id=item_id, cart=cart)
    item.delete()
    
    total_price = sum(i.product_variant.price * i.quantity for i in cart.items.all())
    return JsonResponse({
        'status': 'ok', 
        'total_price': float(total_price),
        'cart_empty': not cart.items.exists()
    })


def product_detail(request, product_id):
    # select_related для продавца и его профиля магазина (избегаем N+1)
    # prefetch_related для атрибутов, изображений и вариантов
    product = get_object_or_404(
        Products.objects.select_related(
            'seller', 'seller__store_profile', 'category', 'brand'
        ).prefetch_related(
            'attribute_values__attribute',
            'product_images_set',
            'product_variants_set',
        ),
        id=product_id
    )
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Favorites.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'cards.html', {
        'product': product,
        'user_favorites': list(user_favorites)
    })


@require_POST
@login_required
def delete_product_image(request, image_id):
    """AJAX: удаление отдельного фото товара продавцом."""
    image = get_object_or_404(
        Product_images,
        id=image_id,
        product__seller=request.user
    )
    product = image.product
    image.delete()
    # Если удалили главное фото — назначаем главной следующую
    if not product.product_images_set.filter(is_main=True).exists():
        first = product.product_images_set.first()
        if first:
            first.is_main = True
            first.save(update_fields=['is_main'])
    return JsonResponse({'status': 'ok', 'image_id': image_id})

def search(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', '-created_at')
    in_stock = request.GET.get('in_stock', '')

    # Base queryset: only active products
    products = Products.objects.filter(status='active').annotate(
        total_quantity=Coalesce(Sum('product_variants__stock__quantity'), 0, output_field=IntegerField()),
        total_reserved=Coalesce(Sum('product_variants__stock__reserved_quantity'), 0, output_field=IntegerField())
    ).annotate(
        available_stock=F('total_quantity') - F('total_reserved')
    )

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if price_min:
        products = products.filter(product_variants__price__gte=price_min)

    if price_max:
        products = products.filter(product_variants__price__lte=price_max)

    if in_stock:
        products = products.filter(available_stock__gt=0)

    products = products.distinct()
    total_count = products.count()

    if sort_by == 'price_asc':
        products = products.order_by('product_variants__price')
    elif sort_by == 'price_desc':
        products = products.order_by('-product_variants__price')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Categories.objects.all()

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Favorites.objects.filter(user=request.user).values_list('product_id', flat=True)

    sort_options = [
        ('-created_at', 'Сначала новые'),
        ('price_asc', 'Сначала дешевле'),
        ('price_desc', 'Сначала дороже'),
    ]

    return render(request, 'search.html', {
        'query': query,
        'products': page_obj,
        'total_count': total_count,
        'categories': categories,
        'selected_category': category_id,
        'price_min': price_min,
        'price_max': price_max,
        'selected_sort': sort_by,
        'sort_options': sort_options,
        'in_stock': in_stock,
        'user_favorites': list(user_favorites),
    })

def checkout(request):
    from .models import Carts, Orders, OrderItems
    from django.shortcuts import render, redirect
    
    # 1. Получаем корзину
    if request.user.is_authenticated:
        cart = Carts.objects.filter(user=request.user).first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Carts.objects.filter(id=cart_id).first() if cart_id else None
        
    if not cart or not cart.items.exists():
        return redirect('cart')
        
    items = cart.items.select_related('product_variant__product')
    total_price = sum(item.product_variant.price * item.quantity for item in items)
    
    if request.method == 'POST':
        # 2. Создаем заказ
        order = Orders.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_amount=total_price,
            status='paid' # Сразу оплачен для демо
        )
        for item in items:
            OrderItems.objects.create(
                order=order,
                product_variant=item.product_variant,
                seller=item.product_variant.product.seller,
                quantity=item.quantity,
                price_per_unit=item.product_variant.price,
                total_price=item.product_variant.price * item.quantity
            )
        # 3. Очищаем корзину
        cart.items.all().delete()
        return render(request, 'checkout_success.html', {'order': order})
        
    return render(request, 'checkout.html', {
        'items': items,
        'total_price': total_price
    })

# ============================================
# Chat Views
# ============================================

@login_required
def chat_list(request):
    # Получаем все уникальные диалоги текущего пользователя
    # Группируем по последнему сообщению с каждым собеседником
    
    # Так как SQLite не поддерживает DISTINCT ON, сделаем это вручную
    messages = Messages.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')
    
    dialogs = {}
    for msg in messages:
        other_user = msg.recipient if msg.sender == request.user else msg.sender
        if other_user.id not in dialogs:
            dialogs[other_user.id] = {
                'other_user': other_user,
                'last_message': msg,
                'unread_count': 0
            }
        # Считаем непрочитанные сообщения от этого пользователя
        if msg.sender == other_user and not msg.is_read:
            dialogs[other_user.id]['unread_count'] += 1
            
    return render(request, 'chat_list.html', {'dialogs': dialogs.values()})

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(Users, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Messages.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            # Возвращаем JSON для AJAX запроса
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'id': msg.id,
                    'content': msg.content,
                    'created_at': msg.created_at.strftime('%H:%M'),
                    'sender_id': msg.sender.id
                })
            return redirect('chat_detail', user_id=user_id)
            
    # Отмечаем сообщения как прочитанные
    Messages.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    messages = Messages.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')
    
    return render(request, 'chat_detail.html', {
        'other_user': other_user,
        'messages': messages
    })

@login_required
def chat_get_new_messages(request, user_id):
    last_message_id = request.GET.get('last_message_id', 0)
    other_user = get_object_or_404(Users, id=user_id)
    
    try:
        last_message_id = int(last_message_id)
    except ValueError:
        last_message_id = 0
        
    new_messages = Messages.objects.filter(
        id__gt=last_message_id,
        sender=other_user,
        recipient=request.user
    ).order_by('created_at')
    
    # Сразу отмечаем прочитанными
    new_messages.update(is_read=True)
    
    data = []
    for msg in new_messages:
        data.append({
            'id': msg.id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M'),
            'sender_id': msg.sender.id
        })
        
    return JsonResponse({'messages': data})
