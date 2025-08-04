import json
import random
from typing import Dict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class QuestGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.scenes = []
        self.current_id = 1
        self.branch_start_id = None
        self.branch_depth = 0
        
        # Инициализация модели
        self.llm = ChatGroq(
            api_key=self.api_key,
            model_name="llama3-8b-8192",
            temperature=0.7,
            max_tokens=100
        )
        
        # Шаблоны промптов
        self.scene_prompt = ChatPromptTemplate.from_template("""
            Жанр: {genre}. Герой: {hero}. Цель: {goal}.
            Контекст: {prev_context}
            Сгенерируй сцену для {scene_type} на русском языке в стиле RPG.
            Опиши ситуацию, окружение или диалог, включая героя и связанную с целью задачу.
            Текст должен быть 2-3 предложения.
        """)
        
        self.choices_prompt = ChatPromptTemplate.from_template("""
            На основе сцены: '{scene_text}' в жанре {genre},
            где герой {hero} стремится {goal},
            предложи {num_choices} варианта действий на русском языке.
            Каждый вариант — короткое предложение, разделённое символом '|'.
            Не добавляй никаких пояснений, только варианты, разделённые '|'.
        """)
        
        self.output_parser = StrOutputParser()

    def parse_input(self, input_file: str) -> Dict:
        """Парсинг входного файла с описанием сюжета"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if len(lines) < 3:
                raise ValueError("Входной файл должен содержать как минимум 3 строки: жанр, герой, цель")
            
            # Извлекаем данные даже если нет разделителя ":"
            genre = lines[0].split(':')[-1].strip() if ':' in lines[0] else lines[0]
            hero = lines[1].split(':')[-1].strip() if ':' in lines[1] else lines[1]
            goal = lines[2].split(':')[-1].strip() if ':' in lines[2] else lines[2]
            
            return {'genre': genre, 'hero': hero, 'goal': goal}
        except Exception as e:
            raise ValueError(f"Ошибка при парсинге файла: {str(e)}")

    def generate_text(self, prompt_template: ChatPromptTemplate, input_data: Dict) -> str:
        """Генерация текста с помощью ChatGroq"""
        try:
            chain = prompt_template | self.llm | self.output_parser
            result = chain.invoke(input_data)
            return result.strip()
        except Exception as e:
            raise RuntimeError(f"Ошибка при генерации текста: {str(e)}")

    def generate_scene(self, plot: Dict, is_branch: bool = False, prev_context: str = "") -> Dict:
        """Генерация одной сцены"""
        scene_type = "побочной ветви" if is_branch else "основного сюжета"
        
        scene_text = self.generate_text(
            self.scene_prompt,
            {
                'genre': plot['genre'],
                'hero': plot['hero'],
                'goal': plot['goal'],
                'prev_context': prev_context,
                'scene_type': scene_type
            }
        )
        
        scene = {
            'scene_id': f"scene_{self.current_id}",
            'text': scene_text,
            'choices': []
        }
        self.current_id += 1
        return scene

    def generate_choices(self, scene: Dict, plot: Dict, num_choices: int = 2) -> Dict:
        """Генерация вариантов выбора для сцены"""
        choices_text = self.generate_text(
            self.choices_prompt,
            {
                'scene_text': scene['text'],
                'genre': plot['genre'],
                'hero': plot['hero'],
                'goal': plot['goal'],
                'num_choices': num_choices
            }
        )
        
        # Обработка вариантов выбора
        choices_list = [choice.strip() for choice in choices_text.split('|') if choice.strip()]
        fallback_choices = ["Продолжить путь", "Осмотреться вокруг"]
        
        for i in range(num_choices):
            choice_text = choices_list[i] if i < len(choices_list) else fallback_choices[i % len(fallback_choices)]
            scene['choices'].append({
                'text': choice_text,
                'next_scene': f"scene_{self.current_id + i}"
            })
        
        return scene

    def generate_quest(self, input_file: str, min_scenes: int = 5, max_scenes: int = 10, branch_depth: int = 3) -> Dict:
        """Основной метод генерации квеста"""
        try:
            plot = self.parse_input(input_file)
            num_scenes = random.randint(max(min_scenes, 5), min(max_scenes, 10))
            context = f"{plot['hero']} начинает приключение в жанре {plot['genre']} с целью {plot['goal']}."

            for i in range(num_scenes):
                if i > 1 and i < num_scenes - branch_depth and not self.branch_start_id and random.random() < 0.4:
                    self.branch_start_id = f"scene_{self.current_id}"
                    scene = self.generate_scene(plot, is_branch=True, prev_context=context)
                    scene = self.generate_choices(scene, plot, num_choices=2)
                    self.scenes.append(scene)
                    context += f" {scene['text']} Ветвление началось."
                    self.branch_depth = branch_depth
                    continue
                
                if self.branch_start_id and self.branch_depth > 0:
                    scene = self.generate_scene(plot, is_branch=True, prev_context=context)
                    if self.branch_depth > 1:
                        scene = self.generate_choices(scene, plot, num_choices=2)
                    else:
                        scene['choices'] = [{
                            'text': 'Вернуться к основной линии',
                            'next_scene': f"scene_{int(self.branch_start_id.split('_')[1]) + 1}"
                        }]
                    self.scenes.append(scene)
                    context += f" {scene['text']}"
                    self.branch_depth -= 1
                    continue
                
                scene = self.generate_scene(plot, prev_context=context)
                if i < num_scenes - 1:
                    scene = self.generate_choices(scene, plot, num_choices=2)
                self.scenes.append(scene)
                context += f" {scene['text']}"

            return {
                'quest': {
                    'genre': plot['genre'],
                    'hero': plot['hero'],
                    'goal': plot['goal'],
                    'scenes': self.scenes
                }
            }
        except Exception as e:
            raise RuntimeError(f"Ошибка при генерации квеста: {str(e)}")

    def save_to_json(self, quest_data: Dict, output_file: str = 'quest.json'):
        """Сохранение квеста в JSON-файл"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(quest_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Ошибка при сохранении JSON: {str(e)}")


if __name__ == "__main__":
    try:
        generator = QuestGenerator()
        quest_data = generator.generate_quest('input_examples/plot1.txt')
        generator.save_to_json(quest_data)
        print("Квест успешно сгенерирован и сохранен в quest.json")
    except Exception as e:
        print(f"Ошибка: {str(e)}")