
import json

import pandas as pd
import streamlit as st

from connectors import (
    WEBSITES,
    SEARCH_PROVIDERS,
    search_provider,
)

from storage import (
    initialize_db,
    save_search,
    get_saved_searches,
    load_search,
    delete_search,
)



st.set_page_config(
    page_title="Multi-Website Portal",
    page_icon="🌐",
    layout="wide",
)

initialize_db()

DEFAULTS = {
    "results": [],
    "last_query": "",
    "last_provider": "Wikipedia",
    "search_counts": {},
    "search_errors": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value



st.title("🌐 Multi-Website Access Portal")

st.caption(
    "Access websites, search supported sources, "
    "and collect reusable research results."
)


with st.sidebar:
    st.header("Navigation")

    page = st.radio(
        "Choose a section",
        [
            "Home",
            "Website Directory",
            "Multi-Source Search",
            "Data Explorer",
            "Saved Searches",
        ],
    )

    st.divider()

    st.caption(f"{len(WEBSITES)} websites in the directory")
    st.caption(f"{len(SEARCH_PROVIDERS)} search providers")


def show_results(results):
    if not results:
        st.info("No results to display.")
        return

    df = pd.DataFrame(results)

    column_config = {}

    if "url" in df.columns:
        column_config["url"] = st.column_config.LinkColumn(
            "Open original",
            display_text="Open result",
        )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="portal_results.csv",
            mime="text/csv",
            key="download_results_csv",
        )

    with col2:
        st.download_button(
            "Download JSON",
            data=json.dumps(
                results,
                indent=2,
                ensure_ascii=False,
            ).encode("utf-8"),
            file_name="portal_results.json",
            mime="application/json",
            key="download_results_json",
        )



if page == "Home":
    st.subheader("Your information hub")

    col1, col2, col3 = st.columns(3)

    col1.metric("Websites", len(WEBSITES))
    col2.metric("Search providers", len(SEARCH_PROVIDERS))
    col3.metric("Saved searches", len(get_saved_searches()))

    st.markdown(
        """
        Use this portal to:

        - Open websites from a categorized directory.
        - Search supported sources.
        - Search one source or all sources at once.
        - Inspect and download results.
        - Save and revisit previous searches.
        """
    )

    st.subheader("Featured websites")

    featured = [
        "Wikipedia",
        "BBC News",
        "World Bank Data",
        "Open-Meteo",
        "GitHub",
        "PubMed",
    ]

    cols = st.columns(3)

    for i, name in enumerate(featured):
        site = next(
            (
                item for item in WEBSITES
                if item["name"] == name
            ),
            None,
        )

        if site is None:
            continue

        with cols[i % 3]:
            st.markdown(f"**{site['name']}**")
            st.caption(site["category"])

            st.link_button(
                "Open website",
                site["url"],
                use_container_width=True,
            )


# --------------------------------------------------
# Website directory
# --------------------------------------------------

elif page == "Website Directory":
    st.subheader("Website Directory")

    categories = sorted(
        {
            item["category"]
            for item in WEBSITES
        }
    )

    selected_category = st.selectbox(
        "Filter by category",
        ["All categories"] + categories,
    )

    search_text = st.text_input(
        "Find a website by name or URL"
    ).strip().lower()

    filtered = [
        site
        for site in WEBSITES
        if (
            selected_category == "All categories"
            or site["category"] == selected_category
        )
        and (
            search_text in site["name"].lower()
            or search_text in site["url"].lower()
        )
    ]

    st.write(f"Found {len(filtered)} websites.")

    for site in filtered:
        with st.container(border=True):
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"### {site['name']}")
                st.caption(site["category"])
                st.code(site["url"], language=None)

            with right:
                st.link_button(
                    "Visit website",
                    site["url"],
                    use_container_width=True,
                )


elif page == "Multi-Source Search":
    st.subheader("Search supported websites")

    provider = st.selectbox(
        "Search provider",
        ["All Sources"] + list(SEARCH_PROVIDERS.keys()),
    )

    query = st.text_input(
        "What would you like to find?",
        placeholder="e.g. climate change, Python, Kenya",
    )

    limit = st.slider(
        "Maximum results per source",
        min_value=5,
        max_value=30,
        value=10,
    )

    if provider == "All Sources":
        st.caption(
            f"Search all {len(SEARCH_PROVIDERS)} providers. "
            f"Up to {limit} results per provider."
        )

    if st.button("Search", type="primary"):
        if not query.strip():
            st.warning("Enter a search term.")

        else:
            providers = (
                list(SEARCH_PROVIDERS.keys())
                if provider == "All Sources"
                else [provider]
            )

            combined_results = []
            search_counts = {}
            search_errors = []

            progress = st.progress(
                0,
                text="Preparing search...",
            )

            for i, source in enumerate(providers):
                progress.progress(
                    i / len(providers),
                    text=f"Searching {source}...",
                )

                try:
                    source_results = search_provider(
                        source,
                        query.strip(),
                        limit,
                    )

                    search_counts[source] = len(source_results)
                    combined_results.extend(source_results)

                    if source_results:
                        try:
                            save_search(
                                source,
                                query.strip(),
                                source_results,
                            )
                        except Exception as exc:
                            search_errors.append(
                                f"{source}: Results found, "
                                f"but saving failed: {exc}"
                            )

                except Exception as exc:
                    search_counts[source] = 0
                    search_errors.append(
                        f"{source}: "
                        f"{type(exc).__name__}: {exc}"
                    )

            progress.progress(
                1.0,
                text="Search complete.",
            )
            progress.empty()

            st.session_state.results = combined_results
            st.session_state.last_query = query.strip()
            st.session_state.last_provider = provider
            st.session_state.search_counts = search_counts
            st.session_state.search_errors = search_errors

            if combined_results:
                st.success(
                    f"Found {len(combined_results)} result(s) "
                    "in total."
                )

            elif search_errors:
                st.error(
                    "No results were retrieved successfully. "
                    "Check the warnings below."
                )

            else:
                st.info(
                    "No results found. Try another search term."
                )

    # Results summary stays inside the search page,
    # but outside the Search button condition.

    if st.session_state.search_counts:
        st.subheader("Results by source")

        count_items = list(
            st.session_state.search_counts.items()
        )

        cols = st.columns(len(count_items))

        for col, (source, count) in zip(cols, count_items):
            col.metric(source, count)

        st.metric(
            "Total results",
            len(st.session_state.results),
        )

    if st.session_state.search_errors:
        st.subheader("Search warnings")

        for error in st.session_state.search_errors:
            st.warning(error)

    if st.session_state.results:
        st.subheader("Search results")

        st.caption(
            f"Provider: {st.session_state.last_provider} | "
            f"Query: {st.session_state.last_query}"
        )

        show_results(st.session_state.results)


elif page == "Data Explorer":
    st.subheader("Data Explorer")

    st.write(
        "View current search results and inspect "
        "the website directory."
    )

    if st.session_state.results:
        st.markdown("### Current search results")
        show_results(st.session_state.results)

    else:
        st.info(
            "No current results. Run a search or load "
            "a saved search first."
        )

    st.markdown("### Website directory data")

    directory_df = pd.DataFrame(WEBSITES)

    st.dataframe(
        directory_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download website directory",
        data=directory_df.to_csv(index=False).encode("utf-8"),
        file_name="website_directory.csv",
        mime="text/csv",
        key="download_directory_csv",
    )


elif page == "Saved Searches":
    st.subheader("Saved Searches")

    saved = get_saved_searches()

    if not saved:
        st.info("No searches have been saved yet.")

    else:
        for item in saved:
            with st.container(border=True):
                st.markdown(
                    f"**{item['provider']}** — "
                    f"{item['query']}"
                )

                st.caption(
                    f"Saved at: {item['created_at']} "
                    f"| ID: {item['id']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "Load results",
                        key=f"load_{item['id']}",
                    ):
                        loaded_results = load_search(item["id"])

                        if loaded_results is not None:
                            st.session_state.results = loaded_results
                            st.session_state.last_query = item["query"]
                            st.session_state.last_provider = item["provider"]
                            st.session_state.search_counts = {}
                            st.session_state.search_errors = []

                            st.success(
                                "Results loaded. "
                                "Open Data Explorer to view them."
                            )

                        else:
                            st.warning(
                                "No results were returned for this saved search."
                            )

                with col2:
                    if st.button(
                        "Delete",
                        key=f"delete_{item['id']}",
                    ):
                        delete_search(item["id"])
                        st.rerun()

    if st.session_state.results:
        st.markdown("### Currently loaded results")
        show_results(st.session_state.results)

