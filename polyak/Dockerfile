FROM python
WORKDIR /home/app
ADD main.py /home/app/


RUN apt update -y

RUN apt-get update -y

RUN apt upgrade -y



RUN apt install ffmpeg -y


RUN pip install aiogram
RUN pip install logging
RUN pip install asyncio
RUN pip install g4f==0.4.0.9
RUN pip install gtts
RUN pip install SpeechRecognition

CMD [ "python3" , "main.py"]