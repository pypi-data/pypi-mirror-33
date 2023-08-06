"""Enable HTTP access to a dataset."""

import argparse
import sys

import dtoolcore


def publish(dataset_uri):
    """Return access URL to HTTP enabled (published) dataset.

    Exits with error code 1 if the dataset_uri is not a dataset.
    Exits with error code 2 if the dataset cannot be HTTP enabled.
    """

    try:
        dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    except dtoolcore.DtoolCoreTypeError:
        print("Not a dataset: {}".format(dataset_uri))
        sys.exit(1)

    try:
        access_uri = dataset._storage_broker.http_enable()
    except AttributeError:
        print(
            "Datasets of type '{}' cannot be published using HTTP".format(
                dataset._storage_broker.key)
        )
        sys.exit(2)

    return access_uri


def cli():
    """Command line utility to HTTP enable (publish) a dataset."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dataset_uri",
        help="Dtool dataset URI"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only return the http URI"
    )
    args = parser.parse_args()
    access_uri = publish(args.dataset_uri)

    if args.quiet:
        print(access_uri)
    else:
        print("Dataset accessible at: {}".format(access_uri))
