import csv

from db.pubtator.db_models import Article, Gene
from db.pubtator.db_queries import get_gene_by_unique_field
from db.pubtator.VARIABLES import get_session
from sqlalchemy.orm import Session

with open("/home/novak/Clingen/repo_to_send/test_outputs/clingen_gene_list", "r") as f:
    gene_symbols = [line.strip() for line in f if line.strip()]

with get_session() as session:
    collected_articles = set()

    len_gene_symbols = len(gene_symbols)
    for i, symbol in enumerate(gene_symbols):
        print(f"Processing gene {i + 1}/{len_gene_symbols}: {symbol}", end="\r")
        gene = get_gene_by_unique_field(session, "hgnc_symbol", symbol)
        if gene:
            for article in gene.articles:
                collected_articles.add(article)

output_file = (
    "/home/novak/Clingen/repo_to_send/test_outputs/articles_by_clingen_gene_list.csv"
)
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["id", "pm_id", "pmc_id"])  # zaglavlja

    for article in collected_articles:
        writer.writerow([article.id, article.pm_id, article.pmc_id])
