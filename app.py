import logging
import traceback

from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request
from models import Payment
from functions import *

# Создаю фласк приложение
app = Flask(__name__)

# Добавляю логирование
handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=1)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(handler)


# Указываю коды валют
class Currency:
    USD = "840"
    EUR = "978"
    RUB = "643"


# Добавляю путь, на который будет приходить запрос
@app.route('/', methods=['GET', "POST"])
def ret_html():
    # При заходе на сайт отдаю страницу html
    if request.method == 'GET':
        app.logger.info('Обработка GET запроса')
        return render_template("main.html")
    else:
        app.logger.info('Обработка POST запроса')
        # При отправке запроса на оплату
        try:
            data = dict(request.form)  # Достаю инфо из фласк запроса
            # Сохранение запроса в базе данных
            Payment.create(currency=data["currency"],
                           amount=data["amount"],
                           comment=data['comment'])
            app.logger.info('Проверка правильности суммы')
            if not check_amount(data['amount']):
                app.logger.error(f'Неверная сумма {data["amount"]}')
                return render_template("main.html")

            # Задаю параметры для оплаты в евро
            if data['currency'] == Currency.EUR:
                return eur(app, data)

            # Задаю параметры для оплаты в usd
            elif data['currency'] == Currency.USD:
                return usd(app, data)

            # Задаю параметры для оплаты в rub
            elif data['currency'] == Currency.RUB:
                return rub(app, data)

        except:
            print(traceback.format_exc())
            return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)

