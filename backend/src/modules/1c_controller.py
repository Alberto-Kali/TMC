import requests
import json

# Параметры подключения
server_address = '192.168.243.207'

# Формирование заголовков с базовой аутентификацией
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Данные для отправки
data = {
    "Код": "000000015",
    "Наименование": "Муниципальное бюджетное общеобразовательное учреждение 'Средняя школа №15'",
    "Учителя_Key": "47bdc287-af91-11ef-80e8-90e868d68e8a",
    "Классы_Key": "bda18f95-af92-11ef-80e8-90e868d68e8a",
    "Учителя@navigationLinkUrl": "Catalog_Школы(guid'bda18f96-af92-11ef-80e8-90e868d68e8a')/Учителя",
    "Классы@navigationLinkUrl": "Catalog_Школы(guid'bda18f96-af92-11ef-80e8-90e868d68e8a')/Классы"

}

try:
    # Отправка POST-запроса
    response = requests.post(
        f'http://{server_address}/SATANA/odata/standard.odata/Catalog_Школы', 
        headers=headers, 
        json=data,
        #auth=(login, password)  # Дополнительная аутентификация
    )

    # Расширенная обработка ответа
    print(f"Статус ответа: {response.status_code}")
    print("Заголовки ответа:", response.headers)
    
    # Попытка вывести текст ответа
    print("Текст ответа:")
    print(response.text)

    # Проверка статуса ответа
    response.raise_for_status()  # Вызовет исключение для плохих статусов

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")