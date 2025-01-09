## Цель: 
Необходимо реализовать скрипт на python, который реализует небольшое API по преобразованию аудио в текст, на вход которого мы подаем аудиофайл в формате mp3, а на выходе получаем json.

Для преобразования аудио в текст использовать библиотеку  VOSK Speech Recognition

### Пример запроса:
POST http://localhost/asr  
в теле запроса передаем путь или url ссылку до mp3 файла.
В ответе на запрос получаем такой json:
```json
{
	"dialog": [
		 {
"source": "receiver",
			"text": "добрый день",
			"duration": 5,
			"raised_voice": true,
			"gender": "male"
		 },
		 {
			"source": "transmitter",
			"text": "здравствуйте",
			"duration": 6,
			"raised_voice": false,
"gender": "female"
		 },
		 {
			"source": "receiver",
			"text": "хотел бы оставить заявку на вебинар",
			"duration": 10,
			"raised_voice": true,
			"gender": "male"
		 },
		 {
			"source": "transmitter",
			"text": "спасибо, ваша заявка принята",
			"duration": 8,
			"raised_voice": true,
			"gender": "female"
		 }
	],
	"result_duration": {
		"receiver": 15,
		"transmitter": 14
	}
}
```
где
- receiver - одна сторона разговора
- transmitter - вторая сторона разговора
- duration - длительность разговора в секундах
- raised_voice- повышенный тон голоса (true - да, false - нет).
- gender - пол человека (male - мужской, female - женский)
- result_duration - сумма всех duration каждой из сторон.


## Запуск:
- (необязательно) скачать и распаковать нужную языковую модель с https://alphacephei.com/vosk/models, указать путь к ней в файле audio_speech_recognition в MODEL_PATH
- установить библиотеки: 
```shell
pip install -r requirements.txt
```
- для библиотеки pydub нужно установить FFmpeg https://ffmpeg.org/download.html
- запуск сервера
```shell
uvicorn main:app
```

Образцы аудио есть в samples