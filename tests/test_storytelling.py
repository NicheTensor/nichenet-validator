
from categories.categories.storytelling.storytelling_config import StorytellingConfig
from validator_model.validator_model import ValidatorModel
from utils.uids_info import AllUidsInfo
from validator_model.generator_model import URLModel


prompting = {
    "<prefix>":"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
    "<assistant_start>":'\nASSISTANT:',
    "<assistant_end>":'</s>',

    "<user_start>":'\nUSER: ',
    "<user_end>":'',
    }


generator = URLModel(url="", model_name="WizardLM/WizardLM-13B-V1.2", prompting = prompting)
validator_model = ValidatorModel(generator=generator)

uids_info = AllUidsInfo(3)

category = StorytellingConfig(validator_model, uids_info, validator_session=None)


testing_promompts = category.generate_testing_prompts()

question = testing_promompts[0]
reply = validator_model.generate_text(question, max_tokens = 500)

evals = category.evaluate_response(question, reply)

print("\n\nPrompts")
for item in testing_promompts:
    print("Prompt:")
    print(item)

print("\n\nAnswer")
print(reply)

print("\n\nEvals:")
print(evals)

