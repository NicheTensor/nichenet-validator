import os
import time
import torch
import argparse
import traceback
import bittensor as bt

import template

from validator.categories.general_chat.general_chat_config import GeneralChatConfig
from validator.categories.storytelling.storytelling_config import StoryTellingConfig
from validator.validator_model.validator_model import ValidatorModel
from validator.utils.uids_info import AllUidsInfo
from validator.utils.weights import process_weights

def get_config():

    parser = argparse.ArgumentParser()

    parser.add_argument( '--netuid', type = int, default = 1, help = "The chain subnet uid." )
    parser.add_argument( '--model.url', type = str, default = None, help = "The url of the model endpoint." )
    parser.add_argument( '--model.name', type = str, default = None, help = "The name of model" )

    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)

    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)

    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)

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
        self.wallet, self.subtensor, self.dendrite, self.metagraph = self.setup()

        if config.model.url is None or config.model.name is None:
            bt.logging.error("Please specify --model.url and --model.name for the validator")
            exit()

        self.validator_model = ValidatorModel(url=self.config.model.url, model_name=self.config.model.name)
        self.max_uid = max(self.metagraph.uids)

        self.all_uids = [int(uid) for uid in self.metagraph.uids]
        self.uids_info = AllUidsInfo(self.max_uid)
        self.setup_categories_config()
        self.step = 0

    def setup(self):
        
        # setup logging
        bt.logging(config=self.config, logging_dir=self.config.full_path)
    
        bt.logging.info(self.config)

        # The wallet holds the cryptographic key pairs for the validator.
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
        return wallet, subtensor, dendrite, metagraph
    
    def setup_categories_config(self):
        self.categories_config = {
            "general_chat": GeneralChatConfig(self.validator_model, self.uids_info, validator_session = self),
            "story_telling": StoryTellingConfig(self.validator_model, self.uids_info, validator_session = self)
        }
        self.unique_categories = set(self.categories_config.keys())
        self.incentive_distribution = {"general_chat": 0.6, "story_telling": 0.4}

    def call_uids(self, query_uids, payload):

        uid_to_axon = dict(zip(self.all_uids, self.metagraph.axons))
        query_axons = [uid_to_axon[int(uid)] for uid in query_uids]

        protocol_payload = template.protocol.PromptingTemplate(prompt_input = payload)

        response = self.dendrite.query(
            query_axons,
            protocol_payload,
            deserialize = True, # All responses have the deserialize function called on them before returning. 
        )

        return response
    
    def forward(self):

        print("Block", self.metagraph.block.item())

        print("subtempo", self.subtensor.tempo(self.config.netuid))

        # Query miners for categories
        payload = {'get_miner_info': True}
        miners_info = self.call_uids(self.all_uids, payload)

        uids_and_miner_info = [(int(uid), info) for uid, info in zip(self.all_uids, miners_info) if info is not None]

        miner_categories = []

        for category_name in self.unique_categories:
            category_uids = [x[0] for x in uids_and_miner_info if x[1]['category'] == category_name]
            if category_uids:
                self.uids_info.set_category_for_uids(category_uids, category_name)
                miner_categories.append(category_name)

        if not miner_categories:
            bt.logging.warning("No active miner available for specified validator categories. Skipping setting weights.")
            return
        
        active_miner_categories = []

        # Query all category miners to get their scores
        for category_name in miner_categories:
            category = self.categories_config[category_name]
            if category.forward(self.call_uids):
                active_miner_categories.append(category_name)

        if active_miner_categories:
            self.set_weights(active_miner_categories)

    def set_weights(self, miner_categories):

        uid_to_scores = {}

        for category_name in miner_categories:
            incentive, miners_uid = self.categories_config[category_name].calculate_miner_incentive_score()
            incentive = [intc * self.incentive_distribution[category_name]  for intc in incentive]
            for idx, uid in enumerate(miners_uid):
                uid_to_scores[uid] = incentive[idx]

        if not uid_to_scores:
            return
                
        scores = torch.tensor(list(uid_to_scores.values()))
        miner_uids = torch.tensor(list(uid_to_scores.keys()))

        # normalizes scores before setting weights.
        weights = torch.nn.functional.normalize(scores, p=1.0, dim=0)

        # (processed_weight_uids,processed_weights,) = bt.utils.weight_utils.process_weights_for_netuid(
        ( processed_weight_uids, processed_weights, ) = process_weights(
            uids=miner_uids,
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
                time.sleep(bt.__blocktime__)

            # If we encounter an unexpected error, log it for debugging.
            except RuntimeError as e:
                bt.logging.error(e)
                traceback.print_exc()

            # If the user interrupts the program, gracefully exit.
            except KeyboardInterrupt:
                bt.logging.success("Keyboard interrupt detected. Exiting validator.")
                exit()



# The main function parses the configuration and runs the validator.
if __name__ == "__main__":

    # Parse the configuration.
    config = get_config()

    # Run the validator.
    session = ValidatorSession(config)
    session.run_validation()
