#! python3
# marquee.py - a marquee for my Smart Mirror Project.

from tkinter import *
import datetime
import time
import logging

class Marquee(Canvas):

    def __init__(self, frame, newsrubot, fps=125):
        self.news = 'Владимир Путин выступил на Генеральной ассамблее ООН в костюме Деда Мороза.   ***   Дмитрий Медведев в ходе своего визита на Дальний восток заявил о невозможности разблокировки своего айфона.   ***  Укробандеровские собакофашисты вновь нарушили перемирие на Донбасе, коварно атаковав позиции отважных ополченцев.   ***    В ходе военных учений в Калининградской области российские войска уничтожили двести танков и триста самолетов противника. Условного.   ***   Президент России заявил о двухкратном снижении темпов прироста скорости падения российской экономики.   ***   Согласно опроса ФГЛПРФ ЗД более половины респондентов заявили о беззаговорочной поддержке курса Президента. Кормильца нашего, храни его Бог, благослави все дела его праведные.   ***   Виталий Мутко во время встречи со студентами МГУ признался, что только искренняя любовь к Отчизне заставляет его оставаться на своём посту.   ***   Глава МИД России Сергей Лавров считает овец перед сном.   ***   "Патриотизм и любовь к Родине обязаны быть в сердце каждого россиянина", - заявил Игорь Сечин на встрече с гостями и журналистами на борту своей яхты в Монте-Карло.   ***   Патриарх Московский и Всея Руси Кирилл считает, что российскому обществу следует отказаться от чрезмерной роскоши. В пользу РПЦ.'
        self.logger = logging.getLogger('Gesell.marquee.Marquee')
        self.logger.debug('Initializing an instance of Marquee Widget...')
        self.newsruBot = newsrubot
        # borderwidth default size is 2 (we don't need any borders), highlightbackground default is white - when the canvas is not in the focus.
        Canvas.__init__(self, frame,  bg='black', borderwidth=0, highlightbackground='black')
        self.fps = fps
        text = ''.join(self.newsruBot.news) + '\n'
        self.text_id = self.create_text(0, 0, text=text, anchor="w", fill='lightblue', font=("SF UI Text", 21, "bold"), tags=("text",))
        (x0, y0, x1, y1) = self.bbox("text")
        x1 = frame.winfo_screenwidth() - int(0.06 * (frame.winfo_screenwidth()))
        width = (x1 - x0)
        height = (y1 - y0)
        self.configure(width=width, height=height)
        self.place(relx=0.03, rely=0.84)
        self.logger.debug('An instance of Marquee Widget has been created.')
        self.animate()

    def animate(self):
        (x0, y0, x1, y1) = self.bbox("text")
        if x1 < 0 or y0 < 0:
            # The text is off the screen. Resetting the x while also getting the news from newsruBot.
            text = ''.join(self.news) + '\n'
            self.itemconfig(self.text_id, text=text)
            #print('Gotcha!', x0,y0,x1,y1)
            x0 = self.winfo_width()
            y0 = int(self.winfo_height()/2)
            #print(x0,y0,x1,y1)
            self.coords("text", x0, y0)
        else:
            self.move("text", -1, 0)
        self.after_id = self.after(int(1000/self.fps), self.animate)

class NewsruBot:
    def __init__(self):
        self.news = 'Владимир Путин выступил на Генеральной ассамблее ООН в костюме Деда Мороза.   ***   Дмитрий Медведев в ходе своего визита на Дальний восток заявил о невозможности разблокировки своего айфона.   ***  Укробандеровские собакофашисты вновь нарушили перемирие на Донбасе, коварно атаковав позиции отважных ополченцев.   ***    В ходе военных учений в Калининградской области российские войска уничтожили двести танков и триста самолетов противника. Условного.   ***   Президент России заявил о двухкратном снижении темпов прироста скорости падения российской экономики.   ***   Согласно опроса ФГЛПРФ ЗД более половины респондентов заявили о беззаговорочной поддержке курса Президента. Кормильца нашего, храни его Бог, благослави все дела его праведные.   ***   Виталий Мутко во время встречи со студентами МГУ признался, что только искренняя любовь к Отчизне заставляет его оставаться на своём посту.   ***   Глава МИД России Сергей Лавров считает овец перед сном.   ***   "Патриотизм и любовь к Родине обязаны быть в сердце каждого россиянина", - заявил Игорь Сечин на встрече с гостями и журналистами на борту своей яхты в Монте-Карло.   ***   Патриарх Московский и Всея Руси Кирилл считает, что российскому обществу следует отказаться от чрезмерной роскоши. В пользу РПЦ.'


if __name__ == '__main__':
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    newsruBot = NewsruBot()
    m = Marquee(window, newsruBot)
    window.mainloop()
