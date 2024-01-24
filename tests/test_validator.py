
from categories.categories.general_chat.general_chat_config import GeneralChatConfig
from categories.categories.storytelling.storytelling_config import StorytellingConfig

from validator_model.validator_model import ValidatorModel
from validator_model.generator_model import URLModel

from utils.uids_info import AllUidsInfo


generator = URLModel(url="", model_name="WizardLM/WizardLM-13B-V1.2")
validator_model = ValidatorModel(generator=generator)


uids_info = AllUidsInfo(3)

categories_config = {
    "general_chat_config":GeneralChatConfig(validator_model, uids_info),
    "storytelling_config":StorytellingConfig(validator_model, uids_info)
}

category = categories_config["storytelling_config"]

testing_prompts = category.generate_testing_prompts()

question = testing_prompts[0]

reply = validator_model.generate_text(question, max_tokens = 1000)
evals = category.evaluate_response(question, reply)

print("\n\nPrompts")
for i, item in enumerate(testing_prompts):
    print(str(i) + ". " + item)

print("\n\nAnswer")
print(reply)

print("\n\nEvals:")
print(evals)