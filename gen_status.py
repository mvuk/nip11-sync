"""Build STATUS.md from inventory/software.csv plus prs.json (open PRs per implementation)."""
import csv, json
rows = list(csv.DictReader(open("inventory/software.csv")))
prs = json.load(open("prs.json"))
def cell(s, n=70): s = (s or "").replace("|", "/").replace("\n", " ").strip(); return s if len(s) <= n else s[:n-1] + "…"
out = ["# Status", "",
       "One row per relay implementation, ordered by measured deployment. Full detail: [inventory/software.md](inventory/software.md).",
       "", "Legend: **NIP-11 PR** = the completeness change · **Payments PR** = the optional payment backend.", "",
       "| Implementation | Language | Maintained | NIP-11 today | NIP-11 PR | Payments PR |", "|---|---|---|---|---|---|"]
for r in rows:
    if r["maintained"].strip().lower().startswith(("n", "dead")): continue
    p = prs.get(r["name"], {})
    repo = r["repo"].split()[0]
    out.append(f"| [{cell(r['name'],40)}]({repo}) | {cell(r['language'],30)} | {cell(r['maintained'],10)} | {cell(r['nip11_status'],60)} | {p.get('nip11','planned')} | {p.get('payments','planned')} |")
out += ["", "Unmaintained and dead implementations are listed in the inventory only."]
open("STATUS.md", "w").write("\n".join(out) + "\n")
print(len(out) - 9, "rows")
