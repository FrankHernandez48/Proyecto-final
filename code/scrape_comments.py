# Imports
import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
key = os.getenv("API_KEY")

# Construir objeto Youtube
youtube = build('youtube', 'v3', developerKey=key)

# Conseguir Channel ID
request_id = youtube.search().list(
    part='snippet',
    q='Skyshock',
    type='channel',
    maxResults=1
)
response_id = request_id.execute()
skyshock_id = response_id['items'][0]['id']['channelId']

# Buscar URLs
request_uploads = youtube.search().list(
    part='snippet',
    channelId=skyshock_id,
    maxResults=45,
    order='date',
    type='video'
)
results_uploads = request_uploads.execute()

# Obtener los IDs de los videos
video_ids = [item['id']['videoId'] for item in results_uploads['items']]

# Lista para almacenar comentarios
comments_data = []

for video_id in video_ids:  # Recorre todos los videos obtenidos
    next_page_token = None

    while True:  
        request_comments = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=50,
            textFormat='plainText',
            pageToken=next_page_token
        )
        response_comments = request_comments.execute()

        for item in response_comments.get('items', []):
            comment_id = item['snippet']['topLevelComment']['id']
            text = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments_data.append({
                "comment_id": comment_id,
                "text": text,
                "video_id": video_id
            })

        next_page_token = response_comments.get('nextPageToken', None)
        if not next_page_token:  # Si ya no hay más páginas, salir del bucle
            break

# Convertir a DataFrame
df = pd.DataFrame(comments_data)

# Guardar como CSV
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
df.to_csv(data_path, index=False)