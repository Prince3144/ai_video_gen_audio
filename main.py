
from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import subprocess
import io
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Get optional parameters with better defaults
        voice_type = data.get("voice", "female")  # male or female
        pitch = data.get("pitch", 50)
        speed = data.get("speed", 160)  # Slightly slower for more natural speech
        volume = data.get("volume", 100)
        gap = data.get("gap", 10)  # Gap between words for smoother speech

        # Create a temporary filename
        filename = "temp_speech.wav"
        
        # Configure voice based on gender
        if voice_type.lower() == "male":
            voice_name = "en+m3"  # Male voice variant
            pitch = data.get("pitch", 40)  # Lower pitch for male
        else:
            voice_name = "en+f3"  # Female voice variant  
            pitch = data.get("pitch", 60)  # Higher pitch for female
        
        # Use espeak-ng with advanced settings for smoother speech
        subprocess.run([
            'espeak-ng', 
            '-w', filename,
            '-v', voice_name,
            '-p', str(pitch),
            '-s', str(speed), 
            '-a', str(volume),
            '-g', str(gap),
            '--punct=none',  # Don't pronounce punctuation
            text
        ], check=True)

        # Check if file was created
        if not os.path.exists(filename):
            return jsonify({"error": "Failed to generate audio"}), 500

        # Return the audio file
        def remove_file(response):
            try:
                os.remove(filename)
            except:
                pass
            return response

        response = send_file(filename, 
                           mimetype="audio/wav", 
                           as_attachment=True,
                           download_name="speech.wav")
        
        # Clean up file after sending
        response.call_on_close(remove_file)
        return response

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Speech generation failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/tts', methods=['GET'])
def tts_info():
    return jsonify({
        "message": "TTS API endpoint",
        "method": "POST",
        "parameters": {
            "text": "Text to convert to speech (required)",
            "voice": "Voice gender: 'male' or 'female' (optional, default: 'female')",
            "pitch": "Voice pitch 0-99 (optional, auto-set based on voice)",
            "speed": "Speech speed 80-450 wpm (optional, default: 160)",
            "volume": "Volume 0-200 (optional, default: 100)",
            "gap": "Gap between words in ms (optional, default: 10)"
        },
        "example": {
            "text": "Hello world, this is a test of the improved text to speech system",
            "voice": "female",
            "pitch": 60,
            "speed": 160,
            "volume": 100,
            "gap": 10
        }
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
