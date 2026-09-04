import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import cytoscape from 'cytoscape';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RotateCcw,
  Layers,
  ArrowUpRight,
  Filter,
  Eye,
  Info,
  X,
  Share2,
} from 'lucide-react';
import RiskBadge from './RiskBadge';

export function CytoscapeGraph({
  graphData,
  height = '480px',
  title = 'Forensic Network Topology',
  onNodeSelect = null,
}) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [layoutName, setLayoutName] = useState('cose');
  const [entityFilter, setEntityFilter] = useState('ALL');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const navigate = useNavigate();

  // Color mapping by entity type and risk score
  const getNodeColor = (type, riskScore) => {
    if (type === 'ring') return '#EF4444';
    if (type === 'device') return '#3B82F6';
    if (type === 'ip') return '#8B5CF6';
    if (type === 'payment_method') return '#F59E0B';
    if (type === 'merchant') return '#EC4899';
    if (type === 'transaction') return '#10B981';

    if (riskScore >= 80) return '#EF4444';
    if (riskScore >= 60) return '#F97316';
    if (riskScore >= 35) return '#F59E0B';
    return '#06B6D4';
  };

  const getNodeShape = (type) => {
    if (type === 'ring') return 'hexagon';
    if (type === 'device') return 'rectangle';
    if (type === 'ip') return 'diamond';
    if (type === 'payment_method') return 'round-rectangle';
    if (type === 'merchant') return 'vee';
    return 'ellipse';
  };

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.nodes) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

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
            borderWidth: isCenter ? 2.5 : 1.5,
            size: isCenter ? 44 : d.type === 'ring' ? 40 : 30,
            shape: getNodeShape(d.type),
          },
        };
      }),
      ...graphData.edges.map((e) => ({
        group: 'edges',
        data: {
          ...e.data,
          lineColor: e.data.type === 'MEMBER_OF' ? '#EF4444' : '#334155',
          width: e.data.weight ? Math.min(3.5, Math.max(1, e.data.weight)) : 1.2,
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
            'color': '#F1F5F9',
            'font-size': '9px',
            'font-family': 'JetBrains Mono, monospace',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'text-background-color': '#070A0F',
            'text-background-opacity': 0.85,
            'text-background-padding': '2px',
            'text-background-shape': 'roundrectangle',
            'transition-property': 'opacity, border-color, border-width',
            'transition-duration': '0.2s',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#06B6D4',
            'border-width': 3.5,
            'shadow-blur': 16,
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
            'arrow-scale': 0.8,
            'curve-style': 'bezier',
            'opacity': 0.65,
            'font-size': '8px',
            'color': '#64748B',
            'font-family': 'JetBrains Mono, monospace',
            'text-rotation': 'autorotate',
            'text-background-color': '#070A0F',
            'text-background-opacity': 0.7,
            'text-background-padding': '1px',
            'transition-property': 'opacity, width, line-color',
            'transition-duration': '0.2s',
          },
        },
        {
          selector: '.highlighted',
          style: {
            'opacity': 1,
            'z-index': 999,
            'border-color': '#06B6D4',
            'border-width': 3,
            'line-color': '#06B6D4',
            'target-arrow-color': '#06B6D4',
          },
        },
        {
          selector: '.dimmed',
          style: {
            'opacity': 0.15,
          },
        },
      ],
      layout: {
        name: layoutName,
        animate: true,
        animationDuration: 400,
        nodeDimensionsIncludeLabels: true,
        padding: 35,
      },
    });

    // Tap on node: select node and trigger drawer callback
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeData = node.data();
      setSelectedNode(nodeData);
      if (onNodeSelect) {
        onNodeSelect(nodeData);
      }
    });

    // Tap on canvas background: clear selection
    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
        cy.elements().removeClass('highlighted dimmed');
      }
    });

    // Hover on node: highlight 1-hop neighborhood
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      setHoveredNode(node.data());
      cy.elements().removeClass('highlighted').addClass('dimmed');
      node.removeClass('dimmed').addClass('highlighted');
      node.neighborhood().removeClass('dimmed').addClass('highlighted');
    });

    // Mouse out from node: restore normal state
    cy.on('mouseout', 'node', () => {
      setHoveredNode(null);
      cy.elements().removeClass('highlighted dimmed');
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graphData, layoutName]);

  // Apply entity type filtering dynamically
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    if (entityFilter === 'ALL') {
      cy.elements().removeClass('dimmed');
    } else {
      cy.elements().addClass('dimmed');
      const matchingNodes = cy.nodes().filter((ele) => ele.data('type') === entityFilter);
      matchingNodes.removeClass('dimmed');
      matchingNodes.connectedEdges().removeClass('dimmed');
    }
  }, [entityFilter]);

  const handleZoomIn = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current && cyRef.current.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current && cyRef.current.fit();
  const handleResetLayout = () => {
    if (cyRef.current) {
      cyRef.current.layout({ name: layoutName, animate: true }).run();
    }
  };

  const handleNavigateEntity = (node) => {
    if (!node) return;
    if (node.type === 'customer') {
      navigate(`/customers/${node.id}`);
    } else if (node.type === 'ring') {
      navigate(`/fraud-rings/${node.id}`);
    } else if (node.type === 'transaction') {
      navigate(`/transactions/${node.id}`);
    }
  };

  const effectiveHeight = isFullscreen ? '750px' : height;

  return (
    <div className={`soc-panel overflow-hidden relative border-soc-border flex flex-col transition-all duration-300 ${isFullscreen ? 'fixed inset-4 z-50 shadow-2xl' : ''}`}>
      {/* Header Bar */}
      <div className="px-4 py-2.5 bg-[#0D131F] border-b border-soc-border flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Layers size={15} className="text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono">
            {title}
          </h3>
          <span className="text-[10px] text-slate-400 font-mono pl-2 border-l border-soc-border">
            {graphData?.total_nodes || 0} nodes · {graphData?.total_edges || 0} edges
          </span>
        </div>

        {/* Entity Type Filter Tabs */}
        <div className="flex items-center gap-1 font-mono text-[9px]">
          <span className="text-slate-400 mr-1 hidden sm:inline">Filter:</span>
          {[
            { id: 'ALL', label: 'All' },
            { id: 'customer', label: 'Accounts' },
            { id: 'device', label: 'Devices' },
            { id: 'ip', label: 'IPs' },
            { id: 'payment_method', label: 'Cards' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setEntityFilter(f.id)}
              className={`px-2 py-0.5 rounded border transition-colors ${
                entityFilter === f.id
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold'
                  : 'bg-soc-surface border-soc-border text-slate-400 hover:text-slate-200'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-1.5">
          <select
            value={layoutName}
            onChange={(e) => setLayoutName(e.target.value)}
            className="text-[10px] font-mono font-semibold bg-[#111927] border border-soc-border rounded px-2 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="cose">Force Directed (CoSE)</option>
            <option value="concentric">Concentric Topology</option>
            <option value="circle">Circular Ring</option>
            <option value="breadthfirst">Hierarchical Tree</option>
          </select>

          <button
            onClick={handleZoomIn}
            className="p-1 rounded bg-[#111927] border border-soc-border text-slate-300 hover:text-slate-100 hover:border-slate-600 transition-colors"
            title="Zoom In"
          >
            <ZoomIn size={13} />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1 rounded bg-[#111927] border border-soc-border text-slate-300 hover:text-slate-100 hover:border-slate-600 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={13} />
          </button>
          <button
            onClick={handleFit}
            className="p-1 rounded bg-[#111927] border border-soc-border text-slate-300 hover:text-slate-100 hover:border-slate-600 transition-colors"
            title="Fit to Screen"
          >
            <Maximize2 size={13} />
          </button>
          <button
            onClick={handleResetLayout}
            className="p-1 rounded bg-[#111927] border border-soc-border text-slate-300 hover:text-slate-100 hover:border-slate-600 transition-colors"
            title="Re-run Layout"
          >
            <RotateCcw size={13} />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1 rounded bg-[#111927] border border-soc-border text-slate-300 hover:text-cyan-400 hover:border-cyan-500/40 transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Expand Fullscreen'}
          >
            {isFullscreen ? <Minimize2 size={13} /> : <Share2 size={13} />}
          </button>
        </div>
      </div>

      {/* Canvas Area with Cyber-Grid Background */}
      <div className="relative w-full soc-grid-bg" style={{ height: effectiveHeight }}>
        <div
          ref={containerRef}
          className="w-full h-full bg-[#070A0F]/90 cursor-grab active:cursor-grabbing"
        />

        {/* Floating Hover HUD Tooltip */}
        {hoveredNode && !selectedNode && (
          <div className="absolute top-3 left-3 bg-[#0D131F]/95 backdrop-blur-md border border-cyan-500/40 rounded px-3 py-1.5 text-xs font-mono text-slate-200 pointer-events-none shadow-2xl z-10 flex items-center gap-2 animate-in fade-in duration-100">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="font-bold text-cyan-300">{hoveredNode.id}</span>
            <span className="text-[10px] text-slate-400 uppercase">({hoveredNode.type})</span>
            {hoveredNode.risk_score !== undefined && (
              <span className="text-[10px] px-1 rounded bg-red-500/20 text-red-300 font-bold border border-red-500/30">
                {hoveredNode.risk_score.toFixed(1)}
              </span>
            )}
          </div>
        )}

        {/* Selected Node Quick Overlay */}
        {selectedNode && (
          <div className="absolute top-3 right-3 w-72 bg-[#0D131F]/95 backdrop-blur-md border border-soc-border rounded p-3 text-xs space-y-2.5 shadow-2xl animate-in fade-in zoom-in-95 duration-150 z-10">
            <div className="flex items-start justify-between pb-1.5 border-b border-soc-border">
              <div>
                <span className="text-[9px] uppercase font-bold text-slate-400 font-mono">
                  {selectedNode.type} NODE
                </span>
                <div className="font-mono font-bold text-slate-100 text-sm">{selectedNode.id}</div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-200"
              >
                <X size={14} />
              </button>
            </div>

            {selectedNode.risk_score !== undefined && selectedNode.risk_score !== null && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[11px]">Risk Rating:</span>
                <RiskBadge
                  level={selectedNode.risk_level || (selectedNode.risk_score >= 80 ? 'CRITICAL' : selectedNode.risk_score >= 60 ? 'HIGH' : 'LOW')}
                  score={selectedNode.risk_score}
                  size="sm"
                />
              </div>
            )}

            {selectedNode.subtext && (
              <div className="text-[11px] text-slate-300 bg-[#111927] p-2 rounded border border-soc-border/70 font-mono">
                {selectedNode.subtext}
              </div>
            )}

            <div className="space-y-1 pt-1">
              {['customer', 'ring', 'transaction'].includes(selectedNode.type) && (
                <button
                  onClick={() => handleNavigateEntity(selectedNode)}
                  className="w-full py-1.5 px-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 text-[11px] font-mono font-bold flex items-center justify-center gap-1.5 transition-colors shadow-sm"
                >
                  <span>Open Forensic Dossier</span>
                  <ArrowUpRight size={13} />
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer Legend Bar */}
      <div className="px-4 py-2 bg-[#0D131F] border-t border-soc-border flex flex-wrap items-center justify-between text-[10px] font-mono text-slate-400">
        <div className="flex flex-wrap items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-red-500 rotate-45 inline-block"></span>
            <span>Syndicate Ring</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
            <span>Customer Account</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-blue-500 inline-block"></span>
            <span>Hardware Device</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-purple-500 rotate-45 inline-block"></span>
            <span>Proxy IP</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-2 rounded-sm bg-amber-500 inline-block"></span>
            <span>Payment Instrument</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 bg-pink-500 inline-block"></span>
            <span>Merchant</span>
          </span>
        </div>
        <span className="text-cyan-400/80">Click node to inspect forensic links</span>
      </div>
    </div>
  );
}

export default CytoscapeGraph;
