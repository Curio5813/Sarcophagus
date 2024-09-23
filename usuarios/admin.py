from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .forms import CustomUsuarioCreationForm, CustomUsuarioChangeForm
from .models import CustomUsuarios


@admin.register(CustomUsuarios)
class CustomUsuarioAdmin(UserAdmin):
    add_form = CustomUsuarioCreationForm
    form = CustomUsuarioChangeForm
    model = CustomUsuarios
    list_display = ('first_name', 'last_name', 'email', 'phone', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informções Pessoais', {'fields': ('first_name', 'last_name', 'phone', 'usable_password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

