from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from calc import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='calc/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', views.dish_list, name='dish_list'),
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('history/', views.calculation_history, name='calculation_history'),
]