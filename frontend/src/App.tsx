import { useState, useEffect, useCallback } from "react";
import { URLForm } from "./components/URLForm";
import { URLList } from "./components/URLList";

interface URLItem {
  id: string;
  original_url: string;
  short_code: string;
  click_count: number;
}

function App() {
  const [urls, setUrls] = useState<URLItem[]>([]);
  const [error, setError] = useState("");

  const fetchUrls = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/urls");
      if (!response.ok) {
        throw new Error("Failed to fetch URLs");
      }
      const data = await response.json();
      setUrls(data);
    } catch (err: any) {
      setError(err.message || "An error occurred fetching URLs");
    }
  }, []);

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/urls/${id}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to delete URL");
      }
      setUrls((prev) => prev.filter((url) => url.id !== id));
    } catch (err: any) {
      setError(err.message || "An error occurred deleting URL");
    }
  };

  useEffect(() => {
    fetchUrls();
  }, [fetchUrls]);

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1>URL Shortener</h1>
      <URLForm onURLShortened={fetchUrls} />
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}
      <URLList urls={urls} onDelete={handleDelete} />
    </div>
  );
}

export default App;
