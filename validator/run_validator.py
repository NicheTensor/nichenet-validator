import os
import time
import torch
import argparse
import traceback
import bittensor as bt
import random
import wandb
run = wandb.init(project="niche-validator")

from validator.prompting_protocol import PromptingProtocol

from categories.categories.general_chat.general_chat_config import GeneralChatConfig
from categories.categories.storytelling.storytelling_config import StorytellingConfig
from categories.categories.wizard_model.wizard_model_config import WizardConfig


from validator_model.validator_model import ValidatorModel
from validator_model.generator_model import URLModel

from categories.categories.viche_model.network_generator import NetworkGenerator


from utils.uids_info import AllUidsInfo
from utils.weights import process_weights

def get_config():

    parser = argparse.ArgumentParser()

    parser.add_argument( '--netuid', type = int, default = 1, help = "The chain subnet uid." )
    parser.add_argument( '--model.url', type = str, default = None, help = "The url of the model endpoint." )
    parser.add_argument( '--model.name', type = str, default = None, help = "The name of model" )
    parser.add_argument( '--confirmation_url_wizard', type = str, default = "", help = "URL to test WizardLM fixed model" )
    

    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)

    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)

    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)

    bt.axon.add_args(parser)

    # To print help message, run python3 template/miner.py --help
    config =  bt.config(parser)

    # Set up logging directory
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'validator',
        )
    )

    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    return config


class ValidatorSession:
    def __init__(self, config):
        self.config = config
        self.wallet, self.subtensor, self.dendrite, self.metagraph, self.axon = self.setup()

        self.subtensor.serve_axon(
                    netuid=self.config.netuid,
                    axon=self.axon,
                )

        if config.model.url is None:
            print("Defaulting to use network for validation since --model.url or --model.name was not specified")
            # bt.logging("Defaulting to use network for validation since --model.url or --model.name was not specified")
            generator = NetworkGenerator(self)
        else:
            generator = URLModel(url=self.config.model.url, model_name=self.config.model.name)


        self.validator_model = ValidatorModel(generator=generator)

        self.max_uid = self.metagraph.uids.data.size(0)

        self.all_uids = [int(uid) for uid in self.metagraph.uids]
        self.uids_info = AllUidsInfo(self.max_uid)
        #print("self.metagraph.uids", self.metagraph.uids.data)

        self.setup_categories_config()
        self.step = 0

    def setup(self):
        
        # setup logging
        bt.logging(config=self.config, logging_dir=self.config.full_path)
    
        bt.logging.info(self.config)

        # The wallet holds the cryptographic key pairs for the 
        wallet = bt.wallet( config = self.config )
        bt.logging.info(f"Wallet: {wallet}")

        # The subtensor is our connection to the Bittensor blockchain.
        subtensor = bt.subtensor( config = self.config )
        bt.logging.info(f"Subtensor: {subtensor}")

        # Dendrite is the RPC client; it lets us send messages to other nodes (axons) in the network.
        dendrite = bt.dendrite( wallet = wallet )
        bt.logging.info(f"Dendrite: {dendrite}")

        # The metagraph holds the state of the network, letting us know about other miners.
        metagraph = subtensor.metagraph( self.config.netuid )
        bt.logging.info(f"Metagraph: {metagraph}")

        # Step 5: Connect the validator to the network
        if wallet.hotkey.ss58_address not in metagraph.hotkeys:
            bt.logging.error(f"\nYour validator: {wallet} if not registered to chain connection: {subtensor} \nRun btcli register and try again.")
            exit()
        else:
            # Each miner gets a unique identity (UID) in the network for differentiation.
            my_subnet_uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
            bt.logging.info(f"Running validator on uid: {my_subnet_uid}")

        # Step 6: Set up initial scoring weights for validation
        # bt.logging.info("Building validation weights.")
        # scores = torch.ones_like(metagraph.S, dtype=torch.float32)
        # bt.logging.info(f"Weights: {scores}")
        axon = bt.axon(wallet=wallet, config=self.config)


        return wallet, subtensor, dendrite, metagraph, axon
    
    def setup_categories_config(self):
        self.categories_config = {
            "general_chat": GeneralChatConfig(self.validator_model, self.uids_info, validator_session = self),
            "storytelling": StorytellingConfig(self.validator_model, self.uids_info, validator_session = self),
            "wizard_model": WizardConfig(self.validator_model, self.uids_info, validator_session = self, confirmation_url=self.config.confirmation_url_wizard),
        }
        self.unique_categories = set(self.categories_config.keys())
        self.incentive_distribution = {"general_chat": 0.6, "storytelling": 0.3, "wizard_model":0.1}

    def call_uids(self, query_uids, payload):

        uid_to_axon = dict(zip(self.all_uids, self.metagraph.axons))
        query_axons = [uid_to_axon[int(uid)] for uid in query_uids]

        protocol_payload = PromptingProtocol(prompt_input = payload)

        response = self.dendrite.query(
            query_axons,
            protocol_payload,
            deserialize = True, # All responses have the deserialize function called on them before returning. 
        )

        run.log({
            "query_uids": str(query_uids),
            "payload": str(payload),
            "response": str(response)
        })

        return response

    def get_viche_uid(self, data):
        viche_uids = []
        for item in data:
            if item[1]["category"] == "viche":
                viche_uids.append(item[0])

        viche_uid = None
        if viche_uids:
            viche_uid = random.choice(viche_uids)

        return viche_uid
    
    def forward(self):

        print("Block", self.metagraph.block.item())

        print("subtempo", self.subtensor.tempo(self.config.netuid))

        # Query miners for categories
        payload = {'get_miner_info': True}
        miners_info = self.call_uids(self.all_uids, payload)

        print("Miner info", miners_info)

        uids_and_miner_info = [(int(uid), info) for uid, info in zip(self.all_uids, miners_info) if info is not None]

        # Set uid for viche model
        self.validator_model.uid = [self.get_viche_uid(uids_and_miner_info)]
        if self.validator_model.uid[0] is None:
            bt.logging.warning("Validator Not found on Network")
            return

        miner_categories = []
        active_miner_categories = []

        print("UIDS and miner info", uids_and_miner_info)

        for category_name in self.unique_categories:
            category_uids = [x[0] for x in uids_and_miner_info if x[1]['category'] == category_name]
            if category_uids:
                self.uids_info.set_category_for_uids(category_uids, category_name)
                miner_categories.append(category_name)
                active_miner_categories.append(category_name)
        
        print("self.uids_info", self.uids_info)
        print("Miner Categories", active_miner_categories)

        if not miner_categories:
            bt.logging.warning("No active miner available for specified validator categories. Skipping setting weights.")
            return
        

        # Query all category miners to get their scores
        for category_name in miner_categories:
            if category_name in self.categories_config.keys():
                print("Running: ", category_name)
                category = self.categories_config[category_name]
                try:
                    category.forward(self.call_uids)
                except Exception as e:
                    bt.logging.error("An error occured with a category: " + str(e))
                    traceback.print_exc()
            else:
                print("Skipping Invalid miner category", category_name)

        if active_miner_categories:
            self.set_weights(active_miner_categories)

    def set_weights(self, miner_categories):

        def normalize_list(floats):
            sum_of_floats = sum(floats)
            if sum_of_floats == 0:
                # If the sum is zero, distribute 1 evenly across all elements
                return [1/len(floats) for _ in floats]
            else:
                return [f / sum_of_floats for f in floats]


        scores = torch.zeros_like(self.metagraph.S, dtype=torch.float32)
        uids = torch.arange(self.metagraph.S.size(0), dtype=torch.float32)


        for category_name in miner_categories:
            incentive, miners_uid = self.categories_config[category_name].calculate_miner_incentive_score()
            incentive = normalize_list(incentive)
            print("incentive", incentive)
            incentive = [incent * self.incentive_distribution[category_name]  for incent in incentive]
            print("incentive", incentive)
            for idx, uid in enumerate(miners_uid):
                scores[uid] = incentive[idx]

        # normalizes scores before setting weights.
        weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)
        print()
        print("self.uids_info", self.uids_info)
        print("scores", scores)
        print("weights", weights)
        print("uids", uids)
        print()

        # (processed_weight_uids,processed_weights,) = bt.utils.weight_utils.process_weights_for_netuid(
        ( processed_weight_uids, processed_weights, ) = process_weights(
            uids=uids,
            weights=weights,
            netuid=self.config.netuid,
            subtensor=self.subtensor,
            metagraph=self.metagraph,
        )

        bt.logging.info(f"Setting weights: {process_weights}")
        # This is a crucial step that updates the incentive mechanism on the Bittensor blockchain.
        # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.

        result = self.subtensor.set_weights(
            netuid = self.config.netuid, # Subnet to set weights on.
            wallet = self.wallet, # Wallet to sign set weights using hotkey.
            uids = processed_weight_uids, # Uids of the miners to set weights for.
            weights = processed_weights, # Weights to set for the miners.,
            wait_for_inclusion = True
        )
        if result: bt.logging.success('Successfully set weights.')
        else: bt.logging.error('Failed to set weights.') 
        
    def run_validation(self):
        while True:
            try:
                self.forward()

                # End the current step and prepare for the next iteration.
                # step += 1

                # Resync our local state with the latest state from the blockchain.
                self.metagraph = self.subtensor.metagraph(self.config.netuid)
                # Sleep for a duration equivalent to the block time (i.e., time between successive blocks).
                sleep_blocks = 10
                bt.logging.info(f"Done with cycle, sleeping for {sleep_blocks * bt.__blocktime__} seconds.")
                time.sleep(bt.__blocktime__*sleep_blocks)

            # If we encounter an unexpected error, log it for debugging.
            except RuntimeError as e:
                bt.logging.error(e)
                traceback.print_exc()

            # If the user interrupts the program, gracefully exit.
            except KeyboardInterrupt:
                bt.logging.success("Keyboard interrupt detected. Exiting ")
                exit()



# The main function parses the configuration and runs the 
if __name__ == "__main__":

    # Parse the configuration.
    config = get_config()

    # Run the 
    session = ValidatorSession(config)
    session.run_validation()
