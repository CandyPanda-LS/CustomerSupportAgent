from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults


"""
    This provides singe text ans
    Usage:
        ddg_search.invoke()
"""
ddg_search = DuckDuckGoSearchRun()

"""
    This provides a list of results, possible to change the output format to output_format="json" also
    Usage:
        ddg_search_results.invoke()
"""
ddg_search_results = DuckDuckGoSearchResults(output_format="list")