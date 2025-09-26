from typing import List, Optional

from db.pubtator.db_models import Article, Disease, Gene, Variant
from db.pubtator.VARIABLES import get_session
from sqlalchemy.orm import Session


def get_variant_ids_for_article(session: Session, article_id: int) -> List[int]:
    article = session.get(Article, article_id)
    return [v.id for v in article.variants] if article else []


def get_gene_ids_for_article(session: Session, article_id: int) -> List[int]:
    article = session.get(Article, article_id)
    return [g.id for g in article.genes] if article else []


def get_disease_ids_for_article(session: Session, article_id: int) -> List[int]:
    article = session.get(Article, article_id)
    return [d.id for d in article.diseases] if article else []


def get_article_ids_for_variant(session: Session, variant_id: int) -> List[int]:
    variant = session.get(Variant, variant_id)
    return [a.id for a in variant.articles] if variant else []


def get_article_ids_for_gene(session: Session, gene_id: int) -> List[int]:
    gene = session.get(Gene, gene_id)
    return [a.id for a in gene.articles] if gene else []


def get_article_ids_for_disease(session: Session, disease_id: int) -> List[int]:
    disease = session.get(Disease, disease_id)
    return [a.id for a in disease.articles] if disease else []


# BETTER


def get_article_by_unique_field(
    session: Session, field: str, value: str
) -> Optional[Article]:
    """Fetch an article using one of its unique fields: 'id', 'pm_id', or 'pmc_id'."""
    if field not in {"id", "pm_id", "pmc_id"}:
        raise ValueError("Field must be one of: 'id', 'pm_id', 'pmc_id'")

    filter_condition = {field: int(value) if field == "id" else value}
    return session.query(Article).filter_by(**filter_condition).first()


def get_variant_by_unique_field(
    session: Session, field: str, value: str
) -> Optional[Variant]:
    """Fetch an variant using one of its unique fields: 'id', or 'exact_match'."""
    if field not in {"id", "exact_match"}:
        raise ValueError("Field must be one of: 'id', 'exact_match'")

    filter_condition = {field: int(value) if field == "id" else value}
    return session.query(Variant).filter_by(**filter_condition).first()


def get_gene_by_unique_field(
    session: Session, field: str, value: str
) -> Optional[Gene]:
    """Fetch an gene using one of its unique fields: 'id', 'ncbi_id', or 'hgnc_symbol'."""
    if field not in {"id", "ncbi_id", "hgnc_symbol"}:
        raise ValueError("Field must be one of: 'id', 'ncbi_id', 'hgnc_symbol'")

    filter_condition = {field: int(value) if field == "id" else value}
    return session.query(Gene).filter_by(**filter_condition).first()


def get_disease_by_unique_field(
    session: Session, field: str, value: str
) -> Optional[Disease]:
    """Fetch an disease using one of its unique fields: 'id', or 'original_ontology'."""
    if field not in {"id", "original_ontology"}:
        raise ValueError("Field must be one of: 'id', 'original_ontology'")

    filter_condition = {field: int(value) if field == "id" else value}
    return session.query(Disease).filter_by(**filter_condition).first()


def get_full_related_data(session: Session, entity_type: str, field: str, value: str):
    """
    Fetch all articles related to a gene/variant/disease, and return their full related content.
    entity_type: 'article', 'gene', 'variant', or 'disease'
    field: unique field for that entity
    value: value of the field
    """
    if entity_type == "article":
        article = get_article_by_unique_field(session, field, value)
        if not article:
            return {}
        return {
            "pm_id": article.pm_id,
            "pmc_id": article.pmc_id,
            "gene": [gene.search_format() for gene in article.genes],
            "disease": [disease.search_format() for disease in article.diseases],
            "variant": [variant.search_format() for variant in article.variants],
        }

    elif entity_type == "gene":
        gene = get_gene_by_unique_field(session, field, value)
        if not gene:
            return {}
        articles = gene.articles

    elif entity_type == "variant":
        variant = get_variant_by_unique_field(session, field, value)
        if not variant:
            return {}
        articles = variant.articles

    elif entity_type == "disease":
        disease = get_disease_by_unique_field(session, field, value)
        if not disease:
            return {}
        articles = disease.articles

    else:
        raise ValueError(
            "entity_type must be one of: 'article', 'gene', 'variant', 'disease'"
        )

    result = []
    for article in articles:
        result.append(
            {
                "pm_id": article.pm_id,
                "pmc_id": article.pmc_id,
                "genes": article.genes,
                "diseases": article.diseases,
                "variants": article.variants,
            }
        )

    return {"articles": result}


if __name__ == "__main__":
    # Example usage
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from VARIABLES import DATABASE_URI

    with get_session() as session:

        # variant_ids = get_variant_ids_for_article(session, article_id)
        # gene_ids = get_gene_ids_for_article(session, article_id)
        # disease_ids = get_disease_ids_for_article(session, article_id)
        # print(f"Variant IDs for article {article_id}: {variant_ids}")
        # print(f"Gene IDs for article {article_id}: {gene_ids}")
        # print(f"Disease IDs for article {article_id}: {disease_ids}")

        # Article ID: 37373000
        # PMC ID: PMC10298356
        # article_id = "PMC10298356"
        # unique_field = "pmc_id"
        # entity_type = "article"
        # x = get_full_related_data(session, entity_type, unique_field, article_id).get("articles", [])[0]
        # print(x)

        original_ontology_id = "MESH:D000079225"
        original_ontology_id = "9725"
        unique_field = "id"
        # unique_field = "original_ontology"
        entity_type = "disease"
        x = get_full_related_data(
            session, entity_type, unique_field, original_ontology_id
        ).get("articles", [])[0]

        # print(x)
        print(f"Article ID: {x['pm_id']}")
        print(f"PMC ID: {x['pmc_id']}")
        print(f"Genes: {[g.ncbi_id for g in x['genes']]}")
        print(f"Diseases: {[d.original_ontology for d in x['diseases']]}")
        print(f"Variants: {[v.exact_match for v in x['variants']]}")

        # variant_id = 1
        # article_ids_for_variant = get_article_ids_for_variant(session, variant_id)
        # print(f"Article IDs for variant {variant_id}: {len(article_ids_for_variant)}")
        # gene_id = 1
        # article_ids_for_gene = get_article_ids_for_gene(session, gene_id)
        # print(f"Article IDs for gene {gene_id}: {len(article_ids_for_gene)}")
        # disease_id = 1
        # article_ids_for_disease = get_article_ids_for_disease(session, disease_id)
        # print(f"Article IDs for disease {disease_id}: {len(article_ids_for_disease)}")

        # gene_ids = get_gene_ids_by_article_field(session, field="id", value="22")
        # print(f"Gene IDs for article with ID 22: {gene_ids}")

        # variant_ids = get_variant_ids_by_article_field(session, field="pmc_id", value="PMC987654")
        # disease_ids = get_disease_ids_by_article_field(session, field="id", value="42")
