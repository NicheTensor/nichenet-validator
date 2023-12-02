import math

class ValidatorModel:
    def __init__(self, generator=None):

        self.generator=generator
    
    def probability_of_labels(self, prompt, max_tokens, labels):
        data = {
            "model": self.generator.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stop":self.generator.prompting["user_start"],
            "logprobs":len(labels) + 5,
        }
        response = self.generator.query(data, timeout=30)
        # print("""response.json()["choices"][0]""", response.json()["choices"][0])
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

    def quick_generate(self, prompt, max_tokens = 500):
      prompt = "<prefix><user_start>"+prompt+"<assistant_start>"
      return self.generate_text(prompt, max_tokens=max_tokens, temperature=0.7)

    def generate_text(self, prompt, max_tokens=100, temperature=0, n=1):

        data = {
            "model": self.generator.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n":n,
            "stop":self.prompting["user_start"],
        }
        
        response = self.generator.query(data, timeout=30)

        if response.status_code != 200:
            raise ValueError(f'Validator model.url {self.url} responded with status ', response.status)

        generations = []
        if response.json().get("choices"):
            for d in response.json()["choices"]:
                generations.append(d["text"])

        if len(generations) == 0:
            raise ValueError(f'Validator model.url {self.url} is not configured correctly.')

        return generations
