import { useState } from 'react';
import Header from '../components/Header';
import StruggleHeatmap from '../components/StruggleHeatmap';
import StudentDetailDialog from '../components/StudentDetailDialog';
import ClassroomHealthOverview from '../components/ClassroomHealthOverview';
import IntegrityVsAnxietyFilter from '../components/IntegrityVsAnxietyFilter';
import PredictiveInterventionTrigger from '../components/PredictiveInterventionTrigger';
import VelocityTrackingAndPairing from '../components/VelocityTrackingAndPairing';
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
    
    // Calculate ECI metrics
    const studentsActive = students.filter(s => s.isActive !== false).length;
    const studentsFlagged = students.filter(s => s.integrityScore < 60 || s.suddenJumpFlag).length;
    const studentsHighRisk = students.filter(s => s.dropoutRiskLevel === 'HIGH' || s.stagnationDurationMinutes > 20).length;
    const averageProgressScore = Math.round(students.reduce((sum, s) => sum + (s.learningProgressScore || 0), 0) / totalStudents);
    
    // Determine stagnation trend
    const stagnationTrend = averageProgressScore < 50 && studentsHighRisk > totalStudents * 0.2
      ? '⚠️ Average progress has dropped 15%+ while stagnation increases. Material may need re-explanation.'
      : null;
    
    // Find top sticking point
    const conceptCounts = {};
    students.forEach(s => {
      if (s.conceptName) {
        conceptCounts[s.conceptName] = (conceptCounts[s.conceptName] || 0) + 1;
      }
    });
    const topStickingPoint = Object.entries(conceptCounts).sort(([, a], [, b]) => b - a)[0]?.[0] || 'None identified';
    
    // Determine classroom health
    const getClassroomHealth = () => {
      if (studentsHighRisk > totalStudents * 0.3) return 'AT-RISK';
      if (averageProgressScore > 70) return 'ACCELERATING';
      return 'STABLE';
    };

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

                {/* ECI System - Classroom Intelligence */}
                <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
                  <h3 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#f1f5f9', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    🧠 Educational Cohort Intelligence (ECI)
                  </h3>

                  {/* Classroom Health - Full Width */}
                  <div style={{ marginBottom: '2rem' }}>
                    <ClassroomHealthOverview 
                      totalStudents={totalStudents}
                      studentsActive={studentsActive}
                      studentsFlagged={studentsFlagged}
                      studentsHighRisk={studentsHighRisk}
                      averageProgressScore={averageProgressScore}
                      stagnationTrend={stagnationTrend}
                    />
                  </div>

                  {/* Integrity vs Anxiety Analysis */}
                  <div style={{ marginBottom: '2rem' }}>
                    <IntegrityVsAnxietyFilter students={students} />
                  </div>

                  {/* Predictive Interventions */}
                  <div style={{ marginBottom: '2rem' }}>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '1rem' }}>
                      🎯 Predictive Interventions & Risk Management
                    </h3>
                    <PredictiveInterventionTrigger students={students} />
                  </div>

                  {/* Velocity & Pairing */}
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '1rem' }}>
                      📊 Advanced Learning Analytics
                    </h3>
                    <VelocityTrackingAndPairing students={students} />
                  </div>
                </div>

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
