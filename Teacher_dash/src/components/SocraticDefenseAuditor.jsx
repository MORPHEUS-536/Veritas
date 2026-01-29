import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { CheckCircle2, XCircle, AlertCircle, Award } from 'lucide-react';

export default function SocraticDefenseAuditor({ student, onApproveCertificate }) {
    const { socraticResults } = student;
    const [certificateApproved, setCertificateApproved] = useState(socraticResults.certificateApproved);

    const handleApprove = () => {
        setCertificateApproved(true);
        onApproveCertificate(student.id);
    };

    const getScoreColor = (score) => {
        if (score >= 85) return 'text-green-400';
        if (score >= 70) return 'text-yellow-400';
        return 'text-red-400';
    };

    const accuracyRate = ((socraticResults.correctAnswers / socraticResults.questionsAsked) * 100).toFixed(0);

    return (
        <Card className="bg-midnight-light border-electric/20">
            <CardHeader>
                <CardTitle className="text-electric flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Socratic Defense Auditor
                </CardTitle>
                <CardDescription className="text-gray-400">
                    AI-led interview results and knowledge validation
                </CardDescription>
            </CardHeader>
            <CardContent>
                {/* Overall Score */}
                <div className="bg-midnight p-6 rounded-lg border border-electric/20 mb-6">
                    <div className="text-center">
                        <div className="text-sm text-gray-400 mb-2">Overall Validation Score</div>
                        <div className={`text-6xl font-bold ${getScoreColor(socraticResults.overallScore)}`}>
                            {socraticResults.overallScore}
                        </div>
                        <div className="text-sm text-gray-500 mt-2">
                            {socraticResults.correctAnswers} / {socraticResults.questionsAsked} questions answered correctly
                        </div>
                    </div>
                </div>

                {/* Interview Statistics */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <CheckCircle2 className="h-4 w-4 text-green-400" />
                            <span className="text-sm text-gray-400">Accuracy Rate</span>
                        </div>
                        <div className="text-2xl font-bold text-green-400">{accuracyRate}%</div>
                    </div>
                    <div className="bg-midnight p-4 rounded-lg border border-electric/20">
                        <div className="flex items-center gap-2 mb-2">
                            <AlertCircle className="h-4 w-4 text-red-400" />
                            <span className="text-sm text-gray-400">Knowledge Gaps</span>
                        </div>
                        <div className="text-2xl font-bold text-red-400">{socraticResults.knowledgeGaps.length}</div>
                    </div>
                </div>

                {/* Knowledge Gaps */}
                {socraticResults.knowledgeGaps.length > 0 && (
                    <div className="mb-6">
                        <div className="flex items-center gap-2 mb-3">
                            <XCircle className="h-4 w-4 text-red-400" />
                            <span className="font-medium text-gray-300">Identified Knowledge Gaps</span>
                        </div>
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                            <div className="space-y-2">
                                {socraticResults.knowledgeGaps.map((gap, index) => (
                                    <div key={index} className="flex items-start gap-2">
                                        <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2"></div>
                                        <span className="text-sm text-red-300">{gap}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Sample Interview Questions */}
                <div className="mb-6">
                    <div className="font-medium text-gray-300 mb-3">Sample Interview Questions</div>
                    <div className="space-y-3">
                        {[
                            { q: "Explain the difference between deductive and inductive reasoning", correct: socraticResults.overallScore > 70 },
                            { q: "Identify the logical fallacy in the given argument", correct: socraticResults.overallScore > 60 },
                            { q: "Construct a valid syllogism on the topic", correct: socraticResults.overallScore > 50 },
                        ].map((item, index) => (
                            <div key={index} className="bg-midnight p-3 rounded-lg border border-electric/20 flex items-start gap-3">
                                {item.correct ? (
                                    <CheckCircle2 className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                                ) : (
                                    <XCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                                )}
                                <span className="text-sm text-gray-300">{item.q}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Certificate Approval */}
                <div className="bg-midnight p-6 rounded-lg border border-electric/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="font-medium text-gray-300 mb-1">Veritas Proof-of-Thought Certificate</div>
                            <div className="text-sm text-gray-400">
                                {certificateApproved
                                    ? 'Certificate has been approved and issued'
                                    : 'Review validation results before approving certificate'}
                            </div>
                        </div>
                        {certificateApproved ? (
                            <Badge variant="default" className="bg-green-500 text-white">
                                <CheckCircle2 className="h-4 w-4 mr-1" />
                                Approved
                            </Badge>
                        ) : (
                            <Button
                                onClick={handleApprove}
                                disabled={socraticResults.overallScore < 70}
                                className={`${socraticResults.overallScore >= 70
                                        ? 'bg-electric hover:bg-electric-dark'
                                        : 'bg-gray-600 cursor-not-allowed'
                                    }`}
                            >
                                <Award className="h-4 w-4 mr-2" />
                                Approve Certificate
                            </Button>
                        )}
                    </div>
                    {socraticResults.overallScore < 70 && !certificateApproved && (
                        <div className="mt-3 text-xs text-yellow-400 flex items-center gap-2">
                            <AlertCircle className="h-4 w-4" />
                            Student must achieve a score of 70 or higher to qualify for certification
                        </div>
                    )}
                </div>

                {/* Validation Node Status */}
                <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                    <span>Validation Node: Active</span>
                    <span className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        Last updated: {new Date().toLocaleTimeString()}
                    </span>
                </div>
            </CardContent>
        </Card>
    );
}
