import os
import re
import glob
import shutil
from dataclasses import dataclass

BOOKS_DIR = "books"
LINES_PER_PAGE = 25

os.makedirs(BOOKS_DIR, exist_ok=True)


def clear():
    os.system("cls" if os.name == "nt" else "clear")

def term_width():
    return shutil.get_terminal_size((80, 20)).columns

def pause(msg="Press Enter to continue"):
    input(msg)


@dataclass
class Chapter:
    title: str
    start: int
    end: int

@dataclass
class Cursor:
    chapter: int = 0
    page: int = 0


def find_books():
    return sorted(glob.glob(os.path.join(BOOKS_DIR, "*.txt")))

def strip_gutenberg(lines):
    for i, ln in enumerate(lines):
        up = ln.upper()
        if "PROJECT GUTENBERG" in up and "START" in up:
            return lines[i + 1 :]
    return lines

def detect_chapters(lines):
    chapters = []
    start = 0
    title = "Beginning"

    pattern = re.compile(
        r"^(chapter|part)\s+\w+|^[IVX]+\.", re.IGNORECASE
    )

    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t:
            continue

        if pattern.match(t) or (t.isupper() and len(t) < 60):
            if i - start > 10:
                chapters.append(Chapter(title, start, i))
            title = t
            start = i

    if len(lines) - start > 10:
        chapters.append(Chapter(title, start, len(lines)))

    if not chapters:
        chapters = [Chapter("Full Text", 0, len(lines))]

    return chapters

def load_book(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = strip_gutenberg(f.readlines())
    return lines, detect_chapters(lines)


def header(text):
    w = term_width()
    print(text[:w])
    print("-" * min(len(text), w))

def render_chapter_menu(book, chapters, current):
    clear()
    header(book)
    print()

    for i, ch in enumerate(chapters):
        mark = ">" if i == current else " "
        print(f"{mark} {i+1:>3}. {ch.title[:60]}")

    print("\n[r]ead  [s]earch  [#] jump  [b]ack  [q]uit")

def render_page(book, chapter, cursor, total_pages, lines):
    clear()
    header(f"{book} — {chapter.title}")
    print(f"Chapter {cursor.chapter+1} | Page {cursor.page+1}/{total_pages}\n")

    start = chapter.start + cursor.page * LINES_PER_PAGE
    end = min(start + LINES_PER_PAGE, chapter.end)

    for ln in lines[start:end]:
        print(ln.rstrip())

    print("\n[n]ext  [p]rev  [c]hapters  [s]earch  [q]uit")


def search_book(lines, query):
    clear()
    results = [(i, ln.strip()) for i, ln in enumerate(lines) if query.lower() in ln.lower()]

    if not results:
        print("No matches.")
        pause()
        return None

    print(f"Results for '{query}':\n")
    for i, (lnum, txt) in enumerate(results[:30]):
        print(f"{lnum:>6}: {txt[:80]}")

    if len(results) > 30:
        print(f"... (+{len(results)-30} more)")

    print("\nEnter line number to jump or blank to cancel")
    choice = input("> ").strip()

    if choice.isdigit():
        return int(choice)

    return None


def read_book(path):
    book = os.path.basename(path).replace(".txt", "")
    lines, chapters = load_book(path)
    cursor = Cursor()
    in_menu = True

    while True:
        if in_menu:
            render_chapter_menu(book, chapters, cursor.chapter)
            cmd = input("> ").lower().strip()

            if cmd == "q":
                return False
            if cmd == "b":
                return True
            if cmd == "r":
                cursor.page = 0
                in_menu = False
            elif cmd == "s":
                q = input("Search: ").strip()
                if q:
                    hit = search_book(lines, q)
                    if hit is not None:
                        cursor.chapter = max(
                            i for i, ch in enumerate(chapters) if ch.start <= hit < ch.end
                        )
                        cursor.page = (hit - chapters[cursor.chapter].start) // LINES_PER_PAGE
                        in_menu = False
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(chapters):
                    cursor.chapter = idx
                    cursor.page = 0
                    in_menu = False

        else:
            ch = chapters[cursor.chapter]
            total_pages = max(1, (ch.end - ch.start + LINES_PER_PAGE - 1) // LINES_PER_PAGE)

            cursor.page = max(0, min(cursor.page, total_pages - 1))
            render_page(book, ch, cursor, total_pages, lines)

            cmd = input("> ").lower().strip()

            if cmd == "n":
                if cursor.page < total_pages - 1:
                    cursor.page += 1
                elif cursor.chapter < len(chapters) - 1:
                    cursor.chapter += 1
                    cursor.page = 0

            elif cmd == "p":
                if cursor.page > 0:
                    cursor.page -= 1
                elif cursor.chapter > 0:
                    cursor.chapter -= 1
                    prev = chapters[cursor.chapter]
                    cursor.page = (prev.end - prev.start - 1) // LINES_PER_PAGE

            elif cmd == "c":
                in_menu = True

            elif cmd == "s":
                q = input("Search: ").strip()
                if q:
                    hit = search_book(lines, q)
                    if hit is not None:
                        cursor.chapter = max(
                            i for i, ch in enumerate(chapters) if ch.start <= hit < ch.end
                        )
                        cursor.page = (hit - chapters[cursor.chapter].start) // LINES_PER_PAGE

            elif cmd == "q":
                return False


def select_book():
    books = find_books()
    if not books:
        clear()
        print("No books found in 'books/'")
        pause()
        return None

    while True:
        clear()
        header("Books")
        print()

        for i, b in enumerate(books, 1):
            print(f"{i}. {os.path.basename(b).replace('.txt','')}")

        print("\n[q]uit")
        c = input("> ").strip().lower()

        if c == "q":
            return None
        if c.isdigit():
            idx = int(c) - 1
            if 0 <= idx < len(books):
                return books[idx]

def main():
    while True:
        book = select_book()
        if not book:
            clear()
            print("Goodbye")
            break
        if not read_book(book):
            break

if __name__ == "__main__":
    main()
