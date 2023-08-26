import os
from googleapiclient.discovery import build
import datetime
import isodate


class PlayList:
    api_key = os.environ.get('YOUTUBE_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    def __init__(self, pl_id: str) -> None:
        """Экземпляр инициализируется id видео. Дальше все данные будут подтягиваться по API."""
        self.__pl_id = pl_id
        self.pl_response = self.youtube.playlists().list(part='snippet', id=self.__pl_id).execute()
        self.playlist_videos = self.youtube.playlistItems().list(playlistId=self.__pl_id,
                                                                 part='contentDetails',
                                                                 maxResults=50,
                                                                 ).execute()
        self.video_ids = [video['contentDetails']['videoId'] for video in self.playlist_videos['items']]
        self.title = self.pl_response['items'][0]['snippet']['title']
        self.url = f'https://www.youtube.com/playlist?list={self.__pl_id}'

    @property
    def total_duration(self):
        video_response = self.youtube.videos().list(part='contentDetails,statistics',
                                                    id=','.join(self.video_ids)
                                                    ).execute()
        total_duration = datetime.timedelta(seconds=0)
        for video in video_response['items']:
            iso_8601_duration = video['contentDetails']['duration']
            duration = isodate.parse_duration(iso_8601_duration)
            total_duration += duration
        return total_duration

    def show_best_video(self):
        likes = []
        for video in self.video_ids:
            video_response = self.youtube.videos().list(part='snippet,statistics,contentDetails,topicDetails',
                                                        id=video
                                                        ).execute()
            likes.append({"id": video, "like": video_response['items'][0]['statistics']['likeCount']})
        max_like = max(likes, key=lambda x: x["like"])
        return f'https://youtu.be/{max_like["id"]}'

