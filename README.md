# NicheNet
NicheNet is a network of specialized AI models, with abilities such as: storytelling, coding, scientific writing, and general chat.
The models on the network are continously measured and ranked, to ensure you can always get the best models available in any niche.
The network uses the Bittensor protocol, meaning it is open for anyone to participate with their model and get rewarded based on performance, ensuring that the latest and best models are always available.

# Introduction to Bittensor
The Bittensor blockchain hosts multiple self-contained incentive mechanisms 'subnets'. Subnets are playing fields through which miners (those producing value) and validators (those producing consensus) determine together the proper distribution of TAO for the purpose of incentivizing the creation of value, i.e. generating digital commodities, such as intelligence, or data. Each consists of a wire protocol through which miners and validators interact and their method of interacting with Bittensor's chain consensus engine [Yuma Consensus](https://bittensor.com/documentation/validating/yuma-consensus) which is designed to drive these actors into agreement about who is creating value.

# NichetNet Validator
This repository is a template for creating nichenet  The template is designed to be simple (rewards miners for responding with the multiple of the value sent by vaidators) and can act as a starting point for those who want to write their own mechanism for validators.   
It is split into below primary files which you should rewrite:
- `template/protocol.py`: The file where the wire-protocol used by miners and validators is defined.   
- `validator/run_py`: The file to run validator

---

# NicheNet Validator
NicheNet works by using a single large language model, here called the validator-model, in order to evaluate models in a wide range of categories.
It works by first using the validator-model to generate questions that are sent to the miners, and then compare the responses to each other, again using the validator-model. In this way miner responses can be ranked and rewarded.

Since there is only a single validator-model, it is easy and fast to iterate, improve and change using only prompt engineering.
This makes it easy to add new categories for datageneration, since simply describing the task in text is enough for the validator model to generate questions for the miners and then score the responses.

# To run the Validator
```
python -m run_validator 
    --netuid <your netuid>  # Must be attained by following the instructions in the docs/running_on_*.md files 
    --subtensor.chain_endpoint <your chain url>  # Must be attained by following the instructions in the docs/running_on_*.md files
    --wallet.name <your miner wallet> # Must be created using the bittensor-cli
    --wallet.hotkey <your validator hotkey> # Must be created using the bittensor-cli
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
    --model.name <model name> # The name of deployed miner model
    --model.url <model url> # The api endpoint url for miner model
```

# Running the template
Before running the template you will need to attain a subnetwork on either Bittensor's main network, test network, or your own staging network. To create subnetworks on each of these subnets follow the instructions in files below:
- `docs/running_on_staging.md`
- `docs/running_on_testnet.md`
- `docs/running_on_mainnet.md`

---

# Installation
This repository requires python3.8 or higher. To install, simply clone this repository and install the requirements.
```bash
https://github.com/NicheTensor/nichenet-git
cd nichenet-validator
python -m pip install -r requirements.txt
python -m pip install -e .
```
---

Once you have installed this repo and attained your subnet via the instructions in the nested docs (staging, testing, or main) you can run the validator with the following commands.
```bash
# To run the Validator
python -m run_validator 
    --netuid <your netuid>  # Must be attained by following the instructions in the docs/running_on_*.md files 
    --subtensor.chain_endpoint <your chain url>  # Must be attained by following the instructions in the docs/running_on_*.md files
    --wallet.name <your miner wallet> # Must be created using the bittensor-cli
    --wallet.hotkey <your validator hotkey> # Must be created using the bittensor-cli
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
    --model.name <model name> # The name of deployed miner model
    --model.url <model url> # The api endpoint url for miner model
```

