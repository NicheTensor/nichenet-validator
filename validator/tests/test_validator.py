from validator.categories.general_chat.general_chat_config import GeneralChatConfig
from validator.categories.storytelling.storytelling_config import StoryTellingConfig
from validator.validator_model.validator_model import ValidatorModel
from validator.utils.uids_info import AllUidsInfo




prompting = {
    "prefix":"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
    "assistant_start":'\nASSISTANT:',
    "assistant_end":'</s>',

    "user_start":'\nUSER: ',
    "user_end":'',
    }


validator_model = ValidatorModel(url="http://209.20.158.61:8000/v1/completions",model_name="WizardLM/WizardLM-13B-V1.2", prompting=prompting)

uids_info = AllUidsInfo(3)

categories_config = {
    "general_chat_config":GeneralChatConfig(validator_model, uids_info),
    "storytelling_config":StoryTellingConfig(validator_model, uids_info)
}

category = categories_config["storytelling_config"]

testing_prompts = category.generate_testing_prompts()

question = testing_prompts[0]

reply = validator_model.quick_generate(question, max_tokens = 1000)
evals = category.evaluate_response(question, reply)

print("\n\nPrompts")
for i, item in enumerate(testing_prompts):
    print(str(i) + ". " + item)

print("\n\nAnswer")
print(reply)

print("\n\nEvals:")
print(evals)