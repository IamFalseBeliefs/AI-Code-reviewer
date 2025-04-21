import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from groq import Groq
import httpx

client = Groq(
    api_key="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",
    http_client=httpx.Client(verify=False)
    )

file_path = ""
original_content = ""
suggested_edits = []
current_suggestion = 0

def analyze_file():
    global file_path, original_content, suggested_edits, current_suggestion
    file_path = filedialog.askopenfilename()
    current_suggestion = 0
    suggested_edits.clear()

    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                original_content = file.read()
        except:
            messagebox.showerror("Error", "Cannot read this file.")
            return

        original_text.delete("1.0", tk.END)
        original_text.insert(tk.END, original_content)

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": (
                        "Review the following code and suggest improved rewrites only if needed.\n\n"
                        "Format:\n### Suggestion: [title]\n### Original:\n[original]\n### Improved:\n[improved]\n\n"
                        f"{original_content}"
                    )
                }]
            )
            ai_reply = response.choices[0].message.content

            suggestion_text.delete("1.0", tk.END)

            suggestion_text.insert(tk.END, ai_reply)

            parse_suggestions(ai_reply)

        except Exception as e:
            suggestion_text.insert(tk.END, f"\nError: {e}")

def parse_suggestions(text):

    global suggested_edits

    suggested_edits.clear()

    if "No improvements necessary" in text:
        return

    blocks = text.split("### Suggestion")
    for block in blocks[1:]:

        try:
            title = block.splitlines()[0].strip(": ")
            original = extract_section(block, "Original", "Improved")
            improved = extract_section(block, "Improved", None)
            if original and improved:
                suggested_edits.append((title, original, improved))

        except:
            continue

    if suggested_edits:
        show_next_suggestion()

def extract_section(text, start, end):

    s = text.find(f"### {start}")

    if s == -1: return None

    s += len(f"### {start}")

    e = text.find(f"### {end}") if end else len(text)

    return text[s:e].strip()

def show_next_suggestion():

    global current_suggestion

    suggestion_text.delete("1.0", tk.END)

    if current_suggestion < len(suggested_edits):

        title, original, improved = suggested_edits[current_suggestion]

        suggestion_text.insert(tk.END, f"{title}\n\nOriginal:\n{original}\n\nImproved:\n{improved}")

    else:
        suggestion_text.insert(tk.END, "All suggestions reviewed.")

def accept_suggestion():

    global current_suggestion, original_content

    if current_suggestion < len(suggested_edits):

        _, old, new = suggested_edits[current_suggestion]

        if old in original_content:

            original_content = original_content.replace(old, new)

        current_suggestion += 1

        show_next_suggestion()

def reject_suggestion():

    global current_suggestion

    current_suggestion += 1

    show_next_suggestion()

def save_file():

    if not original_content or not file_path:
        return

    base, ext = os.path.splitext(file_path)

    new_path = f"{base}_altered{ext}"

    with open(new_path, "w", encoding="utf-8") as f:

        f.write(original_content)

    messagebox.showinfo("Saved", f"Saved as {new_path}")

# GUI
root = tk.Tk()

root.title("AI Code Review BOI")

root.geometry("1000x700")

tk.Button(root, text="Load File", command=analyze_file).pack(pady=2)

frame = tk.Frame(root)

frame.pack(expand=True, fill="both")

original_text = scrolledtext.ScrolledText(frame, font=("Courier", 9), bg="black", fg="lime")

original_text.pack(side="left", expand=True, fill="both", padx=2, pady=2)

suggestion_text = scrolledtext.ScrolledText(frame, font=("Courier", 9), bg="gray15", fg="white")

suggestion_text.pack(side="right", expand=True, fill="both", padx=2, pady=2)

btns = tk.Frame(root)

btns.pack(pady=2)

tk.Button(btns, text="Accept", command=accept_suggestion, bg="green", fg="white").pack(side="left", padx=5)

tk.Button(btns, text="Reject", command=reject_suggestion, bg="red", fg="white").pack(side="left", padx=5)

tk.Button(btns, text="Save Altered File", command=save_file).pack(side="left", padx=5)

root.mainloop()
