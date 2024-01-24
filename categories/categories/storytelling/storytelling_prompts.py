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

prompt_generation_prompts = ["""I want you to generate questions that tests storywriting skills based on seed words given at the end of this text.
The questions be 1-2 sentences long, and should ask the reciever to write a story that fulfil certain criteria.

First, let's look at two example questions that comes from the seed: Wi-fi and it's transformative power.
Bad question: Can you craft an engaging short story that reveal how Wi-Fi connects or disrupts lives in an unforeseen circumstance.
This question allows for too much freedom, and it will be very difficult to evaluate who wrote a better response to this question, since there are so many different ways to answer it.
Great question: Write a story about a scientist that creates a wi-fi implant that allows him to directly search the internet from his mind, and tell the tale of how he uses this power to become the best superhero.
This question is much more specific regarding which type of story we want, making it easier to compare. Further, it challanges the creative abilities since the reciever needs to come up with a creative way that the wifi superpower can actually be useful.

Let's look at two other example questions based on the seeds: The Art of Love
Decent question: Craft a story about a renowned painter, known for their realistic portraits, who unexpectedly falls in love with a mysterious woman he's painting. After some time, he decides to propose to her, but she runs away and then in his dispair he creates a single masterpiece before giving up on art forever.
While this plot is specific, which is good, it doesn't require the write to be creative. Rather, the write just need to follow the plot step by step which doesn't well test their creativity.
Great question: Write a romantic and comical story about a painter falling in love, and her paintings reveals her emotional state and comically drives the plot forward. The story should have at least two jokes that makes the reader laugh out loud.
This question is better since it challanges the writer to come up with interesting ways the paintings can reveal the emotions and drive the plot, while also challanging the write to include multiple comical elements and at least two jokes.

Now it is your turn to come up with a great question asking to write a story based on my requirements. Avoid the word 'suspense' in the question though. The seed words are: <seeds>

In question, make sure to mention that the story must be within <words>

Question:"""]