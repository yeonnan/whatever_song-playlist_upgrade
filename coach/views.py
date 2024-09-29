from django.urls import path
from . import views
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Coach
from .serializers import CoachSerializer
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.conf import settings
import uuid

import os
import subprocess
import librosa
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from spleeter.separator import Separator
import tempfile
import shutil

class CoachPageView(TemplateView):
    template_name = "coach/coach.html"

class InputView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        youtube_url = request.data.get('youtube_url')
        input_file = request.FILES.get('input_file')
        
        if not input_file:
            return Response({"error": "파일을 입력하세요"}, status=status.HTTP_400_BAD_REQUEST)
        
        def download_audio_from_youtube(youtube_url, output_path):
            print("Downloading audio from YouTube...")
            title_command = [
                'yt-dlp',
                '--get-title',
                youtube_url
            ]
            title_result = subprocess.run(title_command, capture_output=True, text=True, check=True)
            title = title_result.stdout.strip()

            audio_command = [
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '--playlist-items', '1',
                '-o', output_path,
                youtube_url
            ]
            subprocess.run(audio_command, check=True)
            return title, output_path

        def separate_vocals(audio_path, output_path):
            print(f"Separating vocals from {audio_path}...")
            separator = Separator('spleeter:2stems')
            separator.separate_to_file(audio_path, output_path)
            vocal_path = os.path.join(output_path, os.path.splitext(os.path.basename(audio_path))[0], 'vocals.wav')
            return vocal_path

        def calculate_highest_dB_freqs(vocal_path):
            print(f"Calculating highest dB frequencies for {vocal_path}...")
            y, sr = librosa.load(vocal_path)
            hop_length = 512
            D = librosa.stft(y, n_fft=1024, hop_length=hop_length)
            magnitude, phase = librosa.magphase(D)
            db_magnitude = librosa.amplitude_to_db(magnitude, ref=np.max)
            freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
            times = librosa.frames_to_time(np.arange(db_magnitude.shape[1]), sr=sr, hop_length=hop_length)

            new_magnitude = np.full_like(db_magnitude, -80)
            for i in range(db_magnitude.shape[1]):
                valid_indices = np.where((freqs >= 82) & (freqs <= 1046.5) & (db_magnitude[:, i] > -80))[0]
                if len(valid_indices) > 0:
                    top_indices = valid_indices[:10] if len(valid_indices) > 10 else valid_indices
                    for idx in top_indices:
                        new_magnitude[idx, i] = db_magnitude[idx, i]

            highest_dB_freqs = []
            time_range = 0.1
            for t in np.arange(0, times[-1], time_range):
                start_idx = np.searchsorted(times, t)
                end_idx = np.searchsorted(times, t + time_range)
                if start_idx < end_idx:
                    max_dB_idx = np.argmax(new_magnitude[:, start_idx:end_idx], axis=None)
                    max_freq_idx = np.unravel_index(max_dB_idx, new_magnitude[:, start_idx:end_idx].shape)
                    if new_magnitude[max_freq_idx[0], start_idx + max_freq_idx[1]] > -80:
                        highest_dB_freqs.append((times[start_idx + max_freq_idx[1]], freqs[max_freq_idx[0]]))

            return highest_dB_freqs

        def classify_vocal_ranges(highest_dB_freqs):
            male_range = (82, 175)  # Male vocal range (approximately E2 to F3)
            female_range = (175, 1046.5)  # Female vocal range (approximately F3 to C6)
            male_count = sum(1 for time, freq in highest_dB_freqs if male_range[0] <= freq <= male_range[1])
            female_count = sum(1 for time, freq in highest_dB_freqs if female_range[0] <= freq <= female_range[1])
            return 'male' if male_count > female_count else 'female'

        def split_freq_ranges(highest_dB_freqs, classification):
            if classification == 'male':
                low_range = (82, 175)  # Low frequency range for male (approximately E2 to F3)
                high_range = (175, 350)  # High frequency range for male (approximately F3 to F4)
            else:
                low_range = (175, 350)  # Low frequency range for female (approximately F3 to F4)
                high_range = (350, 1046.5)  # High frequency range for female (approximately F4 to C6)
            
            low_freqs = [(time, freq) for time, freq in highest_dB_freqs if low_range[0] <= freq <= low_range[1]]
            high_freqs = [(time, freq) for time, freq in highest_dB_freqs if high_range[0] <= freq <= high_range[1]]
            return low_freqs, high_freqs

        def cross_correlation_sync(highest_dB_freqs_youtube, highest_dB_freqs_file):
            print("Performing cross-correlation sync...")
            youtube_times, youtube_freqs = zip(*highest_dB_freqs_youtube)
            file_times, file_freqs = zip(*highest_dB_freqs_file)
            
            youtube_signal = np.interp(np.arange(0, max(youtube_times[-1], file_times[-1]), 0.1), youtube_times, youtube_freqs)
            file_signal = np.interp(np.arange(0, max(youtube_times[-1], file_times[-1]), 0.1), file_times, file_freqs)
            
            correlation = np.correlate(youtube_signal, file_signal, mode='full')
            lag = correlation.argmax() - (len(file_signal) - 1)
            
            return lag * 0.1  # Multiply by the step size to get the lag in seconds

        def save_and_get_graph_path(highest_dB_freqs_youtube, highest_dB_freqs_file, output_path):
            print("Saving highest dB frequencies graph...")
            note_freqs = [82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 130.81, 138.59, 146.83, 155.56, 
                        164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 261.63, 277.18, 293.66, 311.13,
                        329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 523.25, 554.37, 587.33, 622.25,
                        659.25, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, 1046.50]
            note_labels = ['E2', 'F2', 'F#2/Gb2', 'G2', 'G#2/Ab2', 'A2', 'A#2/Bb2', 'B2', 'C3', 'C#3/Db3', 'D3', 'D#3/Eb3',
                        'E3', 'F3', 'F#3/Gb3', 'G3', 'G#3/Ab3', 'A3', 'A#3/Bb3', 'B3', 'C4', 'C#4/Db4', 'D4', 'D#4/Eb4',
                        'E4', 'F4', 'F#4/Gb4', 'G4', 'G#4/Ab4', 'A4', 'A#4/Bb4', 'B4', 'C5', 'C#5/Db5', 'D5', 'D#5/Eb5',
                        'E5', 'F5', 'F#5/Gb5', 'G5', 'G#5/Ab5', 'A5', 'A#5/Bb5', 'B5', 'C6']

            plt.figure(figsize=(12, 8))

            plt.plot([x[0] for x in highest_dB_freqs_youtube], [x[1] for x in highest_dB_freqs_youtube], drawstyle='steps-post', linewidth=1, label='YouTube', color='white')
            plt.plot([x[0] for x in highest_dB_freqs_file], [x[1] for x in highest_dB_freqs_file], drawstyle='steps-post', linewidth=1, label='File', color='orange')

            plt.title('Highest dB Frequencies Over Time')
            plt.xlabel('Time (s)')
            plt.ylabel('Frequency (Hz)')
            plt.legend()

            ax = plt.gca()
            ax.set_yticks(note_freqs)
            ax.set_yticklabels(note_labels)
            ax.set_yscale('linear')  # Use linear scale for evenly spaced labels
            ax.set_ylim([82.41, 1046.50])

            def format_time(x, pos):
                minutes = int(x // 60)
                seconds = int(x % 60)
                return f'{minutes}:{seconds:02}' if minutes > 0 else f'{seconds}'

            ax.xaxis.set_major_locator(plt.MultipleLocator(10))
            ax.xaxis.set_major_formatter(plt.FuncFormatter(format_time))

            # 배경색 제거
            ax.set_facecolor('none')

            graph_id = str(uuid.uuid4())
            graph_path = os.path.join(output_path, f'{graph_id}.png')
            plt.savefig(graph_path, transparent=True)

            return graph_path


        def calculate_similarity(freqs1, freqs2):
            times1, frequencies1 = zip(*freqs1)
            times2, frequencies2 = zip(*freqs2)

            signal1 = np.interp(np.arange(0, max(times1[-1], times2[-1]), 0.1), times1, frequencies1)
            signal2 = np.interp(np.arange(0, max(times1[-1], times2[-1]), 0.1), times2, frequencies2)

            correlation = np.correlate(signal1, signal2, mode='full')
            return correlation.max()

        def main(youtube_url, input_file):
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)

            # YouTube 오디오 다운로드
            audio_path_youtube = os.path.join(output_dir, f'{uuid.uuid4()}_audio.mp3')
            title, _ = download_audio_from_youtube(youtube_url, audio_path_youtube)

            # 보컬 추출
            vocal_output_path_youtube = os.path.join(output_dir, 'vocals_youtube')
            os.makedirs(vocal_output_path_youtube, exist_ok=True)
            vocal_path_youtube = separate_vocals(audio_path_youtube, vocal_output_path_youtube)

            # 보컬 파일이 존재하는지 확인
            if not os.path.exists(vocal_path_youtube):
                print(f"Error: Vocal file not found at {vocal_path_youtube}")
                return

            # 임시 파일에 저장 후 보컬 추출
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in input_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            vocal_output_path_file = os.path.join(output_dir, 'vocals_file')
            os.makedirs(vocal_output_path_file, exist_ok=True)
            vocal_path_file = separate_vocals(temp_file_path, vocal_output_path_file)

            # 보컬 파일이 존재하는지 확인
            if not os.path.exists(vocal_path_file):
                print(f"Error: Vocal file not found at {vocal_path_file}")
                return

            # 최고 dB 주파수 계산
            highest_dB_freqs_youtube = calculate_highest_dB_freqs(vocal_path_youtube)
            highest_dB_freqs_file = calculate_highest_dB_freqs(vocal_path_file)

            # 성별 분류
            classification = classify_vocal_ranges(highest_dB_freqs_youtube)
            print(f"Detected vocal range is classified as: {classification}")

            # 주파수 범위 나누기
            low_freqs_youtube, high_freqs_youtube = split_freq_ranges(highest_dB_freqs_youtube, classification)
            low_freqs_file, high_freqs_file = split_freq_ranges(highest_dB_freqs_file, classification)

            # 크로스 코릴레이션을 통해 싱크 맞춤
            lag = cross_correlation_sync(highest_dB_freqs_youtube, highest_dB_freqs_file)

            if lag > 0:
                highest_dB_freqs_youtube = [(time + lag, freq) for time, freq in highest_dB_freqs_youtube]
            else:
                highest_dB_freqs_file = [(time - lag, freq) for time, freq in highest_dB_freqs_file]

            # 전체 주파수 유사도 계산
            full_similarity = calculate_similarity(highest_dB_freqs_youtube, highest_dB_freqs_file)

            # 저음역대 유사도 계산
            low_similarity = calculate_similarity(low_freqs_youtube, low_freqs_file)

            # 고음역대 유사도 계산
            high_similarity = calculate_similarity(high_freqs_youtube, high_freqs_file)

            # 그래프 저장 및 경로 반환
            graph_output_path = os.path.join(settings.MEDIA_ROOT, 'graph')
            os.makedirs(graph_output_path, exist_ok=True)
            graph_path = save_and_get_graph_path(highest_dB_freqs_youtube, highest_dB_freqs_file, graph_output_path)

            graph_rel_path = os.path.relpath(graph_path, settings.MEDIA_ROOT)

            print(f"All files saved in directory: {output_dir}")
            print(f"Vocal file (YouTube): {vocal_path_youtube}")
            print(f"Vocal file (File): {vocal_path_file}")
            print(f"Graph file: {graph_rel_path}")
            print(f"Full range similarity: {full_similarity}")
            print(f"Low range similarity: {low_similarity}")
            print(f"High range similarity: {high_similarity}")

            # 임시 파일 및 생성된 파일 삭제
            try:
                os.remove(audio_path_youtube)
                os.remove(temp_file_path)
                shutil.rmtree(vocal_output_path_youtube)
                shutil.rmtree(vocal_output_path_file)
            except Exception as e:
                print(f"Error deleting files: {e}")

            return title, graph_rel_path, high_similarity, low_similarity, full_similarity

        title, graph, high_pitch_score, low_pitch_score, pitch_score = main(youtube_url, input_file)

        coach = Coach.objects.create(
            user=user,
            youtube_title = title,
            high_pitch_score = high_pitch_score,
            low_pitch_score = low_pitch_score,
            pitch_score = pitch_score,
            message = '메세지 로직을 추가해주세요',
            graph = graph
        )
        
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ResultPageView(TemplateView):
    template_name = "coach/coach_result.html"

class ResultView(APIView):
    def get(self, request, pk):
        coach = get_object_or_404(Coach, pk=pk)
        serializer = CoachSerializer(coach)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCoachedVocalView(APIView):
    def get(self, request):
        user_coached_vocals = Coach.objects.filter(user=request.user)
        serializer = CoachSerializer(user_coached_vocals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

