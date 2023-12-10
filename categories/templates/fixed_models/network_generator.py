from validator_model.generator_model import GeneratorModel
from categories.templates.fixed_models.fixed_model_config import prompting, model_name

class NetworkGenerator(GeneratorModel):
    def __init__(self, session):
        super().__init__(prompting)  # Call the superclass's constructor
        self.session = session
        self.model_name = model_name

    def query(self, uid, data, timeout=30):

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

        response = self.session.call_uids(self, uid, data)
        return response
    
