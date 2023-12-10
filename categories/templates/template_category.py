class TemplateCategory:
    def __init__(self, validator_model, uids_info, validator_session):

        self.validator_model = validator_model
        self.uids_info = uids_info
        self.validator_session = validator_session

    def forward(self, call_uids):
        #Call uids and update scores
        return True
    
    def calculate_miner_incentive_score(self):
        category_uids = self.uids_info.get_uids_for_category(self.category_name)
        
        incentive_scores = [1/len(category_uids)] * len(category_uids)
        return incentive_scores, category_uids
        