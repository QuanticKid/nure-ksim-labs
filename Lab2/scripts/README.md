# Скрипти ЛР2

Відтворення обох обчислювальних експериментів для зміненої моделі [`Ants_modified.nlogo`](../Ants_modified.nlogo).

| Файл | Що робить |
|---|---|
| `reproduction_experiment.xml` | експеримент 1 (BehaviorSpace): population = 10…150, `reproduction?` off/on, по 10 прогонів; прогін зупиняється, коли на полі не залишилося їжі (не довше 30000 тактів) |
| `CaloriesExperiment.java` | експеримент 2: 30 розстановок купок × калорійність купки №1 = 1…5 (`calorie-mode` = "one rich"). Для кожної розстановки купки стоять на тих самих місцях, змінюється лише калорійність. Записує частку їжі з багатої купки за 400 тактів, такт її повного збору і місце купки за відстанню до гнізда |
| `make_charts.py` | будує `../exp_chart.png` і `../calories_chart.png` з таблиць результатів і друкує середні значення для звіту |
| `../lab2_experiment_raw.csv` | результати експерименту 1 (таблиця BehaviorSpace) |
| `../lab2_calories_raw.csv` | результати експерименту 2 |

## Запуск
Потрібні NetLogo 6.4.0, Java 17+ (файл `.java` запускається напряму, без окремої компіляції) і Python з `matplotlib`. Команди виконуються з цієї папки.

1. Експеримент 1:
   ```
   java -cp "D:/NetLogo 6.4.0/app/netlogo-6.4.0.jar" org.nlogo.headless.Main --model ../Ants_modified.nlogo --setup-file reproduction_experiment.xml --table ../lab2_experiment_raw.csv --threads 6
   ```
2. Експеримент 2 (30 розстановок, кілька хвилин):
   ```
   java -cp "D:/NetLogo 6.4.0/app/netlogo-6.4.0.jar" CaloriesExperiment.java ../Ants_modified.nlogo ../lab2_calories_raw.csv 30
   ```
3. Графіки:
   ```
   python make_charts.py
   ```

Експеримент 1 повторити через BehaviorSpace можна й у самій NetLogo (Tools → BehaviorSpace). Експеримент 2 потребує окремої програми, бо BehaviorSpace не вміє задавати однаковий random-seed для різних значень параметра.
