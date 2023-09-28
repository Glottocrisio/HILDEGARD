import wikipediaapi as wa


# Function to find the shortest path between two Wikipedia articles using BFS
def find_shortest_path(start_article, end_article, max_depth=6):
    # Use the custom session
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)', 'en')

    # Initialize the BFS queue with the starting article
    queue = [(start_article, [start_article])]

    while queue:
        current_article, path = queue.pop(0)

        # Check if the current article is the target article
        if current_article == end_article:
            return path

        # Check if the depth is within the specified limit
        if len(path) < max_depth:
            page = wiki_wiki.page(current_article)
            links = [link.title for link in page.links]
            for link in links:
                if link not in path:
                    queue.append((link, path + [link]))

    # If no path is found within the specified depth, return None
    return None


# Create a function to get links from an article
def get_links(article_title):
    wiki_wiki = wa.Wikipedia('HILDE&GARD/1.0 (your@email.com)', 'en')
    page = wiki_wiki.page(article_title)
    return [link.title for link in page.links]

# Depth-First Search (DFS) to find the shortest path
def dfs(current_article, path, visited, depth):
    if depth > max_depth:
        return None

    visited.add(current_article)
    path.append(current_article)

    if current_article == end_article:
        return path

    for link in get_links(current_article):
        if link not in visited:
            result = dfs(link, path.copy(), visited, depth + 1)
            if result:
                return result

    return None



