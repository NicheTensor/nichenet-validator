class UidInfo:
    def __init__(self,
                 uid,
                 category="", 
                 tags="", 
                 description="", 
                 elo=1200, 
                 validator_elo=1200, 
                 past_response_rate=None, 
                 past_good_response_rate=None, 
                 past_scores=None,
                 past_rankings=None,
                 past_synergies=None,
                 is_miner=True,
                 
                 ):
        
        self.uid = uid
        self.category = category
        self.tags = tags
        self.description = description

        self.elo = elo
        self.validator_elo = validator_elo

        self.past_response_rate = past_response_rate if past_response_rate is not None else []
        self.past_good_response_rate = past_good_response_rate if past_good_response_rate is not None else []
        self.past_scores = past_scores if past_scores is not None else []
        self.past_rankings = past_rankings if past_rankings is not None else []
        self.past_synergies = past_synergies if past_synergies is not None else []

        self.is_miner = is_miner

    def to_dict(self):
        return {
            "uid": self.uid,
            "category": self.category,
            "tags": self.tags,
            "description": self.description,
            "elo": self.elo,
            "validator_elo": self.validator_elo,
            "past_response_rate": self.past_response_rate,
            "past_good_response_rate": self.past_good_response_rate,
            "past_scores": self.past_scores,
            "past_rankings": self.past_rankings,
            "past_synergies": self.past_synergies,
            "is_miner": self.is_miner
        }
    
    def to_dict_simple(self):

        if self.past_rankings:
            average_ranking = sum(self.past_rankings) / max(len(self.past_rankings), 1)
        else:
            average_ranking = None
        return {
            "uid": self.uid,
            "category": self.category,
            "tags": self.tags,
            "description": self.description,
            "validator_elo": self.validator_elo,
            "is_miner": self.is_miner,
            "average_ranking": average_ranking,
        }
        
    def __repr__(self):
        to_return= "".join([
            f"uid={self.uid}",
            f", category={self.category}",
            f", validator_elo={self.validator_elo}",
            f", past_response_rate={self.past_response_rate}",
            f", past_good_response_rate={self.past_good_response_rate}",
            f", past_rankings={self.past_rankings}",
            f", past_synergies={self.past_synergies}",

            f", tags={self.tags}"
        ])
        
        return f"<MinerInfo({to_return})>"

class AllUidsInfo:
    def __init__(self, num_uids = 2048, max_iterations_to_store = 256):
        self.uids = [UidInfo(uid=i) for i in range(num_uids)]
        self.max_iterations_to_store = max_iterations_to_store

    

    
    def __repr__(self):

        to_return = "\n" + "\n".join([str(uid) for uid in self.uids][:5])
        return f"<AllUidsInfo(uids={to_return})>"
    

    def get_all_uids_info(self):
        all_uid_dicts = []
        for uid in self.uids:
            all_uid_dicts.append(uid.to_dict_simple())

        return all_uid_dicts
    

    def get_uids_for_category(self, category_name):
        uids_of_category = []
        for uid in self.uids:
            if category_name == uid.category:
                uids_of_category.append(uid.uid)
        return uids_of_category

    def set_category_for_uids(self, uids, category_name):
        for uid in self.uids:
            if int(uid.uid) in uids:
                uid.category = category_name
    
    def update_validator_elo(self, uids_to_update, scores, k=16):
        for i, uid in enumerate(uids_to_update):

            won = 1 if scores[i] > 1 else 0

            curr_elo = self.uids[uid].validator_elo

            expected_score = 1 / (1 + 10 ** ((1200 - curr_elo) / 400)) #Validator has 1200 elo always

            new_elo = curr_elo + k * (won - expected_score)

            self.uids[uid].validator_elo = new_elo



    def update_list(self, lst, score):
        """Helper function to update a list with a new score, ensuring it does not exceed max_size."""
        if len(lst) >= self.max_iterations_to_store:
            lst.pop(0)
        lst.append(score)

    def update_response_rate(self, uids_to_update, uids_to_reward):
        reward_set = set(uids_to_reward)  # Convert to set for faster lookups
        
        for uid in uids_to_update:
            score = 1 if uid in reward_set else 0
            self.update_list(self.uids[uid].past_response_rate, score)

    def update_good_response_rate(self, uids_to_update, uids_to_reward):
        reward_set = set(uids_to_reward)  # Convert to set for faster lookups
        
        for uid in uids_to_update:
            score = 1 if uid in reward_set else 0
            self.update_list(self.uids[uid].past_good_response_rate, score)


    def update_scores(self, uids_to_update, scores):
        for i, uid in enumerate(uids_to_update):
            self.update_list(self.uids[uid].past_scores, scores[i])

    def update_synergies(self, filtered_responses_uids, uids_to_update, synergies):
        all_synergies = [None] * len(uids_to_update)

        for i, uid in enumerate(filtered_responses_uids):
            all_synergies[uids_to_update.index(uid)] = synergies[i]

        for i, uid in enumerate(uids_to_update):
            self.update_list(self.uids[uid].past_synergies, all_synergies[i])
            
    def update_rankings(self, filtered_responses_uids, uids_to_update, ranks):

        all_ranks = [None] * len(uids_to_update)

        for i, uid in enumerate(filtered_responses_uids):
            all_ranks[uids_to_update.index(uid)] = ranks[i]

        for i, uid in enumerate(uids_to_update):
            rank = all_ranks[i]
            self.update_list(self.uids[uid].past_rankings, rank)


    
# Example Usage:
"""
miner = UidInfo(category="test_category", tags="test_tags")
all_miners = AllMinersInfo()
all_miners.add_miner("0", miner)

print(miner)
print(all_miners)
"""