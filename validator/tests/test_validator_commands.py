from validator.categories.general_chat.general_chat_config import GeneralChatConfig
from validator.validator_model.validator_model import ValidatorModel
from validator.utils.uids_info import AllUidsInfo
import random



validator_model = ValidatorModel(url="http://209.20.158.61:8000/v1/completions",model_name="WizardLM/WizardLM-13B-V1.2")

uids_info = AllUidsInfo(4)

categories_config = {
    "general_chat_config":GeneralChatConfig(validator_model, uids_info),
}

category = categories_config["general_chat_config"]

task = "get_uids_info"

if task == "generate_prompt":
    category = categories_config[request_data["category"]]
    prompts = category.generate_testing_prompts()
    to_return = {"prompts":prompts}


elif task == "evaluate_responses":
    category = categories_config[request_data["category"]]
    filtered_responses, filtered_responses_uids = category.filter_responses(request_data["testing_prompt"], request_data["valid_responses"], request_data["valid_responses_uids"])
    to_return = {"filtered_responses":filtered_responses, "filtered_responses_uids":filtered_responses_uids}

elif task == "score_responses":
    category = categories_config[request_data["category"]]
    scores = category.score_responses( request_data["testing_prompt"], request_data["filtered_responses"], request_data["validator_response"])
    to_return = {"scores":scores}

elif task == "get_uids_info":
    to_return = uids_info.get_all_uids_info()


print(to_return)