import { GraduationCap, LogOut } from 'lucide-react';

export default function Header({ teacherName = "Dr. Sarah Williams" }) {
    return (
        <header className="bg-midnight border-b border-electric/20 sticky top-0 z-40">
            <div className="max-w-[1400px] mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo and Title */}
                    <div className="flex items-center gap-4">
                        <div className="bg-electric p-2 rounded-lg">
                            <GraduationCap className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-electric">Veritas Command Center</h1>
                            <p className="text-sm text-gray-400">Teacher Dashboard</p>
                        </div>
                    </div>

                    {/* Teacher Info */}
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <div className="text-sm font-medium text-gray-200">{teacherName}</div>
                            <div className="text-xs text-gray-500">Instructor</div>
                        </div>
                        <button className="p-2 hover:bg-midnight-light rounded-lg transition-colors text-gray-400 hover:text-electric">
                            <LogOut className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}
