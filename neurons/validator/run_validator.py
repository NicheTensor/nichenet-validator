# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# Bittensor Validator Template:
# TODO(developer): Rewrite based on protocol defintion.

# Step 1: Import necessary libraries and modules
import os
import time
import torch
import argparse
import traceback
import bittensor as bt

# import this repo
import template

from neurons.validator.categories.general_chat.general_chat_config import GeneralChatConfig
from neurons.validator.categories.storytelling.storytelling_config import StoryTellingConfig
from neurons.validator.validator_model.validator_model import ValidatorModel
from neurons.validator.utils.uids_info import AllUidsInfo
import random


# Step 2: Set up the configuration parser
# This function is responsible for setting up and parsing command-line arguments.
def get_config():

    parser = argparse.ArgumentParser()
    # TODO(developer): Adds your custom validator arguments to the parser.
    parser.add_argument('--custom', default='my_custom_value', help='Adds a custom value to the parser.')
    # Adds override arguments for network and netuid.
    parser.add_argument( '--netuid', type = int, default = 1, help = "The chain subnet uid." )
    # Adds override arguments for network and netuid.
    parser.add_argument( '--model.url', type = str, default = None, help = "The url of the model endpoint." )
    # Adds override arguments for network and netuid.
    parser.add_argument( '--model.name', type = str, default = None, help = "The chain subnet uid." )
    # Adds subtensor specific arguments i.e. --subtensor.chain_endpoint ... --subtensor.network ...
    bt.subtensor.add_args(parser)
    # Adds logging specific arguments i.e. --logging.debug ..., --logging.trace .. or --logging.logging_dir ...
    bt.logging.add_args(parser)
    # Adds wallet specific arguments i.e. --wallet.name ..., --wallet.hotkey ./. or --wallet.path ...
    bt.wallet.add_args(parser)
    # Parse the config (will take command-line arguments if provided)
    # To print help message, run python3 template/miner.py --help
    config =  bt.config(parser)

    # Step 3: Set up logging directory
    # Logging is crucial for monitoring and debugging purposes.
    config.full_path = os.path.expanduser(
        "{}/{}/{}/netuid{}/{}".format(
            config.logging.logging_dir,
            config.wallet.name,
            config.wallet.hotkey,
            config.netuid,
            'validator',
        )
    )
    # Ensure the logging directory exists.
    if not os.path.exists(config.full_path): os.makedirs(config.full_path, exist_ok=True)

    # Return the parsed config.
    return config



class ValidatorSession:
    def __init__(self, config):
        self.config = config
        self.wallet, self.subtensor, self.dendrite, self.metagraph, self.my_subnet_uid = self.setup()

        self.validator_model = ValidatorModel(url=config.url, model_name=config.model_name)
        self.max_uid = max(self.metagraph.uids)
        self.uids_info = AllUidsInfo(self.max_uid)
        self.setup_categories_config()
        self.final_scores_dict = {}
        self.step = 0

    def setup(self):
        # Set up logging with the provided configuration and directory.
        bt.logging(config=config, logging_dir=config.full_path)
        bt.logging.info(f"Running validator for subnet: {config.netuid} on network: {config.subtensor.chain_endpoint} with config:")
        # Log the configuration for reference.
        bt.logging.info(config)

        # Step 4: Build Bittensor validator objects
        # These are core Bittensor classes to interact with the network.
        bt.logging.info("Setting up bittensor objects.")

        # The wallet holds the cryptographic key pairs for the validator.
        wallet = bt.wallet( config = config )
        bt.logging.info(f"Wallet: {wallet}")

        # The subtensor is our connection to the Bittensor blockchain.
        subtensor = bt.subtensor( config = config )
        bt.logging.info(f"Subtensor: {subtensor}")

        # Dendrite is the RPC client; it lets us send messages to other nodes (axons) in the network.
        dendrite = bt.dendrite( wallet = wallet )
        bt.logging.info(f"Dendrite: {dendrite}")

        # The metagraph holds the state of the network, letting us know about other miners.
        metagraph = subtensor.metagraph( config.netuid )
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
        return wallet, subtensor, dendrite, metagraph, my_subnet_uid
    
    def setup_categories_config(self):
        self.categories_config = {
            "general_chat": GeneralChatConfig(self.validator_model, self.uids_info, validator_session = self),
            "story_telling": StoryTellingConfig(self.validator_model, self.uids_info, validator_session = self)
        }
        self.unique_categories = set(self.categories_config.keys())
        self.incentive_distribution = {"general_chat": 0.6, "story_telling": 0.4}


    def call_uids(self, uids, payload, template_type = None):

        all_axons = self.metagraph.axons
        axons_to_query = [all_axons[uid] for uid in uids]

        if template_type == None:
            protocol_payload = template.protocol.PromptingTemplate( prompt_input = payload)
        else:
            protocol_payload = template.protocol.PromptingTemplate( prompt_input = payload)

        response = self.dendrite.query(
            # Send the query to all axons in the network.
            axons_to_query,
            # Construct a prompt query.
            protocol_payload,
            # All responses have the deserialize function called on them before returning.
            deserialize = True, 
        )

        return response
    
    def forward(self):

        # Query miners for categories
        all_axons = self.metagraph.axons
        all_uids = self.metagraph.uids
        
        payload = {'get_miner_info': True}
        category_responses = self.call_uids(all_uids, payload)

        uids_and_responses = [(int(uid), response) for uid, response in zip(all_uids, category_responses) if response is not None]

        for category_name in self.unique_categories:
            category_uids = [uids_and_response[0] for uids_and_response in uids_and_responses if uids_and_response[1]['category'] == category_name]

            for uid in self.uids_info.uids:
                if uid.uid in category_uids:
                    uid.category = category_name
                    print(f'{category_name} category set for uid {uid.uid}')

        #Valdiate all categories
        for category_name in self.unique_categories:
            category = self.categories_config[category_name]
            
            category.forward(self.call_uids)

        self.set_weights()

    def set_weights(self):
        for category_name in self.unique_categories:
            incentive, miners = self.categories_config[category_name].calculate_miner_incentive_score()
            print(f'Incentive for miners {miners} are {incentive}')
            incentive = [intc * self.incentive_distribution[category_name]  for intc in incentive]
            for idx, miner in enumerate(miners):
                self.final_scores_dict[miner] = incentive[idx]
        final_scores = torch.tensor(list(self.final_scores_dict.values()))
        miner_uids = list(self.final_scores_dict.keys())

        if not miner_uids:
            return
        
        # Log the results for monitoring purposes.
        # bt.logging.info(f"Received dummy responses: {responses}")

        # Periodically update the weights on the Bittensor blockchain.

        # TODO(developer): Define how the validator normalizes scores before setting weights.
        weights = torch.nn.functional.normalize(final_scores, p=1.0, dim=0)
        bt.logging.info(f"Setting weights: {weights}")
        # This is a crucial step that updates the incentive mechanism on the Bittensor blockchain.
        # Miners with higher scores (or weights) receive a larger share of TAO rewards on this subnet.
        # result = subtensor.set_weights(
        #     netuid = config.netuid, # Subnet to set weights on.
        #     wallet = wallet, # Wallet to sign set weights using hotkey.
        #     uids = metagraph.uids, # Uids of the miners to set weights for.
        #     weights = weights, # Weights to set for the miners.
        #     wait_for_inclusion = True
        # )
        result = self.subtensor.set_weights(
            netuid = self.config.netuid, # Subnet to set weights on.
            wallet = self.wallet, # Wallet to sign set weights using hotkey.
            uids = miner_uids, # Uids of the miners to set weights for.
            weights = weights, # Weights to set for the miners.
            wait_for_inclusion = True
        )
        if result: bt.logging.success('Successfully set weights.')
        else: bt.logging.error('Failed to set weights.') 
        
    def run_validation(self):
        while True:
            try:
                self.forward()

                self.set_weights()

                # End the current step and prepare for the next iteration.
                step += 1
                # Resync our local state with the latest state from the blockchain.
                self.metagraph = self.subtensor.metagraph(config.netuid)
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
    #Start session
    session = ValidatorSession(config)

    # Run the main function.
    session.run_validation( config )
