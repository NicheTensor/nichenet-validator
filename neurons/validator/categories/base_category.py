import random
import template

class BaseCategory:
    def __init__(self, validator_model, uids_info, validator_session):

        self.validator_model = validator_model
        self.uids_info = uids_info
        self.validator_session = validator_session

        self.prompt_generation_prompts = []
        self.evaluation_prompts = []
        self.vs_prompt = {}
        self.category_name="BaseCategory"


        self.synergy_based_on_rank, self.synergy_weights = self.create_synergy_based_on_rank()
        self.validator_elo_score_weights = self.create_validator_elo_score_weights()

        self.validator_elo_reward_weight = 0.2
        self.synergy_reward_weight = 0.8

        self.max_incentivized_miners = 100

        self.questions_token_limit = 300
        self.response_character_limit = 2000

        self.prompt_index = 0




    def create_synergy_based_on_rank(self, num_rewarded = 32, exponent=2, memory_length = 256):
        #Creates a list of how much synergy score each

        synergy_based_on_rank = list(range(1, num_rewarded+1))
        synergy_based_on_rank = [(item**exponent) for item in synergy_based_on_rank]
        synergy_based_on_rank = [100*item/sum(synergy_based_on_rank) for item in synergy_based_on_rank]
        synergy_based_on_rank.reverse()


        # Generate weights such that the most recent victory has the highest weight
        weights = [i for i in range(1, memory_length+1)]
        # Normalize weights so they sum to 1
        weights = [w/sum(weights) for w in weights]


        return synergy_based_on_rank, weights
    def create_validator_elo_score_weights(self, num_rewarded = 32, exponent=1.2):
        validator_elo_score_weights = list(range(1, num_rewarded+1))
        validator_elo_score_weights = [(item**exponent) for item in validator_elo_score_weights]
        validator_elo_score_weights = [100*item/sum(validator_elo_score_weights) for item in validator_elo_score_weights]
        validator_elo_score_weights.reverse()
        return validator_elo_score_weights
    
    def generate_testing_prompts(self):

        all_prompts = []
        for i in range(len(self.prompt_generation_prompts)):
            testing_prompts = self.generate_testing_prompt(prompt_index=i)
            all_prompts.append(testing_prompts)

        return all_prompts
    
    def generate_testing_prompt(self, prompt_index=None):
        if not prompt_index:
            prompt_index = self.prompt_index
            self.prompt_index = self.prompt_index % len(self.prompt_generation_prompts)
        prompt = self.prompt_generation_prompts[prompt_index]
        prompt = self.validator_model.replace_keywords(prompt)
        testing_prompt = self.validator_model.generate_text(prompt, self.questions_token_limit, temperature=0.7)
        return testing_prompt
    



    def evaluate_response(self, question, response):
        all_evaluation = []
        labels = [self.evaluation_label_pass, self.evaluation_label_fail]
        
        for prompt in self.evaluation_prompts:
            
            prompt = self.validator_model.replace_keywords(prompt)
            prompt = prompt.replace("<question>", question).replace("<response>", response)
            label_probabilities = self.validator_model.probability_of_labels(prompt, max_tokens=1, labels=labels)

            all_evaluation.append(label_probabilities[0] > label_probabilities[1] and label_probabilities[0] > 0.7) #shows true if first label (pass) is more likely


        return all_evaluation

    def filter_responses(self, question, responses, uids):

        filtered_uids = []
        filtered_responses = []
        evaluated_responses = {}

        for i, response in enumerate(responses):
            if not response in evaluated_responses:
                evaluated_responses[response] = self.evaluate_response(question, response)


            if not False in evaluated_responses[response]:
                filtered_uids.append(uids[i])
                filtered_responses.append(response)
        
        return filtered_responses, filtered_uids
    

    
    def get_valid_responses(self, responses, uids_to_query):
        #Filter based on if responded, then based on
        valid_responses_uids = []
        valid_responses = []

        for i, response in enumerate(responses):
            if response:
                valid_responses_uids.append(uids_to_query[i])

                response = response[:self.response_character_limit]

                valid_responses.append(response)
        
        return valid_responses, valid_responses_uids

    def forward(self, call_uids):
        
        uids_to_query = self.uids_info.get_category(self.category_name)
        print("uids_to_query", uids_to_query)
        testing_prompt = self.generate_testing_prompt()

        max_tokens = 20
        max_response_time = 30

        prompt_input = {
            'prompt': testing_prompt,
            'max_tokens': max_tokens,
            'max_response_time': max_response_time,
            'get_miner_info': False,
        }

        prompt_outputs = call_uids(uids_to_query, prompt_input)

        print("Prompt outputs", prompt_outputs)

        responses = [prompt_output['response'] for prompt_output in prompt_outputs]

        # responses = None #query uids
        valid_responses, valid_responses_uids = self.get_valid_responses(responses, uids_to_query)
        filtered_responses, filtered_responses_uids = self.filter_responses(testing_prompt, valid_responses, valid_responses_uids)

        validator_response = self.validator_model.quick_generate(testing_prompt, max_tokens=max_tokens)
        scores = self.score_responses( testing_prompt, filtered_responses, validator_response)

        self.update_uid_info(uids_to_query, valid_responses_uids, filtered_responses_uids, scores)

    def rank_indices(self, lst):
        """Return a list with the ranking of each element."""
        epsilon = 1e-10
        sorted_indices = sorted(range(len(lst)), key=lambda k: (lst[k], random.random() * epsilon), reverse=True)
        ranks = [0] * len(lst)
        for i, idx in enumerate(sorted_indices, 1):
            ranks[idx] = i
        return ranks

    def update_uid_info(self, uids_to_query, valid_responses_uids, filtered_responses_uids, scores):
        self.uids_info.update_response_rate(uids_to_query, valid_responses_uids)
        self.uids_info.update_good_response_rate(uids_to_query, filtered_responses_uids)
        self.uids_info.update_validator_elo(filtered_responses_uids, scores)

        rankings = self.rank_indices(scores)
        self.uids_info.update_rankings(filtered_responses_uids, uids_to_query, rankings)

        synergies = self.calculate_synergy(rankings)
        self.uids_info.update_synergies(filtered_responses_uids, uids_to_query, synergies)

    

    def score_responses(self, question, responses, validator_response):

        scores = []
        evaluated_responses = {}
        for response in responses:

            if not response in evaluated_responses:
                _, sum_probabilities = self.vs_response(question, validator_response, response)
                evaluated_responses[response] = sum_probabilities[-1]

            scores.append(evaluated_responses[response])

        return scores
    
    def calculate_synergy(self, rankings):
        num_uids = len(rankings)
        synergies = [0] * num_uids
        for i, rank in enumerate(rankings):
            if rank < len(self.synergy_based_on_rank):
                synergies[i] = self.synergy_based_on_rank[rank]
        return synergies

    def calculate_synergy_wma(self, historical_synergy):
        historical_synergy = [0 if x is None else x for x in historical_synergy]


        if len(historical_synergy) < len(self.synergy_weights):

            if len(historical_synergy) < len(self.synergy_weights)/2:
                zeros_to_fill = [0] * (int(len(self.synergy_weights)/2) - len(historical_synergy))
                historical_synergy = historical_synergy[::-1] + zeros_to_fill + historical_synergy + zeros_to_fill
            else:
                historical_synergy = historical_synergy[::-1] + historical_synergy
                historical_synergy = historical_synergy[-len(self.synergy_weights):]

        synergy = sum(s*w for s, w in zip(historical_synergy, self.synergy_weights))

        return synergy
    
    def calculate_validator_elo_score(self, uids):
        elos = [self.uids_info.uids[uid].validator_elo for uid in uids]
        
        ranked_elos = self.rank_indices(elos)

        validator_elo_scores = [0] * len(ranked_elos)

        for i, rank in enumerate(ranked_elos):
            if rank < len(self.synergy_based_on_rank):
                validator_elo_scores[i] = self.validator_elo_score_weights[rank]
            
        validator_elo_scores = self.normalize(validator_elo_scores)
        return validator_elo_scores
    
    def normalize(self, numbers):
        total = sum(numbers)
        if total == 0:
            return [0.0] * len(numbers)
        return [float(i)/total for i in numbers]

    def calculate_synergy_score(self, uids):
        synergies = []

        for uid in uids:
            synergy = self.calculate_synergy_wma( self.uids_info.uids[uid].past_synergies )
            print("Syngergy", synergy)
            synergies.append(synergy)
        print("Synergies", synergies)
        synergies = self.normalize(synergies)
        return synergies

    def calculate_good_response_rate_score(self, uids):
        good_response_rates = []

        for uid in uids:
            past_good_response_rate = self.uids_info.uids[uid].past_good_response_rate
            if sum(past_good_response_rate) == 0:
                good_response_rate= 0
            else:
                weights = list(range(1, len(past_good_response_rate) + 1))
                good_response_rate = sum(past_good_response_rate[i]*weights[i] for i in range(len(past_good_response_rate))  ) / sum(weights)

            good_response_rates.append(good_response_rate)
        
        return good_response_rates

    def calculate_miner_incentive_score(self):
        incentive_scores = []

        category_uids = self.uids_info.get_uids_for_category(self.category_name)

        validator_elo_scores = self.calculate_validator_elo_score(category_uids)
        synergy_scores = self.calculate_synergy_score(category_uids)
        good_response_rates = self.calculate_good_response_rate_score(category_uids)
        #print("validator_elo_scores", validator_elo_scores)
        #print("synergy_scores", synergy_scores)
        #print("good_response_rates", good_response_rates)

        for i in range(len(category_uids)):
            incentive_score = ( validator_elo_scores[i] * self.validator_elo_reward_weight + synergy_scores[i] * self.synergy_reward_weight ) * good_response_rates[i]
            incentive_scores.append(incentive_score)
            if i < 5:
                print("validator_elo_scores[i]", validator_elo_scores[i], "synergy_scores[i]", synergy_scores[i], "good_response_rates[i]", good_response_rates[i] )


        # if len(incentive_scores) > self.max_incentivized_miners:
        #     threshold = sorted(incentive_scores, reverse=True)[self.max_incentivized_miners + 1]
        #     incentive_scores = [x if x >= threshold else 0 for x in incentive_scores]
        
        for i, item in enumerate(incentive_scores):
            if incentive_scores[i] > (2 / self.max_incentivized_miners):
                incentive_scores[i] = item - (1 / self.max_incentivized_miners)
            else:
                incentive_scores[i] = item / 2


        incentive_scores = self.normalize(incentive_scores)

        return incentive_scores, category_uids
    


    """ Tournament code """
    def vs_response(self, question, response_1, response_2):

        labels = (self.vs_prompt["label_first_winner"], self.vs_prompt["label_second_winner"])

        sum_probabilities = [0, 0]

        for reverse in [False, True]:
            prompt = self.validator_model.replace_keywords(self.vs_prompt["prompt"])

            response_order = (response_1, response_2) if not reverse else (response_2, response_1)
            prompt = prompt.replace("<question>", question).replace("<response1>", response_order[0]).replace("<response2>", response_order[1])

            label_probabilities = self.validator_model.probability_of_labels(prompt, max_tokens=1, labels=labels)

            # Adjust for reverse order
            if reverse:
                label_probabilities.reverse()

            sum_probabilities[0] += label_probabilities[0]
            sum_probabilities[1] += label_probabilities[1]

        winner = sum_probabilities.index(max(sum_probabilities))
        return winner, sum_probabilities


