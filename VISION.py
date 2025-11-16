import pytesseract
import RPi.GPIO as GPIO
from pygame import mixer
from picamera import PiCamera
from PIL import Image
import time
from gtts import gTTS
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array, resize
from tensorflow.keras.models import load_model


LETSGO_AUDIO_PATH = "/home/ratneshp/Desktop/letsgo.mp3"
STOP_AUDIO_PATH = "/home/ratneshp/Desktop/stop.mp3"
CAPTURED_IMAGE_PATH = "/home/ratneshp/Desktop/image.jpg"

SENSOR_PIN_1 = 8
SENSOR_PIN_2 = 3
VIBRATOR_PIN = 37
model = load_model('home/ratneshp/Desktop/ssd_model.h5')

def read_text_from_image(image):

text = pytesseract.image_to_string(image)
    return text

def play_audio(file_path):

mixer.init()
    mixer.music.load(file_path)
    mixer.music.play()


camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    time.sleep(2)
    camera.capture(CAPTURED_IMAGE_PATH)
    camera.stop_preview()
    camera.close()
    return Image.open(CAPTURED_IMAGE_PATH)

def vibrate(duration):
GPIO.output(VIBRATOR_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(VIBRATOR_PIN, GPIO.LOW)

def detect_objects(input_image_path):
img = load_img(input_image_path, target_size=(300, 300))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
predictions = model.predict(img_array)
    
class_names = ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair','cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
    
    detected_objects = []
    for prediction in predictions:
        class_id = np.argmax(prediction[5:])
        confidence = prediction[2]
        
        if confidence > 0.5:
            detected_objects.append((class_names[class_id], confidence))
    return detected_objects
def main():
    
GPIO.setmode(GPIO.BOARD)
    GPIO.setup(SENSOR_PIN_1, GPIO.IN)
    GPIO.setup(SENSOR_PIN_2, GPIO.IN)
    GPIO.setup(VIBRATOR_PIN, GPIO.OUT)

    is_playing_letsgo = False
is_playing_stop = False
while True:
        val = GPIO.input(SENSOR_PIN_1)
        val2 = GPIO.input(SENSOR_PIN_2)

        if val == 1 and val2 == 1 and not is_playing_letsgo:
            print("GO!")
            play_audio(LETSGO_AUDIO_PATH)
            is_playing_letsgo = True
elif (val != 1 or val2 != 1) and is_playing_letsgo:
            print("stop")
            play_audio(STOP_AUDIO_PATH)
            vibrate(2)  # Vibrate for 2 seconds
is_playing_letsgo = False
is_playing_stop = True
elif val == 1 and val2 == 1 and is_playing_stop:
            print("Capturing image...")
            captured_image = capture_image()
            print("Image captured.")

detected_objects = detect_objects(CAPTURED_IMAGE_PATH)

ocr_text = read_text_from_image(CAPTURED_IMAGE_PATH)
            if ocr_text.strip() != "":
                print("OCR Text:", ocr_text)
                tts = gTTS(text=ocr_text, lang='en')
                tts.save("ocr_text.mp3")
                play_audio("ocr_text.mp3")
            else:
                print("No text detected in the image.")

for object_name, confidence in detected_objects:
                print(f"Detected {object_name} with {confidence*100}% confidence.")
                tts = gTTS(text=f"I see a {object_name}.", lang='en')
                tts.save("detected_object.mp3")
                play_audio("detected_object.mp3")

            is_playing_stop = False
time.sleep(0.01)

if _name_ == "_main_":
    main()