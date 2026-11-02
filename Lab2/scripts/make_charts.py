"""ЛР2: будує графіки експериментів з таблиць результатів.

    python make_charts.py

Читає ../lab2_experiment_raw.csv (BehaviorSpace) та ../lab2_calories_raw.csv (CaloriesExperiment.java),
зберігає ../exp_chart.png та ../calories_chart.png і друкує середні значення для таблиць звіту.
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
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 13


def style(ax):
    ax.grid(axis='y', color='#dddddd')
    ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)


def behaviorspace_rows(path):
    """Таблиця BehaviorSpace має 6 рядків заголовка перед назвами стовпців."""
    rows = list(csv.reader(open(path, encoding='utf-8')))
    i = next(k for k, r in enumerate(rows) if r and r[0] == '[run number]')
    return [dict(zip(rows[i], r)) for r in rows[i + 1:]]


# --- Експеримент 1: час збору їжі залежно від population, з появою нових мурах і без ---
runs = defaultdict(list)
for r in behaviorspace_rows(os.path.join(LAB, 'lab2_experiment_raw.csv')):
    runs[(int(r['population']), r['reproduction?'])].append(int(r['ticks']))
pops = sorted({p for p, _ in runs})

fig, ax = plt.subplots(figsize=(8.3, 4.6), dpi=150)
for key, color, light, label in (('false', '#1f4e9c', '#9fb3d8', 'без появи нових мурах'),
                                 ('true', '#d9601a', '#f0b48f', 'з появою нових мурах (reproduction? = on)')):
    for p in pops:
        ax.scatter([p] * len(runs[(p, key)]), runs[(p, key)], color=light, s=18, zorder=2)
    means = [st.mean(runs[(p, key)]) for p in pops]
    ax.plot(pops, means, '-o', color=color, lw=2, ms=7, label=label, zorder=3)
    for p, m in zip(pops, means):
        if key == 'true' and p >= 75:
            continue  # ці підписи накладаються на синю лінію
        ax.annotate(f'{m:.0f}', (p, m), textcoords='offset points',
                    xytext=(7, 6) if key == 'false' else (7, -15), fontsize=11)
ax.scatter([], [], color='#9fb3d8', s=18, label='окремі прогони')
ax.set_xlabel('Початкова кількість мурах (population)')
ax.set_ylabel('Час збору всієї їжі, такти')
ax.set_xticks(pops)
ax.set_ylim(0, None)
ax.legend(frameon=False)
style(ax)
fig.tight_layout()
fig.savefig(os.path.join(LAB, 'exp_chart.png'))

print('Експеримент 1 (population: середній час без / з reproduction?)')
for p in pops:
    a, b = st.mean(runs[(p, 'false')]), st.mean(runs[(p, 'true')])
    print(f'  {p:>4}: {a:7.0f} {b:7.0f}  прискорення {a / b:.1f}')

# --- Експеримент 2: частка їжі з багатої купки залежно від її калорійності ---
share = defaultdict(lambda: defaultdict(list))
t_rich = defaultdict(list)
for r in csv.DictReader(open(os.path.join(LAB, 'lab2_calories_raw.csv'), encoding='utf-8')):
    v = int(r['rich_value'])
    group = 'far' if r['rich_pile_rank_by_distance'] == '3' else 'other'
    for g in ('all', group):
        share[g][v].append(100 * float(r['share_from_rich_first_400_ticks']))
    t_rich[v].append(float(r['ticks_rich_pile_exhausted']))
values = sorted(share['all'])

fig, ax = plt.subplots(figsize=(8.3, 4.6), dpi=150)
for key, color, label, ls, off in (
        ('other', '#9fb3d8', f"багата купка не найдальша ({len(share['other'][1])} розстановок)", '-', (6, 7)),
        ('all', '#d9601a', f"усі {len(share['all'][1])} розстановок", '--', (6, 7)),
        ('far', '#1f4e9c', f"багата купка найдальша від гнізда ({len(share['far'][1])})", '-', (6, -15))):
    means = [st.mean(share[key][v]) for v in values]
    ax.plot(values, means, ls, marker='o', color=color, lw=2.2, ms=7, label=label)
    for v, m in zip(values, means):
        ax.annotate(f'{m:.0f}%', (v, m), textcoords='offset points', xytext=off, fontsize=11)
ax.set_xlabel('Калорійність багатої купки (max-value), решта купок = 1')
ax.set_ylabel('Частка їжі з багатої купки за 400 тактів, %')
ax.set_xticks(values)
ax.set_ylim(0, 80)
ax.legend(frameon=False, fontsize=11, loc='upper left')
style(ax)
fig.tight_layout()
fig.savefig(os.path.join(LAB, 'calories_chart.png'))

print('Експеримент 2 (max-value: частка всі / найдальша / не найдальша, такт збору багатої купки)')
for v in values:
    print(f"  {v}: {st.mean(share['all'][v]):5.1f} {st.mean(share['far'][v]):5.1f} "
          f"{st.mean(share['other'][v]):5.1f}  {st.mean(t_rich[v]):5.0f}")
