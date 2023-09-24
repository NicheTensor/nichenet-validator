from neurons.validator.utils.random_seed import get_random_seed
from neurons.validator.utils.random_seed_story import get_random_story_seed
import math
import requests

class ValidatorModel:
    def __init__(self, url, model_name, prompting = None):
        self.url = url
        self.model_name = model_name

        if prompting == None:
            self.prompting = {
                "prefix":"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
                "assistant_start":'\nASSISTANT:',
                "assistant_end":'</s>',

                "user_start":'\nUSER: ',
                "user_end":'',
                }
        else:
            self.prompting=prompting


    def generate_text(self, input_text, max_tokens=100, temperature = 0.0):

        return self.call_endpoint(input_text, max_tokens,temperature=temperature)[0]

    
    def quick_generate(self, prompt, max_tokens = 1000):
      prompt = "<prefix><user_start>"+prompt+"<assistant_start>"
      prompt = self.replace_keywords(prompt)
      return self.generate_text(prompt, max_tokens=max_tokens, temperature=0.7)
    

    def replace_keywords(self,prompt):

        prompt = prompt.replace("<prefix>",self.prompting["prefix"])

        prompt = prompt.replace("<assistant_start>",self.prompting["assistant_start"])
        prompt = prompt.replace("<assistant_end>",self.prompting["assistant_end"])

        prompt = prompt.replace("<user_start>",self.prompting["user_start"])
        prompt = prompt.replace("<user_end>",self.prompting["user_end"])

        prompt = prompt.replace("<seed>",get_random_seed(1))
        prompt = prompt.replace("<seeds>",get_random_seed(2))
        prompt = prompt.replace("<seeds3>",get_random_seed(3))

        prompt = prompt.replace("<storyseed>", get_random_story_seed(1))
        prompt = prompt.replace("<storyseeds>", get_random_story_seed(2))
        prompt = prompt.replace("<storyseeds3>", get_random_story_seed(3))

        return prompt
    

    def probability_of_labels(self, prompt, max_tokens, labels):
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stop":self.prompting["user_start"],
            "logprobs":len(labels) + 5,
        }
        response = requests.post(self.url, headers={'Content-Type': 'application/json'}, json=data, timeout=30)
        print("""response.json()["choices"][0]""", response.json()["choices"][0])
        logprobs = response.json()["choices"][0]["logprobs"]["top_logprobs"][0]

        # Convert log probabilities to logits (using some math tricks)
        def logprob_to_logit(lp):
            return lp - math.log(1.0 - math.exp(lp))

        # Convert logits back to probabilities
        def logit_to_prob(l):
            e_l = math.exp(l)
            return e_l / (1.0 + e_l)

        label_probabilities = []
        for label in labels:
            curr_logprob = logprobs.get(label, None)
            curr_logit = logprob_to_logit(curr_logprob) if curr_logprob is not None else 0

            # Apply temperature scaling
            temperature = 3.0  # Adjust as needed. Higher values make predictions less extreme.
            curr_logit /= temperature

            curr_prob = logit_to_prob(curr_logit)

            label_probabilities.append(curr_prob)

        # Normalize the probabilities to sum to 100%
        total_prob = sum(label_probabilities)

        label_probabilities = [prob / total_prob for prob in label_probabilities]

        return label_probabilities


    def call_endpoint(self, prompt, max_tokens, temperature, n=1):

        data = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n":n,
            "stop":self.prompting["user_start"],
        }
        
        response = requests.post(self.url, headers={'Content-Type': 'application/json'}, json=data, timeout=30)
        generations = []
        if response.json().get("choices"):
            for d in response.json()["choices"]:
                generations.append(d["text"])

        print("Prompt:\n", prompt)
        for item in generations:
            print("Completion:", item," <end>")

        return generations
