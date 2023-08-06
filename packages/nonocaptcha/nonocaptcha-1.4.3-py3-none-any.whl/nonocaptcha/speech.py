#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Text-to-speech modules"""

import aiobotocore
import aiofiles
import asyncio
import json
import os
import re
import struct
import time
import websockets
import tempfile

from io import StringIO, BytesIO
from datetime import datetime
from uuid import uuid4
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

from config import settings
from nonocaptcha import util


class Sphinx(object):
    MODEL_DIR = settings['speech_api']['sphinx']["model_dir"]
    
    @util.threaded
    def mp3_to_wav(self, mp3_filename):
        wav_filename = mp3_filename.replace(".mp3", ".wav")
        segment = AudioSegment.from_mp3(mp3_filename)
        sound = segment.set_channels(1).set_frame_rate(16000)
        sound.export(wav_filename, format="wav")
        return wav_filename
    
    @util.threaded
    def build_decoder(self):
        config = Decoder.default_config()
        config.set_string(
            "-dict", os.path.join(self.MODEL_DIR, "cmudict-en-us.dict")
        )
        config.set_string(
            "-fdict", os.path.join(self.MODEL_DIR, "en-us/noisedict")
        )
        config.set_string(
            "-featparams", os.path.join(self.MODEL_DIR, "en-us/feat.params")
        )
        config.set_string(
            "-tmat", os.path.join(self.MODEL_DIR, "en-us/transition_matrices")
        )
        config.set_string(
            "-hmm", os.path.join(self.MODEL_DIR, "en-us")
        )
        config.set_string(
            "-lm", os.path.join(self.MODEL_DIR, "en-us.lm.bin")
        )
        config.set_string(
            "-mdef", os.path.join(self.MODEL_DIR, "en-us/mdef")
        )
        config.set_string(
            "-mean", os.path.join(self.MODEL_DIR, "en-us/means")
        )
        config.set_string("-sendump", os.path.join(
            self.MODEL_DIR, "en-us/sendump")
        )
        config.set_string(
            "-var", os.path.join(self.MODEL_DIR, "en-us/variances")
        )
        config.set_string('-logfn', '/dev/null')
        return Decoder(config)
    
    async def get_text(self, mp3_filename):
        decoder = await self.build_decoder()
        decoder.start_utt()
        wav_filename = await self.mp3_to_wav(mp3_filename)
        async with aiofiles.open(wav_filename, 'rb') as stream:
            while True:
              buf = await stream.read(1024)
              if buf:
                decoder.process_raw(buf, False, False)
              else:
                break
        decoder.end_utt()
        hyp = ' '.join([seg.word for seg in decoder.seg()])
        answer = re.sub('<[^<]+?>|\[[^<]+?\]|\([^<]+?\)', '', hyp).strip()
        return answer


class Amazon(object):
    ACCESS_KEY_ID = settings['speech_api']['amazon']['key_id']
    SECRET_ACCESS_KEY = settings['speech_api']['amazon']['secret_access_key']
    REGION_NAME = settings['speech_api']['amazon']['region']
    S3_BUCKET = settings['speech_api']['amazon']['s3_bucket']

    async def get_text(self, audio_data):
        session = aiobotocore.get_session()
        upload = session.create_client(
            's3',
            region_name=self.REGION_NAME,
            aws_secret_access_key=self.SECRET_ACCESS_KEY,
            aws_access_key_id=self.ACCESS_KEY_ID
        )                          
        transcribe = session.create_client(
            'transcribe', 
            region_name=self.REGION_NAME,
            aws_secret_access_key=self.SECRET_ACCESS_KEY,
            aws_access_key_id=self.ACCESS_KEY_ID
        )
        filename = f"{uuid4().hex}.mp3"
        # Upload audio file to bucket
        await upload.put_object(Bucket=self.S3_BUCKET,
                                Key=filename,
                                Body=audio_data)
        job_name = uuid4().hex
        job_uri = (
            f"https://s3.{self.REGION_NAME}.amazonaws.com/{self.S3_BUCKET}/"
            f"{filename}"
        )
        # Send audio file URI to Transcribe
        resp = await transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp3',
            LanguageCode='en-US'
        )
        # Wait 90 seconds for transcription
        timeout = 90
        while time.time() > timeout:
            status = await transcribe.get_transcription_job(
                TranscriptionJobName=job_name
            )
            if(
                status['TranscriptionJob']['TranscriptionJobStatus'] in
                ['COMPLETED', 'FAILED']
            ):
                break
            await asyncio.sleep(5)
        # Delete audio file from bucket
        await upload.delete_object(Bucket=self.S3_BUCKET, Key=filename)
        if 'TranscriptFileUri' in status['TranscriptionJob']['Transcript']:
            transcript_uri = (
                status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            )
            data = json.loads(await util.get_page(transcript_uri))
            transcript = data['results']['transcripts'][0]['transcript']
            return transcript

        # Delete audio file
        await upload.delete_object(Bucket=self.S3_BUCKET, Key=filename)
        
        # Close clients
        await upload._endpoint._aio_session.close()
        await transcribe._endpoint._aio_session.close()


class Azure(object):
    SUB_KEY = settings['speech_api']['azure']["api_subkey"]

    @util.threaded
    def mp3_to_wav(self, mp3_filename):
        wav_filename = mp3_filename.replace(".mp3", ".wav")
        sound = AudioSegment.from_mp3(mp3_filename)
        wav = sound.export(wav_filename, format="wav")
        return wav_filename

    @util.threaded
    def extract_json_body(self, response):
        pattern = "^\r\n"  # header separator is an empty line
        m = re.search(pattern, response, re.M)
        return json.loads(
            response[m.end():]
        )  # assuming that content type is json

    @util.threaded
    def build_message(self, req_id, payload):
        message = b""
        timestamp = datetime.utcnow().isoformat()
        header = (
            f"X-RequestId: {req_id}\r\nX-Timestamp: {timestamp}Z\r\n"
            f"Path: audio\r\nContent-Type: audio/x-wav\r\n\r\n"
        )
        message += struct.pack(">H", len(header))
        message += header.encode()
        message += payload
        return message

    async def bytes_from_file(self, filename, chunksize=8192):
        async with aiofiles.open(filename, "rb") as f:
            while True:
                chunk = await f.read(chunksize)
                if chunk:
                    yield chunk
                else:
                    break

    async def send_file(self, websocket, filename):
        req_id = uuid4().hex
        async for payload in self.bytes_from_file(filename):
            message = await self.build_message(req_id, payload)
            await websocket.send(message)

    async def get_text(self, mp3_filename):
        wav_filename = await self.mp3_to_wav(mp3_filename)
        conn_id = uuid4().hex
        url = (
            f"wss://speech.platform.bing.com/speech/recognition/dictation/cogn"
            f"itiveservices/v1?language=en-US&Ocp-Apim-Subscription-Key="
            f"{self.SUB_KEY}&X-ConnectionId={conn_id}&format=detailed"
        )
        async with websockets.connect(url) as websocket:
            await self.send_file(websocket, wav_filename)
            timeout = time.time() + 15
            while time.time() < timeout:
                response = await websocket.recv()
                content = await self.extract_json_body(response)
                if (
                    "RecognitionStatus" in content
                    and content["RecognitionStatus"] == "Success"
                ):
                    answer = content["NBest"][0]["Lexical"]
                    return answer
                if (
                    "RecognitionStatus" in content
                    and content["RecognitionStatus"] == "EndOfDictation"
                ):
                    return
                await asyncio.sleep(1)
