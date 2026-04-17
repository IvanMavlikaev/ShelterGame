import random
from typing import Optional
import matplotlib.pyplot as plt
import numpy as np



names_male = ['John', 'Jack', 'Steve', 'Donald', 'German', 'Alexander', 'Ivan']
names_female = ['Maria', 'Anna', 'Sara', 'Stefania', 'Lucy']
surnames = ['Stathem', 'Simpson', 'Biden', 'Morrison', 'Li', 'Adisson', 'Modovar', 'Lisevsky', 'Newton', 'Askens', 'Mikkens', 'Aladdin', 'Rocky', 'House', 'Larbotry', 'Brown', 'Akunin', 'Noginsky']
biggest_id = 0

class Person:
    def __init__(self, flag_generate, mother: None, father: None):
        global biggest_id
        biggest_id += 1
        self.id = biggest_id
        self.gender: Optional[str] = None
        self.name: Optional[str] = None
        self.surname:Optional[str] = None
        self.skin_color: Optional[str] = None
        self.hair_color: Optional[str] = None
        self.aggressive_layer: int = 0
        self.intelligence_layer: int = 1
        self.power_layer: int = 1
        self.alcoholism_layer: int = 0
        self.age: int = 18
        self.marriage = 0
        self.partner = ""
        self.died = 0
        if flag_generate == "start":
            self.generate_start_characteristics()
        else:
            self.generate_child(mother, father)

    def generate_start_characteristics(self) -> None:
        self.gender = random.choice(['male', 'female'])
        if self.gender == 'male':
            self.name = random.choice(names_male)
        else:
            self.name = random.choice(names_female)
        self.surname = random.choice(surnames)
        self.skin_color = random.choices(["white", "black", "yellow"], weights=[0.8, 0.1, 0.1])[0]
        if self.skin_color == "white":
            self.hair_color = random.choices(["blond", "black", "brown", "red"], weights=[0.5, 0.2, 0.2, 0.1])[0]
        else:
            self.hair_color = "black"
        self.aggressive_layer = random.choices([0, 1], weights=[0.95, 0.05])[0]
        self.intelligence_layer = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.6, 0.25, 0.1])[0]
        self.power_layer = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.2, 0.1])[0]
        self.alcoholism_layer = random.choices([0, 1], weights=[0.9, 0.1])[0]
        self.age = random.randint(18, 40)

    def generate_child(self, mother: 'Person', father: 'Person') -> None:
        self.gender = random.choice(['male', 'female'])
        if self.gender == 'male':
            self.name = random.choice(names_male)
        else:
            self.name = random.choice(names_female)
        self.surname = father.surname

        if mother.skin_color == father.skin_color:
            self.skin_color = mother.skin_color
        elif mother.skin_color == "white" and father.skin_color == "black" or mother.skin_color == "black" and father.skin_color == "white":
            self.skin_color = "mulatto"
        elif mother.skin_color == "black" and father.skin_color == "yellow" or mother.skin_color == "yellow" and father.skin_color == "black":
            self.skin_color = "black"
        elif mother.skin_color == "white" and father.skin_color == "yellow" or mother.skin_color == "yellow" and father.skin_color == "white":
            self.skin_color = "yellow"
        else:
            self.skin_color = random.choice([mother.skin_color, father.skin_color])

        if self.skin_color == "white":
            self.hair_color = random.choice([mother.hair_color, father.hair_color])
        else:
            self.hair_color = "black"
        self.aggressive_layer = random.choice([mother.aggressive_layer, father.aggressive_layer])
        self.intelligence_layer = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.6, 0.25, 0.1])[0]
        self.power_layer = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.2, 0.1])[0]
        self.alcoholism_layer = random.choice([mother.alcoholism_layer, father.alcoholism_layer])
        self.age = 0
        self.marriage = 0
        self.partner = ""

    def person_die(self):
        if self.age > 80:
            die = random.choices([0, 1], weights=[0.7, 0.3])[0]
            if die == 1:
                self.died = 1


    def print_person(self):
        print(self.gender, self.name, self.surname,  self.age, self.skin_color, self.hair_color, self.aggressive_layer, self.intelligence_layer, self.power_layer, self.alcoholism_layer)



class Population:
    def __init__(self, count):
        self.people_list = []
        for i in range(count):
            self.people_list.append(Person('start', None, None))

    def print_population(self):
        for pers in self.people_list:
            if pers.died == 0:
                pers.print_person()

def year_step(year, population):
    print(f"Год {year}")
    print('Есть ли в этом году новобрачные? Yes | No')
    answer = input()
    while answer == 'Yes':
        print('Имена, Фамилии, возраст')
        person_1 = input().split()
        person_2 = input().split()
        pers1 = None
        pers2 = None
        for pers in population.people_list:
            if person_1[0] == pers.name and person_1[1] == pers.surname:
                pers1 = pers
                pers.marriage = 1
            if person_2[0] == pers.name and person_2[1] == pers.surname:
                pers2 = pers
                pers.marriage = 1
        pers1.partner = pers2
        pers2.partner = pers1
        print('Ещё есть? Yes | No')
        answer = input()

    marriage_list = []
    for pers in population.people_list:
        if pers.marriage == 1 and pers not in marriage_list:
            marriage_list.append(pers)
            marriage_list.append(pers.partner)
            if pers.gender == 'female':
                if pers.age < 40:
                    child = random.choices([0.8, 0.2], weights=[0, 1])[0]
                    if child == 1:
                        new_person = Person("new_person", pers, pers.partner)
                        population.people_list.append(new_person)
            else:
                if pers.partner.age < 40:
                    child = random.choices([0.8, 0.2], weights=[0, 1])[0]
                    if child == 1:
                        new_person = Person("new_person", pers.partner, pers)
                        population.people_list.append(new_person)
    marriage_list = []
    population.print_population()
    year += 1
    for pers in population.people_list:
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
    for pers in population.people_list:
        if not pers.died:
            data[pers.age // 5] += 1
    generate_diagram(data)


if __name__ == "__main__":
    population = Population(10)
    generate_data(population)
    population.print_population()
    year = 0
    year_step(year, population)

