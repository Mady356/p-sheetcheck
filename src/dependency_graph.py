
import networkx as nx
from openpyxl import load_workbook
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import range_boundaries, get_column_letter
import re


def build_dependency_graph(path):
    workbook = load_workbook(path, data_only=False)
    graph = nx.DiGraph()

    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.data_type != "f":
                    continue

                formula_cell = f"{sheet.title}!{cell.coordinate}"
                graph.add_node(formula_cell)

                for token in Tokenizer(cell.value).items:
                    if token.type != "OPERAND" or token.subtype != "RANGE":
                        continue

                    reference = token.value

                    if "!" in reference:
                        sheet_name, reference = reference.rsplit("!", 1)
                        sheet_name = sheet_name.strip("'")
                    else:
                        sheet_name = sheet.title

                    reference = reference.replace("$", "")

                    if re.fullmatch(r"[A-Za-z]{1,3}[1-9][0-9]*", reference):
                        graph.add_edge(
                            f"{sheet_name}!{reference.upper()}",
                            formula_cell
                        )

                    elif ":" in reference:
                        try:
                            min_col, min_row, max_col, max_row = (
                                range_boundaries(reference)
                            )

                            if None in (min_col, min_row, max_col, max_row):
                                continue

                            if ((max_col - min_col + 1)
                                    * (max_row - min_row + 1) > 10000):
                                continue

                            for r in range(min_row, max_row + 1):
                                for c in range(min_col, max_col + 1):
                                    ref = f"{get_column_letter(c)}{r}"
                                    graph.add_edge(
                                        f"{sheet_name}!{ref}",
                                        formula_cell
                                    )
                        except (TypeError, ValueError):
                            pass

    workbook.close()
    return graph


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m src.dependency_graph workbook.xlsx")
        sys.exit(1)

    graph = build_dependency_graph(sys.argv[1])

    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    for node in graph.nodes:
        if graph.in_degree(node) > 0:
            print(f"\nFormula cell: {node}")
            print("Depends on:", list(graph.predecessors(node)))
            print("Used by:", list(graph.successors(node)))
