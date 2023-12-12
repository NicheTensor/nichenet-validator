from categories.templates.template_category import TemplateCategory

import random
import time
import requests
import threading
import json

class FixedModelsTemplateCategory(TemplateCategory):
    def __init__(self, validator_model, uids_info, validator_session, confirmation_url, category_name="fixed_model", time_per_cycle=60*10, generator=None, answer_token_limit=500, max_response_time=12):
        super().__init__(validator_model, uids_info, validator_session)

        self.confirmation_url = confirmation_url
        self.category_name=category_name
        self.time_per_cycle = time_per_cycle
        self.generator = generator
        self.answer_token_limit = answer_token_limit
        self.max_response_time = max_response_time

        # self.fixed_models = [""]

        self.time_per_cycle = time_per_cycle
        self.generator = generator

    def get_data(self):
        return False
    
    def get_question(self):
        question = self.get_data()
        if not question:
            question = self.validator_model.quick_generate("Ask me a random question.", max_tokens=100)
        return question
    
    def forward(self, call_uids):
        t = threading.Thread(target=self.check_against_confirmation_url, args=(call_uids, ))
        t.start()

        return True
    
    def check_against_confirmation_url(self, call_uids):
        # start_time_cycle = time.time()
        uids_to_query = self.uids_info.get_uids_for_category(self.category_name)
        random.shuffle(uids_to_query)

        time_per_uid = self.time_per_cycle * 0.9 / len(uids_to_query)

        for uid in uids_to_query:
            start_time_uid = time.time()
            testing_prompt = self.get_question()
            if not testing_prompt:
                continue
            payload = {
                'prompt': testing_prompt,
                'max_tokens': self.answer_token_limit,
                'max_response_time': self.max_response_time,
                'get_miner_info': False,
            }
            miner_response = call_uids([uid], payload)
            print("payload",payload,flush=True)
            print("uid",uid,flush=True)
            print("miner_response",miner_response,flush=True)
            response = miner_response.get("response", None)
            
            responded = bool(response)
            if responded:
                score = self.score_response(testing_prompt, response)
                self.update_uid_info(uid, responded, score)
            else:
                self.update_uid_info(uid, responded, None)

            if (time.time() - start_time_uid) < time_per_uid:
                time.sleep(random.uniform(0, time_per_uid - (time.time() - start_time_uid)))


    # def check_against_top_trust(self, call_uids):
    #     uids_to_query = self.uids_info.get_uids_for_category(self.category_name)
    #     random.shuffle(uids_to_query)

    #     time_per_uid = self.time_per_cycle * 0.9 / uids_to_query

    #     for uid in uids_to_query:
    #         start_time_uid = time.time()
    #         testing_prompt = self.get_data(uid)
    #         if not testing_prompt:
    #             continue
    #         payload = {
    #             'prompt': testing_prompt,
    #             'max_tokens': self.answer_token_limit,
    #             'max_response_time': self.max_response_time,
    #             'get_miner_info': False,
    #         }
    #         miner_response = call_uids([uid], payload)
    #         response = miner_response.get("response", None)

    #         responded = bool(response)
    #         if responded:
    #             score = self.score_response(testing_prompt, response)
    #             self.update_uid_info(uid, responded, score)
    #         else:
    #             self.update_uid_info(uid, responded, None)

    #         if (time.time() - start_time_uid) < time_per_uid:
    #             time.sleep(random.uniform(0, time_per_uid - (time.time() - start_time_uid)))


    def score_response(self, testing_prompt, response):

        data = {
            "test_input": testing_prompt,
            "fixed_model_response": response,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.confirmation_url, data=json.dumps(data), headers=headers)

        try:
            result =response.json()["result"]
        except:
            result = "unknown"

        return result
