from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Addresses, Products, Users, UserProfiles, Warehouses, StoreProfiles # Подставь точное название своей модели товара

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

class StoreVerificationForm(forms.ModelForm):
    class Meta:
        model = StoreProfiles
        fields = ['company_name', 'inn', 'legal_address', 'description', 'logo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'auth-form input'
    # --- ДОБАВЛЯЕМ ПОДСКАЗКИ (PLACEHOLDERS) СЮДА ---
        self.fields['company_name'].widget.attrs['placeholder'] = 'Например: ООО "Ромашка" или ИП Иванов И.И.'
        self.fields['inn'].widget.attrs['placeholder'] = 'Формат: 10 или 12 цифр'
        self.fields['legal_address'].widget.attrs['placeholder'] = 'Например: 123456, г. Москва, ул. Пушкина, д. 1, оф. 2'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfiles
        fields = ['first_name', 'last_name', 'phone_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'auth-form input'

class ProductForm(forms.ModelForm):
    price = forms.DecimalField(max_digits=19, decimal_places=4, label="Цена (₽)")
    image = forms.ImageField(label="Главное изображение", required=False)
    stock = forms.IntegerField(min_value=0, label="Остаток (шт.)", initial=0)
    
    warehouse = forms.ModelChoiceField(
        queryset=Warehouses.objects.none(),
        label="Склад отгрузки",
        empty_label="Выберите склад",
        required=True
    )

    class Meta:
        model = Products
        fields = ['name', 'category', 'brand', 'description', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'store_profile'):
            self.fields['warehouse'].queryset = Warehouses.objects.filter(
                store=user.store_profile, 
                is_active=True
            )
            
        for field in self.fields.values():
            field.widget.attrs['class'] = 'auth-form input'


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfiles
        fields = ['first_name', 'last_name', 'patronymic', 'phone_number', 'birth_date', 'gender', 'avatar']
        widgets = {
            # Делаем так, чтобы браузер показывал удобный календарик
            'birth_date': forms.DateInput(attrs={'type': 'date'}), 
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        # Выводим нужные поля для доставки
        fields = ['country', 'city', 'street', 'zip_code']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['email']