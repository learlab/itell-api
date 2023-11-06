from models.transcript import TranscriptInput, TranscriptResults
from youtube_transcript_api import YouTubeTranscriptApi
import os
from urllib import parse


class Transcript:
    def __init__(self, transcript_input: TranscriptInput):
        self.url = transcript_input.url
        self.start_time = transcript_input.start_time
        self.end_time = transcript_input.end_time
        self.valid_netlocs = ['www.youtube.com', 'youtu.be']
    
    def get_transcript(self):
        url = self.url
        url_parsed = parse.urlparse(url)
        netloc = url_parsed.netloc
        assert netloc in self.valid_netlocs, f'{netloc} is not a valid location. Only YouTube video transcripts can be fetched.'
        
        qsl = parse.parse_qs(url_parsed.query)
        video_code = qsl['v'][0]
        
        srt = YouTubeTranscriptApi.get_transcript(video_code)

        start_time = self.start_time or 0
        end_time = self.end_time or srt[-1]['start']

        if start_time > srt[-1]['start']:
            raise IndexError('Start time is beyond the range of the video')
        if end_time < start_time:
            raise IndexError('Start time must come before end time')

        transcript_timeframe = [segment for segment in srt if end_time > segment['start'] >= start_time]                                    
        transcript = ' '.join([x['text'] for x in transcript_timeframe])
        
        return transcript


async def generate_transcript(transcript_input: TranscriptInput) -> TranscriptResults:
    data = Transcript(transcript_input)
    transcript = data.get_transcript()
    return TranscriptResults(transcript=transcript)