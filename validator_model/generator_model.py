import requests

class GeneratorModel:
    def __init__(self, prompting = {}):
        
        self.prompting = prompting
    
    def query(self, data, timeout=30):
        return None
    
    def preformat(self,prompt):

        for key in self.prompting.keys():
            prompt = prompt.replace(key, self.prompting[key])

        return prompt


class URLModel(GeneratorModel):
    def __init__(self, prompting=None, url=None, model_name=None):

        if not prompting:
            prompting = {
                "<prefix>":"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
                "<assistant_start>":'\nASSISTANT:',
                "<assistant_end>":'</s>',

                "<user_start>":'\nUSER: ',
                "<user_end>":'',
                }
        super().__init__(prompting)  # Call the superclass's constructor
        self.url = url
        self.model_name = model_name

    def query(self, data, timeout=30):

        data["prompt"] = self.preformat(data["prompt"])
        data["model_name"] = self.model_name
        # Data looks like this:
        # data = {
        #     "model": self.model_name,
        #     "prompt": prompt,
        #     "max_tokens": max_tokens,
        #     "temperature": temperature,
        #     "n":n,
        #     "stop":self.prompting["user_start"],
        # }
        response = requests.post(self.url, headers={'Content-Type': 'application/json'}, json=data, timeout=timeout)
        return response
    
