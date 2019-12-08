import csv
import configparser

from youtube.youtube_client import get_authenticated_service


config = configparser.ConfigParser()
config.read('config.ini')


class YouTubeCommentsDownloader:

    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.comments_data = {} # store by keyword
        self.keywords = None
        self.service = get_authenticated_service()

    def search_by_keywords(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        self.keywords = config['comments']['keywords'].split(',')
        for keyword in self.keywords:
            results = self.search_videos_by_keyword(self.service,
                                                    q=keyword, part='id,snippet', eventType='completed', type='video')
            self.comments_data[keyword] = results
        return

    def get_videos(self, service, **kwargs):
        final_results = []
        results = service.search().list(**kwargs).execute()

        i = 0
        max_pages = 1
        while results and i < max_pages:
            final_results.extend(results['items'])

            # Check if another page exists
            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.search().list(**kwargs).execute()
                i += 1
            else:
                break

        return final_results

    def search_videos_by_keyword(self, service, **kwargs):
        results = self.get_videos(service, **kwargs)
        # for item in results['items']:
        #     print('%s - %s' % (item['snippet']['title'], item['id']['videoId']))
        final_result = []
        for item in results:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            comments = self.get_video_comments(service, part='snippet', videoId=video_id, textFormat='plainText')
            final_result.extend([(video_id, title, comment) for comment in comments])
        return results

    def get_video_comments(self,service, **kwargs):
        comments = []
        results = service.commentThreads().list(**kwargs).execute()

        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
            # if True:
            #     break
            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.commentThreads().list(**kwargs).execute()
            else:
                break

        return comments

    def save_comments_data(self):
        if len(self.comments_data)==0:
            raise Warning("No data to save. Execute search_by_keywords to get data.")
            return
        print(self.comments_data[self.keywords[0]])
        return



if __name__=='__main__':
    yt_comments_downloader = YouTubeCommentsDownloader()
    yt_comments_downloader.search_by_keywords()
