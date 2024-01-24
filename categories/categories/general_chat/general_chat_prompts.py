vs_prompt = """Two language models were presented with the same question:
{'question': <question>}

The output of the models are:
[
   {'model': 1, 'answer': <response1>},
    {'model': 2, 'answer': <response2>}
]

Determine which model provided the superior response. Indicate your choice by stating either 'best_model=1' or 'best_model=2', based on the quality and relevance of the answer.
Your task is to select the response that would likely be deemed superior by the majority of human evaluators.

best_model="""

eval_prompt_1 = """An AI model claiming to be an expert in following user instructions was given the following prompt:
{'instruction': <question>}

The AI model responded with:
{'answer': <response>}

If the models response accurately follows the original instruction, put True as the label. If the response seems diverted from the original instructions, put False.
Your response must be either True or False. Nothing else.
label=""".strip()

eval_prompt_2 = """An AI model claiming to be an expert in following user instructions was given the following prompt:
{'instruction': <question>}

The AI model responded with:
{'answer': <response>}

If the models response accurately follows the original instruction, put True as the label. If the response seems diverted from the original instructions, put False.
Your response must be either True or False. Nothing else.
label=""".strip()

prompt_generation_prompts = ["""Based on seed words provided at the end of this text, craft questions that require critical thinking, creativity, and reasoning to answer.
The goal is to generate questions that can't be addressed solely by reciting facts from memory but rather require the application of knowledge in novel ways.

Consider the distinction between these types of questions, exemplified with the seed word 'Roman Empire':
- Undesirable question: 'Why did the Roman Empire fall?'
    This question may prompt an answer that relies heavily on memorized historical events, which doesn't challenge the responder to think critically or creatively.
- Superior question: 'If you had to advance the Roman Empire's technological capabilities to match an industrial revolution, what strategic changes would you implement in governance and education?'
    This question demands reasoning, the application of historical context, and imaginative problem-solving, making it a valuable test of the abilities we want to evaluate.

Another set of examples using 'Bowl' as a seed word:
- Poor question: 'How do you measure the volume of a bowl?'
    This question doesn't sufficiently challenge the respondent beyond their recall of scientific principles.
- Better question: 'In an environment like the Sahara desert, how could you determine a bowl's volume using only the bowl itself, a ruler, and a bucket?'
    This question invites creative problem-solving but lacks the breadth for multiple innovative answers.
- Exceptional question: 'What inventive marketing strategy would you propose to increase bowl sales, and which public figure would you enlist to maximize its impact?'
    This question allows for a wide range of responses, each with its unique rationale and creativity.

Now, it's your turn to generate an engaging and thought-provoking question. Avoid replication of the provided examples. Instead, conceive a short question strictly using less than 50 words. Use the following seed word to inspire your question:
Seeds: <seeds>

Question:"""]