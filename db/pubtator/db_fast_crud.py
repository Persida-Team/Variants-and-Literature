# fast_crud.py

from db_models import Article, Disease, Gene, Variant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from VARIABLES import DATABASE_URI

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()


# TODO: implement preload_lookup_table based on add or delete pm_ids, genes, diseases, variants
def preload_lookup_tables():
    print("Preloading lookup tables...")
    genes_lookup = {g.ncbi_id: g for g in session.query(Gene).all()}
    diseases_lookup = {d.original_ontology: d for d in session.query(Disease).all()}
    variants_lookup = {v.exact_match: v for v in session.query(Variant).all()}
    articles_lookup = {a.pm_id: a for a in session.query(Article).all()}
    print("Preloaded lookup tables.")
    return genes_lookup, diseases_lookup, variants_lookup, articles_lookup


def prepare_articles_for_commit(batch, lookup):
    genes_lookup, diseases_lookup, variants_lookup, articles_lookup = lookup

    new_genes = []
    new_diseases = []
    new_variants = []
    new_articles = []

    print(f"Processing batch of size {len(batch)}...")
    for article_data in batch:
        pm_id = article_data["pm_id"]
        ncbi_id = article_data.get("ncbi_id", None)
        hgnc_symbol = article_data.get("hgnc_symbol", None)
        original_ontology = article_data.get("original_ontology", None)
        variant_data = article_data.get("variant_data", None)

        article = articles_lookup.get(pm_id)
        if not article:
            article = Article(pm_id=pm_id)
            new_articles.append(article)
            articles_lookup[pm_id] = article

        if ncbi_id:
            gene = genes_lookup.get(ncbi_id)
            if not gene:
                gene = Gene(ncbi_id=ncbi_id, hgnc_symbol=hgnc_symbol)
                new_genes.append(gene)
                genes_lookup[ncbi_id] = gene
            if gene not in article.genes:
                article.genes.append(gene)

        if original_ontology:
            disease = diseases_lookup.get(original_ontology)
            if not disease:
                disease = Disease(original_ontology=original_ontology)
                new_diseases.append(disease)
                diseases_lookup[original_ontology] = disease
            if disease not in article.diseases:
                article.diseases.append(disease)

        if variant_data:
            identified, exact_match = variant_data
            if not identified and exact_match:
                continue
            variant = variants_lookup.get(exact_match)
            if not variant:
                variant = Variant(exact_match=exact_match, identified=identified)
                new_variants.append(variant)
                variants_lookup[exact_match] = variant
            if variant not in article.variants:
                article.variants.append(variant)

    # not committing yet, just adding to the session
    session.add_all(new_genes + new_diseases + new_variants + new_articles)
    print(
        f"Added {len(new_genes)} genes, {len(new_diseases)} diseases, {len(new_variants)} variants, and {len(new_articles)} articles to the session."
    )
    return session, len(new_articles)


def extract_columns_lazy(file_path, col1_name, col2_name):
    import csv

    with open(file_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (row[col1_name], row[col2_name])


def chunked_iterator(iterator, batch_size):
    batch = []
    for item in iterator:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def populate_articles_with_pmc_ids():

    csv_data = extract_columns_lazy("../PMC-ids.csv", "PMID", "PMCID")
    batch_size = 100_000
    for batch_num, batch in enumerate(chunked_iterator(csv_data, batch_size)):

        pmid_to_pmcid = {pmid: pmcid for pmid, pmcid in batch}
        pmids = list(pmid_to_pmcid.keys())
        # Load matching articles
        articles = session.query(Article).filter(Article.pm_id.in_(pmids)).all()

        for article in articles:
            pmcid = pmid_to_pmcid.get(article.pm_id)
            if pmcid:
                article.pmc_id = pmcid

        print(f"Batch {batch_num + 1}: Updated {len(articles)} articles.")
        session.commit()
    session.close()


def only_update_diseases_with_mondo_ids(mesh_to_mondo_input_dict_path):
    import json

    with open(mesh_to_mondo_input_dict_path, "r") as f:
        mesh_to_mondo_input_dict = json.load(f)

    # Query only diseases that have original_ontology present in the dict keys
    mesh_ids = list(mesh_to_mondo_input_dict.keys())
    diseases = (
        session.query(Disease).filter(Disease.original_ontology.in_(mesh_ids)).all()
    )

    updated_count = 0
    for disease in diseases:
        mondo_id = mesh_to_mondo_input_dict.get(disease.original_ontology)
        if mondo_id and disease.mondo_id != mondo_id:
            disease.mondo_id = mondo_id
            updated_count += 1

    print(diseases[:5])
    print(f"Updated {updated_count} diseases with MONDO IDs.")
    session.commit()
    session.close()


def find_duplicate_values_in_input_json(mesh_to_mondo_input_dict_path):
    import json

    with open(mesh_to_mondo_input_dict_path, "r") as f:
        mesh_to_mondo_input_dict = json.load(f)

    duplicates = {}
    for key, value in mesh_to_mondo_input_dict.items():
        if value in duplicates:
            duplicates[value].append(key)
        else:
            duplicates[value] = [key]

    # remove keys with only one value
    duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(duplicates)
    print(len(duplicates))


if __name__ == "__main__":
    # populate_articles_with_pmc_ids()
    only_update_diseases_with_mondo_ids("../mesh_to_mondo.json")
    # find_duplicate_values_in_input_json("../mesh_to_mondo.json")
