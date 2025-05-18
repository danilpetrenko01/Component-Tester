# Component-Tester
### Тестовые компоненты 
Интеграция для создания тестовых компонентов для изучения, тестирования и отладки автоматизации в системе Home Assistant.

## Оглавление
1. [Установка](#Установка)
2. [Конфигурация_компонентов](#Конфигурация_компонентов)

## Установка

Установка происходит через HACS. Укажите данный репозиторий в качестве пользовательского репозитория и он будет доступен для загрузки.

## Конфигурация_компонентов

Для включения интеграции `configuration.yaml` необходимо добавить следующее:

```yaml
tester:
```
При создании компонентов обязательным параметром является только имя устройства и указание платформы.
Чтобы добавить несколько компонентов одного типа надо прописать из подряд.

```yaml
switch:
  - platform: tester
    name: Switch 1
  - platform: tester
    name: Switch 2
```

### Доступность/Availability

По умолчанию все устройства являются доступными.
Как показано ниже в каждом домене, добавление `initial_availability: false`
в конфигурацию может переопределить значение по умолчанию и установить его как недоступный при запуске Home Assistant.
Доступность можно установить с помощью `tester.set_available`
со значением `true` или `false`.
Данная опция не явялется обязательной.


### Переключатели/Switches

Для добавления переключателя используйте следующую схему:

```yaml
switch:
  - platform: tester
    name: 'Switch'
    initial_availability: true
```


### Бинарные сенсоры/Binary Sensors

Для добавления бинарного сенсора используйте следующую схему:

```yaml
binary_sensor:
  - platform: tester
    name: 'Binary Sensor'
    initial_value: 'on'
    class: presence
    initial_availability: true
```
Поддерживаются все основные классы бинарного сенсора.
Используйте `tester.turn_on`, `tester.turn_off` и `tester.toggle` для изменения состояния бинарного сенсора.


### Сенсоры/Sensors

Для добавления бинарного сенсора используйте следующую схему:

```yaml
- platform: tester
  name: 'Temperature'
  class: temperature
  initial_value: 21
  initial_availability: true
  unit_of_measurement: 'C'
```

Используйте `tester.set` для изменения состояния сенсора.

Параметр `unit_of_measurement` может перезаписывать стандартные для класса единицы измерения.
Данная возмодность опциональна и принимает любое значение string. Список классов сенсора может быть найден по ссылке ниже:
[Sensor Entity](https://developers.home-assistant.io/docs/core/entity/sensor/)

### Лампы/Lights

Для добавления лампы используйте следующую схему:

```yaml
light:
  - platform: tester
    name: 'Light'
    initial_value: 'on'
    support_brightness: true
    initial_brightness: 50
    support_color: true
    initial_color: [50,50]
    support_color_temp: true
    initial_color_temp: 255
    support_white_value: true
    initial_white_value: 255
    initial_availability: true
```

- `support_*`; позволяют лампе менять цветовую температуру и яркость.
- `initial_*`; исходные значения.
  
### Замок/Locks

Для добавления замка используйте следующую схему:

```yaml
lock:
  - platform: tester
    name: 'Lock'
    initial_availability: true
```


### Вентилятор/Fans

Для добавления вентилятора используйте следующую схему:

```yaml
fan:
  - platform: tester
    name: 'Fan'
    speed: False
    speed_count: 5
    direction: True
    oscillate: True
    initial_availability: true
```

 При установке нужн выбрать `speed` или `speed_count`. Параметры являются не обязательными, но взаимоисключающими.
- `speed`; Если значение `True` то скорость меняется между низкой, средней и высокой.
- `speed_count`; Количество поддерживаемых скоростей. Будет переведено в проценты.
 4 скорости = 25, 50, 75 и 100%.
- `direction`; Если `True` то можно менять направление вращения.
- `oscillate`; Если `True` то можно включать колебания вентилятора.
