from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F, IntegerField
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AddressForm, ProductForm, UserEditForm, UserProfileEditForm
from .models import Product_variants, Product_images, OrderItems, ProductAttributeValues, Products, models, CategoryAttributes, Addresses, Stocks, Warehouses # Обязательно добавь этот импорт!


# def index(request):
    ## Достаем варианты и сразу "приклеиваем" к ним родительский товар
    ## Ограничим до 20 штук для главной страницы
    # variants = models.Product_variants.objects.select_related('product_id').all()[:20]
    
    ## Отправляем в шаблон под тем именем, которое ты используешь в цикле
    # return render(request, "index.html", {"products_variants": variants})

@login_required
def seller_dashboard(request):
    # Пускаем только продавцов
    if request.user.role != 'seller':
        return redirect('profile')

    my_products = Products.objects.filter(seller=request.user).order_by('-created_at')
    my_sales = OrderItems.objects.filter(seller=request.user).order_by('-order__created_at')

    context = {
        'products': my_products,
        'sales': my_sales,
    }
    return render(request, 'account/seller_dashboard.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        # ПЕРЕДАЕМ user=request.user в форму!
        form = ProductForm(request.POST, request.FILES, user=request.user) 
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            price = form.cleaned_data.get('price', 0)
            stock_qty = form.cleaned_data.get('stock', 0)
            selected_warehouse = form.cleaned_data.get('warehouse') # ДОСТАЕМ ВЫБРАННЫЙ СКЛАД

            variant = Product_variants.objects.create(product=product, price=price)

            # Сохраняем остатки строго на выбранный склад
            Stocks.objects.create(
                product_variant=variant, 
                warehouse=selected_warehouse, 
                quantity=stock_qty
            )
            # ... сохранение картинки ...
            return redirect('seller_dashboard')
        else:
            print("ОШИБКИ ФОРМЫ ДОБАВЛЕНИЯ:", form.errors) # Ловушка для ошибок!
    else:
        # ПЕРЕДАЕМ user=request.user и для пустой формы (чтобы склады загрузились)
        form = ProductForm(user=request.user) 
        
    return render(request, 'add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    # 1. Достаем товар, вариант (где цена) и картинку
    product = get_object_or_404(Products, id=product_id, seller=request.user)
    variant = product.product_variants_set.first()
    image = product.product_images_set.first()

    if request.method == 'POST':
        # ВАЖНО: передаем user=request.user, чтобы форма знала, чьи склады проверять
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        
        if form.is_valid():
            # Сохраняем основные данные товара (Название, Описание, Статус и т.д.)
            form.save() 
            
            # Достаем данные кастомных полей из формы
            price = form.cleaned_data.get('price', 0)
            stock_qty = form.cleaned_data.get('stock', 0)
            selected_warehouse = form.cleaned_data.get('warehouse')

            # 2. Обновляем или создаем Вариант товара (там хранится цена)
            if variant:
                variant.price = price
                variant.save()
            else:
                variant = Product_variants.objects.create(product=product, price=price)

            # 3. Обновляем или создаем Остатки (связка Вариант + Склад)
            if selected_warehouse:
                Stocks.objects.update_or_create(
                    product_variant=variant,
                    warehouse=selected_warehouse,
                    defaults={'quantity': stock_qty}
                )

            # 4. Обновляем картинку, если загрузили новую
            new_image = form.cleaned_data.get('image')
            if new_image:
                if image:
                    image.image = new_image
                    image.save()
                else:
                    Product_images.objects.create(product=product, image=new_image, is_main=True)
                    
            return redirect('seller_dashboard')
            
        else:
            # Если форма не сохранилась, Питон выведет причину в терминал
            print("=== ОШИБКА ВАЛИДАЦИИ ФОРМЫ ===")
            print(form.errors)
            
    else:
        # GET-ЗАПРОС: Подготавливаем данные для заполнения полей при открытии страницы
        initial_data = {}
        if variant:
            initial_data['price'] = variant.price
            
            # Ищем остатки для этого варианта
            stock_record = Stocks.objects.filter(product_variant=variant).first()
            if stock_record:
                initial_data['stock'] = stock_record.quantity
                initial_data['warehouse'] = stock_record.warehouse # Подставляем старый склад
                
        # Создаем форму с подгруженными данными
        form = ProductForm(instance=product, initial=initial_data, user=request.user)

    return render(request, 'add_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Products, id=product_id, seller=request.user)
        product.delete()
    return redirect('seller_dashboard')

@login_required
def profile(request):
    # Пытаемся найти основной адрес пользователя. Если его нет — вернется None
    address = request.user.addresses.filter(is_default=True).first()
    if not address:
        address = request.user.addresses.first()

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = UserProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        address_form = AddressForm(instance=address, data=request.POST) # Подключаем третью форму
        
        if user_form.is_valid() and profile_form.is_valid() and address_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Сохраняем адрес и жестко привязываем его к текущему пользователю
            saved_address = address_form.save(commit=False)
            saved_address.user = request.user
            saved_address.is_default = True
            saved_address.save()
            
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileEditForm(instance=request.user.profile)
        address_form = AddressForm(instance=address)
        
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'address_form': address_form, # Передаем в шаблон
        'current_address': address,
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

    return render(request, 'index.html', {'products': popular_products})

def cart(request):
    return render(request, "cart.html")
def profile(request):
    return render(request, "profile.html")
def cards(request):
    return render(request, "cards.html")
def catalog(request):
    return render(request, "catalog.html")

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

