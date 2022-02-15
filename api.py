
import requests
import pandas as pd
import zipfile
import gzip
import os
import time
import tqdm
from tqdm import tqdm
a = time.time()
# Параметры начальной и конечной даты
startdate = '20210601'
enddate = '20210630'

api_key = 'fc7929039625e70c5cd39e6aea190c87'
secret_key = '7951cda499cd85fc541a822d8c16eedc'
# Отправление запроса в Amplitude
response = requests.get('https://amplitude.com/api/2/export?&e=\{"event_type":"verified_revenue"\}&start='+startdate+'T0&end='+enddate+'T0', auth = (api_key, secret_key))
print('1. Запрос отправлен')

# Скачивание архива с данными
filename = 'period_since'+startdate+'to'+enddate+'_amplitude_data'
with open(filename + '.zip', "wb") as code:
    code.write(response.content)
print('2. Архив с файлами успешно скачан')


# Извлечение файлов в папку на компьютере
z = zipfile.ZipFile(filename + '.zip', 'r')
z.extractall(path = 'D:\\python\\'+filename)
print('3. Архив с файлами извлечен и записан в папку ' + filename)

# Извлечение файлов в папку на компьютере
z = zipfile.ZipFile(filename + '.zip', 'r')
z.extractall(path = 'D:\\python\\'+filename)
print('3. Архив с файлами извлечен и записан в папку ' + filename)

