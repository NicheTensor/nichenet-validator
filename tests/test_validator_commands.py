
from validator_model.validator_model import ValidatorModel
from utils.uids_info import AllUidsInfo
from validator_model.generator_model import URLModel
import random
from categories.categories.general_chat.general_chat_config import GeneralChatConfig



generator = URLModel(url="http://209.20.158.61:8000/v1/completions", model_name="WizardLM/WizardLM-13B-V1.2")
validator_model = ValidatorModel(generator=generator)

uids_info = AllUidsInfo(4)

categories_config = {
    "general_chat_config":GeneralChatConfig(validator_model, uids_info, None),
}

category = categories_config["general_chat_config"]

task = "get_uids_info"

request_data = {
    "testing_prompt":"What is 1+1?",
    "valid_responses":["It is 2", "It is 5"],
    "filtered_responses":["It is 2", "It is 5"],
    "valid_responses_uids":[1,3],
    "validator_response":"1+1 is 2"
}

if task == "generate_prompt":
    prompts = category.generate_testing_prompts()
    to_return = {"prompts":prompts}


elif task == "evaluate_responses":
    filtered_responses, filtered_responses_uids = category.filter_responses(request_data["testing_prompt"], request_data["valid_responses"], request_data["valid_responses_uids"])
    to_return = {"filtered_responses":filtered_responses, "filtered_responses_uids":filtered_responses_uids}

elif task == "score_responses":
    scores = category.score_responses( request_data["testing_prompt"], request_data["filtered_responses"], request_data["validator_response"])
    to_return = {"scores":scores}

elif task == "get_uids_info":
    to_return = uids_info.get_all_uids_info()


print(to_return)