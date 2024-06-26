import cv2
import time
import os
import pyaudio
import wave
import threading
import numpy as np
import ctypes
from datetime import datetime
import moviepy.editor as mp

# Fonction pour obtenir la résolution de l'écran
def get_screen_resolution():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Initialisation de la capture vidéo
cap = cv2.VideoCapture(0)  # 0 pour la webcam par défaut

# Variables pour gérer l'enregistrement
is_recording = False
is_countdown = False
start_time = None
last_movement_time = None
record_duration = 7 * 60  # Durée d'enregistrement en secondes (ici 7 minutes)
countdown_duration = 20  # Durée du compte à rebours en secondes
no_movement_threshold = 5  # Seuil sans mouvement pendant l'enregistrement en secondes
pause_after_recording = 10  # Pause après l'enregistrement avant de relancer la détection de mouvement
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = None

# Obtenir la résolution de l'écran
screen_width, screen_height = get_screen_resolution()

# Définir la taille de la vidéo capturée en fonction de la résolution de l'écran
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
if frame_width > screen_width or frame_height > screen_height:
    scale_factor = min(screen_width / frame_width, screen_height / frame_height)
    scaled_width = int(frame_width * scale_factor)
    scaled_height = int(frame_height * scale_factor)
else:
    scaled_width = frame_width
    scaled_height = frame_height

# Chemin de sauvegarde basé sur l'emplacement du script
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, "Enregistrement")

# Assurez-vous que le répertoire de sauvegarde existe
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Paramètres audio
audio_format = pyaudio.paInt16
channels = 1  # Utilisation d'un seul canal audio
rate = 44100
frames_per_buffer = 1024
audio_frames = []

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=frames_per_buffer)
    global audio_frames
    audio_frames = []

    while is_recording:
        data = stream.read(frames_per_buffer)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

def save_audio(audio_filename):
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(audio_frames))
    wf.close()

def merge_audio_video(audio_filename, video_filename, output_filename):
    video_clip = mp.VideoFileClip(video_filename)
    audio_clip = mp.AudioFileClip(audio_filename)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_filename, codec='libx264')

# Fonction pour détecter le mouvement dans une frame
def detect_movement(frame1, frame2):
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    movement_detected = any(cv2.contourArea(contour) > 500 for contour in contours)
    return movement_detected

# Lecture de la première image
ret, frame1 = cap.read()
ret, frame2 = cap.read()
movement_detected_time = None
pause_start_time = None

# Fonction pour afficher le compteur en plein écran
def display_fullscreen_counter(countdown):
    overlay = np.full_like(frame1, (0, 0, 255), dtype=np.uint8)  # Fond rouge
    alpha = 0.6
    text = f"{countdown}"
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 3, 6)
    text_x = int((frame1.shape[1] - text_size[0]) / 2)
    text_y = int((frame1.shape[0] + text_size[1]) / 2)
    cv2.putText(overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (50, 50, 255), 6, cv2.LINE_AA)
    frame_with_overlay = cv2.addWeighted(overlay, alpha, frame1, 1 - alpha, 0)
    cv2.imshow("feed", frame_with_overlay)

def draw_blinking_dot(frame, elapsed_time):
    alpha = 0.5 + 0.5 * np.sin(elapsed_time * np.pi)  # Varie de 0 à 1
    overlay = frame.copy()
    cv2.circle(overlay, (50, 50), 20, (0, 0, 255), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

while cap.isOpened():
    # Lecture des frames
    frame1 = frame2
    ret, frame2 = cap.read()

    if not ret:
        break

    # Gestion de la pause après enregistrement
    if pause_start_time:
        if time.time() - pause_start_time >= pause_after_recording:
            pause_start_time = None
        else:
            cv2.putText(frame1, "Pause...", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("feed", frame1)
            if cv2.waitKey(40) == 27:
                break
            continue

    # Détection de mouvement
    movement_detected = detect_movement(frame1, frame2)
    current_time = time.time()

    if movement_detected:
        last_movement_time = current_time
        if not is_recording and not is_countdown:
            movement_detected_time = current_time
            is_countdown = True

    if is_countdown:
        elapsed_time_since_movement = current_time - movement_detected_time
        countdown = countdown_duration - int(elapsed_time_since_movement)
        display_fullscreen_counter(countdown)

        if countdown <= 0:
            is_countdown = False
            is_recording = True
            start_time = current_time
            timestamp = datetime.now().strftime('%d%m%Y-%H%M')
            output_file = os.path.join(save_path, f'output_{int(start_time)}.avi')
            audio_file = os.path.join(save_path, f'output_{int(start_time)}.wav')
            final_output_file = os.path.join(save_path, f'CONFESS{timestamp}.mp4')
            out = cv2.VideoWriter(output_file, fourcc, 20.0, (scaled_width, scaled_height))
            audio_thread = threading.Thread(target=record_audio)
            audio_thread.start()
            print(f"Enregistrement démarré : {output_file}")

    # Si l'enregistrement est en cours, écrire la frame
    if is_recording:
        frame_display = frame1.copy()
        draw_blinking_dot(frame_display, current_time - start_time)
        out.write(frame1)
        cv2.imshow("feed", frame_display)

        # Vérifier si aucun mouvement n'a été détecté pendant 5 secondes
        if current_time - last_movement_time > no_movement_threshold:
            is_recording = False
            out.release()
            out = None
            save_audio(audio_file)
            merge_audio_video(audio_file, output_file, final_output_file)
            os.remove(audio_file)
            os.remove(output_file)
            print(f"Enregistrement terminé et fusionné : {final_output_file}")
            last_movement_time = None
            pause_start_time = current_time

    elif not is_countdown:
        # En attente de mouvement
        cv2.putText(frame1, "En attente de mouvements", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("feed", frame1)

    # Gestion de la sortie de la boucle avec la touche 'Échap'
    if cv2.waitKey(40) == 27:
        break

# Libérer les ressources
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
