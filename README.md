![](https://img.shields.io/badge/python-3.7.4-informational)
![](https://img.shields.io/badge/vk__api-11.8.0-informational)

# vktoolkit
Набор скриптов для получения информации из Вконтакте.

## vkextractiontools
Cкрипт написан в рамках изучения **Python**, **API VK** и **Git**.
Позволяет извлекать некоторые данные из профилей Вконтакте в обход их настроек приватности.

### Описание работы скрипта
Работа данного скрипта основана на том, что поиск в ВК игнорирует настройки приватности пользователей.
Для извлечения данных используется подход, аналогичный blind SQL injection:
1. Выполняем поиск по пользователям с определенным значением критерия;
2. Интересующий нас профиль присутствует в результатах поиска?<br>
    - Если да - значение критерия для интересующего профиля верное;
    - Иначе - изменяем значение критерия и повторяем поиск.

### Возможные проблемы
- API VK ограничивает выдачу поиска 1000 профилями. В случае брутфорса распространенного профиля, например, Ивана Иванова,
необходимо изменить скрипт для уточнения параметров поиска такими значениями, как город и т.п, чтобы результат выдачи укладывался в 1000 профилей.

- API VK ограничивает количество выполнений метода API за неизвестную еденицу времени, обойти данное
ограничение возможно путем модификации скрипта балансировкой нагрузки по нескольким профилям,
из под которых осуществляются запросы к API.

### Возможные улучшения скрипта
- Возможно ускорить проверку наличия интересующего профиля в результатах поиска;  
На текущий момент в скрипте используется полный перебор. Возможно добавить критерий к users.search,
чтобы API возвращал отсортированные результаты и применить алгоритм бинарного поиска.
- Возможно ускорить извлечение параметров путем распараллеливания задач по нескольким потокам.

### Использование скрипта
Опции `--day`, `--month`, `--year`, `--status`, `--religion` и `--reg-date` являются флагами и не требуют после себя аргументов.
Аргументы для опций `--min-year` и `--max-year` должны представлять из себя натуральные числа,
при этом аргумент опции `--min-year` должен быть >= 1900 и <= аргумента опции `--max-year`.

В конечном результате программа выводит None:
- Если вы извлекали год рождения, попробуйте изменить с помощью опций `--min-year` и / или `--max-year` диапазон перебора года рождения.
Возможно, дата на рассматриваемом аккаунте старее или моложе параметров по-умолчанию.
- Возможно, вы ввели слишком общий запрос и искомый аккаунт не попал в выдачу 1000 от users.search, тогда измените скрипт для уточнения деталей поиска.
- Возможно, вас заблокировал VK API за слишком частые обращения. Измените учетные данные, используемые для обращений к API,
либо отдохните некоторое время и запустите скрипт позже.

Опции `--login` и `--password` не являются обязательными, если вы не хотите светить учетными данными в истории
командного интерпретатора, их можно выпустить, тогда скрипт запросит учетные данные интерактивно.

### Примеры
Извлечь день, месяц и год рождения профиля https://vk.com/rsherstnev:
```
vkextractiontools.py --login +79632286969 --password yourverysecurepassword --id rsherstnev --day --month --year --min-year 1990 --max-year 2000 
```
Извлечь семейное положение, религиозные взгляды и дату регистрации https://vk.com/rsherstnev:
```
vkextractiontools.py --login +79632286969 --password yourverysecurepassword --id rsherstnev --status --religion --reg-date 
```

## mutualfriends
Cкрипт позволяет узнать общих друзей двух и более профилей в ВК, при этом необязательно, чтобы один из профилей был вашим.

### Возможные проблемы
- Запросы к API VK выполняются из под определенного профиля, и если хотя бы у одного из перечисленных профилей доступ к друзьям
данному профилю закрыт, то скрипт выведет ошибку;

### Использование скрипта
Аргументы опции `--ids` необходимо отделять друг от друга пробелами

Опции `--login` и `--password` не являются обязательными, если вы не хотите светить учетными данными в истории
командного интерпретатора, их можно выпустить, тогда скрипт запросит учетные данные интерактивно.

### Примеры
Вывести общих друзей профилей https://vk.com/rsherstnev, https://vk.com/degustatorvarenikov и https://vk.com/id1337228:
```
mutualfriends.py --login +79632286969 --password yourverysecurepassword --ids rsherstnev degustatorvarenikov id1337228 
```
