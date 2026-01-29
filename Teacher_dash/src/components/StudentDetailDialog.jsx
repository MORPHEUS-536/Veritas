import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import ThoughtEvolutionViewer from './ThoughtEvolutionViewer';
import SocraticDefenseAuditor from './SocraticDefenseAuditor';
import { Badge } from './ui/badge';
import { User, Mail, Clock, TrendingUp } from 'lucide-react';

export default function StudentDetailDialog({ student, open, onOpenChange, onApproveCertificate }) {
    if (!student) return null;

    const getScoreColor = (score) => {
        if (score >= 85) return 'text-green-400';
        if (score >= 70) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto bg-midnight border-electric/30">
                <DialogHeader>
                    <DialogTitle className="text-2xl text-electric flex items-center gap-3">
                        <User className="h-6 w-6" />
                        {student.name}
                    </DialogTitle>
                    <DialogDescription className="text-gray-400">
                        Comprehensive student analysis and validation
                    </DialogDescription>
                </DialogHeader>

                {/* Student Overview */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="bg-midnight-light p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Mail className="h-4 w-4 text-gray-400" />
                            <span className="text-xs text-gray-400">Email</span>
                        </div>
                        <div className="text-sm text-gray-200 truncate">{student.email}</div>
                    </div>
                    <div className="bg-midnight-light p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <TrendingUp className="h-4 w-4 text-gray-400" />
                            <span className="text-xs text-gray-400">Integrity Score</span>
                        </div>
                        <div className={`text-2xl font-bold ${getScoreColor(student.integrityScore)}`}>
                            {student.integrityScore}
                        </div>
                    </div>
                    <div className="bg-midnight-light p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs text-gray-400">Grit Level</span>
                        </div>
                        <Badge variant={student.gritLevel === 'Elite' ? 'default' : 'secondary'}>
                            {student.gritLevel}
                        </Badge>
                    </div>
                    <div className="bg-midnight-light p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <Clock className="h-4 w-4 text-gray-400" />
                            <span className="text-xs text-gray-400">Last Active</span>
                        </div>
                        <div className="text-sm text-gray-200">{student.lastActive}</div>
                    </div>
                </div>

                {/* Tabs for Different Views */}
                <Tabs defaultValue="evolution" className="w-full">
                    <TabsList className="grid w-full grid-cols-2 bg-midnight-light">
                        <TabsTrigger value="evolution" className="data-[state=active]:bg-electric data-[state=active]:text-white">
                            Thought Evolution
                        </TabsTrigger>
                        <TabsTrigger value="socratic" className="data-[state=active]:bg-electric data-[state=active]:text-white">
                            Socratic Defense
                        </TabsTrigger>
                    </TabsList>
                    <TabsContent value="evolution" className="mt-4">
                        <ThoughtEvolutionViewer student={student} />
                    </TabsContent>
                    <TabsContent value="socratic" className="mt-4">
                        <SocraticDefenseAuditor student={student} onApproveCertificate={onApproveCertificate} />
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}
