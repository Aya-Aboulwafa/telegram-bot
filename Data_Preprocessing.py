import pandas as pd
import re

# Load the data
df = pd.read_csv('output.csv')

# Drop unnecessary columns and rows
df = df.drop(columns=['image_url'])
df = df[df['message'] != '.']
df = df[df['chat_title'] != 'testme']

# Drop rows with null or empty values in all columns except 'message_thread_id'
df = df.dropna(subset=[col for col in df.columns if col != 'message_thread_id'])
df = df[df.apply(lambda x: x.str.strip().ne('').all() if x.name != 'message_thread_id' else True, axis=1)]

# Parse timestamp with mixed formats
df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')

# Split timestamp into date and time
df['date'] = df['timestamp'].dt.date
df['time'] = df['timestamp'].dt.time
df = df.drop(columns=['timestamp'])

# Remove rows with any empty fields after stripping whitespace except in 'message_thread_id'
df = df[~df.apply(lambda x: x.str.strip().eq('').any(), axis=1)]

# Define a function to detect and remove Arabic characters
def remove_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return re.sub(arabic_pattern, '', str(text))

# Apply the Arabic removal function to all columns except 'sender'
for col in df.columns:
    if col != 'sender':
        df[col] = df[col].apply(remove_arabic)

# Preprocess the message_thread_id column
df['message_thread_id'] = df['message_thread_id'].replace({
    '12.0': 'Knowledge',
    '3.0': 'Communication',
    '31.0': 'Affiliate',
    '42.0': 'Reservation & Productivity',
    '9.0': 'Quality',
    '11.0': 'Project (coordination)',
    '8.0': 'SaaS',
    '5.0': 'Developer Ecosystem',
    '153.0': 'Workspace (ERB) & Analytics',
    '7.0': 'Apps (Mobile & Desktop)',
    '4.0': 'Learning & Customer',
    '13.0': 'AI',
    '10.0': 'DevOps',
    '14.0': 'Group insights',
    '374.0': 'Training and development',
    '675.0': 'Announcement',
    None: 'Meetings & General Conversations'
})

# Handle any null values in message_thread_id
df['message_thread_id'] = df['message_thread_id'].fillna('Meetings & General Conversations')



df_filtered = df[~df['sender'].isin(['Mahmoud', 'Mohamed Elgammal', 'Magid', 'Ahmed Usama', 'AhmedEGabr','toaa','Mahmoud Mamdouh','Ahmad Samir','Mohamed Ramadan','Mohamed El Koofy'])]

# Save the cleaned data
df_filtered.to_csv('cleaneddata.csv', index=False)


print("Final row count:", len(df))
print("Final row count:", len(df_filtered))

