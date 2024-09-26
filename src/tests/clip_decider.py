from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """"
Answer the ate,plate below

Here is the context: {context}

Question: {question}

Answer:
"""

context = """
You are a program to be an alternative to CapCut's 'Long Video to Shorts' AI application. 
A transcript will be provided for you in srt format.
Please select timeframes that are around (must be less than) 1 minute long.
I will again mention, A MAX of 1 MINUTE long, and a MINIMUM of 30 SECONDS LONG.
All you need to return is the timeframes in the form of [00:15.820 --> 01:17.780].
Again, the format is in mm:ss.ms. So a valid timeframe for you to return would be something like [00:00.000 --> 00:59:000].
Choose timeframes based on what you might think would be the best choices to create into TikTok videos or YouTube shorts.
The most interesting parts of the video, some interesting dialogue, etc.
Provide NO OTHER TEXT besides the timeframes.
"""

model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

f = open("data/temp/audio.srt", "r")

result = chain.invoke({"context": context, 
                       "question": f})

with open("data/temp/decision.txt", 'w') as tf:
    tf.write(result)