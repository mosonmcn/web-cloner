import sys
import os

# Import core modules from the mon directory
from mon.fetcher import Fetcher
from mon.saver import Saver
from mon.parser import Parser
from mon.api_analyzer import APIAnalyzer
from mon.api_verifier import APIVerifier
from mon.explorer import Explorer
from mon.compiler_engine import CompilerEngine

def main():
    # Check if the domain was passed as a command-line argument
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        # Prompt the user for input if no parameter was provided
        try:
            domain = input("Enter domain to clone (e.g., example.com): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Operation cancelled by user.")
            sys.exit(0)

    # Validate that the domain is not empty
    if not domain:
        print("[!] Error: No domain provided. Exiting.")
        sys.exit(1)

    # Basic protocol formatting
    if not domain.startswith(("http://", "https://")):
        target_url = f"https://{domain}"
    else:
        target_url = domain
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

    print(f"[*] Initializing clone process for: {domain} ({target_url})")
    
    # Define output directory
    output_dir = os.path.join("output", domain)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 1. Initialize Fetcher to download the main page
        print("[*] Fetching target page source...")
        fetcher = Fetcher(target_url)
        html_content = fetcher.get_html()
        
        if not html_content:
            print("[!] Error: Failed to fetch content from target domain.")
            sys.exit(1)

        # 2. Parse HTML content and discover assets
        print("[*] Parsing HTML and discovering resources...")
        parser = Parser(html_content, target_url)
        assets = parser.get_assets()
        links = parser.get_links()
        
        # 3. Save resources locally to clone the page
        print(f"[*] Cloning assets locally to: {output_dir}")
        saver = Saver(output_dir)
        saver.save_html(html_content)
        saver.download_assets(assets)

        # 4. Analyze scripts and APIs from discovered endpoints
        print("[*] Running API and Endpoint analysis...")
        analyzer = APIAnalyzer(assets, html_content)
        discovered_apis = analyzer.find_endpoints()

        # 5. Verify live endpoints if needed
        print("[*] Verifying discovered API endpoints...")
        verifier = APIVerifier(discovered_apis)
        verified_results = verifier.verify_all()

        # 6. Map directory structure and export compiled results
        print("[*] Compiling workspace structure...")
        explorer = Explorer(output_dir)
        directory_tree = explorer.generate_tree()

        engine = CompilerEngine(
            domain=domain,
            cloned_path=output_dir,
            apis=verified_results,
            tree=directory_tree
        )
        engine.export_report()

        print(f"[+] Successfully cloned and analyzed: {domain}")
        print(f"[+] Output compiled and saved in: {output_dir}")
        
    except Exception as e:
        print(f"[!] An error occurred during the execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
