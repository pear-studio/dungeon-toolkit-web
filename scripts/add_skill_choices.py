import json

CLASSES_SKILL_CHOICES = {
    "barbarian": {
        "count": 2,
        "options": ["athletics", "animal_handling", "intimidation", "nature", "perception", "survival"]
    },
    "bard": {
        "count": 3,
        "options": ["acrobatics", "deception", "performance", "persuasion", "sleight_of_hand", "stealth", "history", "insight", "medicine", "religion", "animal_handling"]
    },
    "cleric": {
        "count": 2,
        "options": ["history", "insight", "medicine", "persuasion", "religion"]
    },
    "druid": {
        "count": 2,
        "options": ["animal_handling", "insight", "medicine", "nature", "perception", "religion", "survival"]
    },
    "fighter": {
        "count": 2,
        "options": ["acrobatics", "athletics", "animal_handling", "history", "insight", "intimidation", "perception", "survival"]
    },
    "monk": {
        "count": 2,
        "options": ["acrobatics", "athletics", "history", "insight", "medicine", "religion", "stealth"]
    },
    "paladin": {
        "count": 2,
        "options": ["athletics", "intimidation", "medicine", "persuasion", "religion"]
    },
    "ranger": {
        "count": 3,
        "options": ["athletics", "animal_handling", "insight", "investigation", "nature", "perception", "stealth", "survival"]
    },
    "rogue": {
        "count": 4,
        "options": ["acrobatics", "deception", "insight", "investigation", "stealth", "sleight_of_hand"]
    },
    "sorcerer": {
        "count": 2,
        "options": ["arcana", "deception", "insight", "intimidation", "nature", "religion"]
    },
    "warlock": {
        "count": 2,
        "options": ["arcana", "deception", "history", "insight", "intimidation", "investigation", "nature", "religion"]
    },
    "wizard": {
        "count": 2,
        "options": ["arcana", "history", "insight", "investigation", "medicine", "religion"]
    }
}

with open('backend/data/dnd5e_2014/classes.json', 'r', encoding='utf-8') as f:
    classes = json.load(f)

for cls in classes:
    slug = cls['slug']
    if slug in CLASSES_SKILL_CHOICES:
        cls['skill_choices'] = CLASSES_SKILL_CHOICES[slug]

with open('backend/data/dnd5e_2014/classes.json', 'w', encoding='utf-8') as f:
    json.dump(classes, f, ensure_ascii=False, indent=2)

print("Done! Added skill_choices to classes.json")
