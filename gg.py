import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def draw_graph(df, path):

    # Создаём пустой граф
    G = nx.Graph()

    # Проходим по каждой строке df
    for _, row in df.iterrows():
        sender = row['Имя отправителя']
        recipient = row['Имя получателя']

        # Добавляем узлы
        G.add_node(sender)
        G.add_node(recipient)

        # Добавляем ребро между отправителем и получателем
        G.add_edge(sender, recipient)

    # Визуализация графа
    fig, ax = plt.subplots(figsize=(10, 8))  # Создаём фигуру и оси
    pos = nx.spring_layout(G)  # Позиционируем узлы
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color='lightblue',
        edge_color='gray',
        node_size=2000,
        font_size=10,
        font_weight='bold',
        ax=ax
    )
    ax.set_title("Граф связей между отправителями и получателями", fontsize=14)
    # plt.show()
    plt.savefig(path)





# Добавляем столбец с периодами
def add_period_column(df, date_column='Дата открытки (нормализованная)'):
    # Определяем границы периодов
    bins = [1891, 1916, 1940, 1965, 1985, 1992, 2014]
    labels = [
        '1891 - 1916',
        '1917 - 1940',
        '1941 - 1965',
        '1966 - 1985',
        '1986 - 1992',
        '1993 - 2014'
    ]

    # Преобразуем дату в числовой формат (год)
    df['Год'] = pd.to_datetime(df[date_column], errors='coerce').dt.year

    # Добавляем столбец с периодом
    df['Период отправки'] = pd.cut(
        df['Год'],
        bins=bins,
        labels=labels,
        right=False,  # Включаем правую границу
        include_lowest=True  # Включаем минимальное значение
    )

    # Удаляем временный столбец 'Год'
    df.drop(columns=['Год'], inplace=True)

    return df




def find_recipients_by_sender(df, sender_name=None, sender_address=None, recipient_address=None, period=None,
                              recipient_index=None, recipient_name=None):
    
    mask = pd.Series(True, index=df.index)

    if sender_name:
        mask &= df['Имя отправителя'].str.contains(sender_name, case=False, na=False)

    if sender_address:
        mask &= df['Адрес отправителя'].str.contains(sender_address, case=False, na=False)

    if recipient_address:
        mask &= df['Адрес получателя'].str.contains(recipient_address, case=False, na=False)

    if recipient_index:
        mask &= df['Индекс получателя'].astype(str).str.contains(recipient_index, case=False, na=False)

    if period:
        mask &= df['Период отправки'].astype(str).str.contains(period, case=False, na=False)

    if recipient_name:
        mask &= df['Имя получателя'].astype(str).str.contains(recipient_name, case=False, na=False)

    return df[mask][[
        'Имя отправителя',
        'Имя получателя',
        'Адрес получателя',
        'Индекс получателя',
        'Дата открытки (нормализованная)',
        'Доп. сведения о получателе (например, титул, "дядя", "товарищ")',
        'Описание изображения. Обычно приводится на задней стороне или лицевой. Там обычно указывается, что изображено на открытке, автор, год фотографии/картины',
        'Дата печати открытки',
        'Страна (куда)',
        'Населенный пункт (куда)',
        'Период отправки'
    ]]
