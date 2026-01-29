import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { AlertTriangle, TrendingUp, Activity } from 'lucide-react';

export default function ThoughtEvolutionViewer({ student }) {
    const [selectedIndex, setSelectedIndex] = useState(student.thoughtEvolution.length - 1);

    const evolution = student.thoughtEvolution;
    const currentState = evolution[selectedIndex];

    // Detect suspicious jumps (large increase in nodes/connections in short time)
    const detectSuspiciousJump = (index) => {
        if (index === 0) return false;
        const prev = evolution[index - 1];
        const curr = evolution[index];

        const nodeJump = curr.nodes - prev.nodes;
        const connectionJump = curr.connections - prev.connections;

        // If nodes increased by more than 10 or connections by more than 15 in one step
        return nodeJump > 10 || connectionJump > 15;
    };

    const getQualityColor = (quality) => {
        switch (quality) {
            case 'excellent': return 'text-green-400';
            case 'strong': return 'text-blue-400';
            case 'developing': return 'text-yellow-400';
            case 'suspicious': return 'text-red-400';
            case 'basic': return 'text-gray-400';
            default: return 'text-gray-400';
        }
    };

    const formatDate = (timestamp) => {
        return new Date(timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    return (
        <Card className="bg-midnight-light border-electric/20">
            <CardHeader>
                <CardTitle className="text-electric flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Thought Evolution Timeline
                </CardTitle>
                <CardDescription className="text-gray-400">
                    Replay Logic Tree growth to detect AI-generated jumps
                </CardDescription>
            </CardHeader>
            <CardContent>
                {/* Timeline Slider */}
                <div className="mb-6">
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-400 min-w-[120px]">
                            {formatDate(currentState.timestamp)}
                        </span>
                        <input
                            type="range"
                            min="0"
                            max={evolution.length - 1}
                            value={selectedIndex}
                            onChange={(e) => setSelectedIndex(parseInt(e.target.value))}
                            className="flex-1 h-2 bg-midnight rounded-lg appearance-none cursor-pointer slider"
                            style={{
                                background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${(selectedIndex / (evolution.length - 1)) * 100}%, #1a1f2e ${(selectedIndex / (evolution.length - 1)) * 100}%, #1a1f2e 100%)`
                            }}
                        />
                        <span className="text-sm text-gray-400">
                            Step {selectedIndex + 1} of {evolution.length}
                        </span>
                    </div>
                </div>

                {/* Current State Display */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                        <div className="text-sm text-gray-400 mb-1">Nodes</div>
                        <div className="text-3xl font-bold text-electric">{currentState.nodes}</div>
                        {selectedIndex > 0 && (
                            <div className="text-xs text-gray-500 mt-1">
                                +{currentState.nodes - evolution[selectedIndex - 1].nodes} from previous
                            </div>
                        )}
                    </div>
                    <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                        <div className="text-sm text-gray-400 mb-1">Connections</div>
                        <div className="text-3xl font-bold text-electric">{currentState.connections}</div>
                        {selectedIndex > 0 && (
                            <div className="text-xs text-gray-500 mt-1">
                                +{currentState.connections - evolution[selectedIndex - 1].connections} from previous
                            </div>
                        )}
                    </div>
                    <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                        <div className="text-sm text-gray-400 mb-1">Quality</div>
                        <div className={`text-xl font-bold capitalize ${getQualityColor(currentState.quality)}`}>
                            {currentState.quality}
                        </div>
                    </div>
                </div>

                {/* Suspicious Jump Warning */}
                {detectSuspiciousJump(selectedIndex) && (
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-4">
                        <div className="flex items-start gap-3">
                            <AlertTriangle className="h-5 w-5 text-red-400 mt-0.5" />
                            <div>
                                <div className="font-semibold text-red-400 mb-1">Suspicious Jump Detected</div>
                                <div className="text-sm text-gray-300">
                                    Large increase in complexity detected between this step and the previous one.
                                    This could indicate AI-generated content rather than organic thought development.
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Growth Pattern Visualization */}
                <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="h-4 w-4 text-electric" />
                        <span className="text-sm font-medium text-gray-300">Growth Pattern</span>
                    </div>
                    <div className="flex gap-1 h-12 items-end">
                        {evolution.map((state, index) => {
                            const isSuspicious = detectSuspiciousJump(index);
                            const isSelected = index === selectedIndex;
                            const height = (state.nodes / Math.max(...evolution.map(s => s.nodes))) * 100;

                            return (
                                <div
                                    key={index}
                                    className={`flex-1 rounded-t cursor-pointer transition-all ${isSuspicious ? 'bg-red-500' : 'bg-electric'
                                        } ${isSelected ? 'opacity-100 ring-2 ring-electric-light' : 'opacity-50 hover:opacity-75'}`}
                                    style={{ height: `${height}%` }}
                                    onClick={() => setSelectedIndex(index)}
                                    title={`${formatDate(state.timestamp)}: ${state.nodes} nodes`}
                                />
                            );
                        })}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                        <span>{formatDate(evolution[0].timestamp)}</span>
                        <span>{formatDate(evolution[evolution.length - 1].timestamp)}</span>
                    </div>
                </div>

                {/* Legend */}
                <div className="mt-4 flex gap-4 text-xs text-gray-400">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-electric rounded"></div>
                        <span>Organic Growth</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded"></div>
                        <span>Suspicious Jump</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
