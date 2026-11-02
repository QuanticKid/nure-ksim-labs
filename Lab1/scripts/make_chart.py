"""ЛР1, експеримент 2: будує графік залежності часу збору їжі від evaporation-rate.

    python make_chart.py

Читає ../evaporation_raw.csv (таблиця BehaviorSpace, отримана з evaporation_experiment.xml),
зберігає ../exp2_chart.png і друкує таблицю для звіту.
"""
import csv
import os
import statistics as st
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)

# таблиця BehaviorSpace має 6 рядків заголовка перед назвами стовпців
rows = list(csv.reader(open(os.path.join(LAB, 'evaporation_raw.csv'), encoding='utf-8')))
i = next(k for k, r in enumerate(rows) if r and r[0] == '[run number]')
runs = defaultdict(list)
for r in rows[i + 1:]:
    d = dict(zip(rows[i], r))
    runs[int(d['evaporation-rate'])].append(int(d['ticks']))
xs = sorted(runs)
means = [st.mean(runs[x]) for x in xs]

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 14
fig, ax = plt.subplots(figsize=(8.3, 4.6), dpi=150)
for x in xs:
    ax.scatter([x] * len(runs[x]), runs[x], color='#9fb3d8', s=30, zorder=2)
ax.scatter([], [], color='#9fb3d8', s=30, label='окремі прогони')
ax.plot(xs, means, '-o', color='#1f4e9c', lw=2.2, ms=8, label='середнє значення', zorder=3)
for x, m in zip(xs, means):
    ax.annotate(f'{m:.0f}', (x, m), textcoords='offset points', xytext=(8, 6), fontsize=12)
ax.set_xlabel('Швидкість випаровування сліду (evaporation-rate), %')
ax.set_ylabel('Час збору всієї їжі, такти')
ax.set_xticks(xs)
ax.set_ylim(0, 3600)
ax.grid(axis='y', color='#dddddd')
ax.set_axisbelow(True)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, loc='upper left')
fig.tight_layout()
fig.savefig(os.path.join(LAB, 'exp2_chart.png'))

for x in xs:
    print(f"{x:>3} | {', '.join(map(str, runs[x]))} | {st.mean(runs[x]):.0f}")
