import os
import re
import glob

BOOKS_DIR = "books"
LINES_PER_PAGE = 25
os.makedirs(BOOKS_DIR, exist_ok=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def find_books():
    return sorted(glob.glob(os.path.join(BOOKS_DIR, "*.txt")))

def detect_chapters(lines):
    chapters = []
    title = "Start"
    start = 0

    for i, line in enumerate(lines):
        t = line.strip()
        if not t:
            continue

        # simple chapter detection, not trying too hard
        if (
            t.isupper()
            or t.startswith(("Chapter", "CHAPTER", "Part", "PART"))
            or re.match(r"^[IVX]+\.", t)
        ):
            if i - start > 5:
                chapters.append({"title": title, "start": start, "end": i})
            title = t
            start = i

    if len(lines) - start > 5:
        chapters.append({"title": title, "start": start, "end": len(lines)})

    if not chapters:
        return [{"title": "Full Text", "start": 0, "end": len(lines)}]

    return chapters

def load_book(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # skip gutenberg header if present
    for i, ln in enumerate(lines):
        up = ln.upper()
        if "PROJECT GUTENBERG" in up and "START" in up:
            lines = lines[i+1:]
            break

    return lines, detect_chapters(lines)

def display_chapter_menu(name, chapters, cur):
    clear()
    print(name)
    print()
    for i, ch in enumerate(chapters):
        marker = ">" if i == cur else " "
        print(f"{marker} {i+1}. {ch['title'][:50]}")
    print("\n[r]ead  [s]earch  [b]ack  [q]uit")

def display_page(lines, chaps, idx, page, name):
    clear()
    ch = chaps[idx]
    chunk = lines[ch["start"]:ch["end"]]
    pages = (len(chunk) + LINES_PER_PAGE - 1) // LINES_PER_PAGE

    print(f"{name} - {ch['title']}")
    print(f"Chapter {idx+1}/{len(chaps)} | Page {page+1}/{pages}\n")

    s = page * LINES_PER_PAGE
    for ln in chunk[s:s+LINES_PER_PAGE]:
        print(ln.rstrip())

    print("\n[n]ext [p]rev [c]hapters [s]earch [q]uit")

def search_book(lines, q):
    clear()
    hits = []
    for i, ln in enumerate(lines):
        if q.lower() in ln.lower():
            hits.append((i, ln.strip()))

    if not hits:
        print("No matches."); input(); return

    for i, (num, txt) in enumerate(hits[:30]):
        print(f"{num}: {txt}")
    if len(hits) > 30:
        print(f"...(+{len(hits)-30} more)")

    input()

def read_book(path):
    name = os.path.basename(path).replace(".txt", "")
    lines, chaps = load_book(path)
    idx = 0
    page = 0
    in_menu = True

    while True:
        if in_menu:
            display_chapter_menu(name, chaps, idx)
            cmd = input("> ").lower()
            if cmd == "q": return False
            if cmd == "b": return True
            if cmd == "r":
                in_menu = False
                page = 0
            elif cmd == "s":
                q = input("Search: ").strip()
                if q: search_book(lines, q)
            elif cmd.isdigit():
                x = int(cmd)-1
                if 0 <= x < len(chaps):
                    idx = x
                    in_menu = False
                    page = 0
        else:
            ch = chaps[idx]
            chunk = lines[ch["start"]:ch["end"]]
            pages = (len(chunk) + LINES_PER_PAGE - 1) // LINES_PER_PAGE

            display_page(lines, chaps, idx, page, name)
            cmd = input("> ").lower()

            if cmd == "n":
                if page < pages-1:
                    page += 1
                elif idx < len(chaps)-1:
                    idx += 1
                    page = 0

            elif cmd == "p":
                if page > 0:
                    page -= 1
                elif idx > 0:
                    idx -= 1
                    # intentionally rough but effective
                    page = 999

            elif cmd == "c":
                in_menu = True

            elif cmd == "s":
                q = input("Search: ").strip()
                if q: search_book(lines, q)

            elif cmd == "q":
                return False

def select_book():
    books = find_books()
    if not books:
        clear()
        print("No books found in 'books/'")
        input()
        return None

    while True:
        clear()
        print("Books:\n")
        for i, b in enumerate(books, 1):
            print(f"{i}. {os.path.basename(b).replace('.txt','')}")
        print("\n[q]uit")

        c = input("> ").lower()
        if c == "q": 
            return None
        if c.isdigit():
            x = int(c)-1
            if 0 <= x < len(books):
                return books[x]

def main():
    while True:
        b = select_book()
        if not b:
            clear()
            print("Goodbye")
            break
        if not read_book(b):
            break

if __name__ == "__main__":
    main()

