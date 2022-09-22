from config import *
from hashlib import sha256
import requests

from flask import render_template, redirect


# Функция по генерации sign
def generate_sign(keys_required, data_to_sign):
    sorted_data = []
    for key in sorted(keys_required):
        sorted_data.append(str(data_to_sign[key]))

    result = ":".join(sorted_data) + secretKey
    sign = sha256(result.encode('utf-8')).hexdigest()
    return sign

# Функция по проверке суммы
def check_amount(amount):
    try:
        if float(amount) > 0:
            return True
        return False
    except Exception:
        return False

# Функция по обработке запроса с euro
def eur(app, data):
    app.logger.info('Обработка запроса в EUR')
    keys = ['amount', 'currency', 'shop_id', 'shop_order_id']  # Обязательные ключи
    data_for_sign = {
        'amount': data['amount'],
        'currency': data['currency'],
        'shop_order_id': shop_order_id,  # Подтягиваю из конфига
        'shop_id': shop_id  # Подтягиваю из конфига
    }

    sign = generate_sign(keys, data_for_sign)  # Срабатывает функция по генерации sign
    # Возвращает html шаблон с подставленными значениями
    return render_template("eur.html",
                           amount=data['amount'],
                           currency=data['currency'],
                           shop_id=shop_id,
                           shop_order_id=shop_order_id,
                           sign=sign)


# Функция по обработке запроса с usd
def usd(app, data):
    app.logger.info('Обработка запроса в USD')
    keys = ['shop_amount', 'shop_currency', 'shop_id', 'shop_order_id', 'payer_currency']
    data_for_sign = {"payer_currency": data['currency'],
                     "shop_amount": data['amount'],
                     "shop_currency": data['currency'],
                     "shop_id": shop_id,
                     "shop_order_id": shop_order_id}

    sign = generate_sign(keys, data_for_sign)
    data_for_sign["sign"] = sign
    headers = {'content-type': 'application/json'}
    response = requests.post('https://core.piastrix.com/bill/create',
                             json=data_for_sign, headers=headers)  # Делаю post запрос по url

    app.logger.info(f'Статус код - {response.status_code}')
    if response.status_code == 200:
        response = response.json()
        if response['data'].get('url'):  # Проверяю есть ли url в ответе
            url = response['data']['url']
            app.logger.info(f'Редирект - {url}')
            return redirect(url)  # После успешной проверки отправляю редирект на url
        else:
            app.logger.error('url в ответе не найден')
            return render_template("main.html")
    else:
        return render_template("main.html")


# Функция по обработке запроса с rub
def rub(app, data):
    app.logger.info('Обработка запроса в RUB')
    keys = ["amount", 'currency', 'payway', 'shop_id', 'shop_order_id']
    data_for_sign = {"amount": data["amount"],
                     "currency": data["currency"],
                     "payway": payway,
                     "shop_id": shop_id,
                     "shop_order_id": shop_order_id}

    sign = generate_sign(keys, data_for_sign)
    data_for_sign["sign"] = sign
    headers = {'content-type': 'application/json'}
    response = requests.post('https://core.piastrix.com/invoice/create',
                             json=data_for_sign, headers=headers)
    app.logger.info(f'Статус код - {response.status_code}')
    if response.status_code == 200:
        response = response.json()
        if response.get('result'):
            return render_template("rub.html",
                                   method=response['data']['method'],
                                   action=response['data']['url'],
                                   m_curorderid=response['data']['data']['m_curorderid'],
                                   m_historyid=response['data']['data']['m_historyid'],
                                   m_historytm=response['data']['data']['m_historytm'],
                                   referer=response['data']['data']['referer'],
                                   lang=response['data']['data'].get('lang', 'ru'))
        app.logger.error(f'Получен неправильный ответ {response}')
    return render_template("main.html")
