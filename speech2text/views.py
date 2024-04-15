from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube
from openai import OpenAI
import openai
import os
import csv
import tempfile

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def select_audio_type(request):
    return render(request, 'select_audio_type.html')

def create_recording(request):
    return render(request, 'create_recording.html')

def upload_file(request):
    return render(request, 'upload_file.html')

def upload_link(request):
    return render(request, 'upload_link.html')

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
            temp_audio.seek(0)
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
    safety_score = analyze_text_with_chatgpt(transcription.text)
    save_transcription_to_csv(transcription.text, safety_score)
    return transcription.text

def analyze_text_with_chatgpt(text):
    response = openai.Completion.create(
        engine="text-davinci-002",  # or another suitable model like "davinci-codex"
        prompt=generate_prompt(text),
        max_tokens=50
    )
    safety_score = response.choices[0].text.strip()
    return safety_score

def generate_prompt(text):
    return (
        "Please analyze the following text to determine how appropriate it is for a political social media "
        "platform that prohibits hate speech, harassment, bullying, or any form of disruptive or offensive content. "
        "Provide a safety score where 0% indicates completely inappropriate (NSFW) content and 100% indicates "
        "completely appropriate (SFW) content.\n\n"
        f"Text: \"{text}\""
    )

def save_transcription_to_csv(transcription, safety_score):
    directory = "validate"
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, "validate.csv")

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Text', 'isSafe', 'actuallySafe'])

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow({'Text': transcription, 'isSafe': safety_score, 'actuallySafe': ''})
