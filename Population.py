from Person import Person
import config


class Population:
    def __init__(self, count):
        self.people_dict = dict()
        for i in range(count):
            self.people_dict[config.biggest_id] = Person('start', None, None)

    def print_population(self):
        print(self.people_dict.keys())
        for pers in self.people_dict.values():
            if pers.died == 0:
                pers.print_person()