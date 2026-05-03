interface Props {
  source: string;
}

export function JsonlView({ source }: Props) {
  const lines = source.split(/\r?\n/).filter((l) => l.trim().length > 0);
  return (
    <div className="jsonl-view" data-testid="jsonl-view">
      <table>
        <tbody>
          {lines.map((line, i) => {
            let pretty = line;
            try {
              pretty = JSON.stringify(JSON.parse(line));
            } catch {
              /* keep raw */
            }
            return (
              <tr key={i} data-row data-row-index={i}>
                <td className="jsonl-row-num">{i + 1}</td>
                <td className="jsonl-row-body">
                  <code>{pretty}</code>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
