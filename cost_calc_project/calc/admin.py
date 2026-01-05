from django.contrib import admin
from .models import (
    Unit, IngredientGroup, Ingredient, 
    Dish, DishComposition, OverheadCategory, 
    Overhead, CostCalculation
)



@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    search_fields = ('name', 'short_name')

@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'unit', 'current_price')
    list_filter = ('group', 'unit')
    search_fields = ('name', 'group__name')
    list_editable = ('current_price',)

class DishCompositionInline(admin.TabularInline):
    model = DishComposition
    extra = 1
    autocomplete_fields = ['ingredient']

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'output_quantity', 'output_unit', 'is_active')
    list_filter = ('is_active', 'output_unit')
    search_fields = ('name', 'description')
    inlines = [DishCompositionInline]
    list_editable = ('is_active',)

@admin.register(OverheadCategory)
class OverheadCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Overhead)
class OverheadAdmin(admin.ModelAdmin):
    list_display = ('category', 'month', 'amount')
    list_filter = ('category', 'month')
    date_hierarchy = 'month'
    list_editable = ('amount',)

@admin.register(CostCalculation)
class CostCalculationAdmin(admin.ModelAdmin):
    list_display = ('dish', 'calculation_date', 'total_cost', 'portion_cost', 'overhead_per_portion')
    list_filter = ('calculation_date', 'dish')
    search_fields = ('dish__name', 'note')
    date_hierarchy = 'calculation_date'
    readonly_fields = ('calculation_date',)