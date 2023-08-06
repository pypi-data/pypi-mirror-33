import random
from .fixtures import SENTENCES


def create_review(number_of_sentences):
    """
    Create a generic containing (number_of_sentences) sentences.

    Args:
        number_of_sentences (int): The number of sentences desired.

    Returns:
        A paragraph of formatted sentences.
    """

    total_sentences = len(SENTENCES)
    review = ''

    for _ in range(number_of_sentences):
        review += '{}'.format(
            SENTENCES[
                random.randint(0, total_sentences - 1)
            ]
        )
        if _ != number_of_sentences:
            review += ' '

    return review
