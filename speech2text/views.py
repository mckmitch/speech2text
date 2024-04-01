from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI
import os, csv

# Load the environment variables from the .env file
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@csrf_exempt  # Temporarily disable CSRF protection for simplicity
def transcribe_audio(request):
    if request.method == "POST":
        audio_file = request.FILES.get('audio_file')
        if audio_file:
            # Read the uploaded file's content into bytes
            audio_bytes = audio_file.read()
            # Get the content type (MIME type) of the uploaded file
            content_type = audio_file.content_type
            try:
                # Use the file tuple (filename, file_bytes, content_type) for transcription
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(audio_file.name, audio_bytes, content_type)
                )
                save_transcription_to_csv(transcription.text)
                return HttpResponse(transcription.text)
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}")
        else:
            return HttpResponse("No audio file provided.")
    else:
        # For GET requests, render an HTML form for file upload
        return render(request, 'transcribe_form.html')


# Also Creates a new CSV file if it doesn't exist - for quick recreation of csv
def save_transcription_to_csv(transcription):
    # Define directory and file paths
    directory = "validate"
    if not os.path.exists(directory):
        os.makedirs(directory)
    csv_file_path = os.path.join(directory, "validate.csv")

    # Define column labels
    fieldnames = ['Text', 'isSafe', 'actuallySafe']

    # Check if the file exists
    file_exists = os.path.isfile(csv_file_path)

    # Write transcription to CSV
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header if the file is newly created
        if not file_exists:
            writer.writeheader()

        # Write transcription to CSV
        writer.writerow({'Text': transcription, 'isSafe': '', 'actuallySafe': ''})