import requests
from bs4 import BeautifulSoup
import pandas as pd
import telebot
import schedule
import time


# Функция парсинга страниц товаров
def parse_product_pages(sku_list):
    # Создаем пустой список для хранения отзывов
    reviews = []

    # Парсим страницы товаров для каждого SKU
    for sku in sku_list:
        # Получаем страницу товара
        response = requests.get(f"https://www.wildberries.ru/catalog/{sku}/detail.aspx")
        soup = BeautifulSoup(response.text, "html.parser")

        # Получаем отзывы
        reviews_html = soup.find_all("div", class_="review-item")

        # Парсим отзывы
        for review_html in reviews_html:
            review = {}
            review["title"] = review_html.find("div", class_="review-title").text
            review["stars"] = review_html.find("div", class_="review-stars").text
            review["text"] = review_html.find("div", class_="review-text").text
            reviews.append(review)

    # Возвращаем список отзывов
    return reviews


# Функция обработки отзывов
def process_reviews(reviews):
    # Создаем пустой список для хранения негативных отзывов
    negative_reviews = []

    # Определяем, является ли отзыв негативным
    for review in reviews:
        if int(review["stars"]) < 4:
            negative_reviews.append(review)

    # Возвращаем список негативных отзывов
    return negative_reviews


# Функция отправки уведомлений
def send_notifications(negative_reviews):
    # Создаем бота Telegram
    bot = telebot.TeleBot("токен вашего бота")

    # Отправляем уведомления о негативных отзывах
    for review in negative_reviews:
        bot.send_message("id вашей группы",
                         f"Негативный отзыв/название товара/{review['title']}/SKU товара/{review['sku']}"
                         f"/столько-то звезд ({review['stars']})/ текст отзыва/{review['text']}/Текущий рейтинг товара.")


# Функция запуска по расписанию
def run_task():
    # Получаем список SKU товаров из файла Excel
    sku_list = pd.read_excel("file.xlsx")["SKU"].tolist()

    # Парсим страницы товаров
    reviews = parse_product_pages(sku_list)

    # Обрабатываем отзывы
    negative_reviews = process_reviews(reviews)

    # Отправляем уведомления
    send_notifications(negative_reviews)


# Запускаем функцию по расписанию
schedule.every().day.at("09:00").do(run_task)

# Запускаем главный цикл
while True:
    schedule.run_pending()
    time.sleep(1)
