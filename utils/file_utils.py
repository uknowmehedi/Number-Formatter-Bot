import pandas as pd

def read_file(file_path):
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
        return "\n".join(df.astype(str).stack().tolist())
    else:
        raise ValueError("Unsupported file format.")
    
    import os

def cleanup_file(file_path):
    try:
        os.remove(file_path)
        print(f"✅ Deleted: {file_path}")
    except Exception as e:
        print(f"⚠️ Could not delete {file_path}: {e}")
    
     def export_to_file(numbers, format="xlsx", file_path="output"):
    if format == "xlsx":
        df = pd.DataFrame({"Phone Numbers": numbers})
        file_name = f"{file_path}.xlsx"
        df.to_excel(file_name, index=False)
    elif format == "txt":
        file_name = f"{file_path}.txt"
        with open(file_name, "w") as f:
            f.write("\n".join(numbers))
    elif format == "csv":
        df = pd.DataFrame({"Phone Numbers": numbers})
        file_name = f"{file_path}.csv"
        df.to_csv(file_name, index=False)
    else:
        raise ValueError("Unsupported export format.")
    return file_name