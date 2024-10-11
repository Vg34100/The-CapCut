import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
try:
    # When running from the root of the project
    from utils.log_manager import log_info, log_attribute, log_warning, log_error
except ImportError:
    # When running directly
    from log_manager import log_info, log_attribute, log_warning, log_error

def chunk_transcript(transcript, chunk_size):
    words = transcript.split()
    for i in range(0, len(words), chunk_size):
        yield ' '.join(words[i:i + chunk_size])

def count_words(text):
    # Split the text by spaces (and newlines, tabs, etc.) and return the length of the list
    words = text.split()
    return len(words)

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

    TIMEFRAME RULE: Please select timeframes that are less than 1 minute long, around 50 seconds, with a HARD MINIMUM of 30 seconds.

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
    Give me multiple json objects.

    Provide **NO OTHER TEXT** besides the JSON objects.
    HOWEVER give them to me as "plain text", do not do ```json ``` thing. 
    MAKE SURE, all objects are wrapped inside an [] array AND objects are separated by commas, AS WELL AS no trailing commas after the last object.    
    PLEASE use timeframes/clips from ALL THROUGHOUT THE VIDEO. DO NOT focus on only the START OF THE VIDEO.

    Examples of what might make good clips include:
    - Boss Battles
    - Entering new areas for the first time
    - Quest completion
    
    For example:
    55
    00:10:52,630 --> 00:11:07,350
    move onwards this is done threat so loudly the boss boo...

    58
    00:11:21,070 --> 00:11:40,030
    shouldn't have fraud so loudly you just kill my other two friends...
    
    and as some output
        {
        "timestamp": "00:11:02,640 --> 00:11:37,780",
        "description": "Introduces the concept of the Slumber Dojo, a place where you train in your dreams. This is intriguing and has potential for humor and action.",
        "content": "330 00:11:02,640 --> 00:11:04,020 Okay, so straightforward. 331 00:11:04,540 --> 00:11:05,300 I'm a regular character. ... 520 Then, within that dream, you defeat all the foes trying to get you.",
        "duration": 35
        "virality": 90,
        "title": "Train in Your Dreams at the Slumber Dojo!"
    },
    {
        "timestamp": "00:12:03,160 --> 00:12:25,560",
        "description": "Highlights the training process of the Slumber Dojo. The protagonist chooses a challenging option and starts his dream fight.",
        "content": "356 00:12:03,160 --> 00:12:04,840 Alright, are you ready to do some training? 357 00:12:05,360 --> 00:12:06, ... 340 --> 00:12:25,560 Let's go at it. ",
        "duration": 23
        "virality": 75,
        "title": "Slumber Dojo Training Begins!"
    }
    
    These might make a fun little clip. The mention of a boss should be your first clue. 
    Secondly the 'oh my god' is a huge indicator that this clip is something cool or interesting.
    Lastly, as you can see 'she just kidnapped the other two' as you can see this might be something really exciting. 
    So here, the timeframe of [00:10:52.630 --> 00:11:40,030] would be a great frame for a clip.
    make sure that the timeframes are accurate to the length I want (around 50 seconds) and include the full length of what the context you select contains.
    Reminder, a HARD MINIMUM of 30 seconds. And I PREFER around 50 seconds, even if it just means you pick a certain start and add some number around 50 to figure out the end.
    
    END CONTEXT
    """

    log_attribute(f"Reading from... {srt_file}")
    #f = open(srt_file, "r")
    with open(srt_file, "r") as file:
        # Read the entire content of the file
        f = file.read()

    length = len(f) + len(context) + 40
    print(length)

    # model = OllamaLLM(model="gemma2:27b", verbose=True)
    model = OllamaLLM(
        model="gemma2:27b",
        temperature=0.6,          # Lower temperature for more deterministic responses
        top_k=30,                 # Narrow down the token selection to reduce randomness
        top_p=0.85,               # Adjust nucleus sampling for more focused results
        repeat_penalty=1.1,       # Penalize token repetition to avoid loops
        mirostat=2,               # Enable Mirostat for dynamic perplexity control
        mirostat_eta=0.1,         # Set the learning rate for Mirostat
        mirostat_tau=5.0,         # Target perplexity for Mirostat to control randomness
        num_ctx=8196,             # Maximum context tokens for better understanding of inputs
        # stop=["\n", "End"]        # Stop tokens to prevent over-generation and hallucinations
        verbose=True
    )
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model


    all_results = []

    
    chunk_size = 1000  # Adjust as needed based on token limit
    for chunk in chunk_transcript(f, chunk_size):
        # Print the current chunk for debugging
        print({"context": context, "transcript": chunk})

        # Get the result from the model
        result = chain.invoke({"context": context, "transcript": chunk})
        log_info(result)
        
        # Parse the result as JSON (assuming the result is a valid JSON array)
        try:
            json_result = json.loads(result)
            if isinstance(json_result, list):
                # Append the parsed JSON result to the all_results list
                all_results.extend(json_result)
            else:
                log_warning("Expected a list, but got something else.")
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse JSON: {e}")


    # result = chain.invoke({
    #     "context": context,
    #     "transcript": f
    # })

    # log_info(result)

    # Write the combined JSON array to the decision file
    with open(decision_file, 'w') as tf:
        json.dump(all_results, tf, indent=4)  # Pretty-print the JSON if needed


if __name__ == "__main__":
    decide_clips(srt_file="data/temp/[BBP]-[EOW]-RAW__10-04-24__[20]-2-audio.srt", decision_file="out.txt")