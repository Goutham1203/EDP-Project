import hashlib
from datetime import datetime

class Blockchain:
    @staticmethod
    def calculate_hash(voter_id, candidate_id, timestamp, previous_hash):
        """
        Calculate SHA-256 hash for a block (vote).
        """
        data = f"{voter_id}{candidate_id}{timestamp}{previous_hash}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_chain(votes):
        """
        Verify the integrity of the blockchain by recalculating hashes and checking previous_hash links.
        Returns a tuple: (is_valid, error_message)
        """
        if not votes:
            return True, "Chain is empty"

        for i in range(1, len(votes)):
            current_vote = votes[i]
            previous_vote = votes[i-1]

            # 1. Check if previous_hash matches the hash of the previous vote
            if current_vote['previous_hash'] != previous_vote['hash']:
                return False, f"Broken link at vote ID {current_vote['id']}"

            # 2. Recalculate the hash of the current vote and check if it matches
            recalculated_hash = Blockchain.calculate_hash(
                current_vote['voter_id'],
                current_vote['candidate_id'],
                current_vote['timestamp'],
                current_vote['previous_hash']
            )

            if current_vote['hash'] != recalculated_hash:
                return False, f"Tampering detected at vote ID {current_vote['id']}"

        return True, "Chain is valid"
