from validator.categories.templates.fixed_model_template_category import FixedModelsTemplateCategory




class VicheModelConfig(FixedModelsTemplateCategory):
    def __init__(self, validator_model, uids_info, validator_session, confirmation_url):


        prompting = {
            "<prefix>":"A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
            "<assistant_start>":'\nASSISTANT:',
            "<assistant_end>":'</s>',

            "<user_start>":'\nUSER: ',
            "<user_end>":'',
            }

        model_name = "WizardLM/WizardLM-13B-V1.2"

        category_name="wizard_model"

        super().__init__(validator_model, uids_info, validator_session, confirmation_url, category_name=category_name, model_name = model_name, prompting=prompting)

