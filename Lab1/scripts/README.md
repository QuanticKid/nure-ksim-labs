# Скрипти ЛР1

Відтворення експерименту 2 (вплив `evaporation-rate` на час збору їжі) для оригінальної моделі Ants.
Експерименти 1 і 3 виконувалися вручну командою в Command Center (див. [звіт](../README.md#примітки)).

| Файл | Що робить |
|---|---|
| `evaporation_experiment.xml` | налаштування BehaviorSpace: `evaporation-rate` = 5, 10, 15, 20, 25, 30 %, по 5 прогонів, population = 125, diffusion-rate = 50; прогін зупиняється, коли на полі не залишилося їжі (не довше 30000 тактів) |
| `make_chart.py` | будує графік `../exp2_chart.png` з таблиці результатів і друкує таблицю для звіту |
| `../evaporation_raw.csv` | результати прогонів (таблиця BehaviorSpace) |

## Запуск
Потрібні NetLogo 6.4.0, Java 17+ і Python з `matplotlib`. Модель — оригінальна [Ants](https://github.com/NetLogo/models/blob/6.4.0/Sample%20Models/Biology/Ants.nlogo) з бібліотеки NetLogo.

1. Прогони (без графічного інтерфейсу, у 6 потоків):
   ```
   java -cp "D:/NetLogo 6.4.0/app/netlogo-6.4.0.jar" org.nlogo.headless.Main --model Ants.nlogo --setup-file evaporation_experiment.xml --table ../evaporation_raw.csv --threads 6
   ```
   Те саме можна зробити в NetLogo через Tools → BehaviorSpace.
2. Графік:
   ```
   python make_chart.py
   ```
