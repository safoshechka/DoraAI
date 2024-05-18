from pytube import YouTube
from pydub import AudioSegment
import os
import json
from datetime import datetime
import assemblyai as aai
import glob
import logging
import json

logger = logging.getLogger("__main__" + __name__)
aai.settings.api_key = "22c2c4d729ed4281bce0808eb96ea93e"


class VideoParser:
    def __init__(self, config):
        self.config = config
        self.path = self.config['video_parser_path']
        self.source_dir = self.config['source_dir']
        self.urls_file = self.config['urls_file']
        self.chars_limit = self.config['chars_limit']
        self.cnt = -1

        with open(self.urls_file, 'r') as f:
            self.urls = json.load(f)

        self.process_videos()

    def get_audio_from_youtube(self, cnt, url):
        try:
            youtube = YouTube(url)
            video_exists = True
        except Exception as e:
            video_exists = False

        if video_exists:
            video = youtube.streams.get_by_itag(251).download(
                output_path=f"{self.path}/audio/", filename=f"{cnt}.opus"
            )

            os.system(f'ffmpeg -i "{self.path}/audio/{cnt}.opus" -vn "{self.path}/audio/out_{cnt}.wav"')

            audio = AudioSegment.from_wav(f"{self.path}/audio/out_{cnt}.wav")
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio.export(f"{self.path}/audio/out_{cnt}_mono.wav", format="wav")

            return f'{self.path}/audio/out_{cnt}_mono.wav'
        else:
            return video_exists

    def transcribe_audio(self, file):
        config = aai.TranscriptionConfig(language_code="ru")
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(file)
        
        if transcript.status == aai.TranscriptStatus.error:
            logger.error(transcript.error)
        else:
            return transcript.text

    def process_videos(self):
        already_processed_audios = glob.glob(f'{self.path}/audio/out_*_mono.wav')
        already_processed_texts = glob.glob(f'{self.source_dir}/*_0.txt')

        for url in self.urls:
            self.add_video(url)

    def add_video(self, url):
        self.cnt += 1
        already_processed_texts = glob.glob(f'{self.source_dir}/*_0.txt')
        t1 = datetime.now()
        logger.info(f'{self.cnt}: {url}:    Starting...')

        video_exists = True

        if f'{self.source_dir}/{self.cnt}_0.txt' in already_processed_texts:
            logger.info(f'{self.cnt}: {url}:    Already processed!')

        else:
            audio_file = self.get_audio_from_youtube(self.cnt, url)
            if audio_file:
                logger.info(f'{self.cnt}: {url}:    Got audio')
                text = self.transcribe_audio(audio_file)
                logger.info(f'{self.cnt}: {url}:    Got text')

                fcnt = 0
                while len(text) > self.chars_limit:
                    with open(f"{self.source_dir}/{self.cnt}_{fcnt}.txt", 'w') as fl:
                        fl.write(f'{url}\n')
                        fl.write(text[: self.chars_limit])
                    text = text[self.chars_limit:]
                    fcnt += 1

                if text != '':
                    with open(f"{self.source_dir}/{self.cnt}_{fcnt}.txt", 'w') as fl:
                        fl.write(f'{url}\n')
                        fl.write(text[: self.chars_limit])

                self.urls.append(url)
                with open(self.urls_file, 'w') as f:
                    json.dump(self.urls, f)
                logger.info(f'{self.cnt}: {url}:    Added to urls file')

            else:
                video_exists = False

        if video_exists:
            logger.info(f'{self.cnt}: {url}:    Done!')
            logger.info(f'{self.cnt}: {url}:    Time taken: {datetime.now() - t1}\n')
        else:
            logger.info(f"{self.cnt}: {url}:    Video doesn't exist!")
            self.cnt -= 1

        return video_exists

