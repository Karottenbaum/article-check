def run_bot(artikelnummern, output_path):
    with open(output_path, "w") as f:
        f.write("Artikelnummern:\n")
        for nummer in artikelnummern:
            f.write(f"{nummer}\n")
