from Bio import Entrez
import argparse
import json

# Set your email for Entrez (required by NCBI)
Entrez.email = "rtdatasci@gmail.com"

def search_pubmed(query, max_results=10):
    """
    Search PubMed for a given query and return results.

    Args:
        query (str): Search term (e.g., drug or disease name).
        max_results (int): Number of results to fetch (default: 10).

    Returns:
        list[dict]: List of PubMed articles with title, summary, and PubMed ID.
    """
    try:
        # Perform search
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()

        # Fetch article details
        ids = record["IdList"]
        if not ids:
            return []

        handle = Entrez.efetch(db="pubmed", id=','.join(ids), rettype="abstract", retmode="text")
        articles = handle.read()
        handle.close()

        # Process articles
        results = []
        for pmid in ids:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            article = Entrez.read(handle)
            handle.close()

            # Extract details
            medline_citation = article["PubmedArticle"][0]["MedlineCitation"]
            article_title = medline_citation.get("Article", {}).get("ArticleTitle", "No title")
            abstract_text = medline_citation.get("Article", {}).get("Abstract", {}).get("AbstractText", ["No abstract"])[0]

            results.append({
                "pubmed_id": pmid,
                "title": article_title,
                "abstract": abstract_text
            })

        return results

    except Exception as e:
        print(f"Error fetching PubMed data: {e}")
        return []

def save_results(results, output_file):
    """
    Save PubMed search results to a JSON file.

    Args:
        results (list): List of article dictionaries.
        output_file (str): Path to save the results.
    """
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    # Command-line interface
    parser = argparse.ArgumentParser(description="Search PubMed and collect research articles.")
    parser.add_argument("query", type=str, help="Search term (e.g., drug or disease name).")
    parser.add_argument("--max_results", type=int, default=10, help="Max number of results to fetch (default: 10).")
    parser.add_argument("--output", type=str, default="results.json", help="Output file to save the results (default: results.json).")

    args = parser.parse_args()

    print(f"Searching PubMed for '{args.query}'...")
    results = search_pubmed(args.query, args.max_results)

    if results:
        print(f"Found {len(results)} articles. Saving to {args.output}...")
        save_results(results, args.output)
        print("Done!")
    else:
        print("No articles found.")


# test example:
# python /scripts/scrape_pubmed.py "diabetes" --max_results 5 --output diabetes_results.json
