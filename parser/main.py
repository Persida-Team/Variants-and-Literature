import logging
import os
import sys
import time

from combined_parsing import (
    do_all_in_threads,
    do_one_article,
    do_one_article_parallel,
    do_one_article_with_logging,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def print_help_all():
    print(
        """
Usage:   python main.py --all <txt_data_dir>        <xml_data_dir>        <save_dir>    
Example: python main.py --all data/txt/PMC000xxxxxx data/xml/PMC000xxxxxx parsed_articles/
        """
    )


def print_help_one():
    print(
        """
Usage:   python main.py --one <pmc_id> <txt_data_dir>        <xml_data_dir>        <save_dir>
Example: python main.py --one PMC13900 data/txt/PMC000xxxxxx data/xml/PMC000xxxxxx parsed_articles/
        """
    )


def main():
    # take arguments from command line
    args = sys.argv[1:]
    if not len(args):
        print("Provide correct arguments to the script")
        print_help_one()
        print_help_all()
        sys.exit(1)

    mode = args[0]
    if mode == "--all":
        if len(args) != 4:
            print("Provide correct arguments to the script")
            print_help_all()
            sys.exit(1)
    elif mode == "--one":
        if len(args) != 5 or not args[1].startswith("PMC"):
            print("Provide correct arguments to the script")
            print_help_one()
            sys.exit(1)
    else:
        if not len(args):
            print("Provide correct arguments to the script")
            print_help_one()
            print_help_all()
            sys.exit(1)
    if mode == "--one":
        pmc_id, txt_data_dir, xml_data_dir, save_dir = args[1:]
        do_one_article(pmc_id, txt_data_dir, xml_data_dir, save_dir)
    elif mode == "--all":
        start = time.time()
        txt_data_dir_, xml_data_dir_, save_dir_ = args[1:]

        for pmc_group in os.listdir(txt_data_dir_):
            if pmc_group in [
                "PMC001xxxxxx",
                "PMC004xxxxxx",
                "PMC005xxxxxx",
                "PMC007xxxxxx",
                "PMC008xxxxxx",
                "PMC009xxxxxx",
                "PMC011xxxxxx",
            ]:
                continue
            if not os.path.isdir(os.path.join(txt_data_dir_, pmc_group)):
                continue
            txt_data_dir = os.path.join(txt_data_dir_, pmc_group)
            xml_data_dir = os.path.join(xml_data_dir_, pmc_group)
            save_dir = os.path.join(save_dir_, pmc_group)

            # list all the pmc_ids and remove the .txt extension
            pmc_ids = list(set(list(map(lambda x: x[:-4], os.listdir(txt_data_dir)))))
            pmc_number = len(pmc_ids)
            # failed_number = do_all_parallel(
            #     pmc_ids,
            #     txt_data_dir,
            #     xml_data_dir,
            #     save_dir,
            #     pmc_number,
            #     number_of_workers=30,
            # )
            # failed_number = do_all(
            #     pmc_ids,
            #     txt_data_dir,
            #     xml_data_dir,
            #     save_dir,
            #     pmc_number,
            # )
            do_all_in_threads(
                pmc_ids,
                txt_data_dir,
                xml_data_dir,
                save_dir,
                pmc_number,
                num_threads=10,
            )
            failed_number = 0
            end = time.time()
            print(
                f"Done processing {pmc_number - failed_number}/{pmc_number} articles, where {failed_number} failed. Time took : {end - start}"
            )
    else:
        print("Provide correct arguments to the script")
        print_help_one()
        print_help_all()
        sys.exit(1)


def do_all(pmc_ids, txt_data_dir, xml_data_dir, save_dir, pmc_number):
    failed_number = 0
    for i, pmc_id in enumerate(pmc_ids):
        print(f"Processing {i+1}/{pmc_number}: {pmc_id}", end="\r")
        if do_one_article_with_logging(pmc_id, txt_data_dir, xml_data_dir, save_dir):
            continue
        failed_number += 1
    return failed_number


def do_all_parallel(
    pmc_ids, txt_data_dir, xml_data_dir, save_dir, pmc_number, number_of_workers=None
):
    import concurrent.futures

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=number_of_workers
    ) as executor:
        results = list(
            executor.map(
                do_one_article_parallel,
                pmc_ids,
                [txt_data_dir] * pmc_number,
                [xml_data_dir] * pmc_number,
                [save_dir] * pmc_number,
            )
        )
    failed_number = results.count(False)
    return failed_number


if __name__ == "__main__":
    main()
