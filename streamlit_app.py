import re
import requests
import streamlit as st

# ---------- Core helpers ----------
def resolve_and_clean_url(url: str) -> str:
    """Follow redirects and strip query params. Return 'Link Error' on failure."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r = requests.get(url, timeout=10, allow_redirects=True)
        final_url = r.url.split("?")[0]
        return final_url
    except requests.RequestException:
        return "Link Error"


def extract_video_id(url: str) -> str | None:
    """
    Grab the numeric TikTok video ID (last long digit sequence).
    Works for almost all tiktok.com redirect variants.
    """
    match = re.search(r"(\d{8,20})", url)
    return match.group(1) if match else None


# ---------- UI ----------
st.set_page_config(page_title="URL Cleaner & TikTok Player", layout="wide")
st.title("🧹 URL Cleaner & 🎬 TikTok Quick-Play")

tab_clean, tab_play = st.tabs(["Clean (≤ 100 links)", "Clean & Play (≤ 5 links)"])

# --- Tab 1 : Clean only ------------------------------------------------------
with tab_clean:
    st.subheader("Paste URLs (one per line)")
    raw_links_clean = st.text_area("", height=300, key="clean_text")

    if st.button("Clean URLs", key="clean_btn"):
        if not raw_links_clean.strip():
            st.warning("Please paste some URLs first.")
            st.stop()

        urls = [u.strip() for u in raw_links_clean.splitlines() if u.strip()]
        if len(urls) > 100:
            st.error("💡 Limit is 100 links. Please reduce the list.")
            st.stop()

        cleaned, errors = [], []
        for url in urls:
            cleaned_url = resolve_and_clean_url(url)
            (cleaned if cleaned_url != "Link Error" else errors).append(
                cleaned_url if cleaned_url != "Link Error" else url
            )

        st.subheader("Cleaned URLs")
        if cleaned:
            st.code("\n".join(cleaned), language="text")
        st.success(f"Input links : {len(urls)}")
        st.success(f"Cleaned OK  : {len(cleaned)}")
        st.error(f"Errors      : {len(errors)}")
        if errors:
            st.caption("Links that failed to resolve:")
            st.code("\n".join(errors), language="text")

# --- Tab 2 : Clean & play ----------------------------------------------------
with tab_play:
    st.subheader("Paste TikTok URLs (one per line)")
    raw_links_play = st.text_area("", height=200, key="play_text")

    if st.button("Clean & Generate Players", key="play_btn"):
        if not raw_links_play.strip():
            st.warning("Please paste some URLs first.")
            st.stop()

        urls_play = [u.strip() for u in raw_links_play.splitlines() if u.strip()]
        if len(urls_play) > 5:
            st.error("💡 Limit is 5 links. Please reduce the list.")
            st.stop()

        cards = []  # (cleaned_url, play_url | None, error_msg | None)
        for url in urls_play:
            cleaned_url = resolve_and_clean_url(url)
            if cleaned_url == "Link Error":
                cards.append((url, None, "Resolve failed"))
                continue

            vid = extract_video_id(cleaned_url)
            if not vid:
                cards.append((cleaned_url, None, "Video ID not found"))
            else:
                play_url = f"https://tikwm.com/video/media/play/{vid}.mp4"
                cards.append((cleaned_url, play_url, None))

        # Masonry-ish layout: 3 columns per row
        cols = st.columns(3, gap="small")
        for idx, (cleaned, play_url, err) in enumerate(cards):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.caption(cleaned)
                    if err:
                        st.error(err)
                    else:
                        st.video(play_url)
