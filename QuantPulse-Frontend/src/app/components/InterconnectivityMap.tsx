
import { useEffect, useState, useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { AlertTriangle, Activity, Zap, Info, ShieldCheck } from 'lucide-react';
import graphDataRaw from '@/app/data/graphData.json';

// Types
interface Node {
    id: string;
    sector: string;  // Changed from group to sector
    x?: number;
    y?: number;
    color?: string; // For display
    val?: number; // Radius
}

interface Link {
    source: string | Node;
    target: string | Node;
    weight: number;  // Changed from value to weight
    type?: string;
}

interface GraphData {
    nodes: Node[];
    links: Link[];
}

export function InterconnectivityMap() {
    const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [shockActive, setShockActive] = useState(false);
    const graphRef = useRef<any>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Process raw data to match graph format
        // Assign colors based on sector
        const nodes = graphDataRaw.nodes.map(n => ({
            ...n,
            color: getSectorColor(n.sector),
            val: 10 // Larger uniform size for better visibility
        }));

        // Links use weight property
        const links = graphDataRaw.links.map(l => ({ ...l }));

        setData({ nodes, links });
    }, []);

    useEffect(() => {
        // Responsive resize
        const handleResize = () => {
            if (containerRef.current) {
                setDimensions({
                    width: containerRef.current.clientWidth,
                    height: containerRef.current.clientHeight
                });
            }
        };

        window.addEventListener('resize', handleResize);
        handleResize(); // Initial

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Helpers
    const getSectorColor = (sector: string) => {
        // Enhanced color palette with more vibrant, distinct colors
        switch (sector) {
            case 'Banking': return '#8B5CF6'; // Vibrant Purple
            case 'IT': return '#10B981'; // Bright Emerald
            case 'Energy': return '#3B82F6'; // Bright Blue
            case 'Auto': return '#F59E0B'; // Bright Amber
            case 'FMCG': return '#EC4899'; // Bright Pink
            default: return '#94A3B8'; // Slate
        }
    };

    const handleNodeClick = (node: Node) => {
        setSelectedNode(node);
        // Focus camera
        if (graphRef.current) {
            graphRef.current.centerAt(node.x, node.y, 1000);
            graphRef.current.zoom(2.5, 2000);
        }
    };

    const simulateShock = () => {
        setShockActive(prev => !prev);
    };

    // Memoized insights - removed as new structure doesn't have insights
    const totalNodes = useMemo(() => data.nodes.length, [data.nodes]);

    return (
        <div className="flex flex-col h-[calc(100vh-100px)] gap-6 p-1">

            {/* Header / Actions */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-[#F0F0F0] flex items-center gap-2">
                        <Activity className="size-6 text-[#4A9EFF]" />
                        Market Topology
                    </h1>
                    <p className="text-[#A0A0A0] text-sm">Real-time correlation network & contagion analysis</p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={simulateShock}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all border ${shockActive
                            ? 'bg-[#E05252]/10 border-red-500 text-[#E05252] shadow-[0_0_15px_rgba(239,68,68,0.3)]'
                            : 'bg-[#1A6FD4]/10 border-[#1A6FD4]/50 text-[#4A9EFF] hover:bg-[#1A6FD4]/20'
                            }`}
                    >
                        <Zap className="size-4" />
                        {shockActive ? 'Stop Simulation' : 'Simulate Market Shock'}
                    </button>
                </div>
            </div>

            <div className="flex flex-1 gap-6 min-h-0">

                {/* Main Graph Card */}
                <div
                    className="flex-1 relative rounded-xl border border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-sm overflow-hidden shadow-lg"
                    ref={containerRef}
                >
                    {/* Legend/Overlay - Enhanced styling */}
                    <div className="absolute top-4 left-4 z-10 bg-gradient-to-br from-black/70 to-black/50 backdrop-blur-md p-4 rounded-xl border border-white/30 text-xs text-[#F0F0F0] shadow-2xl">
                        <div className="text-sm font-bold mb-3 text-white">Sector Legend</div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="w-4 h-4 rounded-full bg-[#8B5CF6] shadow-lg shadow-purple-500/60 border border-purple-300/30"></span> 
                            <span className="font-medium">Banking</span>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="w-4 h-4 rounded-full bg-[#10B981] shadow-lg shadow-emerald-500/60 border border-emerald-300/30"></span> 
                            <span className="font-medium">IT</span>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="w-4 h-4 rounded-full bg-[#3B82F6] shadow-lg shadow-blue-500/60 border border-blue-300/30"></span> 
                            <span className="font-medium">Energy</span>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="w-4 h-4 rounded-full bg-[#F59E0B] shadow-lg shadow-amber-500/60 border border-amber-300/30"></span> 
                            <span className="font-medium">Auto</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="w-4 h-4 rounded-full bg-[#EC4899] shadow-lg shadow-pink-500/60 border border-pink-300/30"></span> 
                            <span className="font-medium">FMCG</span>
                        </div>
                    </div>

                    <ForceGraph2D
                        ref={graphRef}
                        width={dimensions.width}
                        height={dimensions.height}
                        graphData={data}
                        nodeLabel="id"
                        nodeRelSize={8}

                        // Visuals - Enhanced for better aesthetics
                        backgroundColor="rgba(0,0,0,0)" // Transparent
                        linkColor={(link: any) => {
                            if (shockActive) return 'rgba(239, 68, 68, 0.6)'; // Red with transparency
                            return 'rgba(147, 197, 253, 0.5)'; // Brighter blue for better visibility
                        }}
                        linkWidth={link => {
                            // Display link weight (correlation strength)
                            const weight = link.weight as number;
                            return weight * 5; // Scale for visibility (increased from 3)
                        }}
                        linkLabel={(link: any) => {
                            // Show weight on hover
                            return `Correlation: ${(link.weight * 100).toFixed(1)}%`;
                        }}
                        linkCanvasObjectMode={() => 'after'}
                        linkCanvasObject={(link: any, ctx, globalScale) => {
                            // Draw weight labels on links
                            const weight = link.weight as number;
                            if (weight > 0.15 && globalScale > 1.5) { // Only show for strong correlations when zoomed
                                const start = link.source;
                                const end = link.target;
                                
                                // Calculate midpoint
                                const textPos = {
                                    x: start.x + (end.x - start.x) / 2,
                                    y: start.y + (end.y - start.y) / 2
                                };
                                
                                const label = (weight * 100).toFixed(1) + '%';
                                const fontSize = 10 / globalScale;
                                ctx.font = `${fontSize}px Sans-Serif`;
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                
                                // Background for readability
                                const textWidth = ctx.measureText(label).width;
                                const padding = 2 / globalScale;
                                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                                ctx.fillRect(
                                    textPos.x - textWidth / 2 - padding,
                                    textPos.y - fontSize / 2 - padding,
                                    textWidth + padding * 2,
                                    fontSize + padding * 2
                                );
                                
                                // Text
                                ctx.fillStyle = shockActive ? '#FCA5A5' : '#60A5FA';
                                ctx.fillText(label, textPos.x, textPos.y);
                            }
                        }}
                        nodeCanvasObject={(node, ctx, globalScale) => {
                            // Custom Node Rendering - Enhanced with glow effects
                            const label = node.id;
                            const fontSize = 11 / globalScale;
                            const isSelected = selectedNode?.id === node.id;
                            const nodeRadius = 6;

                            // Outer Glow (if shock or selected)
                            if (shockActive && (node.id === 'ICICIBANK' || node.id === 'SBIN')) {
                                ctx.beginPath();
                                ctx.arc(node.x!, node.y!, nodeRadius * 2.5, 0, 2 * Math.PI, false);
                                const gradient = ctx.createRadialGradient(node.x!, node.y!, 0, node.x!, node.y!, nodeRadius * 2.5);
                                gradient.addColorStop(0, 'rgba(239, 68, 68, 0.6)');
                                gradient.addColorStop(1, 'rgba(239, 68, 68, 0)');
                                ctx.fillStyle = gradient;
                                ctx.fill();
                            } else if (isSelected) {
                                ctx.beginPath();
                                ctx.arc(node.x!, node.y!, nodeRadius * 2, 0, 2 * Math.PI, false);
                                const gradient = ctx.createRadialGradient(node.x!, node.y!, 0, node.x!, node.y!, nodeRadius * 2);
                                gradient.addColorStop(0, 'rgba(96, 165, 250, 0.6)');
                                gradient.addColorStop(1, 'rgba(96, 165, 250, 0)');
                                ctx.fillStyle = gradient;
                                ctx.fill();
                            }

                            // Main Node Circle with border
                            ctx.beginPath();
                            ctx.arc(node.x!, node.y!, nodeRadius, 0, 2 * Math.PI, false);
                            ctx.fillStyle = node.color || '#fff';
                            ctx.fill();
                            
                            // Add border for depth
                            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                            ctx.lineWidth = 1.5 / globalScale;
                            ctx.stroke();

                            // Text with shadow for better readability
                            ctx.font = `bold ${fontSize}px Sans-Serif`;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            
                            // Text shadow
                            ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
                            ctx.shadowBlur = 5;
                            ctx.shadowOffsetX = 0;
                            ctx.shadowOffsetY = 1;
                            
                            ctx.fillStyle = isSelected ? '#fff' : 'rgba(255,255,255,0.95)';
                            ctx.fillText(label, node.x!, node.y! + nodeRadius + 8);
                            
                            // Reset shadow
                            ctx.shadowColor = 'transparent';
                            ctx.shadowBlur = 0;
                        }}

                        // Interaction
                        onNodeClick={handleNodeClick}

                        // Force simulation settings for better clustering
                        d3AlphaDecay={0.02}
                        d3VelocityDecay={0.3}
                        cooldownTicks={100}
                        
                        // Charge force - stronger attraction/repulsion for better grouping
                        nodeCharge={-300}
                        
                        // Link force - stronger to keep connected nodes together
                        linkStrength={1}
                        
                        // Center force - keep graph centered
                        centerForce={0.5}

                        // Particles for shock
                        linkDirectionalParticles={shockActive ? 4 : 0}
                        linkDirectionalParticleSpeed={0.01}
                        linkDirectionalParticleWidth={2}
                        linkDirectionalParticleColor={() => '#EF4444'}
                    />
                </div>

                {/* Sidebar Panel */}
                <div className="w-80 flex flex-col gap-4">
                    {/* Stats Widget */}
                    <div className="p-4 rounded-xl border border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-sm">
                        <h3 className="text-sm font-semibold text-[#F0F0F0] mb-4 flex items-center gap-2">
                            <Info className="size-4 text-[#06B6D4]" /> Network Metrics
                        </h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-[#A0A0A0]">Total Stocks</span>
                                <span className="text-[#4A9EFF] font-mono">{data.nodes.length}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-[#A0A0A0]">Correlations</span>
                                <span className="text-purple-400 font-mono">{data.links.length}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-[#A0A0A0]">Sectors</span>
                                <span className="text-[#4CAF7D] font-mono">5</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-[#A0A0A0]">Avg. Correlation</span>
                                <span className="text-[#E8A838] font-mono">
                                    {data.links.length > 0 
                                        ? (data.links.reduce((sum, l) => sum + (l.weight || 0), 0) / data.links.length * 100).toFixed(1) + '%'
                                        : 'N/A'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Dynamic Context Panel */}
                    <div className={`flex-1 p-4 rounded-xl border border-[rgba(74, 158, 255, 0.15)] bg-[rgba(30, 30, 30, 0.9)] backdrop-blur-sm transition-all ${selectedNode ? 'opacity-100' : 'opacity-60 grayscale'}`}>
                        <h3 className="text-sm font-semibold text-[#F0F0F0] mb-4 flex items-center gap-2">
                            <ShieldCheck className="size-4 text-[#10B981]" /> Stock Analysis
                        </h3>

                        {selectedNode ? (
                            <div className="space-y-4">
                                <div className="text-xl font-bold text-white">{selectedNode.id}</div>
                                <div className="text-sm text-[#A0A0A0]">{selectedNode.sector} Sector</div>

                                <div className="space-y-2">
                                    <div className="text-xs text-[#A0A0A0] uppercase tracking-wider">Network Connections</div>
                                    <div className="text-2xl font-bold text-[#4A9EFF]">
                                        {data.links.filter(l => 
                                            (typeof l.source === 'object' ? l.source.id : l.source) === selectedNode.id ||
                                            (typeof l.target === 'object' ? l.target.id : l.target) === selectedNode.id
                                        ).length}
                                    </div>
                                    <div className="text-xs text-[#A0A0A0]">Direct correlations</div>
                                </div>

                                {/* Strongest Correlations */}
                                <div className="p-3 bg-[#1E1E1E]/50 rounded-lg border border-[#2A2A2A]">
                                    <div className="text-xs text-[#A0A0A0] mb-2">Strongest Correlations</div>
                                    <div className="space-y-1">
                                        {data.links
                                            .filter(l => 
                                                (typeof l.source === 'object' ? l.source.id : l.source) === selectedNode.id ||
                                                (typeof l.target === 'object' ? l.target.id : l.target) === selectedNode.id
                                            )
                                            .sort((a, b) => (b.weight || 0) - (a.weight || 0))
                                            .slice(0, 3)
                                            .map((link, idx) => {
                                                const otherId = (typeof link.source === 'object' ? link.source.id : link.source) === selectedNode.id
                                                    ? (typeof link.target === 'object' ? link.target.id : link.target)
                                                    : (typeof link.source === 'object' ? link.source.id : link.source);
                                                return (
                                                    <div key={idx} className="flex justify-between text-xs">
                                                        <span className="text-[#A0A0A0]">{otherId}</span>
                                                        <span className="text-[#4A9EFF] font-mono">{((link.weight || 0) * 100).toFixed(1)}%</span>
                                                    </div>
                                                );
                                            })}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex items-center justify-center text-[#A0A0A0] text-sm text-center">
                                Select a node to view <br /> correlation analysis
                            </div>
                        )}
                    </div>
                </div>

            </div>

        </div>
    );
}
