# Schema Database cho CheftAi Android

## Table: recipes
- id: String (Primary Key)
- name: String
- calories: Int
- ingredients: List<String>
- cooking_time: Int (minutes)
- difficulty: String (Easy/Medium/Hard)

## Table: user_favorites
- user_id: String
- recipe_id: String (Foreign Key -> recipes.id)

