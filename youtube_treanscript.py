from youtube_transcript_api import YouTubeTranscriptApi

def format_time(seconds):
    """
    초 단위의 시간을 HH:MM:SS 형식의 문자열로 변환합니다.

    Args:
        seconds (float): 초 단위의 시간.

    Returns:
        str: HH:MM:SS 형식의 문자열.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def save_transcript(video_id, languages, include_timecode=False):
    """
    YouTube 동영상의 자막을 가져와 텍스트 파일로 저장합니다.

    Args:
        video_id (str): YouTube 동영상 ID.
        languages (list): 자막을 가져올 언어 목록.
        include_timecode (bool): 출력 파일에 시간 코드를 포함할지 여부.
    """
    try:
        # 자막 가져오기
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)

        # 출력 파일 이름 결정
        suffix = "_with_timecode" if include_timecode else ""
        output_file = f"{video_id}_subtitle{suffix}.txt"

        # 자막을 파일에 저장
        with open(output_file, "w", encoding="utf-8") as file:
            for entry in transcript:
                text = entry['text']
                if include_timecode:
                    start_time = format_time(entry['start'])
                    file.write(f"[{start_time}] {text}\n")
                else:
                    file.write(f"{text}\n")

        print(f"자막이 성공적으로 {output_file}에 저장되었습니다.")

    except Exception as e:
        print(f"자막을 가져오거나 저장하는 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    # YouTube 동영상 ID
    video_id = "zduSFxRajkE"

    # 사용할 언어
    LANGUAGES = ['en']

    # 시간 코드 없이 자막 저장
    save_transcript(video_id, LANGUAGES, include_timecode=False)

    # 시간 코드를 포함하여 자막 저장
    save_transcript(video_id, LANGUAGES, include_timecode=True)