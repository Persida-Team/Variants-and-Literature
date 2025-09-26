import process_input_files_into_db_entries as pifidb


def test_1():
    from db_crud import create_article_with_metadata, get_articles_by_gene

    article = create_article_with_metadata(
        pm_id="123",
        gene_symbols=["BRCA2"],
        disease_names=["Breast Cancer"],
        variant_names=["rs123456"],
    )

    articles = get_articles_by_gene("BRCA1")
    for a in articles:
        print(a.pm_id)


def commit_generator_to_database_with_batch(generator, batch_size):

    import time
    from itertools import islice

    from db_fast_crud import preload_lookup_tables, prepare_articles_for_commit

    start_time = time.time()
    count_so_far = 0
    while True:
        batch_start_time = time.time()
        batch = list(islice(generator, batch_size))
        count_so_far += len(batch)
        if not batch:
            break

        lookup = preload_lookup_tables()

        # session, new_count = prepare_articles_for_commit(batch, ({},{}, {}, {}))
        session, new_count = prepare_articles_for_commit(batch, lookup)
        session.commit()
        print(
            f"Committed {new_count:_}. Total so far: {count_so_far:_}. Time: {time.time() - batch_start_time:.2f} seconds"
        )

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")


def populate_pm_ids():
    from process_input_files_into_db_entries import get_human_pm_ids

    batch_size = 500_000
    generator = get_human_pm_ids()
    commit_generator_to_database_with_batch(generator, batch_size)


def populate_gene_ncbi_ids():
    from process_input_files_into_db_entries import get_gene_ncbi_ids

    batch_size = 1_000_000
    generator = get_gene_ncbi_ids(skip=1_500_000)
    print("Populating gene ncbi ids")
    commit_generator_to_database_with_batch(generator, batch_size)


def populate_disease_ids():
    from process_input_files_into_db_entries import get_disease_original_ontology

    batch_size = 500_000
    generator = get_disease_original_ontology()
    commit_generator_to_database_with_batch(generator, batch_size)


def populate_variant_ids():
    from process_input_files_into_db_entries import get_variants_data

    batch_size = 500_000
    generator = get_variants_data()
    commit_generator_to_database_with_batch(generator, batch_size)


if __name__ == "__main__":
    # test_1()
    # test2_()
    # populate_pm_ids()
    populate_gene_ncbi_ids()
    # populate_disease_ids()
    # populate_variant_ids()

    # pifidb.check_if_human_gene_and_add_symbols()
    print("doing this")
    # gen = pifidb.get_gene_ncbi_ids()
    # print(next(gen))
    # print("finished this")
    # for i in range(1, 10):
    #     print(next(gen))
