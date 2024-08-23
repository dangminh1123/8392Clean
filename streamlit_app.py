import streamlit as st
import requests

def main():
    st.title("URL Cleaner")
    raw_links = st.text_area("Paste your URLs here (one per line):", height=300)
    if st.button("Clean URLs"):
        if raw_links:
            urls = raw_links.splitlines()
            cleaned_links = []
            error_links = []
            for url in urls:
                cleaned_url = resolve_and_clean_url(url)
                if cleaned_url == "Link Error":
                    error_links.append(url)
                else:
                    cleaned_links.append(cleaned_url)
            
            st.subheader("Cleaned URLs:")
            st.code("\n".join(cleaned_links), language="text")
            st.success(f"Number of Links Added: {len(urls)}")
            st.success(f"Number of Links Final: {len(cleaned_links)}")
            st.error(f"Number of Errors: {len(error_links)}")
            if error_links:
                st.error("Error Links:")
                st.write("\n".join(error_links))
        else:
            st.warning("Please paste some URLs first.")

def resolve_and_clean_url(url):
    if not url.startswith('https://'):
        url = 'https://' + url
    try:
        response = requests.get(url, timeout=10)
        final_url = response.url
        clean_url = final_url.split('?')[0]
        return clean_url
    except requests.RequestException:
        return "Link Error"

if __name__ == "__main__":
    main()
