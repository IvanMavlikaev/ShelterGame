import random
import matplotlib.pyplot as plt
import numpy as np
from Person import Person
from Population import Population
import config


def year_step(year, population):
    print(f"Год {year}")
    print('Есть ли в этом году новобрачные? Yes | No')
    answer = input()
    while answer == 'Yes':
        print('id супругов через пробел')
        person_1_id, person_2_id = map(int, input().split())
        pers_1 = population.people_dict[person_1_id]
        pers_1.marriage = 1
        pers_2 = population.people_dict[person_2_id]
        pers_2.marriage = 1
        pers_1.partner = person_2_id
        pers_2.partner = person_1_id
        print('Ещё есть? Yes | No')
        answer = input()

    # marriage_list = []
    # for pers in population.people_dict.values():
    #     if pers.marriage == 1 and pers not in marriage_list:
    #         marriage_list.append(pers)
    #         marriage_list.append(pers.partner)
    #         if pers.gender == 'female':
    #             if pers.age < 40:
    #                 child = random.choices([0.8, 0.2], weights=[0, 1])[0]
    #                 if child == 1:
    #                     new_person = Person("new_person", pers, pers.partner)
    #                     population.people_list.append(new_person)
    #         else:
    #             if pers.partner.age < 40:
    #                 child = random.choices([0.8, 0.2], weights=[0, 1])[0]
    #                 if child == 1:
    #                     new_person = Person("new_person", pers.partner, pers)
    #                     population.people_list.append(new_person)
    # marriage_list = []
    population.print_population()
    year += 1
    for pers in population.people_dict.values():
        pers.person_die()
        if pers.died == 0:
           pers.age += 1

    year_step(year, population)



def generate_diagram(data):
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    bars = plt.bar(range(len(data)), data, color='skyblue', edgecolor='black')
    plt.title('Столбчатая диаграмма (20 элементов)')
    plt.xlabel('Индекс элемента (×5)')
    plt.ylabel('Значение')
    plt.grid(axis='y', alpha=0.75)

    # Устанавливаем подписи на оси X в 5 раз больше
    indices = range(len(data))
    plt.xticks(indices, [f'{i * 5 + 5}' for i in indices])

    # Добавляем значения на столбцы
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                 f'{int(height)}', ha='center', va='bottom', fontsize=9)

    # Горизонтальная диаграмма
    plt.subplot(1, 2, 2)
    plt.barh(range(len(data)), data, color='lightgreen', edgecolor='black')
    plt.title('Горизонтальная столбчатая диаграмма')
    plt.ylabel('Индекс элемента (×5)')
    plt.xlabel('Значение')
    plt.grid(axis='x', alpha=0.75)

    # Устанавливаем подписи на оси Y в 5 раз больше
    plt.yticks(indices, [f'{i * 5 + 5}' for i in indices])

    plt.tight_layout()
    plt.show()

def generate_data(population):
    data = [0] * 20
    for pers in population.people_dict.values():
        if not pers.died:
            data[pers.age // 5] += 1
    #generate_diagram(data)


if __name__ == "__main__":
    population = Population(10)
    generate_data(population)
    population.print_population()
    year = 0
    year_step(year, population)

