import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Info, Layers } from 'lucide-react';
import RiskBadge from './RiskBadge';

export function CytoscapeGraph({ graphData, height = '450px', title = 'Forensic Network Topology' }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [layoutName, setLayoutName] = useState('cose');

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.nodes) return;

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Color definitions
    const getNodeColor = (type, riskScore) => {
      if (type === 'ring') return '#EF4444'; // Red
      if (type === 'device') return '#3B82F6'; // Blue
      if (type === 'ip') return '#A855F7'; // Purple
      if (type === 'payment_method') return '#F59E0B'; // Amber
      if (type === 'merchant') return '#EC4899'; // Pink
      if (type === 'transaction') return '#10B981'; // Emerald
      
      // Customer node coloring by risk
      if (riskScore >= 80) return '#EF4444';
      if (riskScore >= 60) return '#F97316';
      if (riskScore >= 35) return '#F59E0B';
      return '#06B6D4'; // Cyan default
    };

    const getNodeShape = (type) => {
      if (type === 'ring') return 'hexagon';
      if (type === 'device') return 'rectangle';
      if (type === 'ip') return 'diamond';
      if (type === 'payment_method') return 'round-rectangle';
      if (type === 'merchant') return 'vee';
      return 'ellipse';
    };

    const elements = [
      ...graphData.nodes.map((n) => {
        const d = n.data;
        const color = getNodeColor(d.type, d.risk_score);
        const isCenter = d.id === graphData.center_node_id;
        return {
          group: 'nodes',
          data: {
            ...d,
            bgColor: color,
            borderColor: isCenter ? '#FFFFFF' : '#1E293B',
            borderWidth: isCenter ? 3 : 1.5,
            size: isCenter ? 48 : (d.type === 'ring' ? 44 : 34),
            shape: getNodeShape(d.type),
          },
        };
      }),
      ...graphData.edges.map((e) => ({
        group: 'edges',
        data: {
          ...e.data,
          lineColor: e.data.type === 'MEMBER_OF' ? '#EF4444' : '#475569',
          width: e.data.weight ? Math.min(4, Math.max(1, e.data.weight)) : 1.5,
        },
      })),
    ];

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(bgColor)',
            'border-color': 'data(borderColor)',
            'border-width': 'data(borderWidth)',
            'shape': 'data(shape)',
            'width': 'data(size)',
            'height': 'data(size)',
            'label': 'data(label)',
            'color': '#F8FAFC',
            'font-size': '10px',
            'font-family': 'JetBrains Mono, monospace',
            'text-valign': 'bottom',
            'text-margin-y': 5,
            'text-background-color': '#0B0F19',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#06B6D4',
            'border-width': 4,
            'shadow-blur': 15,
            'shadow-color': '#06B6D4',
            'shadow-opacity': 0.8,
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'line-color': 'data(lineColor)',
            'target-arrow-color': 'data(lineColor)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.7,
            'font-size': '8px',
            'color': '#94A3B8',
            'text-rotation': 'autorotate',
            'text-background-color': '#0B0F19',
            'text-background-opacity': 0.7,
            'text-background-padding': '1px',
          },
        },
      ],
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 500,
        nodeDimensionsIncludeLabels: true,
        padding: 30,
      },
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      setSelectedNode(node.data());
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graphData, layoutName]);

  const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current && cyRef.current.fit();
  const handleResetLayout = () => {
    if (cyRef.current) {
      cyRef.current.layout({ name: layoutName, animate: true }).run();
    }
  };

  return (
    <div className="glass-panel p-4 relative overflow-hidden flex flex-col">
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-800 gap-2">
        <div className="flex items-center gap-2">
          <Layers className="text-cyan-400" size={16} />
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">{title}</h4>
          <span className="text-[10px] text-slate-400 font-mono px-2 py-0.5 rounded bg-slate-800/80">
            {graphData?.nodes?.length || 0} Nodes · {graphData?.edges?.length || 0} Edges
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          <select
            value={layoutName}
            onChange={(e) => setLayoutName(e.target.value)}
            className="text-[11px] bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="cose">Force Directed (COSE)</option>
            <option value="concentric">Concentric Radial</option>
            <option value="breadthfirst">Breadthfirst Tree</option>
            <option value="circle">Circle Ring</option>
          </select>
          <button
            onClick={handleZoomIn}
            title="Zoom In"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={handleZoomOut}
            title="Zoom Out"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={handleFit}
            title="Fit to Screen"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <Maximize2 size={14} />
          </button>
          <button
            onClick={handleResetLayout}
            title="Reset Layout"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
          >
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {/* Network Legend */}
      <div className="flex flex-wrap items-center gap-3 py-2 text-[10px] text-slate-400 border-b border-slate-800/60 font-medium">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span> Customer
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-blue-500"></span> Device
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rotate-45 bg-purple-500"></span> IP Address
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-amber-500"></span> Payment Method
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-pink-500"></span> Merchant
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 bg-red-500 clip-hexagon"></span> Fraud Ring
        </span>
      </div>

      {/* Cytoscape Canvas */}
      <div className="relative w-full" style={{ height }}>
        <div ref={containerRef} className="w-full h-full bg-[#070A11] rounded-b-xl" />

        {/* Selected Node Inspector Flyout */}
        {selectedNode && (
          <div className="absolute bottom-3 left-3 bg-slate-900/95 border border-cyan-500/40 p-3 rounded-xl shadow-2xl max-w-xs text-xs backdrop-blur-md z-10 space-y-1.5 animate-in fade-in slide-in-from-bottom-2">
            <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
              <span className="font-bold text-slate-200 font-mono">{selectedNode.id}</span>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                {selectedNode.type}
              </span>
            </div>
            {selectedNode.risk_score !== undefined && selectedNode.risk_score !== null && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Risk Rating:</span>
                <RiskBadge level={selectedNode.risk_level || 'LOW'} score={selectedNode.risk_score} size="sm" />
              </div>
            )}
            {selectedNode.subtext && (
              <p className="text-[11px] text-slate-400">{selectedNode.subtext}</p>
            )}
            <p className="text-[9px] text-slate-500 italic">Click background to dismiss</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CytoscapeGraph;
