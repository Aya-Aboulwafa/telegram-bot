import pandas as pd

df=pd.read_csv('output.csv')

df = df.drop(columns=['image_url'])

df =df.dropna()

df = df[df['chat_title'] != '']
df = df[df['message'] != '']
df = df[df['message'] != '.']
df = df[df['message'] != '/add_meeting']
df= df[df['chat_title'] != 'testme']


#split time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df['time'] = df['timestamp'].dt.time
df = df.drop(columns=['timestamp'])

df = df[~df.apply(lambda x: x.str.strip().eq('').any(), axis=1)]

import re

# Define a function to detect Arabic characters
def contains_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(str(text)))

# Apply the function to remove rows containing Arabic words
df = df[~df.applymap(contains_arabic).any(axis=1)]

df['sender'] = df['sender'].replace({
    'Loly_re': 'alaa',
    'EdroSoli392': 'abdallah edris'
})

len(df)

df.to_csv('cleaneddata.csv', index=False)