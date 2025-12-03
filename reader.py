import os
import re
import glob

BOOKS_DIR = "books" 
LINES_PER_PAGE = 25
os.makedirs(BOOKS_DIR, exist_ok=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def find_books():
    """Find all .txt files in books directory."""
    books = glob.glob(os.path.join(BOOKS_DIR, "*.txt"))
    return sorted(books)

def detect_chapters(lines):
    """Auto-detect chapter/section breaks."""
    chapters = []
    current_title = "Beginning"
    current_start = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not stripped:
            continue
        
        is_chapter = False
        
        if len(stripped) > 5 and stripped.isupper() and len(stripped.split()) >= 2:
            words = stripped.split()
            if len(words) >= 2 or any(w in stripped for w in ["CHAPTER", "PART", "BOOK", "PROLOGUE", "EPILOGUE"]):
                is_chapter = True
        
        if re.match(r'^(Chapter|Part|Book|Section)\s+[IVX\d]+', stripped, re.IGNORECASE):
            is_chapter = True
        
        if re.match(r'^[IVX]+\.?\s+[A-Z]', stripped):
            is_chapter = True
        
        if is_chapter:
            if i > current_start + 5: 
                chapters.append({
                    'title': current_title,
                    'start': current_start,
                    'end': i
                })
            current_title = stripped
            current_start = i
    
    if len(lines) > current_start + 5:
        chapters.append({
            'title': current_title,
            'start': current_start,
            'end': len(lines)
        })
    
    if not chapters:
        chapters = [{'title': 'Full Text', 'start': 0, 'end': len(lines)}]
    
    return chapters

def load_book(filepath):
    """Load book and detect chapters."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    start = 0
    for i, line in enumerate(lines):
        if "START OF" in line.upper() and "PROJECT GUTENBERG" in line.upper():
            start = i + 1
            break
    
    lines = lines[start:]
    chapters = detect_chapters(lines)
    
    return lines, chapters

def display_chapter_menu(book_name, chapters, current_chapter):
    """Show chapter selection menu."""
    clear()
    print("=" * 70)
    print(f"  {book_name}")
    print("=" * 70)
    print("\nChapters:\n")
    
    for i, ch in enumerate(chapters):
        marker = "→" if i == current_chapter else " "
        print(f"{marker} {i+1:2}. {ch['title'][:60]}")
    
    print("\n" + "-" * 70)
    print("Enter chapter number, or: [r]ead current | [s]earch | [b]ack to books | [q]uit")

def display_page(lines, chapters, chapter_idx, page, book_name):
    """Display a page within a chapter."""
    clear()
    ch = chapters[chapter_idx]
    chapter_lines = lines[ch['start']:ch['end']]
    total_pages = (len(chapter_lines) + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    
    print("=" * 70)
    print(f"  {book_name} - {ch['title'][:45]}")
    print(f"  Chapter {chapter_idx + 1}/{len(chapters)} | Page {page + 1}/{total_pages}")
    print("=" * 70)
    print()
    
    start = page * LINES_PER_PAGE
    end = start + LINES_PER_PAGE
    
    for line in chapter_lines[start:end]:
        print(line.rstrip())
    
    print()
    print("-" * 70)
    print("[n]ext | [p]rev | [c]hapters | [s]earch | [q]uit")

def search_book(lines, query):
    """Search entire book."""
    clear()
    print(f"Searching for '{query}'...\n")
    
    results = []
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            results.append((i, line.strip()))
    
    if results:
        print(f"Found {len(results)} matches:\n")
        for line_num, text in results[:30]:
            print(f"Line {line_num}: {text[:65]}")
        if len(results) > 30:
            print(f"\n... and {len(results) - 30} more")
    else:
        print("No matches found.")
    
    input("\nPress Enter...")

def read_book(filepath):
    """Main reading interface for a book."""
    book_name = os.path.basename(filepath).replace('.txt', '')
    lines, chapters = load_book(filepath)
    
    chapter_idx = 0
    page = 0
    in_chapter_menu = True
    
    while True:
        if in_chapter_menu:
            display_chapter_menu(book_name, chapters, chapter_idx)
            cmd = input("Command: ").strip().lower()
            
            if cmd == 'q':
                return False
            elif cmd == 'b':
                return True
            elif cmd == 'r':
                in_chapter_menu = False
                page = 0
            elif cmd == 's':
                query = input("Search for: ").strip()
                if query:
                    search_book(lines, query)
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(chapters):
                    chapter_idx = idx
                    in_chapter_menu = False
                    page = 0
        else:
            ch = chapters[chapter_idx]
            chapter_lines = lines[ch['start']:ch['end']]
            total_pages = (len(chapter_lines) + LINES_PER_PAGE - 1) // LINES_PER_PAGE
            
            display_page(lines, chapters, chapter_idx, page, book_name)
            cmd = input("Command: ").strip().lower()
            
            if cmd == 'n':
                if page < total_pages - 1:
                    page += 1
                elif chapter_idx < len(chapters) - 1:
                    chapter_idx += 1
                    page = 0
            elif cmd == 'p':
                if page > 0:
                    page -= 1
                elif chapter_idx > 0:
                    chapter_idx -= 1
                    page = 999 
            elif cmd == 'c':
                in_chapter_menu = True
            elif cmd == 's':
                query = input("Search for: ").strip()
                if query:
                    search_book(lines, query)
            elif cmd == 'q':
                return False

def select_book():
    """Show book selection menu."""
    books = find_books()
    
    if not books:
        clear()
        print("=" * 70)
        print("  No books found!")
        print("=" * 70)
        print(f"\nPlace .txt files in the '{BOOKS_DIR}/' folder.")
        print("\nPress Enter to exit...")
        input()
        return None
    
    while True:
        clear()
        print("=" * 70)
        print("  BOOK READER")
        print("=" * 70)
        print("\nAvailable books:\n")
        
        for i, book in enumerate(books, 1):
            name = os.path.basename(book).replace('.txt', '')
            print(f"{i}. {name}")
        
        print("\n" + "-" * 70)
        print("Enter book number or [q]uit")
        
        choice = input("Command: ").strip().lower()
        
        if choice == 'q':
            return None
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(books):
                return books[idx]

def main():
    while True:
        book = select_book()
        if not book:
            clear()
            print("Goodbye!")
            break
        
        continue_browsing = read_book(book)
        if not continue_browsing:
            break

if __name__ == "__main__":
    main()
