from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def decide_clips(srt_file, decision_file):
    template = """
    Answer the question below.

    Here is the context: {context}

    Transcript:
    {transcript}

    Answer:
    """

    context = """
    You are a program designed to be an alternative to CapCut's 'Long Video to Shorts' AI application.

    A transcript will be provided for you in SRT format.

    Please select timeframes that are less than 1 minute long, with a minimum of 30 seconds.

    For each selected timeframe, provide a JSON object with the following structure:

    {
        "timestamp": "[start time] --> [end time]",
        "description": "Why you chose this segment",
        "content": "The exact words spoken in this segment",
        "virality": 90,  // An integer from 1 to 100 indicating how viral you think it could be
        "title": "A possible title for this short"
    }

    Again, the timestamp format is mm:ss.ms (e.g., [00:00.000]).

    Choose timeframes based on what you think would make the best TikTok videos or YouTube shorts, focusing on the most interesting parts or dialogue.

    Provide **NO OTHER TEXT** besides the JSON objects.
    HOWEVER give them to me as "plain text", do not do ```json ``` thing. 
    MAKE SURE, all objects are wrapped inside an [] array AND objects are separated by commas, AS WELL AS no trailing commas after the last object.    
    """

    model = OllamaLLM(model="gemma2:27b")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    with open(srt_file, "r") as f:
        transcript = f.read()

    result = chain.invoke({
        "context": context,
        "transcript": transcript
    })

    with open(decision_file, 'w') as tf:
        tf.write(result)