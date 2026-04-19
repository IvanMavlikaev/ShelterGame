import matplotlib.pyplot as plt
from Population import Population, find_ancestor
from Person import Person
import config
import random

current_fig = None

def marriage(population):
    print(f"Год {config.year}")
    print('Есть ли в этом году новобрачные? Yes | No')
    answer = input()
    while answer == 'Yes':
        print('id супругов через пробел')
        person_1_id, person_2_id = map(int, input().split())
        relative = find_ancestor(population, person_1_id, person_2_id)
        if relative != -1:
            print("Вы не можете поженить родственников")
            print('Ещё есть? Yes | No')
            answer = input()
            continue
        pers_1 = population.people_dict[person_1_id]
        pers_1.marriage = 1
        pers_2 = population.people_dict[person_2_id]
        pers_2.marriage = 1
        pers_1.partner = person_2_id
        pers_2.partner = person_1_id
        config.marriage_list.append((person_1_id, person_2_id))
        print('Ещё есть? Yes | No')
        answer = input()


def check_age_parents(pers1, pers2):
    if pers1.gender == 'female' and pers1.age > 40:
        return 0
    elif pers2.gender == 'female' and pers2.age > 40:
        return 0
    if pers1.gender == 'male' and pers1.age > 50:
        return 0
    elif pers2.gender == 'male' and pers2.age > 50:
        return 0
    elif pers1.gender == 'female' and pers1.age > 30:
        return 0.2
    elif pers2.gender == 'female' and pers2.age > 30:
        return 0.2
    elif pers1.gender == 'female' and pers1.age < 30:
        return 0.3
    elif pers2.gender == 'female' and pers2.age < 30:
        return 0.3
    return 0


def birth(population):
    for i, j in config.marriage_list:
        pers1 = population.people_dict[i]
        pers2 = population.people_dict[j]
        prob = check_age_parents(pers1, pers2)
        print(prob)
        fertiliry = random.choices([True, False], weights=[prob, 1 - prob])[0]
        if fertiliry:
            if pers1.gender == 'male':
                child = Person("birth", pers2, pers1)
                population.add_person(child)
            else:
                child = Person("birth", pers1, pers2)
                population.add_person(child)



def update_diagram(data):
    """Обновление диаграммы"""
    global current_fig

    if current_fig is None:
        plt.ion()  # Включаем интерактивный режим
        current_fig = plt.figure(figsize=(6, 6))

    plt.clf()

    indices = range(len(data))

    plt.barh(range(len(data)), data, color='lightgreen', edgecolor='black')
    plt.title('Возрастная пирамида поселенцев')
    plt.ylabel('Возраст')
    plt.xlabel('Значение')
    plt.grid(axis='x', alpha=0.75)

    plt.yticks(indices, [f'{i * 5}-{4 + 5 * i}' for i in indices])

    plt.tight_layout()
    current_fig.canvas.draw()
    current_fig.canvas.flush_events()
    plt.pause(0.01)


def generate_data(population):
    """Сбор данных и обновление диаграммы"""
    data = [0] * 20
    for pers in population.people_dict.values():
        if not pers.died:
            data[pers.age//5] += 1
    update_diagram(data)


def year_step(population):
    """Основной цикл программы"""
    try:
        while True:

            marriage(population)
            birth(population)
            population.print_population()
            config.year += 1

            for pers in list(population.people_dict.values()):
                pers.person_die()
                if pers.died == 0:
                    pers.age += 1

            generate_data(population)

            print(f"\nГод {config.year} завершён\n")

    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
        if current_fig:
            plt.close(current_fig)


if __name__ == "__main__":
    population = Population(10)
    year_step(population)
