import os
import boto3
import requests
import openai
import uuid
from pytube import YouTube

def summarize_transcript(transcript):
	response = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": "You are a knowledge curator helping users to understand the contents of video transcripts."},
			{"role": "user", "content": f"Please summarize the following transcript: '{transcript}'"}
		]
	)
	return response['choices'][0]['message']['content'].strip()

def download_audio(video_id):
	yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
	return yt.streams.get_audio_only().download(filename=video_id)

def transcribe_audio(s3, bucket, file_name):
	transcribe = boto3.client('transcribe')
	job_name = f"TranscriptionJob-{uuid.uuid4()}"
	transcribe.start_transcription_job(
		TranscriptionJobName=job_name,
		Media={'MediaFileUri': f"s3://{bucket}/{file_name}"},
		MediaFormat='mp4',
		LanguageCode='en-US'
	)

	while True:
		status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
		if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
			break

	return status['TranscriptionJob']['Transcript']['TranscriptFileUri'] if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED' else None

def synthesize_speech(s3, bucket, transcript_uri):
	transcript_data = requests.get(transcript_uri).json()
	transcript = ' '.join(item['alternatives'][0]['content'] for item in transcript_data['results']['items'] if item['type'] == 'pronunciation')

	summary = summarize_transcript(transcript)
	summary_file_name = f"summary_{uuid.uuid4()}.txt" 
	s3.put_object(Body=summary, Bucket=bucket, Key=summary_file_name)

	polly = boto3.client('polly')
	response = polly.synthesize_speech(OutputFormat='mp3', Text=summary, VoiceId='Matthew', Engine='neural')

	mp3_file_name = f"speech_{uuid.uuid4()}.mp3"
	with open(mp3_file_name, 'wb') as f:
		f.write(response['AudioStream'].read())

	return mp3_file_name
	
def delete_all_objects(bucket_name):
	s3 = boto3.resource('s3')
	bucket = s3.Bucket(bucket_name)
	bucket.objects.all().delete()

def main():
	video_id = 'U3PiD-g7XJM' #change to any other Video ID from YouTube
	
	bucket = f"bucket-{uuid.uuid4()}"
	file_name = f"{video_id}.mp4"

	openai.api_key = os.getenv('OPENAI_API_KEY')

	s3 = boto3.client('s3')
	s3.create_bucket(Bucket=bucket)

	print ("Downloading audio stream from youtube video...")
	audio_file = download_audio(video_id)
	print ("Uploading video to S3 bucket...")
	s3.upload_file(audio_file, bucket, file_name)
	print("Transcribing audio...")
	transcript_uri = transcribe_audio(s3, bucket, file_name)
	print("Synthesizing speech...")
	mp3_file_name = synthesize_speech(s3, bucket, transcript_uri)
	print(f"Audio summary saved in: {mp3_file_name}\n")

	delete_all_objects(bucket)
	s3.delete_bucket(Bucket=bucket)

if __name__ == "__main__":
    main()
