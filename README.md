## Постановка задачи

Участникам предлагается алгоритмически предсказать погодные условия по некоторой истории измерений.
Команды выполняют следующие задания:

* Имея датасет с погодными показателями за 43 часа наблюдений, сделать предсказание этих же параметров на следующие 5 часов.
* Загрузить результаты в [Telegram бот](https://t.me/yadro_weather_bot), получить оценку качества. Команды соревнуются в точности предсказаний (можно делать неограниченное число попыток).
* Презентация работы команды (публикация кода, слайды).

## Данные

В качестве данных представлены замеры различных показателей в точках (latitude, longitude) на сетке 30x30 с шагом около 5км (по y - с севера на юг, по x - с запада на восток).

Все массивы кроме высот в качестве первой размерности имеют шкалу времени с шагом в 1 час.

Датасет состоих из нескольких файлов (все имеют тип float32):

| Название файла | Размерность | Значения |
|---|---|---|
|[elevation.npy](./data/elevation.npy)  |	30x30 	| Высоты над уровнем моря в метрах|
|[temperature.npy](./data/temperature.npy) |  	43x30x30| 	Температура воздуха (С)|
|[pressure.npy](./data/pressure.npy) |  	43x30x30 	|Атмосферное давление (hPa)|
|[humidity.npy](./data/humidity.npy) | 	43x30x30 	|Влажность в %|
|[wind_speed.npy](./data/wind_speed.npy) |  	43x30x30 	|Скорость ветра (км/ч)|
|[wind_dir.npy](./data/wind_dir.npy) | 	43x30x30 	| Направление ветра (в градусах)|
|[cloud_cover.npy](./data/cloud_cover.npy) |  	43x30x30 |	Облачность (в процентах)|

## Формат решения

Вычисляемая метрика: MAPE (Mean Average Percentage Error). Чем меньше значение - тем лучше.

Решения принимаются в виде .csv файла со следующими столбцами:
```
ID,temperature,pressure,humidity,wind_speed,wind_dir,cloud_cover
```

В файле должно быть 4500 строк, которые соотвтетствуют 5 часам и 900 точкам для каждой из геопозиций в следующем порядке:
```
hour1_y1_x1
hour1_y1_x2
...
hour1_y1_x30
hour1_y2_x1
...
hour1_y30_x30
hour2_y1_x1
...
hour5_y30_x30
```

Пример сохранения файла из NumPy массивов:
```python
import pandas as pd
import numpy as np

solution = np.stack([
    temperature.reshape(-1),  # Из 5x30x30 в 4500
    pressure.reshape(-1),
    humidity.reshape(-1),
    wind_speed.reshape(-1),
    wind_dir.reshape(-1),
    cloud_cover.reshape(-1),
], axis=1)


solution = pd.DataFrame(solution, columns=["temperature", "pressure", "humidity", "wind_speed", "wind_dir", "cloud_cover"])
solution.to_csv("solution.csv", index_label="ID")
```
