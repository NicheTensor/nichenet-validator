import math

class ValidatorModel:
    def __init__(self, generator=None):

        self.generator=generator
        self.uid = None
    
    def probability_of_labels(self, prompt, payload, labels):

        # payload["model"] = self.generator.model_name
        payload["prompt"] = prompt
        payload["system"] = 'You are an expert evaluator.'
        payload["max_tokens"] = 3
        payload["logprobs"] = len(labels) + 5

        payload["get_miner_info"] = False

        response = self.generator.query(self.uid, payload, timeout=180)
        # print("""response.json()["choices"][0]""", response.json()["choices"][0])
        # logprobs = response.json()["choices"][0]["logprobs"]["top_logprobs"][0]
        # if response.status_code != 200:
        #     raise ValueError(f'Validator model.url {self.url} responded with status ', response.status)

        if response:
            logprobs = response[0]["outputs"][0]["logprobs"][0]
        else:
            raise ValueError(f'Validator model.url {self.url} no response')

        # Convert log probabilities to logits
        def logprob_to_logit(lp):
            # Adding a small constant to avoid math domain error when lp is 0.0
            small_constant = 1e-10
            return lp - math.log(1.0 - math.exp(lp) + small_constant)

        # Convert logits back to probabilities
        def logit_to_prob(l):
            e_l = math.exp(l)
            return e_l / (1.0 + e_l)

        def token_to_id(token):
            token_map = {"True": "4365", "False": "6995", "1": "28740", "2": "28750"}
            return token_map[token]

        label_probabilities = []
        for label in labels:
            tokenid = token_to_id(label)
            # print("tokenid", tokenid)
            # print("logprob cc", logprobs)
            try:
                curr_logprob = logprobs[tokenid]
            except:
                curr_logprob = None
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

    def generate_text(self, prompt, type, payload):
        generation = self.generate_texts(prompt, type, payload)
        generation = generation[0]
        return generation

    def generate_texts(self, prompt, type, payload):

        system = 'You are a helpful assistant.'
        if type == 'question':
            system = 'You are an expert question framer.'
            payload["max_tokens"] = 200
        elif type == 'vs' or type == "filter":
            system = "You are an expert evaluator."
        elif type == 'answer':
            payload["max_tokens"] = 1500
            system = 'You are a helpful assistant.'

        # payload["model"] = self.generator.model_name
        payload["prompt"] = prompt
        payload["system"] = system
        payload["get_miner_info"] = False
        
        response = self.generator.query(self.uid, payload, timeout=180)

        # if response.status_code != 200:
        #     raise ValueError(f'Validator model.url {self.url} responded with status ', response.status)

        generations = []
        # if response.json().get("choices"):
        #     for d in response.json()["choices"]:
        #         generations.append(d["text"])

        print("Val e response", response)

        if response:
            for d in response:
                generations.append(d["outputs"][0]["text"])

        if len(generations) == 0:
            raise ValueError(f'Validator model.url {self.url} is not configured correctly.')

        return generations