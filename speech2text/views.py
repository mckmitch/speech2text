from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube
from openai import OpenAI
import os
import csv
import tempfile

def select_audio_type(request):
    return render(request, 'select_audio_type.html')

def create_recording(request):
    # Logic for handling recording creation
    return render(request, 'create_recording.html')

def upload_file(request):
    # Logic for handling file uploads
    return render(request, 'upload_file.html')

def upload_link(request):
    # Logic for handling link submissions
    return render(request, 'upload_link.html')




# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@csrf_exempt
def transcribe_audio(request):
    if request.method == "POST":
        youtube_link = request.POST.get('youtube_link', '')
        audio_file = request.FILES.get('audio_file')

        if youtube_link:
            return handle_youtube_link(youtube_link)
        elif audio_file:
            return handle_audio_file(audio_file)
        else:
            return HttpResponse("No audio file or YouTube link provided.")
    else:
        return render(request, 'transcribe_form.html')

def handle_youtube_link(youtube_link):
    try:
        yt = YouTube(youtube_link)
        audio_stream = yt.streams.filter(only_audio=True).first()
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.mp4', delete=True) as temp_audio:
            audio_stream.stream_to_buffer(temp_audio)
            temp_audio.seek(0)  # Rewind to the beginning of the file
            transcription = transcribe_audio_file(temp_audio)
        return HttpResponse(transcription)
    except Exception as e:
        return HttpResponse(f"An error occurred processing the YouTube link: {str(e)}")

def handle_audio_file(audio_file):
    try:
        transcription = transcribe_audio_file(audio_file)
        return HttpResponse(transcription)
    except Exception as e:
        return HttpResponse(f"An error occurred processing the audio file: {str(e)}")

def transcribe_audio_file(audio_file):
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=(audio_file.name, audio_file.read(), 'audio/mp4')
    )
    save_transcription_to_csv(transcription.text)
    return transcription.text

def save_transcription_to_csv(transcription):
    directory = "validate"
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, "validate.csv")

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Text', 'isSafe', 'actuallySafe'])

        if file.tell() == 0:  # File is empty, write header
            writer.writeheader()

        writer.writerow({'Text': transcription, 'isSafe': '', 'actuallySafe': ''})