# NicheNet Validator
NicheNet works by using a single large language model, here called the validator-model, in order to evaluate models in a wide range of categories.
It works by first using the validator-model to generate questions that are sent to the miners, and then compare the responses to each other, again using the validator-model. In this way miner responses can be ranked and rewarded.

Since there is only a single validator-model, it is easy and fast to iterate, improve and change using only prompt engineering.
This makes it easy to add new categories for datageneration, since simply describing the task in text is enough for the validator model to generate questions for the miners and then score the responses.

# To run the Validator
```
python -m validator.run_validator 
    --netuid <your netuid>  # Must be attained by following the instructions in the docs/running_on_*.md files 
    --subtensor.chain_endpoint <your chain url>  # Must be attained by following the instructions in the docs/running_on_*.md files
    --wallet.name <your miner wallet> # Must be created using the bittensor-cli
    --wallet.hotkey <your validator hotkey> # Must be created using the bittensor-cli
    --logging.debug # Run in debug mode, alternatively --logging.trace for trace mode
    --model.name <model name> # The name of deployed miner model
    --model.url <model url> # The api endpoint url for miner model
```