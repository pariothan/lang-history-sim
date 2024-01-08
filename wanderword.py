import csv
from collections import defaultdict


def reconstruct_word_journey(word_id):
    transfer_log_path = (
        "/Users/sam/Documents/Sam-Code/language_history_sim/save/transfer_log.txt"
    )
    word_journey = {}

    with open(transfer_log_path, "r") as file:
        reader = csv.reader(file)
        transfer_log = list(reader)

    for row in transfer_log:
        (
            donor_word_form,
            adapted_word,
            donor_word_ID,
            donor_ID,
            recipient_ID,
            donor_name,
            recipient_name,
        ) = row
        if donor_word_ID == word_id:
            if not word_journey.get(str(donor_ID) + donor_word_form):
                word_journey[str(donor_ID) + donor_word_form] = {}
            if not word_journey[str(donor_ID) + donor_word_form].get(
                str(recipient_ID) + adapted_word
            ):
                word_journey[str(donor_ID) + donor_word_form][
                    str(recipient_ID) + adapted_word
                ] = {}

    return word_journey


def to_bracketed(tree, node):
    children = [to_bracketed(tree, child) for child in tree.get(node, {})]
    return f"[{node}{''.join(children)}]"


print(reconstruct_word_journey("8192"))

word_journey = reconstruct_word_journey(8192)
bracketed = to_bracketed(word_journey)
print(bracketed)
