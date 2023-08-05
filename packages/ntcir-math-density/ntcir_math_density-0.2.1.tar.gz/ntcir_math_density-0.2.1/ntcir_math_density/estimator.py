"""
These are the estimator functions for the NTCIR Math Density Estimator package.
"""

from logging import getLogger
from multiprocessing import Pool
from pathlib import Path

from numpy import array_split, concatenate, log, exp
from sklearn.neighbors import KernelDensity
from tqdm import tqdm


LOGGER = getLogger(__name__)
KERNEL = {
    "kernel": "gaussian",
    "bandwidth": 0.05,
}
PICKLED_POSITIONS = Path("positions.pkl.gz")


def get_judged_identifiers(input_file):
    """
    Extracts the paragraph identifiers, and the scores of the judged paragraphs from relevance
    judgements in the NTCIR-11 Math-2, and NTCIR-12 MathIR format.

    Parameters
    ----------
    input_file : file
        The input file containing relevance judgements in the NTCIR-11 Math-2, and NTCIR-12 MathIR
        format.

    Yields
    ------
    (str, float)
        The judged paragraph identifiers, and scores.
    """
    for line in tqdm(list(input_file)):
        _, __, identifier, score = line.split(' ')
        yield (identifier, float(score))


def get_identifier(document):
    """
    Extracts the paragraph identifier from a path to a paragraph in the XHTML5 ZIP format.

    Parameters
    ----------
    document : Path
        A path to a paragraph in the XHTML5 ZIP format.

    Returns
    -------
    str
        The paragraph identifier.
    """
    return document.with_suffix("").stem


def get_all_identifiers(dataset):
    """
    Extracts paragraph identifiers from a dataset in the NTCIR-11 Math-2, and NTCIR-12 MathIR XHTML5
    format.

    Parameters
    ----------
    dataset : Path
        A path to a dataset.

    Yields
    -------
    (Path, str)
        A parent directory of a paragraph, and the identifier of the paragraph.
    """
    for document in tqdm(
            dataset.glob("**/*.xhtml.zip"), desc="get_all_identifiers(%s)" % dataset.name):
        identifier = get_identifier(document)
        directory = document.parents[0]
        yield (directory, identifier)


def get_paragraph_number(identifier):
    """
    Extracts the number of a paragraph from the identifier, and the parent directory of the
    paragraph.

    Parameters
    ----------
    directory : Path
        A parent directory of a paragraph.
    identifier : str
        An identifier of a paragraph.

    Returns
    -------
    int
        The number of the paragraph.
    """
    paragraph_number = int(identifier.split('_')[-1]) - 1
    assert paragraph_number >= 0
    return paragraph_number


def get_position(directory, identifier):
    """
    Extracts the position of a paragraph from the identifier, and the parent directory of the
    paragraph.

    Parameters
    ----------
    directory : Path
        A parent directory of a paragraph.
    identifier : str
        An identifier of a paragraph.

    Returns
    -------
    float
        The estimated position of the paragraph in the range [0; 1).
    """
    paragraph_number = get_paragraph_number(identifier)
    paragraph_total = max(  # Not all paragraphs are stored, e.g. because of processing errors.
        get_paragraph_number(get_identifier(document)) + 1
        for document in directory.iterdir())
    assert paragraph_total > paragraph_number and paragraph_total > 0
    position = paragraph_number / paragraph_total
    return position


def _get_position_worker(args):
    directory, identifier = args
    return (directory, identifier, get_position(directory, identifier))


def get_all_positions(dataset, num_workers=1):
    """
    Extracts paragraph identifiers, and positions from a dataset in the NTCIR-11 Math-2, and
    NTCIR-12 MathIR XHTML5 format.

    Parameters
    ----------
    dataset : Path
        A path to a dataset.
    num_workers : int, optional
        The number of processes that will extract paragraph positions from the dataset.

    Yields
    -------
    (Path, str, float)
        A parent directory of a paragraph, the identifier of the paragraph, and an estimate of the
        position of the paragraph in its parent document. The position is in the range [0; 1).
    """
    positions = []
    identifiers = tqdm(
        list(get_all_identifiers(dataset)), desc="get_all_positions(%s)" % dataset.name)
    with Pool(num_workers) as pool:
        for directory, identifier, position in pool.map(_get_position_worker, identifiers):
            positions.append((directory, identifier, position))
    for directory, identifier, position in positions:
        yield (directory, identifier, position)


def get_estimators(positions_all, positions_relevant):
    """
    Extracts density estimators from a judged sample of paragraph positions.

    Parameters
    ----------
    positions_all : dict of (Path, float)
        A sample of paragraph positions from various datasets in the NTCIR-11
        Math-2, and NTCIR-12 MathIR format.
    positions_relevant : dict of (Path, float)
        A sample of relevant paragraph positions from various datasets in the
        NTCIR-11 A subsample of relevant paragraph positions.

    Returns
    -------
    (float, KernelDensity, KernelDensity)
        An estimate of P(relevant), and estimators of p(position), and p(position | relevant).
    """
    samples_all = [
        (position,) for _, positions in positions_all.items() for position in positions]
    samples_relevant = [
        (position,) for _, positions in positions_relevant.items() for position in positions]
    estimators = dict()
    estimators["P(relevant)"] = len(samples_relevant) / len(samples_all)
    LOGGER.info("Fitting prior p(position) density estimator")
    estimators["p(position)"] = KernelDensity(**KERNEL).fit(samples_all)
    LOGGER.info("Fitting conditional p(position | relevant) density estimator")
    estimators["p(position|relevant)"] = KernelDensity(**KERNEL).fit(samples_relevant)
    return (
        estimators["P(relevant)"], estimators["p(position)"], estimators["p(position|relevant)"])


def get_estimates(estimators_tuple, positions, num_workers=1):
    """
    Estimates densities, and probabilities for paragraph positions.

    Parameters
    ----------
    estimators_tuple : (float, KernelDensity, KernelDensity)
        An estimate of the prior probability P(relevant), an estimator of the prior density
        p(position), and an estimator of the conditional density p(position | relevant).
    positions : iterable of float
        Paragraph positions for which densities, and probabilities will be estimated.
    num_workers : int, optional
        The number of processes that will compute the estimates.

    Returns
    -------
    five-tuple of (sequence of float)
        Estimates of P(relevant), p(position), p(position | relevant), P(position, relevant), and
        P(relevant | position) in the form of histograms.
    """
    estimators = dict()
    estimators["P(relevant)"], estimators["p(position)"], \
        estimators["p(position|relevant)"] = estimators_tuple

    log_estimates = dict()
    log_estimates["P(relevant)"] = log(estimators["P(relevant)"])
    X = [(position,) for position in positions]
    with Pool(num_workers) as pool:
        first_job = pool.map_async(estimators["p(position)"].score_samples, tqdm(
            array_split(X, num_workers), desc="p(position)"))
        second_job = pool.map_async(estimators["p(position|relevant)"].score_samples, tqdm(
            array_split(X, num_workers), desc="p(position | relevant)"))
        log_estimates["p(position)"] = concatenate(first_job.get())
        log_estimates["p(position|relevant)"] = concatenate(second_job.get())
    log_estimates["P(position,relevant)"] = \
        log_estimates["p(position|relevant)"] + log_estimates["P(relevant)"]
    log_estimates["P(relevant|position)"] = \
        log_estimates["P(position,relevant)"] - log_estimates["p(position)"]
    return (
        [estimators["P(relevant)"]] * len(X), exp(log_estimates["p(position)"]),
        exp(log_estimates["p(position|relevant)"]), exp(log_estimates["P(position,relevant)"]),
        exp(log_estimates["P(relevant|position)"]))
