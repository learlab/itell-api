from youtube_transcript_api import YouTubeTranscriptApi

class TranscriptPipeline:
    def __init__(self):
        self.timestamps = False

    def __call__(self, url: str, start_time: int, end_time: int):
        if start_time:
            self.timestamps=True
        video_code = url.split('/')[-1][-11:]  
        try:     
            srt = YouTubeTranscriptApi.get_transcript(video_code)
            if self.timestamps == False:
                transcript = '\n'.join([x['text'] for x in srt])
            else:
                if end_time:
                    transcript_timeframe = [x for x in srt if end_time > x['start'] >= start_time]
                else:    
                    transcript_timeframe = [x for x in srt if x['start'] >= start_time]                                 
                transcript = ' '.join([x['text'] for x in transcript_timeframe])
            
            return transcript
        except:
            return None    
