import { useState } from 'react';
import Header from '../components/Header';
import StruggleHeatmap from '../components/StruggleHeatmap';
import StudentDetailDialog from '../components/StudentDetailDialog';
import { mockStudents } from '../data/mockStudentData';
import { Users, TrendingUp, AlertTriangle, Award } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

export default function TeacherDashboard() {
    const [students, setStudents] = useState(mockStudents);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);

    const handleViewStudent = (student) => {
        setSelectedStudent(student);
        setDialogOpen(true);
    };

    const handleApproveCertificate = (studentId) => {
        setStudents(prevStudents =>
            prevStudents.map(student =>
                student.id === studentId
                    ? { ...student, socraticResults: { ...student.socraticResults, certificateApproved: true } }
                    : student
            )
        );
    };

    // Calculate statistics
    const totalStudents = students.length;
    const avgIntegrityScore = (students.reduce((sum, s) => sum + s.integrityScore, 0) / totalStudents).toFixed(1);
    const atRiskStudents = students.filter(s => s.integrityScore < 60).length;
    const certificatesIssued = students.filter(s => s.socraticResults.certificateApproved).length;

    return (
        <div className="min-h-screen bg-midnight text-gray-100">
            <Header />

            <main className="max-w-[1400px] mx-auto px-6 py-8">
                {/* Mission Control Header */}
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-electric mb-2">Mission Control</h2>
                    <p className="text-gray-400">
                        High-intensity command center for identifying real builders through execution quality
                    </p>
                </div>

                {/* Statistics Cards */}
                <div className="grid grid-cols-4 gap-6 mb-8">
                    <Card className="bg-midnight-light border-electric/20">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-gray-400">Total Students</CardTitle>
                            <Users className="h-4 w-4 text-electric" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold text-electric">{totalStudents}</div>
                            <p className="text-xs text-gray-500 mt-1">Active in class</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-midnight-light border-electric/20">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-gray-400">Avg Integrity Score</CardTitle>
                            <TrendingUp className="h-4 w-4 text-green-400" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold text-green-400">{avgIntegrityScore}</div>
                            <p className="text-xs text-gray-500 mt-1">Class average</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-midnight-light border-electric/20">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-gray-400">At Risk</CardTitle>
                            <AlertTriangle className="h-4 w-4 text-red-400" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold text-red-400">{atRiskStudents}</div>
                            <p className="text-xs text-gray-500 mt-1">Need intervention</p>
                        </CardContent>
                    </Card>

                    <Card className="bg-midnight-light border-electric/20">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium text-gray-400">Certificates Issued</CardTitle>
                            <Award className="h-4 w-4 text-yellow-400" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-3xl font-bold text-yellow-400">{certificatesIssued}</div>
                            <p className="text-xs text-gray-500 mt-1">Proof-of-Thought</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Struggle Heatmap */}
                <StruggleHeatmap students={students} onViewStudent={handleViewStudent} />

                {/* Student Detail Dialog */}
                <StudentDetailDialog
                    student={selectedStudent}
                    open={dialogOpen}
                    onOpenChange={setDialogOpen}
                    onApproveCertificate={handleApproveCertificate}
                />
            </main>
        </div>
    );
}
