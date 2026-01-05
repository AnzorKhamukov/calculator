from django.db import models
from django.contrib.auth.models import User

# Справочник единиц измерения
class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    short_name = models.CharField(max_length=10, verbose_name="Сокращение")
    
    def __str__(self):
        return f"{self.name} ({self.short_name})"

# Справочник групп/категорий ингредиентов
class IngredientGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    
    def __str__(self):
        return self.name

# Основной справочник: Ингредиенты/сырье
class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")
    group = models.ForeignKey(IngredientGroup, on_delete=models.SET_NULL, null=True, verbose_name="Группа")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="Единица измерения")
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Текущая цена за ед.")
    min_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Минимальный остаток")
    
    def __str__(self):
        return f"{self.name} - {self.current_price} руб./{self.unit.short_name}"

# Технологическая карта (блюдо/полуфабрикат)
class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование блюда")
    description = models.TextField(blank=True, verbose_name="Описание/технология приготовления")
    output_quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Выход, кг/шт")
    output_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='dishes', verbose_name="Единица выхода")
    is_active = models.BooleanField(default=True, verbose_name="Активно для продажи")
    
    def __str__(self):
        return self.name

# Состав блюда (связь многие-ко-многим с количеством)
class DishComposition(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='composition', verbose_name="Блюдо")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, verbose_name="Ингредиент")
    quantity = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Количество на одну порцию")
    losses_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Процент потерь")
    
    class Meta:
        unique_together = ['dish', 'ingredient']
    
    @property
    def quantity_with_losses(self):
        """Количество с учетом потерь"""
        return self.quantity * (1 + self.losses_percent / 100)
    
    @property
    def ingredient_cost(self):
        """Стоимость ингредиента в составе блюда"""
        return self.quantity_with_losses * self.ingredient.current_price

# Статьи накладных расходов
class OverheadCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование статьи")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name

# Накладные расходы (месячные)
class Overhead(models.Model):
    category = models.ForeignKey(OverheadCategory, on_delete=models.CASCADE, verbose_name="Статья расходов")
    month = models.DateField(verbose_name="Месяц")  # храним первое число месяца
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма, руб.")
    
    class Meta:
        unique_together = ['category', 'month']
    
    def __str__(self):
        return f"{self.category.name} - {self.month:%Y-%m}: {self.amount} руб."

# Расчет себестоимости (храним историю расчетов)
class CostCalculation(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name="Блюдо")
    calculation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата расчета")
    portion_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Себестоимость порции")
    overhead_per_portion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Накладные расходы на порцию")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Полная себестоимость")
    note = models.TextField(blank=True, verbose_name="Примечание")
    
    def __str__(self):
        return f"{self.dish.name} - {self.calculation_date:%Y-%m-%d}: {self.total_cost} руб."