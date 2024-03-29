# -*- coding: utf-8 -*-

# importing libraries 
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import pandas as pd
import numpy as np
import warnings
import subprocess
warnings.filterwarnings("ignore")
# create a speech recognition object
r = sr.Recognizer()

# a function to recognize speech in the audio file
# so that we don't repeat ourselves in in other functions
def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened)
    return text

# a function that splits the audio file into chunks on silence
# and applies speech recognition
def get_large_audio_transcription_on_silence(path,filename):
    """Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks"""
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    df1 = pd.DataFrame(columns = ["filename","audioname","chunk","text"])
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"{filename}_chunk_{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            ff = "{}".format(filename) + "_chunk_" + "{}".format(i)+".wav"
            a = [ff,filename,i,text]
            d = pd.DataFrame({
                    'filename': [ff],
                    'audioname': [filename],
                    'chunk': [i],
                    "text" : [text]
                })
            df1 = df1.append(d)
            print(chunk_filename, ":", text)
            whole_text += text
    # return the text for all chunks detected
    df1["whole_text"] = whole_text
    return whole_text,df1

datadf = pd.DataFrame()
data_dir = (r"Test/")
file_paths = pd.DataFrame({"path" :[os.path.join(data_dir, filename) for filename in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, filename))]})
#print(file_paths)
datadf = datadf._append(file_paths,ignore_index=True)
print(datadf.head())
datadf[['sub',"filename"]] = datadf['path'].str.split( "/", expand=True)
datadf[["audioname","format"]] = datadf['filename'].str.split('.', expand=True)
print(datadf.head())
# path = r"C:\Users\SS Studios\Desktop\SER-based-antispoofing-main\testdata\Test\Barack_Obama_1.wav"
DDF = pd.DataFrame(columns = ["filename","audioname","chunk","text","whole_text"])
for index, row in datadf.iterrows():
    text,df = get_large_audio_transcription_on_silence(row["path"],row["audioname"])
    df.to_csv("{}.csv".format(row["audioname"]))
    DDF = DDF.append(df)
    print(text)
DDF.to_csv("meta_data.csv")