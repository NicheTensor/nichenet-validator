vs_prompt = """
<prefix><user_start>I want you to create a leaderboard of different of large-language models. To do so, I will give you the instructions (prompts) given to the models, and the responses of two models. Please rank the models based on which responses would be preferred by humans. All inputs and outputs should be python dictionaries.

Here is the prompt:
{
    "instruction": \"""<question>\""",
}

Here are the outputs of the models:
[
    {
        "model": "1",
        "answer": \"""<response1>\"""
    },
    {
        "model": "2",
        "answer": \"""<response2>\"""
    }
]

Now please rank the models by the quality of their answers, so that the model with rank 1 has the best output. Then return a list of the model names and ranks, i.e., produce the following output:
[
    {'model': <model-name>, 'rank': <model-rank>},
    {'model': <model-name>, 'rank': <model-rank>}
]

Your response must be a valid Python dictionary and should contain nothing else because we will directly execute it in Python. Please provide the ranking that the majority of humans would give.
<assistant_start>[
    {'model': '
    
""".strip()


eval_prompt_1 = """<prefix><user_start>An AI model got asked the following question:
{
    "instruction": "<question>"
}

The AI model responded with:
{
    "answer": \"""<response>\"""
}

If the models response to the question is contains contains only relevant information, put True as the label. If the response adds information irrelevant to the question, put False.

Your response must be a valid Python dictionary and should contain nothing else because we will directly execute it in Python.
<assistant_start>{
    "label": "
""".strip()

eval_prompt_2 = """<prefix><user_start>An AI model got asked the following question:
{
    "instruction": "<question>"
}

The AI model responded with:
{
    "answer": \"""<response>\"""
}

If the models response to the question is factually correct, put True as the label. If the response is factually incorrect, put False.

Your response must be a valid Python dictionary and should contain nothing else because we will directly execute it in Python.
<assistant_start>{
    "label": "
""".strip()

prompt_generation_prompts = [
            """<prefix><user_start>Your task is to write a question that will be used to evaluate how intelligent different AI models are. The question should be fairly complex and it can be about anything as long as it somehow relates to these seeds: <seeds>
Your question should be clear, make sense, be max 400 characters and possible to understand without any context.<assistant_start> Question:""",
            "<prefix><user_start>Look at these seeds: <seeds>\nBased on them, write a complicated question that only an intelligen person could answer.\nYour question should be max 400 characters.<assistant_start> Question:",
        ]