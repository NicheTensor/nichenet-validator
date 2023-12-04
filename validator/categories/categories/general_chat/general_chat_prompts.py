

vs_prompt = """<prefix><user_start>Here is a prompt:
{
    "instruction": \"""question_full\""",
}

Here are the outputs of the models:
[
    {
        "model": 1,
        "answer": \"""<response1>\"""
    },
    {
        "model": 2,
        "answer": \"""<response2>\"""
    }
]

Please create a dict containting the highest quality answer, i.e., produce the following output:

{
  'best_model': <model-name>
}

Please provide the response that the majority of humans would consider better.

<assistant_start>{
  'best_model': """
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