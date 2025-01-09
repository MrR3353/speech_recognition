import os

import requests
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse

from audio_speech_recognition import convert_mp3_to_wav, analyze_audio

app = FastAPI(debug=True)


@app.post("/asr")
async def asr_endpoint(file_url: str = Form(...)):
    try:
        if file_url.startswith("http"):
            response = requests.get(file_url)
            mp3_path = "temp.mp3"
            with open(mp3_path, "wb") as f:
                f.write(response.content)
        else:
            mp3_path = file_url

        wav_path = convert_mp3_to_wav(mp3_path)
        result = analyze_audio(wav_path)
        print(result)

        # clean temp files
        os.remove(wav_path)
        if file_url.startswith("http"):
            os.remove(mp3_path)

        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app)
