from edge_impulse_linux.audio import AudioImpulseRunner

modelfile = "model/detect-clap-v1.eim"

# runner = AudioImpulseRunner(modelfile)
with AudioImpulseRunner(modelfile) as runner:
    try:
        model_info = runner.init()
        print(f"Model {modelfile} successfully loaded!")
        # model_info = runner.init(debug=True) # to get debug print out
        labels = model_info['model_parameters']['labels']
        
        audio_device_id = 0
        
        for response, audio in runner.classifier(device_id=audio_device_id):
            score = response['result']['classification']['clap']
            if score > 0.75:
                print(f"Clapped!")
            
    
    except Exception as e:
        print(f"Error Occured Aborting")
        print(f"Error: {e}")
        quit()
    
    finally:
        if (runner):
            runner.stop()

    
    
