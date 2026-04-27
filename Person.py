import random
from typing import Optional
import config


class Person:
    def __init__(self, flag_generate, mother, father):
        config.biggest_id += 1
        self.id = config.biggest_id
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
        self.robustness_marriage = -1
        self.desired_partner = None
        self.partner = ""
        self.died = 0
        self.mother = mother
        self.father = father
        self.ancestor_dict = {}
        self.profession = None
        if flag_generate == "start":
            self.generate_start_characteristics()
        else:
            self.generate_child()

    def generate_start_characteristics(self) -> None:
        self.gender = random.choice(['male', 'female'])
        if self.gender == 'male':
            self.name = random.choice(config.names_male)
        else:
            self.name = random.choice(config.names_female)
        self.surname = random.choice(config.surnames)
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

    def generate_child(self) -> None:
        self.gender = random.choice(['male', 'female'])
        if self.gender == 'male':
            self.name = random.choice(config.names_male)
        else:
            self.name = random.choice(config.names_female)
        self.surname = self.father.surname

        if self.mother.skin_color == self.father.skin_color:
            self.skin_color = self.mother.skin_color
        elif self.mother.skin_color == "white" and self.father.skin_color == "black" or self.mother.skin_color == "black" and self.father.skin_color == "white":
            self.skin_color = "mulatto"
        elif self.mother.skin_color == "black" and self.father.skin_color == "yellow" or self.mother.skin_color == "yellow" and self.father.skin_color == "black":
            self.skin_color = "black"
        elif self.mother.skin_color == "white" and self.father.skin_color == "yellow" or self.mother.skin_color == "yellow" and self.father.skin_color == "white":
            self.skin_color = "yellow"
        else:
            self.skin_color = random.choice([self.mother.skin_color, self.father.skin_color])

        if self.skin_color == "white":
            self.hair_color = random.choice([self.mother.hair_color, self.father.hair_color])
        else:
            self.hair_color = "black"
        self.aggressive_layer = random.choice([self.mother.aggressive_layer, self.father.aggressive_layer])
        self.intelligence_layer = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.6, 0.25, 0.1])[0]
        self.power_layer = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.2, 0.1])[0]
        self.alcoholism_layer = random.choice([self.mother.alcoholism_layer, self.father.alcoholism_layer])
        self.age = 0
        self.marriage = 0
        self.partner = ""


    def person_die(self):
        if self.age > 80:
            die = random.choices([0, 1], weights=[0.7, 0.3])[0]
            if die == 1:
                self.died = 1


    def print_person(self):
        print(self.id, self.gender, self.name, self.surname,  self.age, self.skin_color, self.hair_color, self.aggressive_layer, self.intelligence_layer, self.power_layer, self.alcoholism_layer)
