
# Преобразование json к обычному табличному формату
directory = 'D:\\python\\'+filename+'\\324600'
files = os.listdir(directory)
amplitude_dataframe = pd.DataFrame()
print('Прогресс обработки файлов:')
time.sleep(1)
for i in tqdm(files):
    with gzip.open(directory + '\\' + i) as f:
        add = pd.read_json(f, lines = 'True')
    amplitude_dataframe = pd.concat([amplitude_dataframe, add])
time.sleep(1)
print('4. JSON файлы из архива успешно преобразованы и записаны в dataframe')
17:55

# Записать полученной таблицы в Excel-файл
amplitude_dataframe.to_excel('D:\\python\\'+filename+'.xlsx',index=False)
print('5. Dataframe успешно записан в файл ' + filename)

b = time.time()
diff = b-a
minutes = diff//60
print('Выполнение кода заняло: {:.0f} минут(ы)'.format( minutes))