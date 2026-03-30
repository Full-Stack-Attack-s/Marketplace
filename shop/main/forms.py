from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Addresses, Products, Users, UserProfiles, Warehouses # Подставь точное название своей модели товара

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

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
        
        if user and hasattr(user, 'storeprofile'):
            self.fields['warehouse'].queryset = Warehouses.objects.filter(
                store=user.storeprofile, 
                is_active=True
            )
            
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'auth-form-input'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['phone_number']

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfiles
        fields = ['first_name', 'last_name', 'birth_date', 'gender', 'avatar']
        widgets = {
            # Делаем так, чтобы браузер показывал удобный календарик
            'birth_date': forms.DateInput(attrs={'type': 'date'}), 
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        # Выводим нужные поля для доставки
        fields = ['country', 'city', 'street', 'zip_code']