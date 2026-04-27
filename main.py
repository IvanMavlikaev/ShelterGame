import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Population import Population, find_ancestor
from Person import Person
import config
import random
from matplotlib.gridspec import GridSpec
import sys


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


class PopulationSimulator:
    def __init__(self):
        self.population = None
        self.fig = None
        self.current_unit_id = None
        self.marriage_mode = False
        self.selected_spouse1 = None
        self.selected_spouse2 = None
        self.marriage_fig = None
        self.marriage_candidates = []
        self.current_candidate_index = 0
        self.current_candidate_id = None
        self.step = 1
        self.profession_selection_fig = None
        self.vacant_professions = []
        self.current_profession_index = 0
        self.profession_candidates = []

    def show_unit_profile(self, unit_id, ax=None):
        """Отображение анкеты юнита на указанной оси"""
        if ax is None:
            ax = self.profile_ax

        ax.clear()
        person = self.population.people_dict[unit_id]

        # Добавляем информацию о желании брака
        desire_text = ""
        if person.robustness_marriage == 1:
            desire_text = "\n  ЖЕЛАНИЕ: Хочет вступить в брак"
        elif person.robustness_marriage == 2:
            desire_text = f"\n  ЖЕЛАНИЕ: Взаимное желание с ID {person.desired_partner}"

        # Добавляем информацию о профессии
        profession_text = f"\n  Профессия: {person.profession if person.profession else 'Нет'}"

        profile_text = f"""
       ==========================================
            АНКЕТА ЮНИТА ID: {person.id}
       ==========================================

       Основная информация:
         Имя: {person.name} {person.surname}
         Пол: {person.gender}
         Возраст: {person.age} лет
         Статус: {"ЖИВ" if not person.died else "УМЕР"}

       Характеристики:
         Цвет кожи: {person.skin_color}
         Цвет волос: {person.hair_color}
         Агрессивность: {person.aggressive_layer}/1
         Интеллект: {person.intelligence_layer}/5
         Сила: {person.power_layer}/5
         Алкоголизм: {person.alcoholism_layer}/1

       Семейное положение:
         В браке: {"Да" if person.marriage else "Нет"}
         Партнер: {person.partner if person.partner else "Нет"}{desire_text}

       Работа:{profession_text}

       Родители:
         Мать: {person.mother.id if person.mother else "Неизвестно"}
         Отец: {person.father.id if person.father else "Неизвестно"}

       ==========================================
           """

        ax.text(0.05, 0.95, profile_text, transform=ax.transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace')
        ax.set_title(f'ПРОФИЛЬ ЮНИТА #{person.id}', fontsize=12, fontweight='bold')
        ax.axis('off')

        if self.fig:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def update_diagram(self):
        """Обновление возрастной пирамиды"""
        if not hasattr(self, 'diagram_ax'):
            return

        self.diagram_ax.clear()

        # Собираем данные
        data = [0] * 20
        for pers in self.population.people_dict.values():
            if not pers.died:
                age_group = pers.age // 5
                if age_group < 20:
                    data[age_group] += 1

        # Создаем гистограмму
        y_pos = range(len(data))
        bars = self.diagram_ax.barh(y_pos, data)

        # Окрашиваем возрастные группы
        for i, bar in enumerate(bars):
            if i < 4:  # 0-19 лет
                bar.set_color('#90EE90')
            elif i < 12:  # 20-59 лет
                bar.set_color('#32CD32')
            else:  # 60+ лет
                bar.set_color('#228B22')

        self.diagram_ax.set_title(f'Возрастная пирамида (Год {config.year})', fontsize=12, fontweight='bold')
        self.diagram_ax.set_xlabel('Количество человек')
        self.diagram_ax.set_ylabel('Возрастная группа')
        self.diagram_ax.set_yticks(y_pos)
        self.diagram_ax.set_yticklabels([f'{i * 5}-{i * 5 + 4}' for i in y_pos])
        self.diagram_ax.grid(axis='x', alpha=0.3, linestyle='--')

        # Статистика по профессиям
        professions_stats = "\nВажные должности:"
        for prof in self.population.important_professions:
            if self.population.professions[prof] != -1:
                person = self.population.people_dict[self.population.professions[prof]]
                professions_stats += f"\n  {prof}: {person.name} {person.surname}"
            else:
                professions_stats += f"\n  {prof}: ВАКАНСИЯ!"

        alive_count = sum(1 for p in self.population.people_dict.values() if not p.died)
        stats = f'Всего жителей: {alive_count}{professions_stats}'
        self.diagram_ax.text(0.5, -0.25, stats, transform=self.diagram_ax.transAxes,
                             ha='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def check_important_professions(self):
        """Проверка наличия людей на важных должностях"""
        vacant = []
        for profession in self.population.important_professions:
            if self.population.professions[profession] == -1:
                vacant.append(profession)
            else:
                # Проверяем, жив ли человек на должности
                person_id = self.population.professions[profession]
                if person_id in self.population.people_dict:
                    if self.population.people_dict[person_id].died:
                        self.population.remove_from_profession(person_id)
                        vacant.append(profession)
        return vacant

    def show_profession_selection_dialog(self, vacant_professions):
        """Показ диалога для выбора людей на вакантные должности"""
        if not vacant_professions:
            return

        print("\n" + "=" * 60)
        print("⚠️ ВНИМАНИЕ: ОБНАРУЖЕНЫ ВАКАНСИИ НА ВАЖНЫХ ДОЛЖНОСТЯХ!")
        print("=" * 60)
        for prof in vacant_professions:
            print(f"  • {prof}")
        print("=" * 60)

        self.vacant_professions = vacant_professions
        self.current_profession_index = 0
        self.show_profession_selection_for_current()

    def show_profession_selection_for_current(self):
        """Показ окна выбора для текущей вакантной должности"""
        if self.current_profession_index >= len(self.vacant_professions):
            # Все должности заполнены
            if self.profession_selection_fig:
                plt.close(self.profession_selection_fig)
                self.profession_selection_fig = None
            self.update_diagram()
            return

        current_profession = self.vacant_professions[self.current_profession_index]

        # Получаем кандидатов (живые, совершеннолетние)
        self.profession_candidates = [uid for uid, p in self.population.people_dict.items()
                                      if not p.died and p.age >= 18]

        if not self.profession_candidates:
            print(f"Нет доступных кандидатов для должности {current_profession}")
            self.current_profession_index += 1
            self.show_profession_selection_for_current()
            return

        self.current_candidate_index = 0
        self.current_candidate_id = self.profession_candidates[0]

        # Создаем окно выбора
        if self.profession_selection_fig:
            plt.close(self.profession_selection_fig)

        self.profession_selection_fig = plt.figure(f'Назначение на должность: {current_profession}', figsize=(14, 8))

        gs = GridSpec(4, 2, figure=self.profession_selection_fig, height_ratios=[4, 1, 1, 1])

        # Область для анкеты
        self.profession_profile_ax = self.profession_selection_fig.add_subplot(gs[0, 1])

        # Область для информационного текста
        info_ax = self.profession_selection_fig.add_subplot(gs[0, 0])
        info_ax.axis('off')

        # Показываем информацию о должности и текущем кандидате
        info_text = f'ВЫБОР КАНДИДАТА\n\nДолжность: {current_profession}\n\nВсего кандидатов: {len(self.profession_candidates)}\nТекущий: {self.current_candidate_index + 1} из {len(self.profession_candidates)}\n\nВыберите подходящего человека'
        info_ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, fontweight='bold')

        # Кнопки навигации
        btn_prev_ax = self.profession_selection_fig.add_subplot(gs[2, 0])
        btn_next_ax = self.profession_selection_fig.add_subplot(gs[2, 1])
        btn_ok_ax = self.profession_selection_fig.add_subplot(gs[3, 0])
        btn_skip_ax = self.profession_selection_fig.add_subplot(gs[3, 1])

        self.btn_prev_prof = Button(btn_prev_ax, '◀ ПРЕДЫДУЩИЙ', color='lightyellow', hovercolor='orange')
        self.btn_next_prof = Button(btn_next_ax, 'СЛЕДУЮЩИЙ ▶', color='lightyellow', hovercolor='orange')
        self.btn_ok_prof = Button(btn_ok_ax, '✅ НАЗНАЧИТЬ', color='lightgreen', hovercolor='green')
        self.btn_skip_prof = Button(btn_skip_ax, '⏭ ПРОПУСТИТЬ', color='salmon', hovercolor='red')

        # Привязываем обработчики
        self.btn_prev_prof.on_clicked(self.prev_profession_candidate)
        self.btn_next_prof.on_clicked(self.next_profession_candidate)
        self.btn_ok_prof.on_clicked(self.select_profession_candidate)
        self.btn_skip_prof.on_clicked(self.skip_profession)

        # Показываем первого кандидата
        self.show_unit_profile(self.current_candidate_id, self.profession_profile_ax)

        plt.tight_layout()
        plt.show()

    def prev_profession_candidate(self, event):
        """Предыдущий кандидат на должность"""
        if not hasattr(self, 'profession_candidates') or not self.profession_candidates:
            print("Нет кандидатов для переключения")
            return

        self.current_candidate_index = (self.current_candidate_index - 1) % len(self.profession_candidates)
        self.current_candidate_id = self.profession_candidates[self.current_candidate_index]

        # Обновляем анкету
        self.show_unit_profile(self.current_candidate_id, self.profession_profile_ax)

        # Обновляем информационное поле
        if self.profession_selection_fig and len(self.profession_selection_fig.axes) > 2:
            info_ax = self.profession_selection_fig.axes[2]
            info_ax.clear()
            info_ax.axis('off')
            current_profession = self.vacant_professions[self.current_profession_index]
            info_text = f'ВЫБОР КАНДИДАТА\n\nДолжность: {current_profession}\n\nВсего кандидатов: {len(self.profession_candidates)}\nТекущий: {self.current_candidate_index + 1} из {len(self.profession_candidates)}\n\nВыберите подходящего человека'
            info_ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, fontweight='bold')

        self.profession_selection_fig.canvas.draw()
        print(
            f"Переключено на кандидата ID: {self.current_candidate_id} ({self.current_candidate_index + 1}/{len(self.profession_candidates)})")

    def next_profession_candidate(self, event):
        """Следующий кандидат на должность"""
        if not hasattr(self, 'profession_candidates') or not self.profession_candidates:
            print("Нет кандидатов для переключения")
            return

        self.current_candidate_index = (self.current_candidate_index + 1) % len(self.profession_candidates)
        self.current_candidate_id = self.profession_candidates[self.current_candidate_index]

        # Обновляем анкету
        self.show_unit_profile(self.current_candidate_id, self.profession_profile_ax)

        # Обновляем информационное поле
        if self.profession_selection_fig and len(self.profession_selection_fig.axes) > 2:
            info_ax = self.profession_selection_fig.axes[2]
            info_ax.clear()
            info_ax.axis('off')
            current_profession = self.vacant_professions[self.current_profession_index]
            info_text = f'ВЫБОР КАНДИДАТА\n\nДолжность: {current_profession}\n\nВсего кандидатов: {len(self.profession_candidates)}\nТекущий: {self.current_candidate_index + 1} из {len(self.profession_candidates)}\n\nВыберите подходящего человека'
            info_ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, fontweight='bold')

        self.profession_selection_fig.canvas.draw()
        print(
            f"Переключено на кандидата ID: {self.current_candidate_id} ({self.current_candidate_index + 1}/{len(self.profession_candidates)})")

    def select_profession_candidate(self, event):
        """Назначение кандидата на должность"""
        current_profession = self.vacant_professions[self.current_profession_index]

        # Назначаем на должность
        if self.population.assign_profession(self.current_candidate_id, current_profession):
            print(
                f"✅ {self.population.people_dict[self.current_candidate_id].name} {self.population.people_dict[self.current_candidate_id].surname} (ID: {self.current_candidate_id}) назначен на должность {current_profession}")

            # Переходим к следующей вакансии
            self.current_profession_index += 1

            # Закрываем текущее окно
            if self.profession_selection_fig:
                plt.close(self.profession_selection_fig)
                self.profession_selection_fig = None

            # Показываем следующую вакансию
            self.show_profession_selection_for_current()

    def skip_profession(self, event):
        """Пропуск текущей вакансии"""
        print(f"⚠️ Должность {self.vacant_professions[self.current_profession_index]} осталась вакантной")
        self.current_profession_index += 1

        # Закрываем текущее окно
        if self.profession_selection_fig:
            plt.close(self.profession_selection_fig)
            self.profession_selection_fig = None

        # Показываем следующую вакансию
        self.show_profession_selection_for_current()

    def population_desires(self, event):
        """Расчет желаний населения вступить в брак"""
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЖЕЛАНИЙ НАСЕЛЕНИЯ")
        print("=" * 60)

        # Сбрасываем желания у всех
        for pers in self.population.people_dict.values():
            if not pers.died and pers.marriage == 0:
                pers.robustness_marriage = 0
                pers.desired_partner = None

        # Собираем желающих
        candidates = []
        for uid, pers in self.population.people_dict.items():
            if not pers.died and pers.marriage == 0:
                # Определяем вероятность в зависимости от возраста
                if pers.age < 30:
                    probability = 0.2
                elif pers.age <= 40:
                    probability = 0.1
                else:
                    probability = 0

                # Проверяем желание
                if random.random() < probability:
                    pers.robustness_marriage = 1
                    candidates.append(uid)
                    print(f"  ID {pers.id}: {pers.name} {pers.surname} ({pers.age} лет, {pers.gender}) - ХОЧЕТ В БРАК")

        print(f"\nВсего желающих: {len(candidates)}")

        # Ищем взаимные желания
        mutual_desires = []
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                uid1 = candidates[i]
                uid2 = candidates[j]
                pers1 = self.population.people_dict[uid1]
                pers2 = self.population.people_dict[uid2]

                # Проверяем возможность брака
                if (pers1.gender != pers2.gender and
                        find_ancestor(self.population, uid1, uid2) == -1):
                    # Взаимное желание (оба хотят в брак)
                    pers1.robustness_marriage = 2
                    pers2.robustness_marriage = 2
                    pers1.desired_partner = uid2
                    pers2.desired_partner = uid1
                    mutual_desires.append((uid1, uid2))

                    print(f"\n  ВЗАИМНОЕ ЖЕЛАНИЕ!")
                    print(
                        f"    {pers1.name} {pers1.surname} (ID: {uid1}) <-> {pers2.name} {pers2.surname} (ID: {uid2})")

        # Заключаем взаимные браки
        if mutual_desires:
            print(f"\n{'=' * 50}")
            print("ЗАКЛЮЧЕНЫ ВЗАИМНЫЕ БРАКИ:")
            for uid1, uid2 in mutual_desires:
                self.register_marriage(uid1, uid2, is_automatic=True)

        # Показываем итоговую статистику
        print(f"\n{'=' * 50}")
        print("ИТОГИ АНАЛИЗА:")
        print(f"  • Всего желающих: {len(candidates)}")
        print(f"  • Взаимных желаний: {len(mutual_desires)}")
        print(f"  • Заключено браков: {len(mutual_desires)}")
        print("=" * 60 + "\n")

        # Обновляем отображение
        self.update_diagram()

        # Показываем окно с детальной информацией
        self.show_desires_dialog(candidates, mutual_desires)

    def show_desires_dialog(self, candidates, mutual_desires):
        """Показ диалогового окна с желаниями населения"""
        if not candidates and not mutual_desires:
            # Если нет желающих, просто выводим сообщение
            fig = plt.figure('Желания населения', figsize=(8, 4))
            ax = fig.add_subplot(111)
            ax.axis('off')
            ax.text(0.5, 0.5, 'В этом году никто не изъявил желание вступить в брак',
                    ha='center', va='center', fontsize=14, fontweight='bold')
            plt.show(block=False)
            plt.pause(3)
            plt.close(fig)
            return

        # Создаем окно с информацией
        desires_fig = plt.figure('Желания населения', figsize=(12, 8))

        # Создаем текст
        info_text = "ЖЕЛАНИЯ НАСЕЛЕНИЯ В ЭТОМ ГОДУ\n\n"
        info_text += "=" * 50 + "\n\n"

        info_text += "ЖЕЛАЮЩИЕ ВСТУПИТЬ В БРАК:\n"
        for uid in candidates:
            pers = self.population.people_dict[uid]
            if pers.robustness_marriage == 1:
                info_text += f"  • ID {pers.id}: {pers.name} {pers.surname} ({pers.age} лет, {pers.gender})\n"
            elif pers.robustness_marriage == 2:
                info_text += f"  • ID {pers.id}: {pers.name} {pers.surname} ({pers.age} лет, {pers.gender}) - ВЗАИМНО С ID {pers.desired_partner}\n"

        if mutual_desires:
            info_text += "\n" + "=" * 50 + "\n"
            info_text += "ЗАКЛЮЧЕННЫЕ БРАКИ (по взаимному желанию):\n"
            for uid1, uid2 in mutual_desires:
                pers1 = self.population.people_dict[uid1]
                pers2 = self.population.people_dict[uid2]
                info_text += f"  • {pers1.name} {pers1.surname} (ID: {uid1}) + {pers2.name} {pers2.surname} (ID: {uid2})\n"

        ax = desires_fig.add_subplot(111)
        ax.axis('off')
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace')

        plt.tight_layout()
        plt.show(block=False)
        # Автоматически закроем через 5 секунд
        plt.pause(5)
        plt.close(desires_fig)

    def update_marriage_dialog(self):
        """Обновление диалогового окна брака"""
        if not self.marriage_fig:
            return

        # Обновляем информационное поле
        info_ax = self.marriage_fig.axes[2]
        info_ax.clear()
        info_ax.axis('off')

        if self.step == 1:
            info_text = 'ВЫБОР ПЕРВОГО СУПРУГА\n\nВыберите человека для брака\nИспользуйте кнопки навигации'
        else:
            info_text = f'ВЫБОР ВТОРОГО СУПРУГА\n\nВыбран: ID {self.selected_spouse1}\n\nТеперь выберите партнера'

        info_ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, fontweight='bold')

        # Показываем текущего кандидата
        if self.current_candidate_id:
            self.show_unit_profile(self.current_candidate_id, self.marriage_profile_ax)

        self.marriage_fig.canvas.draw()

    def create_marriage_dialog(self, event):
        """Создание диалога для выбора супругов"""
        print("\n" + "=" * 50)
        print("РЕГИСТРАЦИЯ БРАКА (РУЧНОЙ РЕЖИМ)")
        print("=" * 50)

        # Создаем новое окно
        self.marriage_fig = plt.figure('Выбор супруга/супруги', figsize=(14, 8))

        gs = GridSpec(4, 2, figure=self.marriage_fig, height_ratios=[4, 1, 1, 1])

        # Область для анкеты
        self.marriage_profile_ax = self.marriage_fig.add_subplot(gs[0, 1])

        # Область для информационного текста
        info_ax = self.marriage_fig.add_subplot(gs[0, 0])
        info_ax.axis('off')

        # Кнопки навигации
        btn_prev_ax = self.marriage_fig.add_subplot(gs[2, 0])
        btn_next_ax = self.marriage_fig.add_subplot(gs[2, 1])
        btn_ok_ax = self.marriage_fig.add_subplot(gs[3, 0])
        btn_cancel_ax = self.marriage_fig.add_subplot(gs[3, 1])

        self.btn_prev_marriage = Button(btn_prev_ax, 'ПРЕДЫДУЩИЙ', color='lightyellow', hovercolor='orange')
        self.btn_next_marriage = Button(btn_next_ax, 'СЛЕДУЮЩИЙ', color='lightyellow', hovercolor='orange')
        self.btn_ok_marriage = Button(btn_ok_ax, 'ВЫБРАТЬ', color='lightgreen', hovercolor='green')
        self.btn_cancel_marriage = Button(btn_cancel_ax, 'ОТМЕНА', color='salmon', hovercolor='red')

        # Привязываем обработчики
        self.btn_prev_marriage.on_clicked(self.prev_candidate)
        self.btn_next_marriage.on_clicked(self.next_candidate)
        self.btn_ok_marriage.on_clicked(self.select_candidate)
        self.btn_cancel_marriage.on_clicked(self.cancel_marriage)

        # Начинаем с первого шага
        self.step = 1
        self.selected_spouse1 = None
        self.selected_spouse2 = None

        # Получаем кандидатов для первого выбора
        self.update_candidates_list()

        if not self.marriage_candidates:
            print("Нет доступных кандидатов для брака")
            plt.close(self.marriage_fig)
            self.marriage_fig = None
            return

        self.current_candidate_index = 0
        self.current_candidate_id = self.marriage_candidates[0]

        # Обновляем отображение
        self.update_marriage_dialog()

        plt.tight_layout()
        plt.show()

    def update_candidates_list(self):
        """Обновление списка кандидатов в зависимости от шага"""
        if self.step == 1:
            # Первый шаг: все живые и не состоящие в браке
            self.marriage_candidates = [uid for uid, p in self.population.people_dict.items()
                                        if not p.died and p.marriage == 0]
        else:
            # Второй шаг: живые, не в браке, противоположного пола, не родственники
            spouse1 = self.population.people_dict[self.selected_spouse1]
            self.marriage_candidates = [uid for uid, p in self.population.people_dict.items()
                                        if not p.died and p.marriage == 0
                                        and p.gender != spouse1.gender
                                        and uid != self.selected_spouse1
                                        and find_ancestor(self.population, self.selected_spouse1, uid) == -1]

    def prev_candidate(self, event):
        """Предыдущий кандидат"""
        if not self.marriage_candidates:
            return

        self.current_candidate_index = (self.current_candidate_index - 1) % len(self.marriage_candidates)
        self.current_candidate_id = self.marriage_candidates[self.current_candidate_index]
        self.show_unit_profile(self.current_candidate_id, self.marriage_profile_ax)
        self.marriage_fig.canvas.draw()

    def next_candidate(self, event):
        """Следующий кандидат"""
        if not self.marriage_candidates:
            return

        self.current_candidate_index = (self.current_candidate_index + 1) % len(self.marriage_candidates)
        self.current_candidate_id = self.marriage_candidates[self.current_candidate_index]
        self.show_unit_profile(self.current_candidate_id, self.marriage_profile_ax)
        self.marriage_fig.canvas.draw()

    def select_candidate(self, event):
        """Выбор кандидата"""
        if self.step == 1:
            # Выбираем первого супруга
            self.selected_spouse1 = self.current_candidate_id
            print(f"Выбран первый супруг: ID {self.selected_spouse1}")

            # Переходим ко второму шагу
            self.step = 2

            # Обновляем список кандидатов для второго выбора
            self.update_candidates_list()

            if not self.marriage_candidates:
                print("Нет подходящих кандидатов для второго супруга!")
                self.cancel_marriage(None)
                return

            # Сбрасываем индекс для нового списка
            self.current_candidate_index = 0
            self.current_candidate_id = self.marriage_candidates[0]

            # Обновляем отображение
            self.update_marriage_dialog()

        elif self.step == 2:
            # Выбираем второго супруга
            self.selected_spouse2 = self.current_candidate_id
            print(f"Выбран второй супруг: ID {self.selected_spouse2}")

            # Регистрируем брак
            self.register_marriage(self.selected_spouse1, self.selected_spouse2, is_automatic=False)

            # Закрываем окно выбора
            plt.close(self.marriage_fig)
            self.marriage_fig = None

            # Возвращаемся к главному окну
            self.update_diagram()
            if self.current_unit_id in [self.selected_spouse1, self.selected_spouse2]:
                self.show_unit_profile(self.current_unit_id)

            # Сбрасываем состояние
            self.step = 1
            self.selected_spouse1 = None
            self.selected_spouse2 = None

    def cancel_marriage(self, event):
        """Отмена регистрации брака"""
        print("Регистрация брака отменена")
        if self.marriage_fig:
            plt.close(self.marriage_fig)
            self.marriage_fig = None
        self.step = 1
        self.selected_spouse1 = None
        self.selected_spouse2 = None

    def register_marriage(self, person_1_id, person_2_id, is_automatic=False):
        """Регистрация брака"""
        pers1 = self.population.people_dict[person_1_id]
        pers2 = self.population.people_dict[person_2_id]

        # Регистрируем брак
        pers1.marriage = 1
        pers2.marriage = 1
        pers1.partner = person_2_id
        pers2.partner = person_1_id
        config.marriage_list.append((person_1_id, person_2_id))

        # Устанавливаем robustness_marriage
        if is_automatic:
            # Взаимное желание - уровень 2
            pers1.robustness_marriage = 2
            pers2.robustness_marriage = 2
            print(f"✅ Автоматический брак между {person_1_id} и {person_2_id} (взаимное желание, уровень 2)")
        else:
            # Ручной брак - уровень 1
            pers1.robustness_marriage = 1
            pers2.robustness_marriage = 1
            print(f"✅ Ручной брак между {person_1_id} и {person_2_id} (уровень 1)")

    def next_unit(self, event):
        """Переключение на следующего юнита"""
        alive_units = [uid for uid, p in self.population.people_dict.items() if not p.died]
        if alive_units:
            if self.current_unit_id not in alive_units:
                self.current_unit_id = alive_units[0]
            else:
                current_index = alive_units.index(self.current_unit_id)
                current_index = (current_index + 1) % len(alive_units)
                self.current_unit_id = alive_units[current_index]
            self.show_unit_profile(self.current_unit_id)

    def prev_unit(self, event):
        """Переключение на предыдущего юнита"""
        alive_units = [uid for uid, p in self.population.people_dict.items() if not p.died]
        if alive_units:
            if self.current_unit_id not in alive_units:
                self.current_unit_id = alive_units[0]
            else:
                current_index = alive_units.index(self.current_unit_id)
                current_index = (current_index - 1) % len(alive_units)
                self.current_unit_id = alive_units[current_index]
            self.show_unit_profile(self.current_unit_id)

    def next_year(self, event):
        """Переход к следующему году"""
        print(f"\n{'=' * 50}")
        print(f"ГОД {config.year + 1}")
        print(f"{'=' * 50}")

        # Рождение детей от браков
        new_births = []
        for i, j in config.marriage_list:
            pers1 = self.population.people_dict[i]
            pers2 = self.population.people_dict[j]

            if not pers1.died and not pers2.died:
                prob = check_age_parents(pers1, pers2)
                # Учитываем robustness_marriage при рождении
                if pers1.robustness_marriage == 2:
                    prob = min(prob * 1.5, 0.8)  # Взаимное желание - выше шанс
                elif pers1.robustness_marriage == 1:
                    prob = min(prob * 1.2, 0.7)  # Ручной брак

                fertile = random.choices([True, False], weights=[prob, 1 - prob])[0]
                if fertile:
                    if pers1.gender == 'male':
                        child = Person("birth", pers2, pers1)
                    else:
                        child = Person("birth", pers1, pers2)
                    new_births.append(child)
                    print(f"Родился: {child.name} {child.surname} (ID: {child.id})")

        for child in new_births:
            self.population.add_person(child)

        # Старение и смерть
        deaths = []
        for pers in list(self.population.people_dict.values()):
            if not pers.died:
                old_age = pers.age
                pers.person_die()
                if pers.died:
                    # Снимаем с должности при смерти
                    self.population.remove_from_profession(pers.id)
                    deaths.append(pers)
                else:
                    pers.age += 1

        if deaths:
            print(f"\nУмерли:")
            for pers in deaths:
                print(f"   {pers.name} {pers.surname} (ID: {pers.id}) в возрасте {pers.age} лет")

        config.year += 1

        alive_count = sum(1 for p in self.population.people_dict.values() if not p.died)
        print(f"\nИТОГИ {config.year} ГОДА:")
        print(f"   Всего жителей: {alive_count}")
        print(f"   Родилось: {len(new_births)}")
        print(f"   Умерло: {len(deaths)}")
        print(f"{'=' * 50}\n")

        # Обновление отображения
        self.update_diagram()

        # Обновляем анкету если текущий юнит умер
        if self.current_unit_id and self.population.people_dict[self.current_unit_id].died:
            alive_units = [uid for uid, p in self.population.people_dict.items() if not p.died]
            if alive_units:
                self.current_unit_id = alive_units[0]
                self.show_unit_profile(self.current_unit_id)

        # Проверяем важные профессии
        vacant = self.check_important_professions()
        if vacant:
            self.show_profession_selection_dialog(vacant)

    def quit_program(self, event):
        """Выход из программы"""
        print("\nПрограмма завершена")
        plt.close('all')
        sys.exit(0)

    def setup_gui(self):
        """Настройка графического интерфейса"""
        print("Настройка GUI...")
        self.fig = plt.figure('Population Simulator', figsize=(14, 8))

        gs = GridSpec(6, 2, figure=self.fig, height_ratios=[4, 1, 1, 1, 1, 1])

        # Область для диаграммы
        self.diagram_ax = self.fig.add_subplot(gs[0, 0])
        # Область для анкеты
        self.profile_ax = self.fig.add_subplot(gs[0, 1])

        # Кнопки управления
        btn_next_year_ax = self.fig.add_subplot(gs[1, :])
        btn_desires_ax = self.fig.add_subplot(gs[2, :])
        btn_marriage_ax = self.fig.add_subplot(gs[3, :])
        btn_prev_ax = self.fig.add_subplot(gs[4, 0])
        btn_next_ax = self.fig.add_subplot(gs[4, 1])
        btn_quit_ax = self.fig.add_subplot(gs[5, :])

        # Создаем кнопки
        self.btn_next_year = Button(btn_next_year_ax, 'СЛЕДУЮЩИЙ ГОД',
                                    color='lightgreen', hovercolor='green')
        self.btn_desires = Button(btn_desires_ax, 'ЖЕЛАНИЯ НАСЕЛЕНИЯ',
                                  color='lightblue', hovercolor='blue')
        self.btn_marriage = Button(btn_marriage_ax, 'СОЗДАТЬ БРАК (РУЧНОЙ)',
                                   color='lightyellow', hovercolor='orange')
        self.btn_prev = Button(btn_prev_ax, 'ПРЕДЫДУЩИЙ ЮНИТ',
                               color='lightyellow', hovercolor='orange')
        self.btn_next = Button(btn_next_ax, 'СЛЕДУЮЩИЙ ЮНИТ',
                               color='lightyellow', hovercolor='orange')
        self.btn_quit = Button(btn_quit_ax, 'ВЫХОД',
                               color='salmon', hovercolor='red')

        # Привязываем обработчики
        self.btn_next_year.on_clicked(self.next_year)
        self.btn_desires.on_clicked(self.population_desires)
        self.btn_marriage.on_clicked(self.create_marriage_dialog)
        self.btn_prev.on_clicked(self.prev_unit)
        self.btn_next.on_clicked(self.next_unit)
        self.btn_quit.on_clicked(self.quit_program)

        # Инициализация
        self.update_diagram()

        # Выбираем первого живого юнита
        alive_units = [uid for uid, p in self.population.people_dict.items() if not p.died]
        if alive_units:
            self.current_unit_id = alive_units[0]
            self.show_unit_profile(self.current_unit_id)

        plt.tight_layout()
        print("GUI настроен")

    def run(self):
        """Запуск симуляции"""
        print("\n" + "=" * 60)
        print("POPULATION SIMULATOR")
        print("=" * 60)
        print("\nУправление:")
        print("   НАЖИМАЙТЕ НА КНОПКИ МЫШЬЮ:")
        print("     • СЛЕДУЮЩИЙ ГОД - продвижение симуляции")
        print("     • ЖЕЛАНИЯ НАСЕЛЕНИЯ - анализ желаний и автоматические браки")
        print("     • СОЗДАТЬ БРАК (РУЧНОЙ) - ручной выбор супругов")
        print("     • ПРЕДЫДУЩИЙ/СЛЕДУЮЩИЙ ЮНИТ - навигация по анкетам")
        print("     • ВЫХОД - закрытие программы")
        print("\nПримечание: Автоматические браки (уровень 2) имеют больший шанс рождения детей")
        print("\nСистема профессий: Важные должности проверяются каждый год")
        print("=" * 60 + "\n")

        # Создаем начальное население
        self.population = Population(10)
        self.setup_gui()

        # Запускаем GUI
        plt.show(block=True)


if __name__ == "__main__":
    simulator = PopulationSimulator()
    simulator.run()