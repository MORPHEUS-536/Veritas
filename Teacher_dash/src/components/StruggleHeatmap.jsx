import { useState } from 'react';
import { ArrowUpDown, Eye } from 'lucide-react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from './ui/table';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

export default function StruggleHeatmap({ students, onViewStudent }) {
    const [sortConfig, setSortConfig] = useState({ key: 'integrityScore', direction: 'desc' });

    const handleSort = (key) => {
        setSortConfig((prev) => ({
            key,
            direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc',
        }));
    };

    const sortedStudents = [...students].sort((a, b) => {
        const aValue = a[sortConfig.key];
        const bValue = b[sortConfig.key];

        if (sortConfig.key === 'gritLevel') {
            const gritOrder = { 'Low': 1, 'Medium': 2, 'High': 3, 'Elite': 4 };
            return sortConfig.direction === 'asc'
                ? gritOrder[aValue] - gritOrder[bValue]
                : gritOrder[bValue] - gritOrder[aValue];
        }

        if (typeof aValue === 'number') {
            return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
        }

        return sortConfig.direction === 'asc'
            ? String(aValue).localeCompare(String(bValue))
            : String(bValue).localeCompare(String(aValue));
    });

    const getScoreColor = (score) => {
        if (score >= 85) return 'text-green-400';
        if (score >= 70) return 'text-yellow-400';
        if (score >= 55) return 'text-orange-400';
        return 'text-red-400';
    };

    const getGritBadgeVariant = (grit) => {
        switch (grit) {
            case 'Elite': return 'default';
            case 'High': return 'secondary';
            case 'Medium': return 'warning';
            case 'Low': return 'danger';
            default: return 'outline';
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Active': return 'text-green-400';
            case 'Struggling': return 'text-orange-400';
            case 'At Risk': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    return (
        <Card className="bg-midnight-light border-electric/20">
            <CardHeader>
                <CardTitle className="text-electric text-2xl font-bold">Struggle Heatmap</CardTitle>
                <CardDescription className="text-gray-400">
                    Real-time ranking by Integrity Score and Grit Level
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border border-electric/20 overflow-hidden">
                    <Table>
                        <TableHeader>
                            <TableRow className="border-b border-electric/20 hover:bg-midnight">
                                <TableHead className="text-electric font-semibold">
                                    <button
                                        onClick={() => handleSort('name')}
                                        className="flex items-center gap-1 hover:text-electric-light transition-colors"
                                    >
                                        Student Name
                                        <ArrowUpDown className="h-4 w-4" />
                                    </button>
                                </TableHead>
                                <TableHead className="text-electric font-semibold">
                                    <button
                                        onClick={() => handleSort('integrityScore')}
                                        className="flex items-center gap-1 hover:text-electric-light transition-colors"
                                    >
                                        Integrity Score
                                        <ArrowUpDown className="h-4 w-4" />
                                    </button>
                                </TableHead>
                                <TableHead className="text-electric font-semibold">
                                    <button
                                        onClick={() => handleSort('gritLevel')}
                                        className="flex items-center gap-1 hover:text-electric-light transition-colors"
                                    >
                                        Grit Level
                                        <ArrowUpDown className="h-4 w-4" />
                                    </button>
                                </TableHead>
                                <TableHead className="text-electric font-semibold">Status</TableHead>
                                <TableHead className="text-electric font-semibold">Flags</TableHead>
                                <TableHead className="text-electric font-semibold">Last Active</TableHead>
                                <TableHead className="text-electric font-semibold text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {sortedStudents.map((student) => (
                                <TableRow
                                    key={student.id}
                                    className="border-b border-electric/10 hover:bg-midnight/50 transition-colors cursor-pointer"
                                    onClick={() => onViewStudent(student)}
                                >
                                    <TableCell className="font-medium text-gray-200">
                                        <div>
                                            <div>{student.name}</div>
                                            <div className="text-xs text-gray-500">{student.email}</div>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <span className={`text-2xl font-bold ${getScoreColor(student.integrityScore)}`}>
                                            {student.integrityScore}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={getGritBadgeVariant(student.gritLevel)}>
                                            {student.gritLevel}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className={`font-medium ${getStatusColor(student.status)}`}>
                                        {student.status}
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex gap-1">
                                            {student.flags.includes('disengagement') && (
                                                <Badge variant="danger" className="text-xs">
                                                    🚨 Drop Detected
                                                </Badge>
                                            )}
                                            {student.flags.includes('logic-mismatch') && (
                                                <Badge variant="warning" className="text-xs">
                                                    ⚠️ Logic Mismatch
                                                </Badge>
                                            )}
                                            {student.flags.length === 0 && (
                                                <span className="text-gray-500 text-xs">None</span>
                                            )}
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-gray-400 text-sm">{student.lastActive}</TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onViewStudent(student);
                                            }}
                                            className="border-electric/30 text-electric hover:bg-electric/10"
                                        >
                                            <Eye className="h-4 w-4 mr-1" />
                                            View
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </CardContent>
        </Card>
    );
}
