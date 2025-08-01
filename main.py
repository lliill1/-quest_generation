import json
import random
from typing import Dict, List

class QuestGenerator:
    def __init__(self):
        self.scenes = []
        self.current_id = 1
        self.branch_depth = 0
        self.branch_start_id = None
        
    def parse_input(self, input_file: str) -> Dict:
        """Парсинг входного файла с описанием сюжета"""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        genre = lines[0].split(':')[-1].strip() if ':' in lines[0] else lines[0]
        hero = lines[1].split(':')[-1].strip() if ':' in lines[1] else lines[1]
        goal = lines[2].split(':')[-1].strip() if ':' in lines[2] else lines[2]
        
        return {
            'genre': genre,
            'hero': hero,
            'goal': goal
        }
    
    def generate_scene(self, plot: Dict, is_branch: bool = False) -> Dict:
        """Генерация одной сцены"""
        scene_templates = [
            f"{plot['hero']} оказывается перед выбором: ",
            f"Внезапно {plot['hero']} сталкивается с ",
            f"Перед {plot['hero']} открывается путь: ",
            f"{plot['hero']} замечает что-то странное: ",
            f"На пути {plot['hero']} возникает препятствие: "
        ]
        
        scene_text = random.choice(scene_templates)
        
        if is_branch:
            scene_text = "[Ветвь] " + scene_text
        
        scene = {
            'scene_id': self.current_id,
            'text': scene_text,
            'choices': [],
            'next_scene': None
        }
        
        self.current_id += 1
        return scene
    
    def generate_choices(self, scene: Dict, plot: Dict, num_choices: int = 2) -> Dict:
        """Генерация вариантов выбора для сцены"""
        choice_templates = [
            "Исследовать ",
            "Атаковать ",
            "Спрятаться от ",
            "Поговорить с ",
            "Игнорировать ",
            "Использовать ",
            "Попытаться обойти "
        ]
        
        for i in range(num_choices):
            choice_text = random.choice(choice_templates)
            scene['choices'].append({
                'text': choice_text,
                'next_scene': self.current_id + i
            })
        
        return scene
    
    def generate_quest(self, input_file: str, min_scenes: int = 5, max_scenes: int = 10) -> Dict:
        """Основной метод генерации квеста"""
        plot = self.parse_input(input_file)
        num_scenes = random.randint(min_scenes, max_scenes)
        
        # Генерация основной линии
        for i in range(num_scenes):
            # Создаем развилку на случайной сцене (но не последней)
            if i > 1 and i < num_scenes - 3 and not self.branch_start_id and random.random() < 0.3:
                self.branch_start_id = self.current_id
                scene = self.generate_scene(plot, is_branch=True)
                scene = self.generate_choices(scene, plot, num_choices=2)
                self.scenes.append(scene)
                self.branch_depth = 3  # Глубина ветви
                continue
            
            if self.branch_start_id and self.branch_depth > 0:
                # Генерация ветви
                scene = self.generate_scene(plot, is_branch=True)
                if self.branch_depth > 1:
                    scene = self.generate_choices(scene, plot)
                else:
                    # Последняя сцена ветви возвращает в основную линию
                    scene['choices'] = [{
                        'text': 'Вернуться к основной линии',
                        'next_scene': self.branch_start_id + 1
                    }]
                self.branch_depth -= 1
                self.scenes.append(scene)
                continue
            
            # Генерация обычной сцены
            scene = self.generate_scene(plot)
            if i < num_scenes - 1:  # У последней сцены нет выбора
                scene = self.generate_choices(scene, plot)
            self.scenes.append(scene)
        
        return {
            'quest': {
                'genre': plot['genre'],
                'hero': plot['hero'],
                'goal': plot['goal'],
                'scenes': self.scenes
            }
        }
    
    def save_to_json(self, quest_data: Dict, output_file: str = 'quest.json'):
        """Сохранение квеста в JSON-файл"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(quest_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generator = QuestGenerator()
    quest_data = generator.generate_quest('input_examples/plot1.txt')
    generator.save_to_json(quest_data)
    print("Квест успешно сгенерирован и сохранен в quest.json")