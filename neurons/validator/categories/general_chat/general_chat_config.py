from neurons.validator.categories.base_category import BaseCategory
from neurons.validator.categories.general_chat.general_chat_prompts import vs_prompt, eval_prompt_1, eval_prompt_2, prompt_generation_prompts

class GeneralChatConfig(BaseCategory):
    def __init__(self, validator_model, uids_info, validator_session):
        super().__init__(validator_model, uids_info, validator_session)
        
        self.prompt_generation_prompts = prompt_generation_prompts

        self.evaluation_prompts = [eval_prompt_1, eval_prompt_2]
        self.evaluation_label_pass = "True"
        self.evaluation_label_fail = "False"

        self.vs_prompt = {
            "prompt":vs_prompt,
            "label_first_winner":"1",
            "label_second_winner":"2",
        }

        self.category_name="general_chat"