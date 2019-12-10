import csv
import configparser
import pickle as pk

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
        try:
            results = service.search().list(**kwargs).execute()
        except:
            print(kwargs)
            return
        i = 0
        max_pages = 2
        while results and i < max_pages:
            final_results.extend(results['items'])

            # Check if another page exists
            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                try:
                    results = service.search().list(**kwargs).execute()
                except:
                    break
                i += 1
            else:
                break

        return final_results

    def search_videos_by_keyword(self, service, **kwargs):
        results = self.get_videos(service, **kwargs)
        if not results:
            return
        # for item in results['items']:
        #     print('%s - %s' % (item['snippet']['title'], item['id']['videoId']))
        final_result = []
        for item in results:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            # print(title, video_id)
            comments = self.get_video_comments(service, part='snippet', videoId=video_id, textFormat='plainText')
            final_result.extend([(video_id, title, comment) for comment in comments])

        return final_result

    def get_video_comments(self,service, **kwargs):
        comments = []
        try:
            results = service.commentThreads().list(**kwargs).execute()
        except:
            print(kwargs)
            return
        # print(results)

        parent_ids = []
        while results:
            for item in results['items']:
                thread_id = item['id']
                topLevelComment_snippet = item['snippet']['topLevelComment']['snippet']

                comment_obj = {}
                comment_obj['thread_id'] = thread_id
                comment_obj['comment'] = topLevelComment_snippet['textDisplay']
                comment_obj['author'] = topLevelComment_snippet['authorDisplayName']
                comment_obj['authorChannelId'] = topLevelComment_snippet['authorChannelId']
                comment_obj['videoId'] = topLevelComment_snippet['videoId']
                comment_obj['canRate'] = topLevelComment_snippet['canRate']
                comment_obj['viewerRating'] = topLevelComment_snippet['viewerRating']
                comment_obj['likeCount'] = topLevelComment_snippet['likeCount']
                # print(item)
                comments.append(comment_obj)

                try:
                    replies = item['replies']['comments']

                except:
                    replies = []
                if len(replies)!=item['snippet']['totalReplyCount']:
                    parent_ids.append(thread_id)

                for reply in replies:
                    comment_obj = {}
                    comment_obj['thread_id'] = thread_id
                    comment_obj['comment'] = reply['snippet']['textDisplay']
                    comment_obj['author'] = reply['snippet']['authorDisplayName']
                    comment_obj['authorChannelId'] = reply['snippet']['authorChannelId']
                    comment_obj['videoId'] = reply['snippet']['videoId']
                    comment_obj['canRate'] = reply['snippet']['canRate']
                    comment_obj['viewerRating'] = reply['snippet']['viewerRating']
                    comment_obj['likeCount'] = reply['snippet']['likeCount']
                    comments.append(comment_obj)

            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.commentThreads().list(**kwargs).execute()
            else:
                break
        # print(comments)
        # print(parent_ids)
        # print(kwargs)
        # if len(parent_ids)>0:
        for parent_id in parent_ids:
            results_comments = service.comments().list(part='snippet',parentId=parent_ids).execute()
            # print("Result Comment : ", results_comments)
            for item in results_comments['items']:
                comment_obj['thread_id'] = parent_id
                comment_obj['comment'] = item['snippet']['textDisplay']
                comment_obj['author'] = item['snippet']['authorDisplayName']
                comment_obj['authorChannelId'] = item['snippet']['authorChannelId']
                comment_obj['videoId'] = item['snippet']['videoId']
                comment_obj['canRate'] = item['snippet']['canRate']
                comment_obj['viewerRating'] = item['snippet']['viewerRating']
                comment_obj['likeCount'] = item['snippet']['likeCount']
                comments.append(comment_obj)
        return comments

    def save_comments_data(self):
        if len(self.comments_data)==0:
            raise Warning("No data to save. Execute search_by_keywords to get data.")
            return
        # print(self.comments_data[self.keywords[0]])
        pk.dump(self.comments_data, open('comments_data_'+'_'.join(self.keywords)+'.pkl', 'wb'))
        return



if __name__=='__main__':
    yt_comments_downloader = YouTubeCommentsDownloader()
    yt_comments_downloader.search_by_keywords()
    yt_comments_downloader.save_comments_data()
