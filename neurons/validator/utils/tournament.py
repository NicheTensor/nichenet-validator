
def single_elimination_tournament(model, category, question, responses, uids):
    queue = [(uids[i], responses[i]) for i in range(len(responses))] #[(uid, response), (uid, response)]
    matches = []

    round_counter = 1
    while len(queue) > 1:
        round_queue = queue.copy()
        queue = []
        while len(round_queue) > 1:
            response_1 = round_queue.pop(0)
            response_2 = round_queue.pop(0)

            winner_index = model.vs_response(category, question, response_1[1], response_2[1])
            if winner_index == 0:
                winner = response_1
            else:
                winner = response_2

            matches.append({
                "round": round_counter,
                "response_indexes": [response_1[0], response_2[0]],
                "winner": winner[0]
            })

            queue.append(winner)
        if len(round_queue) == 1:
            queue.append(round_queue[0])
        round_counter += 1
    winner = queue[0][0]
    return matches, winner


def new_elo_from_match(elo_1, elo_2, first_winner, k=16):

    expected_score_1 = 1 / (1 + 10 ** ((elo_2 - elo_1) / 400))
    expected_score_2 = 1 - expected_score_1

    score_1 = 1 if first_winner else 0
    score_2 = 1 - score_1

    elo_1_new = elo_1 + k * (score_1 - expected_score_1)
    elo_2_new = elo_2 + k * (score_2 - expected_score_2)

    return elo_1_new, elo_2_new


