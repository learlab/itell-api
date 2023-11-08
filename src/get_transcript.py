from models.transcript import TranscriptInput, TranscriptResults
from youtube_transcript_api import YouTubeTranscriptApi
from fastapi import HTTPException
from urllib import parse


async def generate_transcript(transcript_input: TranscriptInput) -> TranscriptResults:
    url_parsed = parse.urlparse(transcript_input.url)
    qsl = parse.parse_qs(url_parsed.query)
    video_code = qsl["v"][0]

    srt = YouTubeTranscriptApi.get_transcript(video_code)

    start_time = transcript_input.start_time or 0
    end_time = transcript_input.end_time or srt[-1]["start"]

    if start_time > srt[-1]["start"]:
        raise HTTPException(
            status_code=400, detail="Start time is beyond the range of the video"
        )
    if end_time < start_time:
        raise HTTPException(
            status_code=400, detail="Start time must come before end time"
        )

    transcript_timeframe = [
        segment for segment in srt if end_time > segment["start"] >= start_time
    ]

    transcript = " ".join([x["text"] for x in transcript_timeframe])

    return TranscriptResults(transcript=transcript)
