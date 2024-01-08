import csv
from collections import defaultdict


def reconstruct_word_journey(word_id):
    transfer_log_path = (
        "/Users/sam/Documents/Sam-Code/language_history_sim/save/transfer_log.txt"
    )
    word_journey = defaultdict(list)

    with open(transfer_log_path, "r") as file:
        reader = csv.reader(file)
        transfer_log = list(reader)

    for row in transfer_log:
        donor_word_form, adapted_word, donor_word_ID, donor_ID, recipient_ID = row
        if donor_word_ID == word_id:
            word_journey[donor_ID].append(recipient_ID)
            word_id = donor_word_ID

    return dict(word_journey)


word_journey = reconstruct_word_journey(input("Gimme ID:"))
print(word_journey)
