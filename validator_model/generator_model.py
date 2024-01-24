import requests

class GeneratorModel:
    def __init__(self, prompting = {}):
        
        self.prompting = prompting
    
    def query(self, data, timeout=180):
        return None
    
    def prompt_template(self, system, user):

        system_template = f"""<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
"""
        return system_template
    
    # def preformat(self,prompt):

    #     for key in self.prompting.keys():
    #         prompt = prompt.replace(key, self.prompting[key])

    #     return prompt


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

    def query(self, uid, data, timeout=180):

        # data["prompt"] = self.preformat(data["prompt"])
        data["model_name"] = self.model_name
        sampling_params = data["sampling_params"]
        sampling_params["stop"] = "<|im_end|>"

        payload_data = {
            "input": {
                "prompt": self.prompt_template(data["input"]["system"], data["input"]["prompt"])
            },
            "sampling_params": sampling_params,
        }

        # Data looks like this:
        # data = {
        #     "model": self.model_name,
        #     "prompt": prompt,
        #     "max_tokens": max_tokens,
        #     "temperature": temperature,
        #     "n":n,
        #     "stop":self.prompting["user_start"],
        # }
        # response = requests.post(self.url, headers={'Content-Type': 'application/json'}, json=data, timeout=timeout)


        # url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync"
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'Bearer {RUNPOD_API_KEY}'
        # }

        url = self.url
        headers = {
            'Content-Type': 'application/json',
        }

        # print("Validator Endpoint Input", payload_data)
        response = requests.post(url, headers=headers, json=payload_data, timeout=timeout)
        # print("Validator Endpoint Response", response.json())
        # print("-------------")
        # print("")
        return response.json()
    
