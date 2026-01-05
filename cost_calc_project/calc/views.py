from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from .models import Dish, DishComposition, Overhead, CostCalculation
from decimal import Decimal

@login_required
def dish_list(request):
    """Список всех блюд с краткой информацией"""
    dishes = Dish.objects.filter(is_active=True).prefetch_related('composition')
    return render(request, 'calc/dish_list.html', {'dishes': dishes})

@login_required
def dish_detail(request, dish_id):
    """Детальная информация по блюду с расчетом себестоимости"""
    dish = get_object_or_404(Dish, id=dish_id)
    compositions = dish.composition.all().select_related('ingredient')
    
    # Расчет стоимости ингредиентов
    ingredient_cost = Decimal('0')
    for comp in compositions:
        ingredient_cost += comp.ingredient_cost
    
    # Расчет накладных расходов (упрощенно - равномерно по всем блюдам)
    total_overhead = Overhead.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_dishes = Dish.objects.filter(is_active=True).count()
    overhead_per_dish = total_overhead / total_dishes if total_dishes > 0 else Decimal('0')
    
    # Итоговая себестоимость
    total_cost = ingredient_cost + overhead_per_dish
    
    # Сохраняем расчет в историю
    if request.method == 'POST':
        calculation = CostCalculation.objects.create(
            dish=dish,
            portion_cost=ingredient_cost,
            overhead_per_portion=overhead_per_dish,
            total_cost=total_cost,
            note=f"Расчет от {request.user.username}"
        )
    
    context = {
        'dish': dish,
        'compositions': compositions,
        'ingredient_cost': ingredient_cost,
        'overhead_per_dish': overhead_per_dish,
        'total_cost': total_cost,
    }
    return render(request, 'calc/dish_detail.html', context)

@login_required
def calculation_history(request):
    """История всех расчетов"""
    calculations = CostCalculation.objects.all().select_related('dish').order_by('-calculation_date')
    return render(request, 'calc/history.html', {'calculations': calculations})
