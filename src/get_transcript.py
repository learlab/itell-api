from supabase.client import Client
from src.database import get_client
import re
from models.transcript import TranscriptInput, TranscriptResults
from youtube_transcript_api import YouTubeTranscriptApi
import os



class Transcript:
    def __init__(self, transcript_input: TranscriptInput, db: Client):
        # TODO: Change to use section slug
        # This process should be the same for all textbooks.
        if transcript_input.textbook_name.name == "THINK_PYTHON":
            section_index = f"{transcript_input.chapter_index:02}"
        elif transcript_input.textbook_name.name in ["MACRO_ECON", "MATHIA"]:
            section_index = (
                f"{transcript_input.chapter_index:02}-{transcript_input.section_index:02}"
            )
        else:
            raise ValueError("Textbook not supported.")

        # Fetch content and restructure data
        self.data = (
            db.table("subsections")
            .select("raw_text", "start_time", "end_time")
            .eq("section_id", section_index)
            .eq("subsection", transcript_input.subsection_index)
            .execute()
            .data
        )[0]
    
    def get_transcript(self):
        timestamps = False
        url = re.findall('https://www.youtube.com.+"', self.data['raw_text'])[0]
        start_time = self.data['start_time']
        end_time = self.data['end_time']
        
        if start_time:
            timestamps=True
        video_code = url.split('/')[-1][-12:-1] 
        try:     
            srt = YouTubeTranscriptApi.get_transcript(video_code)
            if timestamps == False:
                transcript = ' '.join([x['text'] for x in srt])
            else:
                if end_time:
                    transcript_timeframe = [x for x in srt if end_time > x['start'] >= start_time]
                else:    
                    transcript_timeframe = [x for x in srt if x['start'] >= start_time]                                 
                transcript = ' '.join([x['text'] for x in transcript_timeframe])
            
            return transcript
        except:
            return None


async def generate_transcript(transcript_input: TranscriptInput) -> TranscriptResults:
    db = get_client(transcript_input.textbook_name)

    data = Transcript(transcript_input, db)
    transcript = data.get_transcript()

    return TranscriptResults(transcript=transcript)