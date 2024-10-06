from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from utils.log_manager import log_info, log_attribute, log_warning, log_error

def decide_clips(srt_file, decision_file):
    template = """
    Answer the question below.

    Here is the context: {context}

    Transcript:
    {transcript}

    Answer:
    """

    context = """
    START CONTEXT
    You are a program designed to be an alternative to CapCut's 'Long Video to Shorts' AI application.

    A transcript will be provided for you in SRT format.

    TIMEFRAME RULE: Please select timeframes that are less than 1 minute long, around 50 seconds, with a minimum of 30 seconds.

    For each selected timeframe, provide a JSON object with the following structure:

    {
        "timestamp": "[start time] --> [end time]",
        "description": "Why you chose this segment",
        "content": "The exact words spoken in this segment",
        "virality": 90,  // An integer from 1 to 100 indicating how viral you think it could be
        "title": "A possible title for this short"
    }

    Again, the timestamp format is hh:mm:ss,ms (e.g., [00:00:09,400]).

    Choose timeframes based on what you think would make the best TikTok videos or YouTube shorts, focusing on the most interesting parts or dialogue.
    Make sure that the first 3-5 seconds are the most interesting as that is the hook. Make sure the full timestamps follows the timeframe rule.
    Give me 10 json objects.

    Provide **NO OTHER TEXT** besides the JSON objects.
    HOWEVER give them to me as "plain text", do not do ```json ``` thing. 
    MAKE SURE, all objects are wrapped inside an [] array AND objects are separated by commas, AS WELL AS no trailing commas after the last object.    
    PLEASE use timeframes/clips from ALL THROUGHOUT THE VIDEO. DO NOT focus on only the START OF THE VIDEO.
    PLEASE BE SMART ABOUT THIS. TAKE A MINUTE TO THINK ABOUT WHAT YOU ARE DOING. MAKE SURE WHAT YOU GIVE ME IS ACCURATE AND ACTUALLY MIGHT BE INTERESTING AS A SHORT AND FOLLOWS THE ABOVE GUIDE.
    TAKE AN EXTRA LOOK at sections where I might say "this might make a good clip" I MEAN YOU SHOULD PROBABLY TAKE THIS PART.
    PLEASE DO NOT HALLUCINATE... Actually use the content of the provided transcript...

    Examples of what might make good clips include:
    - Boss Battles
    - Entering new areas for the first time
    - Quest completion
    
    For example:
    55
    00:10:52,630 --> 00:11:07,350
    move onwards this is done threat so loudly the boss book will hear you oh I think the boss but

    56
    00:11:07,350 --> 00:11:14,410
    Bob they'll above Bob whoa can you see those those buggy looking eyes you mean the ones that

    57
    00:11:14,410 --> 00:11:21,070
    are rapidly getting bigger and bigger no oh my god she just kidnapped the other two I told you

    58
    00:11:21,070 --> 00:11:28,030
    shouldn't have fraud so loudly you just kill my other two friends it's always feet that are causing
    
    These might make a fun little clip. The mention of a boss should be your first clue. 
    Secondly the 'oh my god' is a huge indicator that this clip is something cool or interesting.
    Lastly, as you can see 'she just kidnapped the other two' as you can see this might be something really exciting. 
    So here, the timeframe of [00:10:52.630 --> 00:11:28,030] would be a great frame for a clip.
    END CONTEXT
    """

    model = OllamaLLM(model="gemma2:27b")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    log_attribute(f"Reading from... {srt_file}")
    f = open(srt_file, "r")


    result = chain.invoke({
        "context": context,
        "transcript": f
    })
    log_info(result)

    with open(decision_file, 'w') as tf:
        tf.write(result)