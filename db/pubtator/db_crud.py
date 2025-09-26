# crud.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Article, Gene, Disease, Variant, Base
from VARIABLES import DATABASE_URI



engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# CREATE
def create_article_with_metadata(pm_id, gene_symbols=[], disease_names=[], variant_names=[]):
    # Try to fetch existing article
    article = session.query(Article).filter_by(pm_id=pm_id).first()
    
    if not article:
        article = Article(pm_id=pm_id)
        session.add(article)

    # Add related genes
    for symbol in gene_symbols:
        gene = session.query(Gene).filter_by(gene_symbol=symbol).first()
        if not gene:
            gene = Gene(gene_symbol=symbol)
            session.add(gene)
        if gene not in article.genes:
            article.genes.append(gene)

    # Add related diseases
    for name in disease_names:
        disease = session.query(Disease).filter_by(disease_name=name).first()
        if not disease:
            disease = Disease(disease_name=name)
            session.add(disease)
        if disease not in article.diseases:
            article.diseases.append(disease)

    # Add related variants
    for name in variant_names:
        variant = session.query(Variant).filter_by(variant_name=name).first()
        if not variant:
            variant = Variant(variant_name=name)
            session.add(variant)
        if variant not in article.variants:
            article.variants.append(variant)

    session.commit()
    return article

# READ
def get_articles_by_gene(gene_symbol):
    return session.query(Article).join(Article.genes).filter_by(gene_symbol=gene_symbol).all()

# UPDATE
def update_article_title(article_id, new_title):
    article = session.get(Article, article_id)
    if article:
        article.title = new_title
        session.commit()

# DELETE
def delete_article(article_id):
    article = session.get(Article, article_id)
    if article:
        session.delete(article)
        session.commit()
