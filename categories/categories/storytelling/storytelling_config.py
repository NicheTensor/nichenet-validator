from categories.templates.synergy_category.synergy_category import SynergyCategory
from categories.categories.storytelling.storytelling_prompts import prompt_generation_prompts, eval_prompt_1, eval_prompt_2, vs_prompt
from categories.categories.storytelling.random_seed import get_random_seeds




class StorytellingConfig(SynergyCategory):
    def __init__(self, validator_model, uids_info, validator_session=None):
        super().__init__(validator_model, uids_info, validator_session)

        self.prompt_generation_prompts = prompt_generation_prompts

        self.evaluation_prompts = [eval_prompt_1, eval_prompt_2] # , eval_prompt_2
        self.evaluation_label_pass = "True"
        self.evaluation_label_fail = "False"

        self.vs_prompt = {
            "prompt":vs_prompt,
            "label_first_winner":"1",
            "label_second_winner":"2",
        }

        self.category_name="storytelling"

    def replace_keywords(self, text):
         text = text.replace("<seed>",get_random_seeds(1))
         text = text.replace("<seeds>",get_random_seeds(2))
         text = text.replace("<seeds3>",get_random_seeds(3))
         return text