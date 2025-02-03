import os
import sys
import signal
from edge_impulse_linux.audio import AudioImpulseRunner

def signal_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

runner = None
signal.signal(signal.SIGINT, signal_handler)
audio_device_id = 2

modelfile = "model/detect-clap-v1.eim"
runner = AudioImpulseRunner(modelfile)
try:
    model_info = runner.init()
    labels = model_info['model_parameters']['labels']
    print(f"Model {modelfile} successfully loaded!")
except Exception as e:
    print(f"Error Occured Aborting")
    print(f"Error: {e}")
    quit()

while True:
    for response, audio in runner.classifier(device_id=audio_device_id):
        print(response) 
