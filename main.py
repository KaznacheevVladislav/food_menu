import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def get_site_access(url):
    """Проверяет корректность ссылки возвращает объект класса BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        src = response.text
        return BeautifulSoup(src, 'lxml')
    except Exception as ex:
        exit(f"{ex}\nCan't get data from server. URL: {url}")


def get_recipes_links(eda_url):
    """Возвращает ссылки на блюда."""
    soup = get_site_access(eda_url)

    dishes = soup.find_all('div', class_='card__description')
    recipes_links = {}
    for dish in dishes:
        dish_title = dish.find('div', class_='card__title title').text
        dish_link = dish.find('a').get('href')
        recipes_links[dish_title] = f'https://www.edimdoma.ru{dish_link}'
    return recipes_links


def get_recipe(title, link):
    """Формирует csv файл с ингредиентами и txt файл с рецептом"""
    soup = get_site_access(link)
    # На сколько порций рассчитано
    portions = soup.find(class_='field__container').find(attrs={'name': 'servings'})['value']
    # Записываем заголовки столбцов
    with open(f'recipes/{title}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Ингредиенты',
                'Количество',
                'Цена',
                f'Количество порций: {portions}'
            )
        )

    products = soup.find(class_='field-row recipe_ingredients').find_all(class_='definition-list-table')
    # Перебираем продукты из списка ингредиентов
    for product in products:
        product_title = product.find(class_='recipe_ingredient_title').text
        product_count = product.find(class_='definition-list-table__td definition-list-table__td_value').text
        product_price = 0  # Здесь вызов функция с ценой
        # Записываем ингредиент и его количество в таблицу csv
        with open(f'recipes/{title}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    product_title,
                    product_count,
                    product_price
                )
            )
    # Создаем txt файл с инструкцией по приготовлению
    cooking_steps = soup.find_all(class_='plain-text recipe_step_text')
    with open(f'recipes/{title}.txt', 'w') as file:
        for number, step in enumerate(cooking_steps, 1):
            file.write(f'{number}. {step.text}\n\n')


def main():
    Path('recipes').mkdir(parents=True, exist_ok=True)

    edimdoma_url = 'https://www.edimdoma.ru/retsepty?tags%5Brecipe_mealtime%5D%5B%5D=%D0%B7%D0%B0%D0%B2%D1%82%D1%80%D0%B0%D0%BA&with_ingredient=&with_ingredient_condition=and&without_ingredient=&user_ids=&field=&direction=&query='
    recipes_links = get_recipes_links(edimdoma_url)
    for dish_title, dish_link in recipes_links.items():
        get_recipe(dish_title, dish_link)


if __name__ == '__main__':
    main()