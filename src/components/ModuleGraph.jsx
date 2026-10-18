// Lightweight dependency graph renderer, no additional npm dependency needed.
// Each arrow means source module imports target module.
function ModuleGraph({ graph }) {
  const allNodes = graph?.nodes ?? [];
  const allEdges = graph?.edges ?? [];
  const nodes = allNodes.slice(0, 24);
  if (!nodes.length) return <p className="dl-muted">No parsed modules available.</p>;

  const cols = nodes.length <= 4 ? 2 : nodes.length <= 9 ? 3 : 4;
  const cardW = 220;
  const cardH = 70;
  const gapX = 35;
  const gapY = 65;
  const margin = 25;
  const rows = Math.ceil(nodes.length / cols);
  const width = 2 * margin + cols * cardW + (cols - 1) * gapX;
  const height = 2 * margin + rows * cardH + (rows - 1) * gapY;
  const positions = new Map(nodes.map((node, index) => [node.id, {
    x: margin + (index % cols) * (cardW + gapX),
    y: margin + Math.floor(index / cols) * (cardH + gapY),
  }]));
  const edges = allEdges.filter((edge) => positions.has(edge.source) && positions.has(edge.target));

  return (
    <div>
      <p className="dl-muted dl-small">Arrows show imports between analyzed source files. Isolated nodes have no resolved internal imports.</p>
      <div className="dl-graph-scroll">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Repository module dependency graph with ${allNodes.length} modules and ${allEdges.length} internal dependencies`}>
          <defs><marker id="dl-arrow" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#6485cf" /></marker></defs>
          {edges.map((edge, index) => {
            const a = positions.get(edge.source);
            const b = positions.get(edge.target);
            const ax = a.x + cardW / 2;
            const ay = a.y + cardH / 2;
            const bx = b.x + cardW / 2;
            const by = b.y + cardH / 2;
            const dx = bx - ax; const dy = by - ay;
            const distanceFactor = Math.min(
              dx ? (cardW / 2 + 7) / Math.abs(dx) : Infinity,
              dy ? (cardH / 2 + 7) / Math.abs(dy) : Infinity,
            );
            return <line key={`${edge.source}:${edge.target}:${index}`} x1={ax + dx * distanceFactor} y1={ay + dy * distanceFactor} x2={bx - dx * distanceFactor} y2={by - dy * distanceFactor} stroke="#6485cf" strokeWidth="2" markerEnd="url(#dl-arrow)" />;
          })}
          {nodes.map((node) => {
            const p = positions.get(node.id);
            const basename = node.id.split('/').pop();
            const directory = node.id.includes('/') ? node.id.slice(0, node.id.lastIndexOf('/')) : '/';
            return <g key={node.id}><title>{node.id}</title><rect x={p.x} y={p.y} width={cardW} height={cardH} rx="12" fill="#f2f6ff" stroke="#bdcceb" strokeWidth="1.5" /><text x={p.x + 12} y={p.y + 29} fontSize="15" fontWeight="600" fill="#233660">{basename.length > 24 ? `${basename.slice(0, 22)}…` : basename}</text><text x={p.x + 12} y={p.y + 49} fontSize="12" fill="#71809b">{directory.length > 30 ? `…${directory.slice(-27)}` : directory}</text></g>;
          })}
        </svg>
      </div>
      {allNodes.length > nodes.length && <p className="dl-muted dl-small">Displaying the first {nodes.length} of {allNodes.length} modules.</p>}
      {!edges.length && <p className="dl-muted dl-small">No internal edges were resolved among the displayed modules.</p>}
    </div>
  );
}
export default ModuleGraph;
