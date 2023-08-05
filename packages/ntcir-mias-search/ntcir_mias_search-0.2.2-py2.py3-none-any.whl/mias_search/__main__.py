"""
This is the command-line interface for the MIaS Search package.
"""

from argparse import ArgumentParser
import gzip
import logging
from logging import getLogger
from pathlib import Path
import pickle
from sys import stdout
from urllib.parse import urlparse

import numpy  # Required to unpickle positions.pkl.gz

from .processing import get_results, merge_results, rerank_results, Topic, WebMIaSIndex


LOG_PATH = Path("__main__.log")
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(message)s"
LOGGER = getLogger(__name__)
ROOT_LOGGER = getLogger()


def main():
    """ Main entry point of the app """
    ROOT_LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.StreamHandler(LOG_PATH.open("wt"))
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    ROOT_LOGGER.addHandler(file_handler)

    terminal_handler = logging.StreamHandler(stdout)
    terminal_handler.setFormatter(formatter)
    terminal_handler.setLevel(logging.INFO)
    ROOT_LOGGER.addHandler(terminal_handler)

    LOGGER.debug("Parsing command-line arguments")
    parser = ArgumentParser(
        description="""
            Use topics in the NTCIR-10 Math, NTCIR-11 Math-2, and NTCIR-12 MathIR format to query
            the WebMIaS interface of the MIaS Math Information Retrieval system and to retrieve
            result document lists.
        """)
    parser.add_argument(
        "--dataset", required=True, type=Path, help="""
            A path to a directory containing a dataset in the NTCIR-11 Math-2, and NTCIR-12 MathIR
            XHTML5 format. The directory does not need to exist, since the path is only required for
            extracting data from the file with estimated positions of paragraph identifiers.
        """)
    parser.add_argument(
        "--topics", required=True, type=Path, help="""
            A path to a file containing topics in the NTCIR-10 Math, NTCIR-11 Math-2, and NTCIR-12
            MathIR format.
        """)
    parser.add_argument(
        "--positions", type=Path, required=True, help="""
            The path to the file, where the estimated positions of all paragraph identifiers from
            our dataset were stored by the NTCIR Math Density Estimator package.
        """)
    parser.add_argument(
        "--estimates", type=Path, required=True, help="""
            The path to the file, where the density, and probability estimates for our dataset were
            stored by the NTCIR Math Density Estimator package.
        """)
    parser.add_argument(
        "--webmias-url", type=urlparse, required=True, help="""
            The URL at which a WebMIaS Java Servlet has been deployed.
        """)
    parser.add_argument(
        "--webmias-index-number", type=int, default=0, help="""
            The numeric identifier of the WebMIaS index that corresponds to the dataset. Defaults to
            %(default)d.
        """)
    parser.add_argument(
        "--num-workers-querying", type=int, default=1, help="""
            The number of processes that will send queries to WebMIaS. Defaults to %(default)d. Note
            that querying, reranking, and merging takes place simmultaneously.
        """)
    parser.add_argument(
        "--num-workers-reranking", type=int, default=5, help="""
            The number of processes that will rerank results. Defaults to %(default)d. Note that
            querying, reranking, and merging takes place simmultaneously.
        """)
    parser.add_argument(
        "--num-workers-merging", type=int, default=9, help="""
            The number of processes that will merge results. Defaults to %(default)d. Note that
            querying, reranking, and merging takes place simmultaneously.
        """)
    parser.add_argument(
        "--output-directory", type=Path, required=True, help="""
            The path to the directory, where the output files will be stored.
        """)
    args = parser.parse_args()

    LOGGER.debug("Performing sanity checks on the command-line arguments")
    assert args.topics.exists() or args.topics.is_file(), \
        "The file %s with topics does not exist" % args.topics
    assert args.positions.exists() or args.positions.is_file(), \
        "The file %s with positions does not exist" % args.positions
    assert args.estimates.exists() or args.estimates.is_file(), \
        "The file %s with estimates does not exist" % args.estimates
    assert args.output_directory.exists() and args.output_directory.is_dir(), \
        "Directory %s, where the output files are to be stored, does not exist" % \
        args.output_directory
    assert args.webmias_index_number >= 0
    assert args.num_workers_querying > 0
    assert args.num_workers_reranking > 0
    assert args.num_workers_merging > 0

    LOGGER.info("Reading topics from %s", args.topics.name)
    with args.topics.open("rt") as f:
        topics = list(Topic.from_file(f))
    assert len(topics) >= 2
    LOGGER.info("%d topics (%s, %s, ...) contain %d formulae, and %d keywords",
        len(topics), topics[0], topics[1],
        sum(len(topic.formulae) for topic in topics),
        sum(len(topic.keywords) for topic in topics))

    LOGGER.info(
        "Establishing connection with a WebMIaS Java Servlet at %s", args.webmias_url.geturl())
    webmias = WebMIaSIndex(args.webmias_url, args.webmias_index_number)

    LOGGER.info("Unpickling %s", args.positions.name)
    with gzip.open(args.positions.open("rb"), "rb") as f:
        positions = pickle.load(f)[args.dataset]

    LOGGER.info("Unpickling %s", args.estimates.name)
    with gzip.open(args.estimates.open("rb"), "rb") as f:
        estimates = pickle.load(f)[-1]

    LOGGER.info("Querying %s, reranking, and merging", webmias)
    results = get_results(topics, webmias, args.output_directory, args.num_workers_querying)
    reranked_results = rerank_results(
        results, positions, estimates, args.output_directory, args.num_workers_reranking)
    identifiers = positions.keys()
    final_results = merge_results(
        reranked_results, identifiers, args.output_directory, args.num_workers_merging)
    for _ in final_results: pass


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
