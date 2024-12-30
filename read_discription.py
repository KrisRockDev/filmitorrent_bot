txt = r'd:\filmtorrent\2023.08.13 17-46 Сердце Стоун (2023)\Описание.txt'
with open(txt, mode='r', encoding='utf8') as discription:
    message_text = discription.readlines()

res_txt = ''

for i in message_text:
    word_list = ['✅Опубликовано:', '🔗url:']
    if i.split(' ')[0] not in word_list:
        res_txt += i
        # print(i.strip())

# res_txt = res_txt.replace('Время', '🕒Продолжительность').replace('Название', '🎥Название').replace('Рейтинг: 0\n', '').replace('Рейтинг', '💥Рейтинг',).replace('Актеры', '🤡Актеры',).replace('Режиссер', '👤Режиссер',).replace('Страна', '🚩Страна',).replace('Год', '📅Год',).replace('Жанр', '📌Жанр',)

print(res_txt)

