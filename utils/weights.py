import torch
import bittensor

U32_MAX = 4294967295
U16_MAX = 65535

def process_weights(
    uids,
    weights: torch.Tensor,
    netuid: int,
    subtensor: "bittensor.subtensor",
    metagraph: "bittensor.metagraph" = None,
    exclude_quantile: int = 0,
) -> torch.FloatTensor:
    bittensor.logging.debug("process_weights_for_netuid()", netuid)
    bittensor.logging.debug("weights", weights)
    bittensor.logging.debug("netuid", netuid)
    bittensor.logging.debug("subtensor", subtensor)
    bittensor.logging.debug("metagraph", metagraph)

    # Get latest metagraph from chain if metagraph is None.
    if metagraph == None:
        metagraph = subtensor.metagraph(netuid)

    # Cast weights to floats.
    if not isinstance(weights, torch.FloatTensor):
        weights = weights.type(torch.float32)

    # Network configuration parameters from an subtensor.
    # These parameters determine the range of acceptable weights for each neuron.
    quantile = exclude_quantile / U16_MAX
    min_allowed_weights = subtensor.min_allowed_weights(netuid=netuid)
    max_weight_limit = subtensor.max_weight_limit(netuid=netuid)
    bittensor.logging.debug("quantile", quantile)
    bittensor.logging.debug("min_allowed_weights", min_allowed_weights)
    bittensor.logging.debug("max_weight_limit", max_weight_limit)

    # Find all non zero weights.
    non_zero_weight_idx = torch.argwhere(weights > 0).squeeze(dim=1)
    non_zero_weight_uids = uids[non_zero_weight_idx]
    non_zero_weights = weights[non_zero_weight_idx]
    if non_zero_weights.numel() == 0 or metagraph.n < min_allowed_weights:
        bittensor.logging.warning("No non-zero weights returning all ones.")
        final_weights = torch.ones((len(uids))) / len(uids)
        bittensor.logging.debug("final_weights", final_weights)
        return torch.tensor(list(range(len(final_weights)))), final_weights

    elif non_zero_weights.numel() < min_allowed_weights:
        bittensor.logging.warning(
            "No non-zero weights less then min allowed weight, returning all ones."
        )
        # ( const ): Should this be torch.zeros( ( metagraph.n ) ) to reset everyone to build up weight?
        weights = (
            torch.ones((len(uids))) / len(uids) * 1e-5
        )  # creating minimum even non-zero weights
        weights[non_zero_weight_idx] += non_zero_weights
        bittensor.logging.debug("final_weights", weights)
        normalized_weights = bittensor.utils.weight_utils.normalize_max_weight(
            x=weights, limit=max_weight_limit
        )
        return torch.tensor(list(range(len(normalized_weights)))), normalized_weights

    bittensor.logging.debug("non_zero_weights", non_zero_weights)

    # Compute the exclude quantile and find the weights in the lowest quantile
    max_exclude = max(0, len(non_zero_weights) - min_allowed_weights) / len(
        non_zero_weights
    )
    exclude_quantile = min([quantile, max_exclude])
    lowest_quantile = non_zero_weights.quantile(exclude_quantile)
    bittensor.logging.debug("max_exclude", max_exclude)
    bittensor.logging.debug("exclude_quantile", exclude_quantile)
    bittensor.logging.debug("lowest_quantile", lowest_quantile)

    # Exclude all weights below the allowed quantile.
    non_zero_weight_uids = non_zero_weight_uids[lowest_quantile <= non_zero_weights]
    non_zero_weights = non_zero_weights[lowest_quantile <= non_zero_weights]
    bittensor.logging.debug("non_zero_weight_uids", non_zero_weight_uids)
    bittensor.logging.debug("non_zero_weights", non_zero_weights)

    # Normalize weights and return.
    normalized_weights = bittensor.utils.weight_utils.normalize_max_weight(
        x=non_zero_weights, limit=max_weight_limit
    )
    bittensor.logging.debug("final_weights", normalized_weights)

    return non_zero_weight_uids, normalized_weights