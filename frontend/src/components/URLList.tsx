import React from "react";

interface URLItem {
  id: string;
  original_url: string;
  short_code: string;
  click_count: number;
}

interface URLListProps {
  urls: URLItem[];
  onDelete: (id: string) => void;
}

export const URLList: React.FC<URLListProps> = ({ urls, onDelete }) => {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ccc" }}>
            <th style={{ padding: "0.5rem" }}>Original URL</th>
            <th style={{ padding: "0.5rem" }}>Short URL</th>
            <th style={{ padding: "0.5rem" }}>Clicks</th>
            <th style={{ padding: "0.5rem" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {urls.length === 0 ? (
            <tr>
              <td colSpan={4} style={{ padding: "1rem", textAlign: "center" }}>
                No URLs created yet
              </td>
            </tr>
          ) : (
            urls.map((url) => {
              const shortUrl = `http://localhost/${url.short_code}`;
              return (
                <tr key={url.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "0.5rem", maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    <a href={url.original_url} target="_blank" rel="noopener noreferrer">
                      {url.original_url}
                    </a>
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <a href={shortUrl} target="_blank" rel="noopener noreferrer">
                      {shortUrl}
                    </a>
                  </td>
                  <td style={{ padding: "0.5rem" }}>{url.click_count}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <button onClick={() => onDelete(url.id)} style={{ padding: "0.25rem 0.5rem", color: "red" }}>
                      Delete
                    </button>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
};
