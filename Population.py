from Person import Person
import config
import random

class Population:
    def __init__(self, count):
        self.people_dict = dict()
        self.professions = {
            "Leader": -1,
            "Main doctor": -1,
            "Main guard": -1,
            "Chef": -1,
            "First manager": -1,
            "Manager": [],
            "Doctor": [],
            "Guard": [],
            "Head teacher": -1,
            "Teacher": [],
            "Librarian": -1,
        }
        self.important_professions = ["Leader", "Main doctor", "Main guard", "Chef", "First manager"]
        for i in range(count):
            self.people_dict[config.biggest_id] = Person('start', None, None)

    def add_person(self, person):
        self.people_dict[person.id] = person

    def print_population(self):
        for pers in self.people_dict.values():
            if pers.died == 0:
                pers.print_person()

    def assign_profession(self, person_id, profession):
        """Назначение профессии человеку"""
        if person_id not in self.people_dict:
            print(f"Ошибка: Человек с ID {person_id} не найден")
            return False

        person = self.people_dict[person_id]
        if person.died:
            print(f"Ошибка: {person.name} {person.surname} (ID: {person_id}) умер")
            return False

        # Проверяем, подходит ли профессия для одиночной должности
        if profession in ["Leader", "Main doctor", "Main guard", "Chef", "First manager", "Head teacher", "Librarian"]:
            if self.professions[profession] != -1:
                old_person = self.professions[profession]
                print(f"Предупреждение: Должность {profession} уже занята ID {old_person}")
                return False
            self.professions[profession] = person_id
        else:
            # Для коллективных должностей
            if person_id not in self.professions[profession]:
                self.professions[profession].append(person_id)

        person.profession = profession
        print(f"✅ {person.name} {person.surname} (ID: {person_id}) назначен на должность {profession}")
        return True

    def remove_from_profession(self, person_id):
        """Снятие человека с должности при смерти"""
        if person_id not in self.people_dict:
            return

        person = self.people_dict[person_id]
        if person.profession:
            profession = person.profession

            if profession in ["Leader", "Main doctor", "Main guard", "Chef", "First manager", "Head teacher",
                              "Librarian"]:
                if self.professions[profession] == person_id:
                    self.professions[profession] = -1
                    print(f"⚠️ {person.name} {person.surname} (ID: {person_id}) снят с должности {profession} (умер)")
            else:
                if person_id in self.professions[profession]:
                    self.professions[profession].remove(person_id)
                    print(f"⚠️ {person.name} {person.surname} (ID: {person_id}) снят с должности {profession} (умер)")

            person.profession = None


def add_ancestor(person_id, population, generation, mother_id, father_id):
    person = population.people_dict[person_id]
    if mother_id is not None and father_id is not None:
        person.ancestor_dict[mother_id] = generation
        person.ancestor_dict[father_id] = generation
        mother_mother_id = None
        if population.people_dict[mother_id].mother is not None:
            mother_mother_id = population.people_dict[mother_id].mother.id
        mother_father_id = None
        if population.people_dict[mother_id].father is not None:
            mother_father_id = population.people_dict[mother_id].father.id
        father_mother_id = None
        if population.people_dict[father_id].mother is not None:
            father_mother_id = population.people_dict[father_id].mother.id
        father_father_id = None
        if population.people_dict[father_id].mother is not None:
            father_father_id = population.people_dict[father_id].father.id
        add_ancestor(person_id, population, generation + 1, mother_mother_id, mother_father_id)
        add_ancestor(person_id, population, generation + 1, father_mother_id, father_father_id)


def find_ancestor(population, person1, person2):
    if population.people_dict[person1].ancestor_dict == {}:
        mother_id = None
        if population.people_dict[person1].mother is not None:
            mother_id = population.people_dict[person1].mother.id
        father_id = None
        if population.people_dict[person1].father is not None:
            father_id = population.people_dict[person1].father.id
        add_ancestor(person1, population, 1, mother_id, father_id)
    if population.people_dict[person2].ancestor_dict == {}:
        mother_id = None
        if population.people_dict[person2].mother is not None:
            mother_id = population.people_dict[person2].mother.id
        father_id = None
        if population.people_dict[person2].father is not None:
            father_id = population.people_dict[person2].father.id
        add_ancestor(person2, population, 1, mother_id, father_id)
    print(population.people_dict[person1].ancestor_dict)
    print(population.people_dict[person2].ancestor_dict)
    for ancestor_id in population.people_dict[person1].ancestor_dict.keys():
        if ancestor_id in population.people_dict[person2].ancestor_dict.keys():
            if population.people_dict[person1].ancestor_dict[ancestor_id] == population.people_dict[person2].ancestor_dict[ancestor_id]:
                return population.people_dict[person1].ancestor_dict[ancestor_id]
            else:
                return -2
    return -1


def divorsce(person1, person2):
    if person1.robustness_marriage == 2 or person2.robustness_marriage == 2:
        return False
    elif person1.robustness_marriage == 1 or person2.robustness_marriage == 1:
        probability = random.choices([0, 1], weights=[0.95, 0.05])[0]
        return probability
    probability = random.choices([0, 1], weights=[0.9, 0.1])[0]
    return probability



