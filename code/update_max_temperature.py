import pandas as pd
import numpy as np
from datetime import datetime
import re

# seperate ()
def split_city_year(city):
    match = re.match(r'(.+?)（(.+?)）', city)
    if match:
        return match.groups()
    return city, None

file_name = './date/day_temperature_master.csv'
file_name_flourish = './date/day_temperature_flourish.csv'


# this is master file
df = pd.read_csv(file_name, index_col=0)
df['date'] = pd.to_datetime(df['date'])

df = df.sort_values(['date', 'city'])

df_max = pd.read_csv('https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/mxtemsadext00_rct.csv', encoding='shift_jis', dtype={'観測所番号':str})
# extract three city
city_code = ['44132', '62078', '51106']
df_main = df_max[df_max['観測所番号'].isin(city_code)]

df_main.loc[:, ['city', 'kana']] = df_main['地点'].apply(lambda x: pd.Series(split_city_year(x)))
df_name = df_main['地点'].apply(lambda x: pd.Series(split_city_year(x)))
df_name = df_name.set_axis(['city', 'kana'], axis=1)
df_main = pd.concat([df_name, df_main], axis=1)

df_main = df_main.iloc[:, [0, 11]].set_axis(['city', '24年'], axis=1)

# what day
current_year = datetime.now().year
current_month = datetime.now().month
current_day = datetime.now().day
current_date = f'{current_year}-{current_month:02d}-{current_day:02d}'

df_main['date'] = current_date
df_main['date'] = pd.to_datetime(df_main['date'])

# merge new data
df_merge = pd.merge(df, df_main, on=['city', 'date'], how='left', suffixes=('', '_new'))

if '24年_new' in df_merge.columns:
    df_merge['24年'] = df_merge['24年'].combine_first(df_merge['24年_new'])
    df_merge = df_merge.drop(columns=['24年_new'])
else:
    pass

order = {'東京': 0, '名古屋': 1, '大阪': 2}
df_merge['sort_key'] = df_merge['city'].map(order)
df_merge = df_merge.sort_values('sort_key').drop('sort_key', axis=1)
df_merge = df_merge.set_axis(['date', '2023年', '平年', 'city', '24年'], axis=1)

df_merge.to_csv(file_name)
#Flourish用に列入れ替え
df_merge_2 = df_merge.iloc[:, [0, 3, 2, 1, 4]]
df_merge_2.to_csv(file_name_flourish)