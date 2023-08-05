#!/usr/bin/env python

"""Run all the benchmarks with specific parameters"""
import argparse

from scvi.benchmark import run_benchmarks
from scvi.dataset import load_datasets

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=250, help="how many times to process the dataset")
    parser.add_argument("--dataset", type=str, default="cortex", help="which dataset to process")
    parser.add_argument("--nobatches", action='store_true', help="whether to ignore batches")
    parser.add_argument("--nocuda", action='store_true',
                        help="whether to use cuda (will apply only if cuda is available")
    parser.add_argument("--benchmark", action='store_true',
                        help="whether to use cuda (will apply only if cuda is available")
    parser.add_argument("--url", type=str, help="the url for downloading dataset")
    args = parser.parse_args()

    dataset = load_datasets(args.dataset, url=args.url)
    run_benchmarks(dataset, n_epochs=args.epochs, use_batches=(not args.nobatches), use_cuda=(not args.nocuda),
                   show_batch_mixing=True, benchmark=args.benchmark)
